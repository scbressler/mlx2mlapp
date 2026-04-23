classdef TestSliderY708 < matlab.apps.App

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
                <Limits>[1 30]</Limits>
                <Position>[20 708 1060 3]</Position>
                <Value>6</Value>
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
    <Name>TestSliderY708</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>bbbbbbbb-2222-3333-4444-555555555555</AppId>
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
