classdef textArea_example_app < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure    matlab.ui.Figure
        TextArea_2  matlab.ui.control.TextArea
        TextArea    matlab.ui.control.TextArea
        Label       matlab.ui.control.Label
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
            <Label name='Label'>
                <HorizontalAlignment>'right'</HorizontalAlignment>
                <Position>[76 312 25 22]</Position>
                <Text>''</Text>
            </Label>
            <TextArea name='TextArea_2'>
                <BackgroundColor>[0.149 0.149 0.149]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[0.4 1 0.4]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[55 293 532 60]</Position>
                <Value>'The value of a is 1'</Value>
            </TextArea>
            <TextArea name='TextArea'>
                <BackgroundColor>[0 0 0]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[1 1 1]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[55 368 532 60]</Position>
                <Value>{'a = 1;'; 'fprintf(''The value of a is %d.'', a);'}</Value>
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
    <Name>textArea_example</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>e5894dc8-8b79-40f8-a3e5-11302a97e456</AppId>
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
<Thumbnail autoCapture='true'>data:image/jpg;base64,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</Thumbnail>
%}