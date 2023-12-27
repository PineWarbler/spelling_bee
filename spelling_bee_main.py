# -*- coding: utf-8 -*-
"""
Created on Mon Jan  3 10:04:49 2022

@author: Peter Reynolds
"""
import sys

# import library for managing the splash screen
try:
    import pyi_splash
except:
    pass

import unidecode
import pandas as pd
import numpy as np
import random
from gtts import gTTS
import os
import playsound
import datetime
import csv
import time
from colorama import just_fix_windows_console
import pwinput
from print_colors_in_terminal import PrintAngry, PrintGreen, PrintYellow
from configparser import ConfigParser  # this is for reading the .ini file containing user settings

from get_word_info_functions import *


def scrub_word_list(word_list):
    # clean up each word spelling...
    newList = [None] * len(word_list)  # create empty list
    newList = word_list
    for i in range(len(word_list)):
        newList[i] = newList[i].lower()  # put in lowercase
        newList[i] = newList[i].replace(' ', '')  # remove spaces
        newList[i] = newList[i].replace('-', '')  # remove hyphens
        newList[i] = newList[i].replace('.', '')  # remove periods
        newList[i] = newList[i].replace("'", '')  # remove apostrophes
    return word_list


def speak(text,
          maxDictationLength,
          folder="",
          filename="auto-discard_spelling_bee_audio.mp3"):
    splitted = text.split(" ")  # create list containing each word
    if len(splitted) > maxDictationLength:  # cap at maximum
        splitted = splitted[0:maxDictationLength]
        text = ' '.join(splitted)
        text += '.............et cetera'  # the repeated ellipsis is for a pause

    tts = gTTS(text=text, lang='en', tld='com')

    path = folder + filename

    if os.path.isfile(path):  # if the file already exists, erase it to avoid raising a Permission Error
        os.remove(path)

    tts.save(path)
    playsound.playsound(path, block=True)
    os.remove(path)


def prepare_list_for_speech(myList):
    # include commas and 'or' between possibilities...
    if len(myList) > 1:
        t = ''
        for i in range(len(myList) - 1):
            t += myList[i] + ', '
        t += 'or ' + myList[len(myList) - 1]
    else:
        t = myList[0]
    return t


def record_mistake(filename, difficulty_level, word_index, correct_spelling, wrong_spelling, timestamp_formatted,
                   timestamp_raw):
    # writing to csv file 
    try:
        with open(filename, 'a', newline='') as csvfile:  # a for append (don't overwrite previous entries)
            # creating a csv writer object 
            csvwriter = csv.writer(csvfile)

            # writing the current data row
            csvwriter.writerow(
                [difficulty_level, word_index, correct_spelling, wrong_spelling, timestamp_formatted, timestamp_raw])
    except PermissionError:
        errorString = "Unable to load '" + filename + "'\nCheck that the above file is closed and that it exists on this machine."
        print(errorString)


def get_left_off_place(difficulty_level):
    lastLeftOff = [int(i.strip()) for i in config.get("aux_info_files", "progressHistory").split(",")]
    return lastLeftOff[difficulty_level - 1]


def record_left_off_place(difficulty_level, index):
    config = ConfigParser(comment_prefixes=';', allow_no_value=True)  # these extra arguments allow comments to be
    # preserved in the .ini file
    config.read('user_config.ini')

    s = [i.strip() for i in config.get("aux_info_files", "progressHistory").split(",")]
    s[difficulty_level - 1] = str(index)
    config.set('aux_info_files', 'progressHistory', ', '.join(s))
    try:
        with open('user_config.ini', 'w') as configfile:  # save
            config.write(configfile)

    except PermissionError:
        errorString = ("Unable to load 'user_config.ini' \nCheck that the above file is closed and that it exists on "
                       "this machine.")
        PrintAngry(errorString, useColor)


def get_missed_indices(filename):
    """Returns a numpy array of indices of words misspelled (recent to past) """
    try:
        data = pd.read_csv(filename,
                           encoding="ISO-8859-1")  # fancy encoding for the exotic markings sometimes encountered in the official word lists
    except FileNotFoundError:
        PrintAngry(
            "Couldn't find the requested mistake history file: " + filename + ". Check the path chosen in the "
                                                                              "user_config file.",
            useColor)
        time.sleep(2)
        PrintAngry("Exiting program now.", useColor)
        time.sleep(2)
        sys.exit()

    d = data.word_index.to_numpy()
    reversed_order = d[::-1]
    return reversed_order


