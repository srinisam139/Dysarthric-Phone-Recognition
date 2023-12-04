function extract_ema(json_file_path)

    save_directory = '/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/phone_data';
    
    % Create a container map
    countMap = containers.Map;

    % Read the JSON file and decode the data
    json_data = fileread(json_file_path);
    data_struct = jsondecode(json_data);
     
    % Iterate through the nested structure
    field_names = fieldnames(data_struct);
    for i = 1:numel(field_names)
        dir_name = field_names{i};
        disp(class(dir_name))
        values = data_struct.(dir_name);
        disp(class(values))
        
        for j = 1:numel(values)
            person_prompts = values(j);
            phones = person_prompts.text;
            pos_file_path = person_prompts.pos_file_path;
            
            data = loaddata(pos_file_path); % Loading the pos file path to extract the position data

            NumPoints = size(data,1);  % Assuming number of points is along the first dimension
	        data_idx = 1 : NumPoints;
            %disp(data_idx)
	        t = (1/200) * data_idx;
            
            for k = 1:numel(phones)
                phone = phones(k).phone;
                prompt = phones(k).prompt;
                start_time = str2double(phones(k).start_time);
                end_time = str2double(phones(k).end_time);

                % Your processing logic here for each 'phones' entry
                disp(['Directory: ', dir_name]);
                disp(['Prompt Index: ', num2str(j)]);
                disp(['phone: ',phone,' start_time: ', num2str(start_time, '%.4f'),' end_time: ', num2str(end_time, '%.4f')])

                start_time_diff = abs(t - start_time);
                end_time_diff = abs(t - end_time);
    
                %Finding the minimum value in the index
                start_minimumvalue = min(start_time_diff);
                end_minimumvalue = min(end_time_diff);

                %Finding the index of the minimum value
                start_index = find(start_time_diff == start_minimumvalue, 1);
                end_index = find(end_time_diff == end_minimumvalue, 1);
                
                disp(['start_index: ', num2str(start_index), ' end_index: ', num2str(end_index)])
                disp(['Type of start_index: ', class(start_index), ' Type of end_index: ', class(end_index)])

                %Slicing the specific phones using start_index and end_index
                sliced_data = data(start_index:end_index, :, :);
                disp(['Shape of the sliced data ', num2str(size(sliced_data))])
                

                % Checking if the prompt directory is available to save the
                % sliced EMA files in the respective prompt
                prompt_dir = fullfile(save_directory,dir_name,'EMA',prompt);
                if ~isfolder(prompt_dir)
                    mkdir(prompt_dir);
                end

                
                % Full file path
                fullFilePath = fullfile(prompt_dir, sprintf('%s_sliced.h5', phone));

                %disp(person_prompts)
                % formattedstring for dictionary
                formattedstring = sprintf('%s_%s_%s', dir_name,prompt,phone);
                
                % Check if the dataset exists
                if exist(fullFilePath, 'file') == 2
                    
                    countMap(formattedstring) = countMap(formattedstring) + 1;

                    fullFilePath = fullfile(prompt_dir, sprintf('%s_sliced_%d.h5', phone, countMap(formattedstring)));
                    
                    h5create(fullFilePath, ['/' phone], size(sliced_data));

                    % Save the array to an HDF5 file
                    h5write(fullFilePath, ['/' phone], sliced_data);
                else
                    countMap(formattedstring) = 1;

                    h5create(fullFilePath, ['/' phone], size(sliced_data))
            
                    % Save the array to an HDF5 file
                    h5write(fullFilePath, ['/' phone], sliced_data);
                end
                phones(k).ema_file_path = fullFilePath;
                %disp(phones(k))
            end
            values(j).text = phones;
        end
        data_struct.(dir_name) = values;
        %disp(data_struct.dir_name)
    end

    % Convert the updated MATLAB structure back to JSON
    updatedJsonString = jsonencode(data_struct);

    % Save the updated JSON to a file or use it as needed
    % For example, you can use the following to save to a file
    jsonFilePath = '/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/master_sliced_ema_data.json';
    fid = fopen(jsonFilePath, 'w');
    fwrite(fid, updatedJsonString, 'char');
    fclose(fid);
    
    % Display the updated JSON
    %disp(updatedJsonString);
end
