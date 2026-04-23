classdef TestGoldenMinCallback < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure  matlab.ui.Figure
        Slider    matlab.ui.control.Slider
    end


    properties (Access = private)
        slider = 0 % Description
    end


    % Callbacks that handle component events
    methods

        % Value changed function: Slider
        function SliderValueChanged(app, event)
            app.slider = app.Slider.Value;
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
                <Position>[20 708 1060 3]</Position>
                <Value>0</Value>
                <ValueChangedFcn>SliderValueChanged</ValueChangedFcn>
            </Slider>
        </Children>
    </UIFigure>
</Components>
%}

%---
%[app:appDetails]
%{
<?xml version='1.0' encoding='UTF-8'?>
<AppDetails>
    <Name>TestGoldenMinCallback</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>aaaaaaaa-1111-2222-3333-444444444444</AppId>
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
