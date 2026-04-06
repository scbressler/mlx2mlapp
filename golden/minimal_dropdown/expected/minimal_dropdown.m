classdef minimal_dropdown < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure  matlab.ui.Figure
        DropDown  matlab.ui.control.DropDown
    end

    
    properties (Access = private)
        value = 'one' % Description
    end
    

    % Callbacks that handle component events
    methods

        % Value changed function: DropDown
        function DropDownValueChanged(app, event)
            app.value = app.DropDown.Value;
            disp(app.value);
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
            <DropDown name='DropDown'>
                <Items>{'one', 'two'}</Items>
                <Position>[270 229 100 22]</Position>
                <Value>'one'</Value>
                <ValueChangedFcn>DropDownValueChanged</ValueChangedFcn>
            </DropDown>
        </Children>
    </UIFigure>
</Components>
%}

%---
%[app:appDetails]
%{
<?xml version='1.0' encoding='UTF-8'?>
<AppDetails>
    <Name>minimal_dropdown</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>a2b3c4d5-e6f7-8901-2345-678901234567</AppId>
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
