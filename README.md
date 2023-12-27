# spelling_bee
## **spelling_bee** is a full-featured, interactive spelling bee study tool coded in Python 


## Features:
-   Artificial voice prompt supplies proper pronunciation
-   Supplies, upon user request, a word's definition, etymology, part of speech, example usage sentence, and phonetic spelling--all sourced from the [Merriam-Webster](https://www.merriam-webster.com/) dictionary (official dictionary of the Scripps Howard Bee)
-   Study words from a specified difficulty level using sequential studying starting at input word index, using previously missed words, or using randomly selected words
-   Keeps track of words misspelled by the user; misspelled words can be reviewed later using the missed studying option
-	Users can customize appearance and behavior by editing the [config file](/user_config.ini)


## Notes:
This version of [spelling_bee](/spelling_bee_main.py) is optimized to be compiled as a standalone executable program using [PyInstaller](https://pyinstaller.readthedocs.io/en/stable/).  The splash screen and icon are included in this repository also.

### The accompanying .CSV files
This program requires two .csv files to operate: 
-   [Words_of_champions_2022.csv](/Words_of_champions_2022.csv) contains all spelling words, divided by columns into unique difficulty levels
-   [word_stats_2022.csv](/word_stats_2022.csv) contains a list of words missed by the user
N.B. The (relative) paths to each of these files must be inputted into the [config file](/user_config.ini) under the correct section


### Using a different list of spelling words:
The author of this program developed it to use the 2022 Scripts Howard official list "Words of Champions." However, users may want to update the word list in future years.
	
1. Find the current list of spelling bee words ("Words of Champions") on the [Scripps Howard website](https://spellingbee.com/).
2. Insert the words (copying and pasting en masse works well) according to their difficulty levels to the proper columns of the [word list](/Words_of_champions_2022)
3. Remove all asterisks ("*") and non-spelling words; separate alternate spellings of a single word (put in a single cell) by a semicolon and a space
	-   e.g. `honor; honour`
4. Ensure that the path entry in the [config file](/user_config.ini) is up to date if it was renamed or moved

### Clearing user spelling history:
Users may clear their spelling history by opening the [word_stats](/word_stats_2022.csv) file and deleting all the non-header rows (not the first row)
Likewise, to edit the place last left off, open the [config file](/user_config.ini) and change the `progressHistory` one or more indices (order corresponding to `one_bee`, `two_bee`, `three_bee`) to the desired index

## License

[The GNU General Public License v3.0](LICENSE) Copyright © 2023 Peter Reynolds
