function discal(AmpFileName, ChanIdx, PointIdx);
% DISCAL    Calculates calibration factors from arbitrary quantities of data. 
%           The function repeatedly calculates positions for the given samples and varies
%           re-calibration factors to harmonize the distances between
%           channels. The function can operate on any data set but may be
%           very slow when operating on large number of points. 
%
%           DisCal runs in an infinite loop. To stop it, you must delete the
%           semaphore file 'discal.lck'. (This way, the function be can easily
%           controlled remotely via a ssh or ftp connection or via a Windows share)
%
%           To save disk space and bandwith if loaded via a network connection, the
%           re-calibration data is written in a single precision binary format.
%           Use the function LoadDCData to read the binary file back into MATLAB.
%           
%           discal(AmpFileName, ChanIdx, ResultFile, DiscalOptions);
%
%           The function also creates a (text-) logfile, containing the calibration data
%           in a readable but truncated format.
%
%
%           see  CAL_PREPDATA, DISCALEVAL

%---------------------------------------------------------------------
% Copyright © 2006-2007 by Andreas Zierdt (Anderas.Zierdt@phonetik.uni-muenchen.de)
% 
% This program is free software; you can redistribute it and/or modify it under 
% the terms of the GNU General Public License as published by the 
% Free Software Foundation; either version 2 of the License, or (at your option) 
% any later version.
%
% This program is distributed in the hope that it will be useful, 
% but WITHOUT ANY WARRANTY; without even the implied warranty of
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
% GNU General Public License for more details.
%
% You should have received a copy of the GNU General Public License along with 
% this program; if not, write to the Free Software Foundation, Inc., 
% 51 Franklin Street, Fifth Floor, Boston, MA 
%---------------------------------------------------------------------
LOGFILENAME = 'discal_log.txt';
DATFILENAME = 'discal.mat';
LOCKFILENAME = 'discal.lck';
rand('state', sum(100*clock));			% random seed

if (nargin < 3)
	PointIdx = [];
end

if (nargin < 2)
	ChanIdx = 1:12;
end

% load amplitude data
[data.MAmps, data.amp_comment, data.amp_descriptor, data.amp_dimension,...
			data.amp_private, data.samplerate, data.amp_unit] = loadsdata(AmpFileName); 
if (isempty(data.MAmps))
	error(['no such file: ' AmpFileName]);
end

% TAPAD variables
data.NumPoints = size(data.MAmps, 1);
data.ReCalibrationFactors = zeros(6, 12);	% set unused channels to zero 
data.ReCalibrationFactors(:, ChanIdx) = ones(6, length(ChanIdx));
data.Result = NaN * ones(data.NumPoints, 7, 12);
data.Residuals = NaN * ones(data.NumPoints, 6, 12);	
data.TAPADIterations = zeros(data.NumPoints, 1, 12);
data.DerivativParameters = zeros(5*3+1, 6, 12);
if (isempty(PointIdx))
	data.PointIdx = 1:data.NumPoints;
elseif (max(PointIdx) > data.NumPoints)
	error('Point index too large');
else
	data.PointIdx = PointIdx;
end
if (length(ChanIdx) < 2)
	error('At least two channels required');
else
	data.ChanIdx = ChanIdx;
end
if exist(DATFILENAME)
		error(['first remove/rename ' DATFILENAME]);
end

% use this semaphore file (lock-file) as a simple method to remotely
% stop execution
[lockfile, msg] = fopen(LOCKFILENAME, 'w');
if (lockfile == -1)
	error(['can not create ' LOCKFILENAME ' ' msg]);
else
	fprintf(lockfile, '%s', 'Remove this file to stop discal');
	fclose(lockfile); clear lockfile;
end
	
disp(['Distance related re-calibration (DisCal) Version ' tapadversion ' started at ' datestr(now)]);
disp(['Amplitude file: ' AmpFileName '  DisCal data file: ' DATFILENAME]);	
disp(''); disp('Remove the file ''discal.lck'' to stop the calculation!');

