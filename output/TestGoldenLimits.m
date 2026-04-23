classdef TestGoldenLimits < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure              matlab.ui.Figure
        Slider                matlab.ui.control.Slider
        SliderCodeTextArea    matlab.ui.control.TextArea
        SliderOutputTextArea  matlab.ui.control.TextArea
    end


    properties (Access = private)
        slider = 6 % Description
    end


    % Callbacks that handle component events
    methods

        % Value changed function: Slider
        function SliderValueChanged(app, event)
            app.slider = app.Slider.Value;
            diaryFile = [tempname '.txt'];
            diary(diaryFile);
            diary('on');
            disp(app.slider)
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
                <Limits>[1 30]</Limits>
                <Position>[20 708 1060 3]</Position>
                <Value>6</Value>
                <ValueChangedFcn>SliderValueChanged</ValueChangedFcn>
            </Slider>
            <TextArea name='SliderCodeTextArea'>
                <BackgroundColor>[0 0 0]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[1 1 1]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[20 558 1060 120]</Position>
                <Value>'disp(slider)'</Value>
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
    <Name>TestGoldenLimits</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>77777777-aaaa-bbbb-cccc-dddddddddddd</AppId>
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
