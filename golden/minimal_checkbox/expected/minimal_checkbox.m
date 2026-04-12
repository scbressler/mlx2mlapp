classdef minimal_checkbox < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure                matlab.ui.Figure
        CheckBox                matlab.ui.control.CheckBox
        CheckBoxCodeTextArea    matlab.ui.control.TextArea
        CheckBoxOutputTextArea  matlab.ui.control.TextArea
    end

    
    properties (Access = private)
        value = false % Description
    end
    

    % Callbacks that handle component events
    methods

        % Value changed function: CheckBox
        function CheckBoxValueChanged(app, event)
            app.value = app.CheckBox.Value;
            diaryFile = [tempname '.txt'];
            diary(diaryFile);
            diary('on');
            disp(app.value)
            diary('off');
            if exist(diaryFile, 'file')
                capturedOutput = fileread(diaryFile);
                delete(diaryFile);
            else
                capturedOutput = '';
            end
            app.CheckBoxOutputTextArea.Value = strsplit(strtrim(capturedOutput), newline);
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
            <CheckBox name='CheckBox'>
                <Position>[20 708 1060 32]</Position>
                <Text>'CheckBox'</Text>
                <Value>false</Value>
                <ValueChangedFcn>CheckBoxValueChanged</ValueChangedFcn>
            </CheckBox>
            <TextArea name='CheckBoxCodeTextArea'>
                <BackgroundColor>[0 0 0]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[1 1 1]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[20 578 1060 120]</Position>
                <Value>'disp(value)'</Value>
            </TextArea>
            <TextArea name='CheckBoxOutputTextArea'>
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
    <Name>minimal_checkbox</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>4d5e6f7a-8b9c-0123-defa-123456789012</AppId>
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
