classdef minimal_dropdown < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure               matlab.ui.Figure
        DropdownDropDown       matlab.ui.control.DropDown
        DropdownDropDownLabel  matlab.ui.control.Label
    end

    % Callbacks that handle component events
    methods

        % Value changed function: DropdownDropDown
        function DropdownDropDownValueChanged(app, event)
            value = app.DropdownDropDown.Value;
            disp(value);
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
            <Label name='DropdownDropDownLabel'>
                <HorizontalAlignment>'right'</HorizontalAlignment>
                <Position>[244 229 63 22]</Position>
                <Text>'Drop down'</Text>
            </Label>
            <DropDown name='DropdownDropDown' label='DropdownDropDownLabel'>
                <Items>{'one', 'two'}</Items>
                <Position>[322 229 100 22]</Position>
                <Value>'one'</Value>
                <ValueChangedFcn>DropdownDropDownValueChanged</ValueChangedFcn>
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
    <AppId>1d4d5370-501d-4f0d-9d72-626b2d14ef5d</AppId>
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