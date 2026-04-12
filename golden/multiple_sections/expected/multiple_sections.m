classdef multiple_sections < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure  matlab.ui.Figure
        Label_1   matlab.ui.control.Label
        Label_2   matlab.ui.control.Label
        UIAxes_1  matlab.ui.control.UIAxes
        Label_3   matlab.ui.control.Label
        Label_4   matlab.ui.control.Label
        UIAxes_2  matlab.ui.control.UIAxes
    end

    % Callbacks that handle component events
    methods

        % Code that executes after component creation
        function startupFcn(app)
            fs = 1000; % sampling frequency (Hz)
            dur = 1; % signal duration (seconds)
            f0 = 4; % sinusoidal frequency (Hz)
            t = (0:1/fs:dur)';
            signal = sin(2*pi*f0*t);
            plot(app.UIAxes_1, t,signal);
            xdata = randn(100,1);
            ydata = randn(100,1);
            scatter(app.UIAxes_2, xdata,ydata);
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
                <Text>'Multi-Section Demo'</Text>
            </Label>
            <Label name='Label_2'>
                <Position>[20 668 1060 22]</Position>
                <Text>'This is an example of a Live Script with multiple sections'</Text>
                <WordWrap>'on'</WordWrap>
            </Label>
            <UIAxes name='UIAxes_1'>
                <Position>[20 398 1060 260]</Position>
                <Title.String>''</Title.String>
                <XLabel.String>''</XLabel.String>
                <YLabel.String>''</YLabel.String>
                <ZLabel.String>''</ZLabel.String>
            </UIAxes>
            <Label name='Label_3'>
                <FontSize>18</FontSize>
                <FontWeight>'bold'</FontWeight>
                <Position>[20 338 1060 40]</Position>
                <Text>'Section 2'</Text>
            </Label>
            <Label name='Label_4'>
                <Position>[20 306 1060 22]</Position>
                <Text>'Another section with a different data plot'</Text>
                <WordWrap>'on'</WordWrap>
            </Label>
            <UIAxes name='UIAxes_2'>
                <Position>[20 36 1060 260]</Position>
                <Title.String>''</Title.String>
                <XLabel.String>''</XLabel.String>
                <YLabel.String>''</YLabel.String>
                <ZLabel.String>''</ZLabel.String>
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
    <Name>multiple_sections</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>d5e6f7a8-b9c0-1234-5678-901234567890</AppId>
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
