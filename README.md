# spelling_bee
## **spelling_bee** is a full-featured, interactive spelling bee study tool coded in Python 


## Features:
-   Study words from a specified difficulty level using sequential studying starting at input word index, using previously missed words, or using randomly selected words
-   Supplies, upon user request, a word's definition, etymology, part of speech, example usage sentence, and phonetic spelling--all sourced from the [Merriam Webster](https://www.merriam-webster.com/) dictionary (official dictionary of the Scripts Howard)
-   Keeps track of words misspelled by the user; misspelled words can be reviewed later using the missed studying option
-   Artificial voice prompt supplies proper pronunciation

## Notes:
This version of [spelling_bee](/spelling_bee_main.py) contains has been adapted for compiling this program as a standalone executable program using [PyInstaller](https://pyinstaller.readthedocs.io/en/stable/).  The splash screen and icon are included in this repository also.

### Explaining the accompanying .CSV files
This program requires three .csv files to operate: 
-   [words_of_champions_2022.csv](/words_of_champions_2022.csv) contains all spelling words, divided by columns into unique difficulty levels
-   [word_stats_2022.csv](/word_stats_2022.csv) contains a list of words missed by the user
-   [progress_history_2022.csv](/progress_history_2022.csv) contains the index of the most recent word which the user studied (for persistent session memory)


### Using a different list of spelling words:
The author of this program developed it to use the 2022 Scripts Howard official list "Words of Champions." However, users may want to update the word list in future years.
	
1. Find the current list of spelling bee words ("Words of Champions") on the [Scripts Howard website](https://spellingbee.com/).
2. Insert the words (copying and pasting en masse works well) according to their difficulty levels to the proper columns of the [word list](/Words_of_champions_2022)
3. Remove all asterisks ("*") and non-spelling words; separate alternate pronunciations (put in a single cell) by a semicolon and a space
	-   e.g. `honor; honour`
4. Ensure that the updated .csv file is still named "Words_of_champions_2022.csv"

### Clearing user spelling history:
Users may clear their spelling history by opening the [word_stats](/word_stats_2022.csv) file and deleting all the non-header rows (not the first row)
Likewise, to edit the place last left off, open [progress_history](progress_history_2022.csv) and change the appropriate cell values to the desired word index

## License

[The GNU General Public License v3.0](LICENSE) Copyright © 2022 Peter Reynolds
