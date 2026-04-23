%[text] ## Section 1: Spinner
spinner = 0; %[control:spinner:5a39]{"position":[11,12]}
%[text] ## Section 2: Button
  %[control:button:3204]{"position":[1,2]}
fprintf('Spinner value is %d',spinner); %[output:341e34af]
%[text] 

%[appendix]{"version":"1.0"}
%---
%[metadata:view]
%   data: {"layout":"hidecode"}
%---
%[control:spinner:5a39]
%   data: {"defaultValue":0,"label":"Spinner","max":100,"min":-100,"run":"Nothing","runOn":"ValueChanging","step":1}
%---
%[control:button:3204]
%   data: {"label":"Run","run":"Section"}
%---
%[output:341e34af]
%   data: {"dataType":"text","outputData":{"text":"Spinner value is 3","truncated":false}}
%---
