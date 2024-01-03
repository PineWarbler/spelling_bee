import sys
import pandas as pd
import numpy as np
import random
from urllib.request import urlopen
import requests
import re
import urllib
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
import unidecode
import print_colors_in_terminal
from print_colors_in_terminal import PrintAngry, PrintGreen, PrintYellow
from configparser import ConfigParser, NoOptionError  # this is for reading the .ini file containing user settings


# from get_word_assets_from_MW_online import *
def get_MW_definition(html):
    beginFlag = r'<span class="dtText">'  # ??
    # beginFlag = r'<span class="dtText"><strong class="mw_t_bc">: </strong>' # this flag only works for non-names
    closureFlag = "</span>"
    foundStarts = [m.start() for m in re.finditer(beginFlag, html)]

    if len(foundStarts) == 0:
        return None  # because couldn't find a definition

    definition = []

    for i in range(0, len(foundStarts)):
        particle = html[foundStarts[i] + len(beginFlag): html.find(closureFlag, foundStarts[i])]
        particle = re.sub('<[^<]+?>', '', particle)

        # remove colons...
        particle = particle.replace(':', '')
        definition.append(particle)
    return definition


def get_MW_etymology(html):
    beginFlag = r'<p class="et">'
    closureFlag = "</p>"
    foundStarts = [m.start() for m in re.finditer(beginFlag, html)]

    if foundStarts == []:
        return None

    etymology = []

    for i in range(0, len(foundStarts)):

        particle = html[foundStarts[i] + len(beginFlag): html.find(closureFlag, foundStarts[i])]

        if "entry" not in particle:
            particle = re.sub('<[^<]+?>', '', particle)  # remove nested <..> tags
            particle = particle.replace('\n', ' ')  # remove newline breaks
            particle = re.sub(' +', ' ', particle)  # remove double spaces
            particle = particle.replace("&amp", "and")

            etymology.append(particle)
        else:
            pass
    return etymology


def get_MW_example_sentences(html):
    soup = BeautifulSoup(html, "html.parser")

    concatenated = []
    from_web = soup.find_all("span", class_="sub-content-thread ex-sent sents")

    if from_web is not None and len(from_web) != 0:
        for i in range(0, len(from_web)):
            to_append = from_web[i].text.replace("<em>", "")
            to_append = to_append.replace("</em>", "")
            to_append = to_append.strip().split("\n")[0]  # end at end of sentence
            concatenated.append(to_append.strip())
        return concatenated
    else:
        return None


def get_MW_parts_of_speech(html):
    beginFlag = r'class="important-blue-link"'
    closureFlag = r"</span>"
    foundStarts = [m.start() for m in re.finditer(beginFlag, html)]

    partsofSpeech = ['Noun', "Verb", 'Adjective', "Adverb", 'Preposition', "Pronoun", "Conjunction", "Interjection"]
    foundPartsofSpeech = []

    for i in range(0, len(foundStarts)):

        particle = html[foundStarts[i] + len(beginFlag): html.find(closureFlag, foundStarts[i])]
        particle = re.sub('<[^<]+?>', '', particle)  # remove nested <..> tags
        particle = particle.replace('\n', '')  # remove newline breaks
        particle = re.sub(' +', ' ', particle)  # remove double spaces

        for string in partsofSpeech:
            if string.lower() in particle and string not in foundPartsofSpeech:
                foundPartsofSpeech.append(string)

    return foundPartsofSpeech


def get_MW_phonetic_spelling(html):
    soup = BeautifulSoup(html, "html.parser")

    # the Merriam-Webster dictionary has several different places in the html where it displays the phonetic spelling.
    # check each if can't find

    phoneticSpellings = soup.find("a", {"class": "play-pron-v2"})

    if phoneticSpellings is None or len(phoneticSpellings) == 0:
        # try another method
        phoneticSpellings = soup.find("div", {"class": "prons-entry-list-item"})
    if phoneticSpellings is None or len(phoneticSpellings) == 0:
        return None

    return [phoneticSpellings.text.replace("\xa0", "")]


# read in user configuration settings from the .ini file
config = ConfigParser(comment_prefixes=';', allow_no_value=True)
config.read('user_config.ini')

word_list_file = config.get("word_list_stuff", "word_list")

try:
    downloaded_word_assets_path = config.get("aux_info_files", "downloaded_word_assets_path")
except NoOptionError:
    downloaded_word_assets_path = "downloaded_word_assets.csv"
    PrintYellow(
        "You have not supplied a path or filename at which to save the downloaded word assets.  Will default to `" + downloaded_word_assets_path + "`.",
        True)

