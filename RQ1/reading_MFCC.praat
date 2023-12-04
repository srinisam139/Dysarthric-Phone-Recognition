if (praatVersion < 6100)
	printline Requires Praat version 6.1 or higher. Please upgrade your Praat version 
	exit
endif


reference_tier = 1
askBeforeDelete = 1

alphabets$# = {"ih", "iy", "eh", "ah", "ae", "ao", "ay", "ay", "aa", "er", "ey", "uw", "ow", "aw", "uh", "oy", "t", "r", "n", "l", "s", "d", "k", "p", "m", "z", "w", "b", "f", "dh", "g", "v", "y", "ng", "sh", "ch", "jh", "th", "zh", "h", "hh"}

file_path$ ="/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/file_paths.csv"
output_directory$ = "/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/phone_data/" 
Read Table from comma-separated file: file_path$


# Loop through the table and access individual cells
numOfTableRows = Get number of rows

writeInfoLine: "Number of rows in the csv file is ", numOfTableRows
for nt from 1 to numOfTableRows
	
	appendInfoLine: nt
	person_name$ = Get value: nt, "person_name"

	new_directory$ = output_directory$ + person_name$ + "/" + "matrix/" + person_name$ + "_" + "time_frame" + ".txt"

	if askBeforeDelete = 1 and fileReadable: new_directory$
		# pauseScript: "File exists! Deleting it!"
		appendInfoLine: "Deleting the following file: ", new_directory$
		deleteFile: new_directory$
	endif

endfor


for nt from 1 to numOfTableRows

	appendInfoLine: " ******************************************"

	person_name$ = Get value: nt, "person_name"
	session_name$ = Get value: nt, "session_name"
	file_number$ = Get value: nt, "file_number"
	prompt$ = Get value: nt, "text"
	wav_path$ = Get value: nt, "wav_file_path"
	prompt_path$ = Get value: nt, "prompt_file_path"
	phone_path$ = Get value: nt, "phn_file_path"

	if nt = 1
	appendInfoLine: person_name$, " " ,session_name$, " ", file_number$
	endif
	if nt > 1
	appendInfoLine: person_name$, " " ,session_name$, " " ,file_number$
	endif

	Read from file: wav_path$
	selectObject: "Sound " + file_number$
	To MFCC: 12, 0.015, 0.005, 100.0, 100.0, 0.0
	To Matrix
	Save as headerless spreadsheet file: output_directory$ + person_name$ + "/" + "matrix" + "/" + session_name$ + "_" + prompt$ + "_" + file_number$

	appendInfoLine: "The prompt read now is ", prompt$

	Read from file: phone_path$
	selectObject: "TextGrid " + file_number$
	total_interval = Get number of intervals: reference_tier
	appendInfoLine: "Total number of interval is ", total_interval

	new_directory$ = output_directory$ + person_name$ + "/" + "matrix/" + person_name$ + "_" + "time_frame" + ".txt"

	appendInfoLine: new_directory$
	
	appendFile: new_directory$

	for intervalNums from 1 to total_interval

		selectObject: "TextGrid " + file_number$
		intervalName$ = Get label of interval: reference_tier, intervalNums
		appendInfoLine: "Interval Number ", intervalNums, " Reading the tier ", intervalName$
		
		for i from 1 to size (alphabets$#)
			if intervalName$ = alphabets$# [i]
				selectObject: "TextGrid " + file_number$
				start = Get start time of interval: reference_tier, intervalNums
				end = Get end time of interval: reference_tier, intervalNums
				appendInfoLine: "Get start time ", start, " Get end time ", end

				selectObject: "MFCC " + file_number$
				start_frame = Get frame number from time: start
				end_frame = Get frame number from time: end
				appendInfoLine: "Get start frame ", start_frame, " Get end frame ", end_frame
				
				appendFileLine: new_directory$, "word:", "'",prompt$,"'"," ", "intervalName-", intervalName$ ," start_time:", start, " end_time:", end, " start_frame:", start_frame, " end_frame:", end_frame
			
			endif
		endfor
	endfor
	removeObject: "Matrix " + file_number$
	removeObject: "MFCC " + file_number$
	removeObject: "Sound " + file_number$
	removeObject: "TextGrid " + file_number$
	selectObject: "Table file_paths"  
endfor