def censor_sentence(word, sentence):
    """
    censors a word from a given sentence using a dynamic matching threshold
    Parameters
    ----------
    word : str
        word to censor (it and its variants)
    sentence : str
        example sentence

    Returns
        censored sentence (not containing word or its variants) as a str

    """
    from difflib import get_close_matches
    splitted = sentence.split(" ")  # create list containing each word

    # determine threshold
    if len(word) > 7:
        thresh = (len(word) - 3) / len(
            word)  # because three is usually the maximum # letter deviations in a word '-ing'
    else:
        thresh = 0.65  # this is a good median threshold

    closest_matches = get_close_matches(word=word, possibilities=splitted, n=len(splitted), cutoff=thresh)

    for offender in closest_matches:
        index = [i for i in range(len(splitted)) if splitted[i] == offender][0]
        splitted[index] = '**similar word**'

    back2string = ' '.join(splitted)

    return back2string


# read in user configuration settings from the .ini file
config = ConfigParser(comment_prefixes=';', allow_no_value=True)
config.read('user_config.ini')

splash_screen_visible_time = abs(config.getfloat('timing', 'splash_screen_visible_time'))
maxDictationLength = abs(config.getint("Misc", "maxDictationLength"))
useColor = config.getboolean("Misc", "use_colored_text")
if useColor:
    just_fix_windows_console()  # enables ANSI escape codes to work in the Windows terminal

hideTyping = config.getboolean("Misc", "hideTyping")
if hideTyping:
    typingMask = config.get("Misc", "typingMask")
    if len(typingMask) > 1:
        PrintYellow("Warning: typingMask will be clipped to the first character", useColor)
        typingMask = typingMask[0]
    if typingMask == '""':
        typingMask = ""

useAuralFeedbackForMisspellings = config.getboolean("Misc", "auralFeedbackForMisspellings")

word_list_file = config.get("word_list_stuff", "word_list")
mistakeHistory = config.get("aux_info_files", "mistakeHistory")

# read in the indices of the last word in each difficulty studied by the user
lastLeftOffIndices = [int(i.strip()) for i in config.get("aux_info_files", "progressHistory").split(",")]

mistake_delay = abs(config.getfloat("timing", "mistake_delay"))

valid_difficulty_choices = [1, 2, 3]

SLEEP_TIME = 5  # Not to be changed by user; for returning to main menu on error

try:
    data = pd.read_csv(word_list_file, encoding="ISO-8859-1", skiprows=0)
except FileNotFoundError:
    PrintAngry(
        "Couldn't find the requested word list file: " + word_list_file + " . Check the path chosen in the user_config file.",
        useColor)
    time.sleep(2)
    PrintAngry("Exiting program now.", useColor)
    time.sleep(2)
    sys.exit()

repeat_hotkeys = ['a', 'again']
definition_hotkeys = ['d', 'def']
usage_hotkeys = ['u', 'use']
PoS_hotkeys = ['p', 'part']
etymology_hotkeys = ['e', 'etym']
phonetic_symbol_hotkeys = ['s', 'sym']

menu_return_hotkeys = ['m', 'menu']


def print_spelling_menu():
    print("\nOptions:\n",
          repeat_hotkeys, " for repeat pronunciation\n",
          definition_hotkeys, "   for definitions\n",
          usage_hotkeys, "   for example sentences\n",
          PoS_hotkeys, "  for parts of speech\n",
          etymology_hotkeys, "  for etymologies\n",
          phonetic_symbol_hotkeys, "   for phonetic spellings\n\n",

          [str(i) for i in valid_difficulty_choices], "to change word difficulty level\n",
          menu_return_hotkeys, "  to see this menu again\n"
          )


one = np.array(data.one_bee[~pd.isnull(data.one_bee)])

two = np.array(data.two_bee[~pd.isnull(data.two_bee)])

three = np.array(data.three_bee[~pd.isnull(data.three_bee)])

together = [one, two, three]

# close the splash screen before running the main program
# if pyi_splash.is_alive():
#     # Close the splash screen. It does not matter when the call
#     # to this function is made, the splash screen remains open until
#     # this function is called or the Python program is terminated.
#     time.sleep(splash_screen_visible_time)  # don't want startlingly quick closing splash screen
#     pyi_splash.close()

