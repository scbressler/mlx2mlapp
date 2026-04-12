mydate = datetime("2026-04-10", "InputFormat", "uuuu-MM-dd"); %[control:datePicker:1c4c]{"position":[10,61]}
disp(mydate); %[output:82e2bc54]

%[appendix]{"version":"1.0"}
%---
%[metadata:view]
%   data: {"layout":"onright"}
%---
%[control:datePicker:1c4c]
%   data: {"displayFormat":"dd-MMM-uuuu","label":"Date picker","run":"Section"}
%---
%[output:82e2bc54]
%   data: {"dataType":"text","outputData":{"text":"   10-Apr-2026\n\n","truncated":false}}
%---