% initialize result data structure
result.Version = ['Distance related re-calibration (DisCal) Version ' tapadversion];
result.AmpFileName = AmpFileName;
result.NumDataPoints = data.NumPoints;
result.ChanIdx = ChanIdx;
result.PointIdx = uint16(data.PointIdx);
BLOCKSIZE = 100;
result.ReCalibrationFactors = repmat(single(0), [6+1 length(ChanIdx) BLOCKSIZE]);

tic; data= do_tapad(data);  t = toc; result.cnt = 1;
[r, S] = SensorSpacing('', ChanIdx, data.Result(data.PointIdx, :, :), data.amp_comment, data.samplerate);
result.ReCalibrationFactors(1:6, :, result.cnt) = data.ReCalibrationFactors(:, ChanIdx)
result.ReCalibrationFactors(7, :, result.cnt) = calc_quality(ChanIdx, S);

disp(['First calculation took ' num2str(round(t/60)) ' min and ' num2str(rem(t, 60)) ' s for ' num2str(length(data.PointIdx)) ' points']);
disp(['Initial Quality: ' num2str(double(result.ReCalibrationFactors(7, :, result.cnt)) , '%6.3f')]); 

while exist(LOCKFILENAME)
	save(DATFILENAME, 'result'); 
	data.ReCalibrationFactors = zeros(6, 12);	% set unused channels to zero 
	data.ReCalibrationFactors(:, ChanIdx) = ones(6, length(ChanIdx))...
		+ 0.01 * randn(6, length(ChanIdx)); % add random values (approx. 0 - 25 Digit, 5 Digit is System Noise)
	try
		data= do_tapad(data); 				% calculate positions based on the altered ReCalibrationFactors
		result.cnt = result.cnt + 1;
		if (mod(result.cnt, BLOCKSIZE) == 0)
			result.ReCalibrationFactors = cat(3, result.ReCalibrationFactors, repmat(single(0), [6+1 length(ChanIdx) BLOCKSIZE]));
		end
		% now calculate the variance of the inter-channel distances
		[r, S] = SensorSpacing('', data.ChanIdx, data.Result(data.PointIdx, :, :), data.amp_comment, data.samplerate);
		result.ReCalibrationFactors(1:6, :, result.cnt) = data.ReCalibrationFactors(:, ChanIdx);
		result.ReCalibrationFactors(7, :, result.cnt) = calc_quality(ChanIdx, S);
		msg = num2str(result.cnt);
	catch
		msg = ['TAPAD failed: ' lasterr]; 
	end
 	disp(msg); 
	pause(1); 									% a short break to catch a possible <Ctrl-C>
end

result.ReCalibrationFactors = result.ReCalibrationFactors(:, :, 1:result.cnt); % discard unused entries
save(DATFILENAME, 'result'); 
return 

%------------- subfunctions -----------
function Q = calc_quality(ChanIdx, S)
	Q = zeros(size(ChanIdx));
	for i_chan = 1:length(ChanIdx)		% iterate channels
		channel = ChanIdx(i_chan);
		idx = find(sum(S.Channels == channel));
		Q(i_chan) = norm(S.SpatialDist.IQR(idx));
	end
return
		
% perform position calculation 
function data = do_tapad(data)
	startpoint = [0 0 0 0 0];
	Derivatives = ones(size(data.MAmps));
	lsq_options = optimset('lsqnonlin');
	lsq_options = optimset('LargeScale', 'off', 'LevenbergMarquardt', 'on', 'TolX', 1E-8, 'TolFun', 1E-8, 'MaxIter', 30, 'MaxFunEvals', 2000);
	lsq_options = optimset(lsq_options, 'Display', 'off', 'Diagnostics', 'off');
	for i_chan = 1:length(data.ChanIdx)		% iterate channels
		channel = data.ChanIdx(i_chan);
		for i_point = 1:length(data.PointIdx)					% iterate samples
			point = data.PointIdx(i_point);
			[data.Result(point, 1:7, channel), data.Residuals(point, :, channel), data.TAPADIterations(point, 1, channel)] =...
					calcpos(data.MAmps(point, :, channel) .* data.ReCalibrationFactors(:, channel)', Derivatives(point, :, channel), startpoint, lsq_options); 
			data.Result(point, 4:5, channel) = NormalizeAngles(data.Result(point, 4:5, channel));
		end
	end
return

