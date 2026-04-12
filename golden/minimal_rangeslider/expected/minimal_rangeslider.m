classdef minimal_rangeslider < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure                   matlab.ui.Figure
        RangeSlider                matlab.ui.control.RangeSlider
        RangeSliderCodeTextArea    matlab.ui.control.TextArea
        RangeSliderOutputTextArea  matlab.ui.control.TextArea
    end

    
    properties (Access = private)
        slider_range = [0 100] % Description
    end
    

    % Callbacks that handle component events
    methods

        % Value changed function: RangeSlider
        function RangeSliderValueChanged(app, event)
            app.slider_range = app.RangeSlider.Value;
            diaryFile = [tempname '.txt'];
            diary(diaryFile);
            diary('on');
            fprintf('Range: %g to %g', app.slider_range(1), app.slider_range(2))
            diary('off');
            if exist(diaryFile, 'file')
                capturedOutput = fileread(diaryFile);
                delete(diaryFile);
            else
                capturedOutput = '';
            end
            app.RangeSliderOutputTextArea.Value = strsplit(strtrim(capturedOutput), newline);
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
            <RangeSlider name='RangeSlider'>
                <Limits>[0 100]</Limits>
                <Position>[20 708 1060 32]</Position>
                <Value>[0 100]</Value>
                <ValueChangedFcn>RangeSliderValueChanged</ValueChangedFcn>
            </RangeSlider>
            <TextArea name='RangeSliderCodeTextArea'>
                <BackgroundColor>[0 0 0]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[1 1 1]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[20 578 1060 120]</Position>
                <Value>'fprintf(''Range: %g to %g'', slider_range(1), slider_range(2))'</Value>
            </TextArea>
            <TextArea name='RangeSliderOutputTextArea'>
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
    <Name>minimal_rangeslider</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>3c4d5e6f-7a8b-9012-cdef-012345678901</AppId>
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
