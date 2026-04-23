classdef SquareWaveBuilderNoCode < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure               matlab.ui.Figure
        Label_1                matlab.ui.control.Label
        Label_2                matlab.ui.control.Label
        Label_3                matlab.ui.control.Label
        Label_4                matlab.ui.control.Label
        Label_5                matlab.ui.control.Label
        Label_6                matlab.ui.control.Label
        Label_7                matlab.ui.control.Label
        PlotItButton           matlab.ui.control.Button
        PlotItOutputTextArea   matlab.ui.control.TextArea
        DropDown               matlab.ui.control.DropDown
        SquareWaveFrequencyHz  matlab.ui.control.Slider
        NumberOfHarmonics      matlab.ui.control.Slider
    end

    
    properties (Access = private)
        domain = 'Time Domain' % Description
    end
    

    % Callbacks that handle component events
    methods

        % Button pushed function: PlotItButton
        function PlotItButtonPushed(app, event)
            diaryFile = [tempname '.txt'];
            diary(diaryFile);
            diary('on');
            f = 1; % square wave fundamental frequency (Hz)
            K = 6; % number of odd harmonics
            fs = 1000; % sampling frequency (samples/second)
            dur = 1; % square wave duration (seconds)
            t = (0:1/fs:dur)'; % time vector (seconds)
            fr = fs*(0:numel(t)-1)'/numel(t);
            yt = [];
            for k = 1:K
            yt(:,k) = (4/pi)*(1/(2*k-1))*sin(2*pi*(2*k-1)*f*t);
            end
            f2 = figure;
            ax2 = axes;
            if app.domain == 'Time Domain'
            plot(ax2,t,yt,'Color',0.72*ones(1,3),'LineWidth',0.5);
            hold on;
            plot(ax2,t,sum(yt,2),'b-','LineWidth',1);
            xlabel('Time (seconds)');
            ylabel('Amplitude');
            ylim([-1.4 1.4]);
            grid on;
            legend(ax2.Children([end 1]),{'Harmonics','Square Wave'});
            title(ax2,sprintf('%d-Hz Square Wave (%d harmonics)',f,K));
            hold off;
            elseif app.domain == 'Frequency Domain'
            Yw = fft(sum(yt,2));
            stem(ax2,fr,abs(Yw)/numel(Yw),'r.-');
            xlabel('Frquency (Hz)');
            ylabel('Magnitude');
            grid on;
            xlim([0 f*(2*(K+1)-1)]);
            title(ax2,sprintf('%d-Hz Square Wave (%d harmonics)',f,K));
            hold off;
            end
            diary('off');
            if exist(diaryFile, 'file')
                capturedOutput = fileread(diaryFile);
                delete(diaryFile);
            else
                capturedOutput = '';
            end
            app.PlotItOutputTextArea.Value = strsplit(strtrim(capturedOutput), newline);
        end
        % Value changed function: DropDown
        function DropDownValueChanged(app, event)
            app.domain = app.DropDown.Value;
        end
        % Value changed function: SquareWaveFrequencyHz
        function SquareWaveFrequencyHzValueChanged(app, event)
        end
        % Value changed function: NumberOfHarmonics
        function NumberOfHarmonicsValueChanged(app, event)
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
                <WordWrap>'on'</WordWrap>
            </Label>
            <Label name='Label_3'>
                <Position>[20 636 1060 22]</Position>
                <Text>'The square wave is also an excellent example that can be used to show the concept of Fourier decomposition.  A square wave is made up of the sum of multiple amplitude-scaled harmonics of a fundamental sinusoid.'</Text>
                <WordWrap>'on'</WordWrap>
            </Label>
            <Label name='Label_4'>
                <Position>[20 604 1060 22]</Position>
                <Text>'This Live Script document will walk you through how a square wave is constructed from the sum of multiple sine waves.'</Text>
                <WordWrap>'on'</WordWrap>
            </Label>
            <Label name='Label_5'>
                <FontSize>18</FontSize>
                <FontWeight>'bold'</FontWeight>
                <Position>[20 554 1060 40]</Position>
                <Text>'Build your own square wave'</Text>
            </Label>
            <Label name='Label_6'>
                <Position>[20 522 1060 22]</Position>
                <Text>'While the Fourier series equation shows the square wave is the sum of infinitely many odd-integer harmonic sinusoids, we obviously can''t do that as a simulation.  However, we can demonstrate how the square wave starts to take form as more and more odd harmonics are added.  Use the sliders to construct your Fourier seriers representation of a square wave.  Observe how the square wave starts to take shape as you add more and more harmonics.  Also notice how the overshoot artifacts at the edges of the square wave transitions.'</Text>
                <WordWrap>'on'</WordWrap>
            </Label>
            <Label name='Label_7'>
                <Position>[20 490 1060 22]</Position>
                <Text>'Explore further by viewing the Fourier (Frequency) domain representation of the square wave you created.'</Text>
                <WordWrap>'on'</WordWrap>
            </Label>
            <Button name='PlotItButton'>
                <ButtonPushedFcn>PlotItButtonPushed</ButtonPushedFcn>
                <Position>[20 448 1060 32]</Position>
                <Text>'Plot it'</Text>
            </Button>
            <TextArea name='PlotItOutputTextArea'>
                <BackgroundColor>[0.149 0.149 0.149]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[0.4 1 0.4]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[20 318 1060 120]</Position>
                <Value>''</Value>
            </TextArea>
            <DropDown name='DropDown'>
                <Items>{'Time Domain', 'Frequency Domain'}</Items>
                <Position>[20 276 1060 32]</Position>
                <Value>'Time Domain'</Value>
                <ValueChangedFcn>DropDownValueChanged</ValueChangedFcn>
            </DropDown>
            <Slider name='SquareWaveFrequencyHz'>
                <Limits>[1 6]</Limits>
                <Position>[20 234 1060 32]</Position>
                <Value>1</Value>
                <ValueChangedFcn>SquareWaveFrequencyHzValueChanged</ValueChangedFcn>
            </Slider>
            <Slider name='NumberOfHarmonics'>
                <Limits>[1 30]</Limits>
                <Position>[20 172 1060 32]</Position>
                <Value>6</Value>
                <ValueChangedFcn>NumberOfHarmonicsValueChanged</ValueChangedFcn>
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
    <Name>SquareWaveBuilderNoCode</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>d789dfbd-a248-4dad-81bd-40aa2ef12042</AppId>
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
