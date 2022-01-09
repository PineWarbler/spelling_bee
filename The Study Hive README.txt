Operating Instructions for Study Hive

© Peter Reynolds 2022
No portion of the Study Hive program may be used for commercial use.

this README last edited 01/04/2021

Operating Instructions:
	To launch the spelling app, find and start the executable file called "The Hive.exe" within the "Study Hive v. x.x.x" folder on your computer
	Other necessary operating instructions are shown inside the program
	To close the app, press CTRL + C.
	This program requires an internet connection to operate (for using voice prompts and retrieving definitions, etymologies, parts of speech, etc.)

Explaining the accompanying .CSV files
	The Hive requires three .csv files to operate: 
		a file containing all spelling words ("Words_of_champions_2022.csv"), divided by columns into unique difficulty levels
		a file containing a list of words missed by the user ("word_stats_2022.csv")
		a file containing the index of the most recent word which the user studied ("progress_history_2022.csv") (for persistent session memory)
	N.B. All three of these .csv files must be closed before launching The Hive executable.  Otherwise, missed words may not be recorded. 
	However, users may view missed terms when The Hive is not running by opening "word_stats_2022.csv".


Loading a different list of words onto The Hive:
	The author of this program developed it to use the 2022 Scripts Howard official list "Words of Champions." However, users may want to update the word list in future years.
	
	1. Find the current list of spelling bee words ("Words of Champions") on the Scripts Howard website.
	2. Insert the words (copying and pasting en masse works well) according to their difficulty levels to the proper columns of the "Words_of_champions_2022.csv"
	3. Remove all asterisks ("*") and non-spelling words; separate alternate pronunciations (put in a single cell) by a semicolon and a space
		e.g. honor; honour
	4. Ensure that the updated .csv file is still named "Words_of_champions_2022.csv" and that it is located in the same folder as The Hive executable

Clearing user spelling history:
	Users may clear their spelling history by opening "word_stats_2022.csv" and deleting all the non-header rows (not the first row)
	Likewise, to edit the place last left off, open "progress_history_2022.csv" and change the appropriate cell values to the desired word index




	