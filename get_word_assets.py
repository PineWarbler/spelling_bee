from configparser import ConfigParser, NoOptionError
import pandas as pd
from get_word_assets_from_MW_online import *
from print_colors_in_terminal import *


def cleanAssetEntryForReturn(asset_string):
    # takes in a string, returns a cleaned list
    asset_string = ' '.join(asset_string.split())  # remove instances of two or more adjacent spaces
    asset_list = asset_string.split("%")
    for i in range(0, len(asset_list)):
        asset_list[i] = asset_list[i].strip()
    return asset_list


def get_word_asset(word, difficulty_level, index, asset_type):
    """
    First, try to get asset from a .csv file downloaded on the user's machine
    If that fails, try to load directly from internet
    returns a list
    """
    try:
        asset_from_file = get_word_asset_from_file(word, difficulty_level, index, asset_type)
        if asset_from_file is not None:
            return asset_from_file
    except FileNotFoundError:
        # try to get asset from online
        try:
            if asset_type == "Definition":
                asset = get_MW_definition(word)
            elif asset_type == "Example_Sentence":
                asset = get_MW_example_sentences(word)
            elif asset_type == "Part_of_Speech":
                asset = get_MW_parts_of_speech(word)
            elif asset_type == "Etymology":
                asset = get_MW_etymology(word)
            elif asset_type == "Phonetic_Spelling":
                asset = get_MW_phonetic_spelling(word)
            else:
                raise AttributeError("Invalid asset request string.")
            return asset

        except urllib.error.HTTPError:
            print_colors_in_terminal.PrintYellow(
                "Couldn't get " + asset_type + " for word " + word + ". The word doesn't appear to exist on the "
                                                                     "Merriam-Webster"
                                                                     "dictionary website, and no pre-downloaded asset file could be "
                                                                     "found.", True)
            return None
        except urllib.error.URLError:
            print_colors_in_terminal.PrintYellow(
                "Couldn't get " + asset_type + " for word " + word + ". No internet connection could be found, and no pre-downloaded "
                                                    "asset file could be found.", True)
            return None


def get_word_asset_from_file(word, difficulty_level, index, asset_type):
    """
    Queries the file containing word assets for the requested word's asset_type
    returns `None` if no asset could be found or there was an error in retrieval
    if the asset is found, will return the asset as a list
    """

    config = ConfigParser(comment_prefixes=';', allow_no_value=True)
    config.read('user_config.ini')

    try:
        downloaded_word_assets_path = config.get("aux_info_files", "downloaded_word_assets_path")
    except NoOptionError:
        downloaded_word_assets_path = "downloaded_word_assets.csv"  # try the default path

    # try:
    # may raise a FileNotFoundError
    df = pd.read_csv(downloaded_word_assets_path, encoding="utf-16", skiprows=0, sep='\t',
                     lineterminator='\r', dtype=str)
    # except FileNotFoundError:
    #     return None

    df = df.replace(r'\n', '', regex=True)  # for some reason, files sometimes have newlines

    dl = str(difficulty_level)
    idx = str(index)
    queryString = "`Difficulty_Level` == @dl and `Index` == @idx"
    queryResult = df.query(queryString, inplace=False)

    try:
        asset = queryResult[asset_type].loc[queryResult.index[0]]
        # print("raw asset: " + asset)
    except KeyError:
        return None
    except IndexError:
        return None

    if asset == "None":
        return None
    else:
        return cleanAssetEntryForReturn(asset)


print(get_word_asset("screeno", 1, 527, "Example_Sentence"))
