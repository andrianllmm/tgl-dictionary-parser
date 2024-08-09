# Tagalog Dictionary Parser

**A Python script that parses a Tagalog dictionary website and converts it into several useful formats.**


## About

This parser parses the dictionary from [Pinoy Dictionary](https://tagalog.pinoydictionary.com/) in HTML format and outputs it to [JSON format](output/tgl_dictionary.json), [frequency list](output/tgl_freqlist.csv), and [word list](output/tgl_wordlist.txt).

## Output

> <strong style="font-size: large;">40,064 words collected</strong> <small>(as of 08/09/2024)</small>

| Resource | Format | Link |
| --- | --- | --- |
| Dictionary | json | [output/tgl_dictionary.json](output/tgl_dictionary.json) |
| Frequency list | csv | [output/tgl_freqlist.csv](output/tgl_freqlist.csv) |
| Word list | txt | [output/tgl_wordlist.txt](output/tgl_wordlist.txt) |


### JSON Dictionary

The JSON dictionary is structured as a list of words and its corresponding list of attributes. The attributes include part of speech, definition, etymology, classifications, synonyms, antonyms, example sentences, inflections, and sources. The entries are sorted alphabetically.

```json
[
    {
        "word": "The word itself",
        "attributes": [
            {
                "pos": "Simplified arts of speech",
                "definition": "The definition",
                "origin": "The etymology",
                "classification": "Any classification",
                "similar": [
                    "List of synonyms"
                ],
                "opposite": [
                    "List of antonyms"
                ],
                "examples": [
                    "List of example sentences that use the word"
                ],
                "inflections": [
                    "List of inflected forms"
                ],
                "sources": [
                    "List of sources"
                ]
            }
        ]
    },
]
```


### Frequency list

The frequency list is structured as a list of words and its corresponding frequency value derived from the [Leipzig Corpora Collection Dataset (2021 Wikipedia 100k corpus)](https://wortschatz.uni-leipzig.de/en/download/Tagalog). The list is sorted from highest to lowest frequency value.

```csv
ng,134442
sa,127336
ang,106986
```


### Word list

The word list is simply the list of words sorted alphabetically.


## License

This project is licensed under the [Apache License](LICENSE).

---

For more information contact [maagmaandrian@gmail.com](mailto:maagmaandrian@gmail.com) with any additional questions or comments.