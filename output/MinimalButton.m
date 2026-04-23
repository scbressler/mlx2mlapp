classdef MinimalButton < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure           matlab.ui.Figure
        RunButton          matlab.ui.control.Button
        RunCodeTextArea    matlab.ui.control.TextArea
        RunOutputTextArea  matlab.ui.control.TextArea
    end

    
    properties (Access = private)
        counter = 0 % Description
    end
    

    % Callbacks that handle component events
    methods

        % Button pushed function: RunButton
        function RunButtonPushed(app, event)
            diaryFile = [tempname '.txt'];
            diary(diaryFile);
            diary('on');
            app.counter = app.counter + 1;
            disp(app.counter);
            diary('off');
            if exist(diaryFile, 'file')
                capturedOutput = fileread(diaryFile);
                delete(diaryFile);
            else
                capturedOutput = '';
            end
            app.RunOutputTextArea.Value = strsplit(strtrim(capturedOutput), newline);
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
            <Button name='RunButton'>
                <ButtonPushedFcn>RunButtonPushed</ButtonPushedFcn>
                <Position>[20 708 1060 32]</Position>
                <Text>'Run'</Text>
            </Button>
            <TextArea name='RunCodeTextArea'>
                <BackgroundColor>[0 0 0]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[1 1 1]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[20 578 1060 120]</Position>
                <Value>{'counter = counter + 1;'; 'disp(counter);'}</Value>
            </TextArea>
            <TextArea name='RunOutputTextArea'>
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
    <Name>MinimalButton</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>4a2a5cc4-07e5-4900-b433-8f1bf1f5b6d7</AppId>
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
