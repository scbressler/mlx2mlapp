classdef minimal_axes < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure  matlab.ui.Figure
        UIAxes    matlab.ui.control.UIAxes
    end

    % Callbacks that handle component events
    methods

        % Code that executes after component creation
        function startupFcn(app)
            fs = 1000;
            t = (0:1/fs:1)';
            xt = sin(2*pi*4*t);
            plot(app.UIAxes, t,xt);
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
        <Position>[100 100 640 480]</Position>
        <Children>
            <UIAxes name='UIAxes'>
                <Position>[15 15 610 440]</Position>
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
    <Name>minimal_axes</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>b3c4d5e6-f7a8-9012-3456-789012345678</AppId>
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
