classdef SquareWaveBuilder < matlab.apps.App

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
        PlotItCodeTextArea     matlab.ui.control.TextArea
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
            <DropDown name='DropDown'>
                <Items>{'Time Domain', 'Frequency Domain'}</Items>
                <Position>[20 146 1060 32]</Position>
                <Value>'Time Domain'</Value>
                <ValueChangedFcn>DropDownValueChanged</ValueChangedFcn>
            </DropDown>
            <Slider name='SquareWaveFrequencyHz'>
                <Limits>[1 6]</Limits>
                <Position>[20 104 1060 3]</Position>
                <Value>1</Value>
                <ValueChangedFcn>SquareWaveFrequencyHzValueChanged</ValueChangedFcn>
            </Slider>
            <Slider name='NumberOfHarmonics'>
                <Limits>[1 30]</Limits>
                <Position>[20 42 1060 3]</Position>
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
<Thumbnail autoCapture='true'></Thumbnail>
%}
