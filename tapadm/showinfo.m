function info = showinfo(FileName);
% SHOWINFO   reads the given file and returns a string with information on
%            the sample rate, data format, sensor names and the processing
%            history.
%
%            info = ShowInfo(FileName);

%---------------------------------------------------------------------
% Copyright © 2006 by Andreas Zierdt (Anderas.Zierdt@phonetik.uni-muenchen.de)
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

info = frametext('file_name', FileName);
[data, comment, descriptor, dimension, private, samplerate, unit] = loadsdata(FileName);

N = size(descriptor, 1);
desctxt = ' ';
for (i=1:N)
	desctxt = [desctxt ' ' descriptor(i, :)];
end

info = sprintf('%s\n%s', info, frametext('processing_history', comment));
info = sprintf('%s\n%s', info, frametext('sample_rate', [num2str(samplerate) ' Hz']));
info = sprintf('%s\n%s', info, frametext('data_format', desctxt));
if (size(dimension.axis, 1) == 3)
	sensor_names = char(dimension.axis{3, :});
	N = size(sensor_names, 1);
	sn = sprintf('%s', sensor_names(1, :));
	for (i=2:N)
		sn = sprintf('%s\n%s', sn, sensor_names(i, :));
	end
	info = sprintf('%s\n%s', info, frametext('sensor_names', sn));
end

sc = [num2str(size(data, 1)) ' points'];
sc = sprintf('%s\n%s', sc, [num2str(size(data, 1)/samplerate) ' s']);
info = sprintf('%s\n%s', info, frametext('data_length', sc));
