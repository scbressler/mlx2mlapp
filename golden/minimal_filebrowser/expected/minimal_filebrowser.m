classdef minimal_filebrowser < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure            matlab.ui.Figure
        File                matlab.ui.control.EditField
        FileCodeTextArea    matlab.ui.control.TextArea
        FileOutputTextArea  matlab.ui.control.TextArea
    end

    
    properties (Access = private)
        fname = '' % Description
    end
    

    % Callbacks that handle component events
    methods

        % Value changed function: File
        function FileValueChanged(app, event)
            app.fname = app.File.Value;
            diaryFile = [tempname '.txt'];
            diary(diaryFile);
            diary('on');
            disp(app.fname)
            diary('off');
            if exist(diaryFile, 'file')
                capturedOutput = fileread(diaryFile);
                delete(diaryFile);
            else
                capturedOutput = '';
            end
            app.FileOutputTextArea.Value = strsplit(strtrim(capturedOutput), newline);
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
            <EditField name='File'>
                <Position>[20 708 1060 32]</Position>
                <Value>''</Value>
                <ValueChangedFcn>FileValueChanged</ValueChangedFcn>
            </EditField>
            <TextArea name='FileCodeTextArea'>
                <BackgroundColor>[0 0 0]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[1 1 1]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[20 578 1060 120]</Position>
                <Value>'disp(fname)'</Value>
            </TextArea>
            <TextArea name='FileOutputTextArea'>
                <BackgroundColor>[0.149 0.149 0.149]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[0.4 1 0.4]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[20 448 1060 120]</Position>
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
    <Name>minimal_filebrowser</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>0d1e2f3a-4b5c-6789-def0-789012345678</AppId>
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
