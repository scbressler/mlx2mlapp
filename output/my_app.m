classdef my_app < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure               matlab.ui.Figure
        Label_1                matlab.ui.control.Label
        Spinner                matlab.ui.control.Spinner
        SpinnerLabel           matlab.ui.control.Label
        SpinnerCodeTextArea    matlab.ui.control.TextArea
        SpinnerOutputTextArea  matlab.ui.control.TextArea
        Label_2                matlab.ui.control.Label
        RunButton              matlab.ui.control.Button
        RunCodeTextArea        matlab.ui.control.TextArea
        RunOutputTextArea      matlab.ui.control.TextArea
    end

    
    properties (Access = private)
        spinner = 0 % Description
    end
    

    % Callbacks that handle component events
    methods

        % Button pushed function: RunButton
        function RunButtonPushed(app, event)
            diaryFile = [tempname '.txt'];
            diary(diaryFile);
            diary('on');
            fprintf('Spinner value is %d',app.spinner);
            diary('off');
            if exist(diaryFile, 'file')
                capturedOutput = fileread(diaryFile);
                delete(diaryFile);
            else
                capturedOutput = '';
            end
            app.RunOutputTextArea.Value = strsplit(strtrim(capturedOutput), newline);
        end
        % Value changed function: Spinner
        function SpinnerValueChanged(app, event)
            app.spinner = app.Spinner.Value;
            diaryFile = [tempname '.txt'];
            diary(diaryFile);
            diary('on');
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
            <Label name='Label_1'>
                <FontSize>18</FontSize>
                <FontWeight>'bold'</FontWeight>
                <Position>[20 700 1060 40]</Position>
                <Text>'Section 1: Spinner'</Text>
            </Label>
            <Label name='SpinnerLabel'>
                <HorizontalAlignment>'right'</HorizontalAlignment>
                <Position>[20 663 100 22]</Position>
                <Text>'Spinner'</Text>
            </Label>
            <Spinner name='Spinner' label='SpinnerLabel'>
                <Limits>[-100 100]</Limits>
                <Position>[130 658 950 32]</Position>
                <Step>1</Step>
                <Value>0</Value>
                <ValueChangedFcn>SpinnerValueChanged</ValueChangedFcn>
            </Spinner>
            <TextArea name='SpinnerCodeTextArea'>
                <BackgroundColor>[0 0 0]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[1 1 1]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[20 528 1060 120]</Position>
                <Value>''</Value>
            </TextArea>
            <TextArea name='SpinnerOutputTextArea'>
                <BackgroundColor>[0.149 0.149 0.149]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[0.4 1 0.4]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[20 398 1060 120]</Position>
                <Value>''</Value>
            </TextArea>
            <Label name='Label_2'>
                <FontSize>18</FontSize>
                <FontWeight>'bold'</FontWeight>
                <Position>[20 338 1060 40]</Position>
                <Text>'Section 2: Button'</Text>
            </Label>
            <Button name='RunButton'>
                <ButtonPushedFcn>RunButtonPushed</ButtonPushedFcn>
                <Position>[20 296 1060 32]</Position>
                <Text>'Run'</Text>
            </Button>
            <TextArea name='RunCodeTextArea'>
                <BackgroundColor>[0 0 0]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[1 1 1]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[20 166 1060 120]</Position>
                <Value>"fprintf('Spinner value is %d',spinner);"</Value>
            </TextArea>
            <TextArea name='RunOutputTextArea'>
                <BackgroundColor>[0.149 0.149 0.149]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[0.4 1 0.4]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[20 36 1060 120]</Position>
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
    <Name>my_app</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>7ea2b258-7b3f-4957-b843-1b7f8fc35e51</AppId>
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
