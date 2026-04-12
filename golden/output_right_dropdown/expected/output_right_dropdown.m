classdef output_right_dropdown < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure                matlab.ui.Figure
        DropDown                matlab.ui.control.DropDown
        DropDownCodeTextArea    matlab.ui.control.TextArea
        DropDownOutputTextArea  matlab.ui.control.TextArea
    end

    
    properties (Access = private)
        value = 'one' % Description
    end
    

    % Callbacks that handle component events
    methods

        % Value changed function: DropDown
        function DropDownValueChanged(app, event)
            app.value = app.DropDown.Value;
            diaryFile = [tempname '.txt'];
            diary(diaryFile);
            diary('on');
            disp(app.value);
            diary('off');
            if exist(diaryFile, 'file')
                capturedOutput = fileread(diaryFile);
                delete(diaryFile);
            else
                capturedOutput = '';
            end
            app.DropDownOutputTextArea.Value = strsplit(strtrim(capturedOutput), newline);
        end
    end

end

%[appendix]
%---
%[app:layout]
%{
<?xml version='1.0' encoding='UTF-8'?>
<Components>
    <UIFigure name='UIFigure'>
        <Name>'MATLAB App'</Name>
        <Position>[100 100 1100 760]</Position>
        <Children>
            <DropDown name='DropDown'>
                <Items>{'one', 'two'}</Items>
                <Position>[20 708 520 32]</Position>
                <Value>'one'</Value>
                <ValueChangedFcn>DropDownValueChanged</ValueChangedFcn>
            </DropDown>
            <TextArea name='DropDownCodeTextArea'>
                <BackgroundColor>[0 0 0]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[1 1 1]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[20 578 520 120]</Position>
                <Value>'disp(value);'</Value>
            </TextArea>
            <TextArea name='DropDownOutputTextArea'>
                <BackgroundColor>[0.149 0.149 0.149]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[0.4 1 0.4]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[560 578 520 120]</Position>
                <Value>''</Value>
            </TextArea>
        </Children>
    </UIFigure>
</Components>
%}

%---
%[app:appDetails]
%{
<?xml version='1.0' encoding='UTF-8'?>
<AppDetails>
    <Name>output_right_dropdown</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>e5f6a7b8-c9d0-1234-efab-234567890123</AppId>
    <AppType>Standard</AppType>
    <MATLABRelease>R2025b</MATLABRelease>
    <MinimumSupportedMATLABRelease>R2025a</MinimumSupportedMATLABRelease>
</InternalData>
%}

%---
%[app:thumbnail]
%{
<!-- Thumbnail is used by file previewers. To change how the thumbnail is captured or stored, use the App Details dialog box in App Designer. -->
<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<Thumbnail autoCapture='true'></Thumbnail>
%}
