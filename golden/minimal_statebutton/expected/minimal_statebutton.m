classdef minimal_statebutton < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure                   matlab.ui.Figure
        StateButton                matlab.ui.control.StateButton
        StateButtonCodeTextArea    matlab.ui.control.TextArea
        StateButtonOutputTextArea  matlab.ui.control.TextArea
    end

    
    properties (Access = private)
        val = false % Description
    end
    

    % Callbacks that handle component events
    methods

        % Value changed function: StateButton
        function StateButtonValueChanged(app, event)
            app.val = app.StateButton.Value;
            diaryFile = [tempname '.txt'];
            diary(diaryFile);
            diary('on');
            disp(app.val)
            diary('off');
            if exist(diaryFile, 'file')
                capturedOutput = fileread(diaryFile);
                delete(diaryFile);
            else
                capturedOutput = '';
            end
            app.StateButtonOutputTextArea.Value = strsplit(strtrim(capturedOutput), newline);
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
            <StateButton name='StateButton'>
                <Position>[20 708 1060 32]</Position>
                <Text>'StateButton'</Text>
                <Value>false</Value>
                <ValueChangedFcn>StateButtonValueChanged</ValueChangedFcn>
            </StateButton>
            <TextArea name='StateButtonCodeTextArea'>
                <BackgroundColor>[0 0 0]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[1 1 1]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[20 578 1060 120]</Position>
                <Value>'disp(val)'</Value>
            </TextArea>
            <TextArea name='StateButtonOutputTextArea'>
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
    <Name>minimal_statebutton</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>5e6f7a8b-9c0d-1234-efab-234567890123</AppId>
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
