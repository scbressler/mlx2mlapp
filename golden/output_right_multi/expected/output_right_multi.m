classdef output_right_multi < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure           matlab.ui.Figure
        CodeTextArea       matlab.ui.control.TextArea
        OutputTextArea     matlab.ui.control.TextArea
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
        % Code that executes after component creation
        function startupFcn(app)
            diaryFile = [tempname '.txt'];
            diary(diaryFile);
            diary('on');
            a = 1;
            fprintf('a = %d\n', a);
            diary('off');
            if exist(diaryFile, 'file')
                capturedOutput = fileread(diaryFile);
                delete(diaryFile);
            else
                capturedOutput = '';
            end
            app.OutputTextArea.Value = strsplit(strtrim(capturedOutput), newline);
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
            <TextArea name='CodeTextArea'>
                <BackgroundColor>[0 0 0]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[1 1 1]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[20 620 520 120]</Position>
                <Value>{'a = 1;'; 'fprintf(''a = %d\n'', a);'}</Value>
            </TextArea>
            <TextArea name='OutputTextArea'>
                <BackgroundColor>[0.149 0.149 0.149]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[0.4 1 0.4]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[560 620 520 120]</Position>
                <Value>''</Value>
            </TextArea>
            <Button name='RunButton'>
                <ButtonPushedFcn>RunButtonPushed</ButtonPushedFcn>
                <Position>[20 568 520 32]</Position>
                <Text>'Run'</Text>
            </Button>
            <TextArea name='RunCodeTextArea'>
                <BackgroundColor>[0 0 0]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[1 1 1]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[20 438 520 120]</Position>
                <Value>{'counter = counter + 1;'; 'disp(counter);'}</Value>
            </TextArea>
            <TextArea name='RunOutputTextArea'>
                <BackgroundColor>[0.149 0.149 0.149]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[0.4 1 0.4]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[560 438 520 120]</Position>
                <Value>''</Value>
            </TextArea>
        </Children>
    </UIFigure>
</Components>
%}

%---
%[app:runConfiguration]
%{
<?xml version='1.0' encoding='UTF-8'?>
<RunConfiguration>
    <StartupFcn>startupFcn</StartupFcn>
</RunConfiguration>
%}

%---
%[app:appDetails]
%{
<?xml version='1.0' encoding='UTF-8'?>
<AppDetails>
    <Name>output_right_multi</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>a1b2c3d4-e5f6-7890-abcd-ef1234567890</AppId>
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
