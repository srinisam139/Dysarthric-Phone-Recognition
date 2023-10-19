if (praatVersion < 6100)
	printline Requires Praat version 6.1 or higher. Please upgrade your Praat version 
	exit
endif


reference_tier = 1

high_vowel$# = {"iy"}


file_path$ ="/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/file_paths.txt"
output_directory$ = "/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/matrix/" 
Read Table from tab-separated file: file_path$



# Loop through the table and access individual cells
numOfTableRows = Get number of rows
for nt from 1 to numOfTableRows

	appendInfoLine: " ******************************************"

	person_name$ = Get value: nt, "person_name"
	session_name$ = Get value: nt, "session_name"
	file_number$ = Get value: nt, "file_number"
	wav_path$ = Get value: nt, "wav_file_path"
	prompt_path$ = Get value: nt, "prompt_file_path"
	phone_path$ = Get value: nt, "phn_file_path"
	if nt = 1
	writeInfoLine: person_name$, " " ,session_name$, " ", file_number$
	endif
	if nt > 1
	appendInfoLine: person_name$, " " ,session_name$, " " ,file_number$
	endif

	
	Read from file: wav_path$
	selectObject: "Sound " + file_number$
	To MFCC: 12, 0.015, 0.005, 100.0, 100.0, 0.0
	To Matrix
	Save as headerless spreadsheet file: output_directory$ + person_name$ + "_" + session_name$ + "_" + file_number$

	Read Strings from raw text file: prompt_path$
	selectObject: "Strings " + file_number$
	prompt_name$ = Get string: 1
	appendInfoLine: "The prompt read now is ", prompt_name$


	Read from file: phone_path$
	selectObject: "TextGrid " + file_number$
	total_interval = Get number of intervals: reference_tier
	appendInfoLine: "Total number of interval is ", total_interval

	start_frame = 0
	end_frame = 0

	vowel_found = 1
	
	for intervalNums from 1 to total_interval
		selectObject: "TextGrid " + file_number$
		intervalName$ = Get label of interval: reference_tier, intervalNums
		appendInfoLine: "Interval Number ", intervalNums, " Reading the vector ", intervalName$
		for i from 1 to size (high_vowel$#)
			if high_vowel$# [i] == intervalName$ and vowel_found
				vowel_found = 0
				start = Get start time of interval: reference_tier, intervalNums
				end = Get end time of interval: reference_tier, intervalNums
				appendInfoLine: "Get start time ", start, " Get end time ", end
				selectObject: "MFCC " + file_number$
				start_frame = Get frame number from time: start
				end_frame = Get frame number from time: end
				appendFileLine: output_directory$ + person_name$ + "_" ,session_name$ + "_" + file_number$ + "_" +"frames", "start_frame:", start_frame, "	end_frame:", end_frame
			endif
		endfor
	endfor
	removeObject: "TextGrid "
	removeObject: "Strings " + file_number$
	selectObject: "Table file_paths"  
endfor
