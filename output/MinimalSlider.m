classdef MinimalSlider < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure              matlab.ui.Figure
        Slider                matlab.ui.control.Slider
        SliderCodeTextArea    matlab.ui.control.TextArea
        SliderOutputTextArea  matlab.ui.control.TextArea
    end

    % Callbacks that handle component events
    methods

        % Value changed function: Slider
        function SliderValueChanged(app, event)
            diaryFile = [tempname '.txt'];
            diary(diaryFile);
            diary('on');
            slider = -10;
            disp(slider)
            diary('off');
            if exist(diaryFile, 'file')
                capturedOutput = fileread(diaryFile);
                delete(diaryFile);
            else
                capturedOutput = '';
            end
            app.SliderOutputTextArea.Value = strsplit(strtrim(capturedOutput), newline);
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
            <Slider name='Slider'>
                <Limits>[-100 100]</Limits>
                <Position>[20 708 1060 32]</Position>
                <Value>0</Value>
                <ValueChangedFcn>SliderValueChanged</ValueChangedFcn>
            </Slider>
            <TextArea name='SliderCodeTextArea'>
                <BackgroundColor>[0 0 0]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[1 1 1]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[20 558 1060 120]</Position>
                <Value>{'slider = -10;'; 'disp(slider)'}</Value>
            </TextArea>
            <TextArea name='SliderOutputTextArea'>
                <BackgroundColor>[0.149 0.149 0.149]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[0.4 1 0.4]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[20 428 1060 120]</Position>
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
    <Name>MinimalSlider</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>6b3ad6a7-026a-4698-acac-f549fdcc189b</AppId>
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
