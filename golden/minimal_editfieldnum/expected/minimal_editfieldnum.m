classdef minimal_editfieldnum < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure            matlab.ui.Figure
        Valb                matlab.ui.control.NumericEditField
        ValbLabel           matlab.ui.control.Label
        ValbCodeTextArea    matlab.ui.control.TextArea
        ValbOutputTextArea  matlab.ui.control.TextArea
    end

    
    properties (Access = private)
        addThis = 0 % Description
    end
    

    % Callbacks that handle component events
    methods

        % Value changed function: Valb
        function ValbValueChanged(app, event)
            app.addThis = app.Valb.Value;
            diaryFile = [tempname '.txt'];
            diary(diaryFile);
            diary('on');
            fprintf('Value is %g', app.addThis)
            diary('off');
            if exist(diaryFile, 'file')
                capturedOutput = fileread(diaryFile);
                delete(diaryFile);
            else
                capturedOutput = '';
            end
            app.ValbOutputTextArea.Value = strsplit(strtrim(capturedOutput), newline);
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
            <Label name='ValbLabel'>
                <HorizontalAlignment>'right'</HorizontalAlignment>
                <Position>[20 713 100 22]</Position>
                <Text>'Valb'</Text>
            </Label>
            <NumericEditField name='Valb' label='ValbLabel'>
                <Position>[130 708 950 32]</Position>
                <Value>0</Value>
                <ValueChangedFcn>ValbValueChanged</ValueChangedFcn>
            </NumericEditField>
            <TextArea name='ValbCodeTextArea'>
                <BackgroundColor>[0 0 0]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[1 1 1]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[20 578 1060 120]</Position>
                <Value>char("fprintf('Value is %g', addThis)")</Value>
            </TextArea>
            <TextArea name='ValbOutputTextArea'>
                <BackgroundColor>[0.149 0.149 0.149]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[0.4 1 0.4]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[20 448 1060 120]</Position>
                <Value>''</Value>
            </TextArea>
        </Children>
    </UIFigure>
</Components>
%}

%---
%[app:appDetails]
%{
<?xml version='1.0' encoding='UTF-8'?>
<AppDetails>
    <Name>minimal_editfieldnum</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>6f7a8b9c-0d1e-2345-fabc-345678901234</AppId>
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
