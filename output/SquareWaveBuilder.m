classdef SquareWaveBuilder < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure               matlab.ui.Figure
        NumberOfHarmonics      matlab.ui.control.Slider
        SquareWaveFrequencyHz  matlab.ui.control.Slider
        DropDown               matlab.ui.control.DropDown
        PlotItCodeTextArea     matlab.ui.control.TextArea
        PlotItButton           matlab.ui.control.Button
        Label_7                matlab.ui.control.Label
        Label_6                matlab.ui.control.Label
        Label_5                matlab.ui.control.Label
        Label_4                matlab.ui.control.Label
        Label_3                matlab.ui.control.Label
        Label_2                matlab.ui.control.Label
        Label_1                matlab.ui.control.Label
    end

    properties (Access = private)
        domain = 'Time Domain' % Description
    end
    

    % Callbacks that handle component events
    methods

        % Button pushed function: PlotItButton
        function PlotItButtonPushed(app, event)
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
        end

        % Value changed function: DropDown
        function DropDownValueChanged(app, event)
            app.domain = app.DropDown.Value;
        end

        % Value changed function: SquareWaveFrequencyHz
        function SquareWaveFrequencyHzValueChanged(app, event)
            % value changed
        end

        % Value changed function: NumberOfHarmonics
        function NumberOfHarmonicsValueChanged(app, event)
            % value changed
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
                <Text>'While the Fourier series equation shows the square wave is the sum of infinitely many odd-integer harmonic sinusoids, we obviously can&apos;t do that as a simulation.  However, we can demonstrate how the square wave starts to take form as more and more odd harmonics are added.  Use the sliders to construct your Fourier seriers representation of a square wave.  Observe how the square wave starts to take shape as you add more and more harmonics.  Also notice how the overshoot artifacts at the edges of the square wave transitions.'</Text>
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
            <TextArea name='PlotItCodeTextArea'>
                <BackgroundColor>[0 0 0]</BackgroundColor>
                <Editable>'off'</Editable>
                <FontColor>[1 1 1]</FontColor>
                <FontName>'Courier New'</FontName>
                <Position>[20 318 1060 120]</Position>
                <Value>{'f = 1; % square wave fundamental frequency (Hz)'; 'K = 6; % number of odd harmonics'; 'fs = 1000; % sampling frequency (samples/second)'; 'dur = 1; % square wave duration (seconds)'; 't = (0:1/fs:dur)''; % time vector (seconds)'; 'fr = fs*(0:numel(t)-1)''/numel(t);'; 'yt = [];'; 'for k = 1:K'; '    yt(:,k) = (4/pi)*(1/(2*k-1))*sin(2*pi*(2*k-1)*f*t);'; 'end'; 'f2 = figure;'; 'ax2 = axes;'; 'if domain == ''Time Domain'''; '    plot(ax2,t,yt,''Color'',0.72*ones(1,3),''LineWidth'',0.5);'; '    hold on;'; '    plot(ax2,t,sum(yt,2),''b-'',''LineWidth'',1);'; '    xlabel(''Time (seconds)'');'; '    ylabel(''Amplitude'');'; '    ylim([-1.4 1.4]);'; '    grid on;'; '    legend(ax2.Children([end 1]),{''Harmonics'',''Square Wave''});'; '    title(ax2,sprintf(''%d-Hz Square Wave (%d harmonics)'',f,K));'; '    hold off;'; 'elseif domain == ''Frequency Domain'''; '    Yw = fft(sum(yt,2));'; '    stem(ax2,fr,abs(Yw)/numel(Yw),''r.-'');'; '    xlabel(''Frquency (Hz)'');'; '    ylabel(''Magnitude'');'; '    grid on;'; '    xlim([0 f*(2*(K+1)-1)]);'; '    title(ax2,sprintf(''%d-Hz Square Wave (%d harmonics)'',f,K));'; '    hold off;'; 'end'}</Value>
            </TextArea>
            <DropDown name='DropDown'>
                <Items>{'Time Domain', 'Frequency Domain'}</Items>
                <Position>[20 276 1060 32]</Position>
                <Value>'Time Domain'</Value>
                <ValueChangedFcn>DropDownValueChanged</ValueChangedFcn>
            </DropDown>
            <Slider name='SquareWaveFrequencyHz'>
                <Limits>[1 6]</Limits>
                <Position>[20 234 1060 3]</Position>
                <Value>1</Value>
                <ValueChangedFcn>SquareWaveFrequencyHzValueChanged</ValueChangedFcn>
            </Slider>
            <Slider name='NumberOfHarmonics'>
                <Limits>[1 30]</Limits>
                <Position>[20 172 1060 3]</Position>
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
    <Name>SquareWaveBuilder</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>45965089-cc0b-41cd-ba53-d8e90e7f221e</AppId>
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