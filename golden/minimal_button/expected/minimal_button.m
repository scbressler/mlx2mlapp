classdef minimal_button < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure   matlab.ui.Figure
        RunButton  matlab.ui.control.Button
    end

    
    properties (Access = private)
        counter = 0 % Description
    end
    

    % Callbacks that handle component events
    methods

        % Button pushed function: RunButton
        function RunButtonPushed(app, event)
            app.counter = app.counter + 1;
            disp(app.counter);
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
            <Button name='RunButton'>
                <ButtonPushedFcn>RunButtonPushed</ButtonPushedFcn>
                <Position>[272 219 100 22]</Position>
                <Text>'Run'</Text>
            </Button>
        </Children>
    </UIFigure>
</Components>
%}

%---
%[app:appDetails]
%{
<?xml version='1.0' encoding='UTF-8'?>
<AppDetails>
    <Name>minimal_button</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>598f11e1-95d1-4d6c-ad56-33eeae3af8f1</AppId>
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
