import csv
import json
import os


script_dir = os.path.dirname(os.path.realpath(__file__))


def get_wordlist(dictionary):
    """Get word list from dictionary."""
    return sorted(list(set([entry["word"].lower() for entry in dictionary])))


def get_freqlist(
    wordlist,
    freqlist_org_path=os.path.join(script_dir, "data/freqlist_org.csv"),
):
    """Get frequency list from with word list.

    Notes:
        Original frequency list source: Leipzig Corpora Collection (https://wortschatz.uni-leipzig.de/tl/download)
    """
    # If frequency list is available
    if freqlist_org_path:
        with open(freqlist_org_path) as freqlist_org_file:
            freqlist_org = {
                str(row[1]): int(row[2]) for row in csv.reader(freqlist_org_file, delimiter="\t")
            }

        # Merge uppercase and lowercase words
        freqlist_lower = {}
        freqlist_upper = {}

        for word in freqlist_org:
            if word.islower():
                freqlist_lower[word] = freqlist_org[word]
            elif any(c.isupper() for c in word):
                freqlist_upper[word] = freqlist_org[word]

        for word in freqlist_upper:
            if word.lower() in freqlist_lower:
                freqlist_lower[word.lower()] += freqlist_upper[word]
            else:
                freqlist_lower[word.lower()] = freqlist_upper[word]

        freqlist_merged = freqlist_lower

        # Filter against word list
        freqlist = {}
        for word in wordlist:
            if word in freqlist_merged:
                freqlist[word] = freqlist_merged[word] + 1
            else:
                freqlist[word] = 1

    # If no frequency list is available
    else:
        freqlist = {word: 1 for word in wordlist}

    # Sort by frequency
    return dict(sorted(freqlist.items(), key=lambda x: x[1], reverse=True))


def export_wordlist(
    wordlist, out_path=os.path.join(script_dir, "output/tgl_wordlist.txt")
):
    """Export word list to a txt file.
    """
    with open(out_path, "w") as out_file:
        out_file.write("\n".join(wordlist))


def export_freqlist(
    freqlist, out_path=os.path.join(script_dir, "output/tgl_freqlist.csv")
):
    """Export frequency list to a CSV file.
    """
    with open(out_path, "w") as out_file:
        writer = csv.writer(out_file)
        for word in freqlist:
            writer.writerow([word, freqlist[word]])


def get_dictionary(in_path=os.path.join(script_dir, "output/tgl_dictionary.json")):
    """Get dictionary from a a JSON file."""
    with open(in_path) as in_file:
        return json.load(in_file)


if __name__ == "__main__":
    dictionary = get_dictionary()

    wordlist = get_wordlist(dictionary)
    export_wordlist(wordlist)

    freqlist = get_freqlist(wordlist)
    export_freqlist(freqlist)
