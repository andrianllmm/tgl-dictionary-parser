import concurrent.futures
import json
import os
import re
import requests
import sys
import time
from bs4 import BeautifulSoup

from helpers import *


script_dir = os.path.dirname(os.path.realpath(__file__))


def parse_all(auto_match=False):
    """Parses every dictionary entry from a website to a list.

    Args:
        auto_match (bool, optional): Performs auto matching if True, does not if False. Defaults to False

    Returns:
        list: A list of dictionaries, each representing a dictionary entry containing:
            - 'word': The word
            - 'pos': Parts of Speech
            - 'definitions': List of definitions
            - 'origin': Origin or etymology
            - 'classification': Some classification
            - 'similar': List of similar words
            - 'opposite': List of opposite
            - 'examples': List of examples
            - 'inflections': List of inflections
            - 'sources': List of sources

    Notes:
        Data source: Tagalog Pinoy Dictionary (https://tagalog.pinoydictionary.com/)
    """
    starting_letters = set("abcdeghijklmnoprstuwxyz")

    dictionary = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = executor.map(parse_letter, starting_letters)

        for result in results:
            dictionary.extend(result)

    if auto_match:
        return auto_match_entries(dictionary)

    return dictionary


def parse_letter(letter):
    """Parses every dictionary entry that starts with a specified letter from a website to a list.

    Args:
        letter (str): Any letter in the Tagalog alphabet.

    Returns:
        list: A list of dictionaries of the extracted dictionary entries.
    """
    letter = letter.strip().lower()

    data = []
    page_num = 1

    while True:
        print(f"Page {page_num}")

        if page_num == 1:
            url = f"https://tagalog.pinoydictionary.com/list/{letter}/"
        else:
            url = f"https://tagalog.pinoydictionary.com/list/{letter}/{page_num}/"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        }

        time.sleep(0.01)
        page = requests.get(url, headers=headers)

        if page.status_code == 404:
            print("Terminated: page not found")
            break

        soup = BeautifulSoup(page.content, "html.parser")

        entries = soup.find_all(class_="word-group")
        if not entries:
            print("Terminated: entries not present")
            break

        for entry in entries:
            if new_entry := parse_entry(entry):
                # New word
                if not data or new_entry["word"] != data[-1]["word"]:
                    data.append(new_entry)

                # Previous word if word not present and there's a previous word
                elif len(data) >= 1:
                    data[-1]["attributes"].extend(new_entry["attributes"])

        page_num += 1

    return data


def parse_entry(entry):
    """Parses a dictionary entry.

    Args:
        entry (bs4.BeautifulSoup): The dictionary entry.

    Returns:
        dict: A dictionary containing the word and its attributes.
    """
    word_html = entry.find(class_="word").find(class_="word-entry").find("a")
    source = word_html.get("href")
    full_definition_html = entry.find(class_="definition").find("p")

    word = word_html.text.strip()

    # Remove texts in parenthesis in word (e.g. https://tagalog.pinoydictionary.com/word/abay-mga/)
    word = re.sub(r"\(.+\)", "", word).strip()

    # Remove repeated words (e.g. https://tagalog.pinoydictionary.com/word/adisyon-adisyon/)
    if "," in word:
        word = word.split(",")[0].strip()

    if not is_valid(word):
        return None

    print(word)

    full_definition = full_definition_html.text.strip()

    # Removes word that is prefixed in definition (e.g. https://tagalog.pinoydictionary.com/word/aalug-alog/)
    full_definition = re.sub(f"^{word}", "", full_definition).lstrip(" .,;:!?")

    # Get inflections which is at the start of the definition and enclosed within parentheses
    # (e.g. https://tagalog.pinoydictionary.com/word/abain/)
    if match := re.match(r"^\(([^\(\)]*(?:\(.+\))?[^\(\)]*)\)", full_definition):
        inflections_str = match.group(1).replace(".", ",").strip()
        inflections = [i.strip() for i in inflections_str.split(",")]

        # Get definition by removing inflections
        full_definition = full_definition[len("(" + inflections_str + ")") :].strip()
    else:
        inflections = []

    # Get pos which is at the start of the definition with a pattern of <pos>., <pos>.; <pos>.
    # (e.g. https://tagalog.pinoydictionary.com/word/abahin/)
    if match := re.match(r"^((?:(?:\d\. )?[a-z]+\.,?;? ?)+)", full_definition):
        pos = match.group(1).strip()

        definition = full_definition[len(pos) :].strip()

        # Formats pos (e.g. 'n., pl.' => 'n.pl.')
        pos = format_pos(pos)
    else:
        pos = None

        definition = full_definition.strip()

    # Split definition based on numbers (e.g. 1. this; 2. that => ['this', 'that'])
    # (e.g. https://tagalog.pinoydictionary.com/word/abala/)
    definitions = [
        to_sentence(definition.strip(" ;"))
        for definition in re.split(r"\d+\.\s*", definition)
        if definition
    ]

    # Save attributes
    attributes = []
    for definition in definitions:
        attributes.append(
            {
                "pos": pos,
                "definition": definition,
                "origin": None,
                "classification": None,
                "similar": [],
                "opposite": [],
                "examples": [],
                "inflections": inflections,
                "sources": [source],
            }
        )

    new_entry = {"word": word, "attributes": attributes}

    return new_entry


def export(
    dictionary,
    out_path=os.path.join(script_dir, "output/tgl_dictionary.json"),
    overwrite=False,
):
    """Exports a list of dictionaries representing a dictionary entry to a JSON file.

    Args:
        dictionary (list): A list of dictionaries, each representing a dictionary entry.
        out_path (str, optional): The path to the output JSON file. Defaults to '<script_dir>/output/tgl_dictionary.json'
        overwrite (bool, optional): Overwrites existing output file if True, otherwise if False. Defaults to False.

    Returns:
        bool: True if successful, False otherwise.
    """
    print("Exporting...")

    if not overwrite and os.path.isfile(out_path):
        permit = None
        while permit not in ["y", "n"]:
            permit = input(f"{out_path} already exists.\n Overwrite? (Y/n) ").lower()
            if permit == "n":
                sys.exit("Terminated")

    with open(out_path, "w") as out_file:
        json.dump(dictionary, out_file, indent=4, ensure_ascii=False)

    print("Exported successfully.")

    return True


if __name__ == "__main__":
    export(parse_all())