print('Welcome to the Study Hive!\n=======================\n')
print('© 2023 Peter Reynolds\n')
print('Press CTRL + C to exit the program at any time.\n')
print("All spelling mistakes are logged in", mistakeHistory)

reset_loop = True  # flag for catching if user reaches end of spelling list and must return to main menu

while True:
    if reset_loop == True:
        reset_loop = False  # reset to not continue looping

        print_spelling_menu()

        # get word difficulty
        valid_input = False
        while not valid_input:
            difficulty = input('Please enter a word difficulty level [1] [2] [3] : \n> ')

            try:
                int(difficulty)
                if int(difficulty) in valid_difficulty_choices:
                    valid_input = True
                else:
                    PrintAngry("That is not an option. Please input a valid difficulty level.", useColor)
            except:
                PrintAngry("That is not an option. Please input a valid integer difficulty level.", useColor)

        # get starting point
        valid_input = False
        while not valid_input:
            print("\n----- Study Options -----")
            print(" Start sequential studying at word index                                 (enter an integer)\n",
                  "Start sequentially where you previously left off                        (enter `p` or `prev`)\n",
                  "Start random-order studying at random starting index                    (enter `r` or `random`)\n",
                  "Start studying missed words (all difficulties; from recent to older)    (enter `m` or `miss`)"
                  )
            style_input = input('>  ')

            if style_input in ['r', 'random']:
                valid_input = True
                style = 'random'
            elif style_input in ['p', 'prev']:
                valid_input = True
                style = 'previous'
                # get the current progress state now before looping commences to minimize unnecessary .csv readings
                previous_index = get_left_off_place(difficulty_level=int(difficulty))
            elif style_input in ['m', 'miss']:
                valid_input = True
                style = 'miss'
                review_array = get_missed_indices(mistakeHistory)
            else:  # then input should be an integer as index
                try:
                    int(style_input)
                    valid_input = True
                    style = 'index'
                except:
                    printAngry(str(style_input) + " is not an option. Please input a valid integer or string.",
                               useColor)

        index_counter = 0
        while True:

            if style == 'random':
                current_word_index = random.randint(0, len(together[int(difficulty) - 1]) - 1)
                rawWord = together[int(difficulty) - 1][current_word_index]
                begin_index = 0

            elif style == 'index':
                current_word_index = int(style_input) + index_counter
                try:
                    rawWord = together[int(difficulty) - 1][current_word_index]
                except IndexError:
                    # congratulate user on level completion and return to main menu
                    exitString = '\nCongratulations! You have reached the end of level ' + str(
                        difficulty) + ' words.  Program returning to menu in ' + str(SLEEP_TIME) + ' seconds...\n'
                    print(exitString)
                    time.sleep(SLEEP_TIME)
                    reset_loop = True
                    break

                begin_index = int(style_input)

            elif style == 'previous':
                current_word_index = previous_index + index_counter
                try:
                    rawWord = together[int(difficulty) - 1][current_word_index]
                except:
                    # congratulate user on level completion and return to main menu
                    exitString = '\nCongratulations! You have reached the end of level ' + str(
                        difficulty) + ' words.  Program returning to menu in ' + str(SLEEP_TIME) + ' seconds...\n'
                    print(exitString)
                    time.sleep(SLEEP_TIME)
                    reset_loop = True
                    break

                begin_index = previous_index


            elif style == 'miss':
                try:
                    rawWord = together[int(difficulty) - 1][review_array[index_counter]]
                except:
                    # congratulate user on level completion and return to main menu
                    exitString = '\nCongratulations! You have finished reviewing missed words. Program returning to menu in ' + str(
                        SLEEP_TIME) + ' seconds...\n'
                    print(exitString)
                    time.sleep(SLEEP_TIME)
                    reset_loop = True
                    break

                current_word_index = review_array[index_counter]

            index_counter += 1

            # alternate spellings separated by `; `
            withoutAccents = unidecode.unidecode(rawWord)
            word = withoutAccents.split('; ')

            word = scrub_word_list(word)

            word_spelled = False
            while not word_spelled:

                speak("Please spell " + withoutAccents.split('; ')[0], maxDictationLength)

                if hideTyping:
                    rawSpellInput = pwinput.pwinput(prompt="Type spelling: ", mask=typingMask)
                else:
                    rawSpellInput = input("Type spelling: ")

                spellInput = scrub_word_list([rawSpellInput])[0]

                # check whether the user spelled the word correctly...
                if spellInput in word:
                    PrintGreen("Correctly Spelled! " + rawWord, useColor)
                    PrintGreen('--------', useColor)
                    word_spelled = True

                elif spellInput in definition_hotkeys:
                    definition = get_MW_definition(str(word[0]))
                    if definition == None:
                        PrintYellow("Definition: No definition found on the Merriam Webster website.  Sorry!", useColor)
                    else:
                        censored = censor_sentence(word=str(word[0]), sentence=definition[0])
                        PrintYellow("Definition: " + censored, useColor)
                        speak("Definition: " + definition[0], maxDictationLength)

                elif spellInput in usage_hotkeys:
                    usage_example = get_MW_example_sentences(str(word[0]))
                    if usage_example == None:
                        print("No example sentences found on the Merriam Webster website.  Sorry!")
                    else:
                        # censor out the word for printing...
                        censored = censor_sentence(word=str(word[0]), sentence=usage_example[0])
                        PrintYellow("Example Sentence: " + censored + '.', useColor)
                        speak("Example Sentence: " + usage_example[0], maxDictationLength)

                elif spellInput in PoS_hotkeys:
                    parts = get_MW_parts_of_speech(str(word[0]))

                    t = prepare_list_for_speech(parts)

                    PrintYellow("Part(s) of Speech: " + t, useColor)  # only show first sentence
                    speak("Parts of Speech: " + t, maxDictationLength)

                elif spellInput in phonetic_symbol_hotkeys:
                    phonetic = get_MW_phonetic_spelling(str(word[0]))
                    if phonetic is None:
                        PrintYellow("No phonetic spelling could be found on the Merriam-Webster website.  Sorry!", useColor)
                    else:
                        t = prepare_list_for_speech(phonetic)
                        PrintYellow("Phonetic Spelling: " + t, useColor)

                elif spellInput in etymology_hotkeys:
                    etymology = get_MW_etymology(str(word[0]))

                    if etymology is None or len(etymology) == 0:
                        PrintYellow("No etymology found on the Merriam-Webster website.  Sorry!", useColor)
                    else:
                        censored = censor_sentence(word=str(word[0]), sentence=etymology[0])
                        PrintYellow('Etymology: ' + censored, useColor)

                elif spellInput in repeat_hotkeys:
                    # say the word again
                    speak(withoutAccents.split('; ')[0], maxDictationLength)

                elif spellInput in [str(i) for i in valid_difficulty_choices]:
                    if int(spellInput) != difficulty:
                        print(
                            '\nDifficulty now changed to level ' + spellInput + ' words. Study style is still set to ' + style + ' studying.\n')
                        difficulty = int(spellInput)
                        break
                    else:
                        print('\nDifficulty level is already set to ' + spellInput + ' words.\n')

                elif spellInput in menu_return_hotkeys:
                    print_spelling_menu()

                else:
                    if hideTyping:
                        PrintAngry("Oops! What you said: " + rawSpellInput, useColor)  # show the user what he inputted
                    else:
                        PrintAngry("Oops! Not quite.",
                                   useColor)  # don't need to repeat the user's input because his typing is visible

                    PrintAngry("Correct: " + rawWord, useColor)

                    if useAuralFeedbackForMisspellings:
                        speak("The correct spelling is " + " ".join(rawWord.replace(";", " or ")), 1E9)

                    time.sleep(mistake_delay)

                    print('--------')

                    time.sleep(mistake_delay)

                    word_spelled = True

                    # record mistake in mistake csv file
                    thisTime = datetime.datetime.fromtimestamp(time.time()).strftime('%c')
                    wordIndex = current_word_index

                    record_mistake(filename=mistakeHistory,
                                   difficulty_level=difficulty,
                                   word_index=current_word_index,
                                   correct_spelling=rawWord,
                                   wrong_spelling=spellInput,
                                   timestamp_formatted=thisTime,
                                   timestamp_raw=time.time())

                # record progress to progress.csv
                if style not in ['random', 'miss']:
                    record_left_off_place(int(difficulty), begin_index + index_counter)

            word_spelled = False

        else:
            pass
