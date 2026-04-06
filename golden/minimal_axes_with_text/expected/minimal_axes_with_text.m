classdef minimal_axes_with_text < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure  matlab.ui.Figure
        Label_1   matlab.ui.control.Label
        Label_2   matlab.ui.control.Label
        UIAxes    matlab.ui.control.UIAxes
    end

    % Callbacks that handle component events
    methods

        % Code that executes after component creation
        function startupFcn(app)
            fs = 1000; % sampling frequency (Hz)
            dur = 1; % signal duration (seconds)
            f0 = 4; % sinusoid frequency (Hz)
            t = (0:1/fs:dur)'; % time vector
            signal = sin(2*pi*f0*t);
            plot(app.UIAxes, t,signal);
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
        <Position>[100 100 1440 1024]</Position>
        <Children>
            <Label name='Label_1'>
                <FontSize>18</FontSize>
                <FontWeight>'bold'</FontWeight>
                <Position>[20 964 1400 40]</Position>
                <Text>'Sine Wave Demo'</Text>
            </Label>
            <Label name='Label_2'>
                <Position>[20 932 1400 22]</Position>
                <Text>'This plots a sine wave'</Text>
                <WordWrap>'on'</WordWrap>
            </Label>
            <UIAxes name='UIAxes'>
                <Position>[20 482 1400 440]</Position>
            </UIAxes>
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
    <Name>minimal_axes_with_text</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>c4d5e6f7-a8b9-0123-4567-890123456789</AppId>
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