try:
    data = pd.read_csv(word_list_file, encoding="ISO-8859-1", skiprows=0)
except FileNotFoundError:
    PrintAngry(
        "Couldn't find the requested word list file: " + word_list_file + " . Check the path chosen in the user_config file.",
        True)
    time.sleep(2)
    PrintAngry("Exiting program now.", True)
    time.sleep(2)
    sys.exit()

assetDF = pd.DataFrame(
    columns=['Difficulty_Level', 'Index', 'Word', 'Definition', 'Example_Sentence', 'Part_of_Speech', 'Etymology',
             'Phonetic_Spelling'])

# read in word_list
one = np.array(data.one_bee[~pd.isnull(data.one_bee)])
two = np.array(data.two_bee[~pd.isnull(data.two_bee)])
three = np.array(data.three_bee[~pd.isnull(data.three_bee)])


def rSleep():
    # optional; to evade bot-detection while scraping
    time.sleep(random.uniform(0.5, 5))


together = [one, two, three]  # one,
# together = [["floruit", "orthogonal", "marimba", "zurna", "exodus"]]

noneFoundString = "None"

currRow = 0

for l in tqdm(range(0, len(together)), desc="difficulty level", leave=True):  # for each difficulty level
    for w in tqdm(range(0, len(together[l])), desc="word index", leave=False):  # for each word index in that level
        difficulty = l + 1  # because zero-based indexing
        index = w

        word_raw = together[l][w]
        word = word_raw.split(";")[0].strip()
        word = word.replace(" ", "%20")
        word = unidecode.unidecode(word)

        # all of the get_MW_... functions return a list, so reformat each list as a single string delimited by `%`

        asset_types = ["Definition", "Example_Sentence", "Part_of_Speech", "Etymology", "Phonetic_Spelling"]

        # create a new empty row which will later be filled out and appended to pandas DF
        newRow = {
            'Difficulty_Level': difficulty,
            'Index': index,
            'Word': word_raw,
            'Definition': noneFoundString,
            'Example_Sentence': noneFoundString,
            'Part_of_Speech': noneFoundString,
            'Etymology': noneFoundString,
            'Phonetic_Spelling': noneFoundString
        }
        rSleep()
        baseurl = "https://www.merriam-webster.com/dictionary/"
        url = baseurl + word.replace(" ", "%20")
        max_retries = 5
        delay = random.uniform(0.7, 5)  # seconds
        for h in range(max_retries):
            try:
                page = urlopen(url)  # may raise an assortment of errors, but these will be caught by calling methods
                html = page.read().decode("utf-8")
                break
            except ConnectionResetError:
                # try again... see https://stackoverflow.com/a/71330299
                time.sleep(delay)
                delay *= 5
                print("Encountered a connection reset error. Attempt #" + str(h) + " of " + str(max_retries))
            except urllib.error.HTTPError:
                print_colors_in_terminal.PrintYellow(
                    "Couldn't get any assets for the word `" + word + "` because it doesn't appear to exist on the Merriam-Webster online dictionary",
                    True)
                break
            except urllib.error.URLError:
                print_colors_in_terminal.PrintYellow(
                    "No internet connection could be found, so the program will quit in 5 seconds.", True)
                time.sleep(5)
                sys.exit(1)

        for asset_type in asset_types:

            if asset_type == "Definition":
                definition = get_MW_definition(html)
                if definition is not None:
                    newRow["Definition"] = "%".join(definition)

            elif asset_type == "Example_Sentence":
                example_sentence = get_MW_example_sentences(html)
                if example_sentence is not None:
                    newRow["Example_Sentence"] = "%".join(example_sentence)

            elif asset_type == "Part_of_Speech":
                part_of_speech = get_MW_parts_of_speech(html)
                if part_of_speech is not None:
                    newRow["Part_of_Speech"] = "%".join(part_of_speech)

            elif asset_type == "Etymology":
                etymology = get_MW_etymology(html)
                if etymology is not None:
                    newRow["Etymology"] = "%".join(etymology)

            elif asset_type == "Phonetic_Spelling":
                phonetic_spelling = get_MW_phonetic_spelling(html)
                if phonetic_spelling is not None:
                    newRow["Phonetic_Spelling"] = "%".join(phonetic_spelling)
            else:
                raise AttributeError("Invalid asset request string.")

        assetDF = assetDF.append(newRow, ignore_index=True)

        currRow += 1
        # print(currRow, word_raw.split(";")[0].strip())

    assetDF.to_csv(downloaded_word_assets_path, index=False, encoding='utf-16', errors='ignore')
PrintGreen("Finished downloading the assets, which may be found in '" + downloaded_word_assets_path + "'", True)
