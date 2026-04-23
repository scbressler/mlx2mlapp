classdef TestSliderLowGoodLimits < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure  matlab.ui.Figure
        Slider    matlab.ui.control.Slider
    end

    % Callbacks that handle component events
    methods

        % Value changed function: Slider
        function SliderValueChanged(app, event)
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
                <Position>[20 42 1060 3]</Position>
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
    <Name>TestSliderLowGoodLimits</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>bbbbbbbb-cccc-dddd-eeee-ffffffffffff</AppId>
    <AppType>Standard</AppType>
    <MATLABRelease>R2025b</MATLABRelease>
    <MinimumSupportedMATLABRelease>R2025a</MinimumSupportedMATLABRelease>
</InternalData>
%}

%---
%[app:thumbnail]
%{
<!-- Thumbnail is used by file previewers. To change how the thumbnail is captured or stored, use App Designer. -->
<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<Thumbnail autoCapture='true'></Thumbnail>
%}
