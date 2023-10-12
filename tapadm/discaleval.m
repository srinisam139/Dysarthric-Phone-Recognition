function ReCalibrationFactors = discaleval(DisCalData, ReCalibrationFactors); 

% DISCALEVAL evaluates DisCal calibration data.
%
%           S = discaleval(Filename);
%           
%           see discal.m

%---------------------------------------------------------------------
% Copyright © 2007 by Andreas Zierdt (Anderas.Zierdt@phonetik.uni-muenchen.de)
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

if (nargin < 2)
	ReCalibrationFactors = ones(6, 12);
end

%load 'E:\2007\dither_dfgmj_mo1\dc3\discal.mat';
ChanIdx = DisCalData.ChanIdx; NChannels = length(ChanIdx);
NCombinations = factorial(NChannels); SNC = sqrt(NCombinations);
N = DisCalData.cnt;
AllReCalibrationFactors = double(DisCalData.ReCalibrationFactors);
OriginalErr = AllReCalibrationFactors(7, :, 1);
disp(['Channels: ' num2str(ChanIdx)])
disp(['OriginalErr: ' num2str(OriginalErr)])

for (i=1:length(ChanIdx))
	channel = ChanIdx(i);
	
	RCF = squeeze(AllReCalibrationFactors(:, i, :))';	
	better = find(RCF(:, 7) <= OriginalErr(i));
	RCF = sortrows(RCF(better, :), 7);	
	RCF(:, 7) = RCF(:, 7) / SNC;	% Estimated position error in mm (rms over all combinations)	

	disp(['possible calibration factors for channel ' num2str(channel)])
	disp(num2str(RCF))
	ReCalibrationFactors(:, channel) = RCF(1, 1:6)';
end
