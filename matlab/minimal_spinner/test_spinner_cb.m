classdef test_spinner_cb < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure      matlab.ui.Figure
        Spinner       matlab.ui.control.Spinner
        SpinnerLabel  matlab.ui.control.Label
    end

    properties (Access = private)
        val = 0 % Description
    end

    % Callbacks that handle component events
    methods

        % Value changed function: Spinner
        function SpinnerValueChanged(app, event)
            app.val = app.Spinner.Value;
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
            <Label name='SpinnerLabel'>
                <HorizontalAlignment>'right'</HorizontalAlignment>
                <Position>[27 421 46 22]</Position>
                <Text>'Spinner'</Text>
            </Label>
            <Spinner name='Spinner' label='SpinnerLabel'>
                <Position>[88 421 100 22]</Position>
                <ValueChangedFcn>SpinnerValueChanged</ValueChangedFcn>
            </Spinner>
        </Children>
    </UIFigure>
</Components>
%}

%---
%[app:appDetails]
%{
<?xml version='1.0' encoding='UTF-8'?>
<AppDetails>
    <Name>test_spinner_cb</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>43544e97-f35e-4496-a056-c8efa6079627</AppId>
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
