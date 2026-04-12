classdef minimal_editfieldtext < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure            matlab.ui.Figure
        Name                matlab.ui.control.EditField
        NameCodeTextArea    matlab.ui.control.TextArea
        NameOutputTextArea  matlab.ui.control.TextArea
    end

    
    properties (Access = private)
        name = '' % Description
    end
    

    % Callbacks that handle component events
    methods

        % Value changed function: Name
        function NameValueChanged(app, event)
            app.name = app.Name.Value;
            diaryFile = [tempname '.txt'];
            diary(diaryFile);
            diary('on');
            fprintf('Hello, %s', app.name)
            diary('off');
            if exist(diaryFile, 'file')
                capturedOutput = fileread(diaryFile);
                delete(diaryFile);
            else
                capturedOutput = '';
            end
            app.NameOutputTextArea.Value = strsplit(strtrim(capturedOutput), newline);
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
            <EditField name='Name'>
                <Position>[20 708 1060 32]</Position>
                <Value>''</Value>
                <ValueChangedFcn>NameValueChanged</ValueChangedFcn>
            </EditField>
            <TextArea name='NameCodeTextArea'>
                <BackgroundColor>[0 0 0]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[1 1 1]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[20 578 1060 120]</Position>
                <Value>'fprintf(''Hello, %s'', name)'</Value>
            </TextArea>
            <TextArea name='NameOutputTextArea'>
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
    <Name>minimal_editfieldtext</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>7a8b9c0d-1e2f-3456-abcd-456789012345</AppId>
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
