classdef test_spinner_codevalue < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure               matlab.ui.Figure
        Spinner                matlab.ui.control.Spinner
        SpinnerLabel           matlab.ui.control.Label
        SpinnerCodeTextArea    matlab.ui.control.TextArea
        SpinnerOutputTextArea  matlab.ui.control.TextArea
    end

    properties (Access = private)
        val = 0 % Description
    end

    % Callbacks that handle component events
    methods

        % Value changed function: Spinner
        function SpinnerValueChanged(app, event)
            app.val = app.Spinner.Value;
            diaryFile = [tempname '.txt'];
            diary(diaryFile);
            diary('on');
            fprintf('Value is %d', app.val)
            diary('off');
            if exist(diaryFile, 'file')
                capturedOutput = fileread(diaryFile);
                delete(diaryFile);
            else
                capturedOutput = '';
            end
            app.SpinnerOutputTextArea.Value = strsplit(strtrim(capturedOutput), newline);
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
            <Label name='SpinnerLabel'>
                <HorizontalAlignment>'right'</HorizontalAlignment>
                <Position>[20 713 100 22]</Position>
                <Text>'Spinner'</Text>
            </Label>
            <Spinner name='Spinner' label='SpinnerLabel'>
                <Limits>[-100 100]</Limits>
                <Position>[130 708 950 32]</Position>
                <Step>1</Step>
                <Value>0</Value>
                <ValueChangedFcn>SpinnerValueChanged</ValueChangedFcn>
            </Spinner>
            <TextArea name='SpinnerCodeTextArea'>
                <BackgroundColor>[0 0 0]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[1 1 1]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[20 578 1060 120]</Position>
                <Value>'fprintf(''Value is %d'', val)'</Value>
            </TextArea>
            <TextArea name='SpinnerOutputTextArea'>
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
    <Name>test_spinner_codevalue</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>97089je2-k80j-9941-f501-hdje1524172</AppId>
    <AppType>Standard</AppType>
    <MATLABRelease>R2025b</MATLABRelease>
    <MinimumSupportedMATLABRelease>R2025a</MinimumSupportedMATLABRelease>
</InternalData>
%}

%---
%[app:thumbnail]
%{
<!-- Thumbnail is used by file previewers. To change how the thumbnail is captured or stored, use the App Designer Details dialog box in App Designer. -->
<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<Thumbnail autoCapture='true'></Thumbnail>
%}
