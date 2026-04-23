classdef SWB_LabelsDropDown < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure  matlab.ui.Figure
        DropDown  matlab.ui.control.DropDown
        Label_7   matlab.ui.control.Label
        Label_6   matlab.ui.control.Label
        Label_5   matlab.ui.control.Label
        Label_4   matlab.ui.control.Label
        Label_3   matlab.ui.control.Label
        Label_2   matlab.ui.control.Label
        Label_1   matlab.ui.control.Label
    end

    properties (Access = private)
        domain = 'Time Domain' % Description
    end
    

    % Callbacks that handle component events
    methods

        % Value changed function: DropDown
        function DropDownValueChanged(app, event)
            app.domain = app.DropDown.Value;
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
            <Label name='Label_1'>
                <FontSize>18</FontSize>
                <FontWeight>'bold'</FontWeight>
                <Position>[20 700 1060 40]</Position>
                <Text>'Square Wave Tutorial'</Text>
            </Label>
            <Label name='Label_2'>
                <Position>[20 668 1060 22]</Position>
                <Text>'The square wave is a special type of waveform often encountered in electronics and signal processing.  In music, the square wave is one of several basic oscillators used in subtractive synthesis.'</Text>
            </Label>
            <Label name='Label_3'>
                <Position>[20 636 1060 22]</Position>
                <Text>'The square wave is also an excellent example that can be used to show the concept of Fourier decomposition.  A square wave is made up of the sum of multiple amplitude-scaled harmonics of a fundamental sinusoid.'</Text>
            </Label>
            <Label name='Label_4'>
                <Position>[20 604 1060 22]</Position>
                <Text>'This Live Script document will walk you through how a square wave is constructed from the sum of multiple sine waves.'</Text>
            </Label>
            <Label name='Label_5'>
                <FontSize>18</FontSize>
                <FontWeight>'bold'</FontWeight>
                <Position>[20 554 1060 40]</Position>
                <Text>'Build your own square wave'</Text>
            </Label>
            <Label name='Label_6'>
                <Position>[20 522 1060 22]</Position>
                <Text>'While the Fourier series equation shows the square wave is the sum of infinitely many odd-integer harmonic sinusoids, we obviously can&apos;t do that as a simulation.  However, we can demonstrate how the square wave starts to take form as more and more odd harmonics are added.  Use the sliders to construct your Fourier seriers representation of a square wave.  Observe how the square wave starts to take shape as you add more and more harmonics.  Also notice how the overshoot artifacts at the edges of the square wave transitions.'</Text>
            </Label>
            <Label name='Label_7'>
                <Position>[20 490 1060 22]</Position>
                <Text>'Explore further by viewing the Fourier (Frequency) domain representation of the square wave you created.'</Text>
            </Label>
            <DropDown name='DropDown'>
                <Items>{'Time Domain', 'Frequency Domain'}</Items>
                <Position>[20 146 1060 32]</Position>
                <Value>'Time Domain'</Value>
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
    <Name>SquareWaveBuilder</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>332044ef-1505-480e-9b37-b60b36c8ed83</AppId>
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
<Thumbnail autoCapture='true'>data:image/jpg;base64,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gAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAguLuK2x5rogP8TttH51EdTthjNzbDIyD5wwasSQrKfmwfYqCP1qL7FDx+7i46ful/woAdDcC4QvC0Uig4ykmRn8BUm6T+4v8A31/9amRwCFNkRVF9FQAU/a//AD0P/fIoAN0n9xf++v8A61G6T+4v/fX/ANaja/8Az0P/AHyKNr/89D/3yKADdJ/cX/vr/wCtRuk/uL/31/8AWo2v/wA9D/3yKNr/APPQ/wDfIoAN0n9xf++v/rUbpP7i/wDfX/1qNr/89D/3yKNr/wDPQ/8AfIoAN0n9xf8Avr/61G6T+4v/AH1/9aja/wDz0P8A3yKNr/8APQ/98igA3Sf3F/76/wDrUbpP7i/99f8A1qNr/wDPQ/8AfIo2v/z0P/fIoAN0n9xf++v/AK1G6T+4v/fX/wBaja//AD0P/fIo2v8A89D/AN8igA3Sf3F/76/+tRuk/uL/AN9f/Wo2v/z0P/fIo2v/AM9D/wB8igA3Sf3F/wC+v/rUbpP7i/8AfX/1qNr/APPQ/wDfIo2v/wA9D/3yKADdJ/cX/vr/AOtRuk/uL/31/wDWo2v/AM9D/wB8ija//PQ/98igA3Sf3F/76/8ArUbpP7i/99f/AFqNr/8APQ/98ija/wDz0P8A3yKADdJ/cX/vr/61G6T+4v8A31/9aja//PQ/98ija/8Az0P/AHyKAGPMY8bwils7QX5OBnjjngVNUbRswwZMj/dFSUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAH//Z</Thumbnail>
%}