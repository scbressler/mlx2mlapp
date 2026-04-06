classdef axesExample < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure  matlab.ui.Figure
        UIAxes    matlab.ui.control.UIAxes
    end

    % Callbacks that handle component events
    methods

        % Code that executes after component creation
        function startupFcn(app)
            plot(app.UIAxes,1:10,rand(1,10));
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
            <UIAxes name='UIAxes'>
                <Position>[171 184 300 185]</Position>
                <Title.String>'Title'</Title.String>
                <XLabel.String>'X'</XLabel.String>
                <YLabel.String>'Y'</YLabel.String>
                <ZLabel.String>'Z'</ZLabel.String>
            </UIAxes>
        </Children>
    </UIFigure>
</Components>
%}

%---
%[app:runConfiguration]
%{
<?xml version='1.0' encoding='UTF-8'?>
<RunConfiguration>
    <StartupFcn>startupFcn</StartupFcn>
</RunConfiguration>
%}

%---
%[app:appDetails]
%{
<?xml version='1.0' encoding='UTF-8'?>
<AppDetails>
    <Name>axesExample</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>8cb3a696-6b3e-40e2-890a-a6284d6a2b32</AppId>
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
<Thumbnail autoCapture='true'>data:image/jpg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAClANwDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3WiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKguZpIFRki8xd37znlV2k5/MAfjVpYmKgnAyOlADKKk8lvUUeS3qKAI6Kk8lvUVFc2S3dpNbybSkqFGBGeCMUALRXL/8IEEkDW2sXltgKAITtwB2GOma6zyW9RQBHRUnkt6ijyW9RQBHRUnkt6ikMRAJyKAGUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAGLda9CC9v5Exdpmt+McHB+Y+1dEhzGpwRkDrWJc6xYiOSEzEOztAAVPLYP6ds1toQ0akHIIBFADqKRGDoGU5B6UydisDkdcYH17UARRLIY/NRzlyW2scggnj6cVJ54X/WqYz7jj86kVQiKo6AYFLTbEkMM0YUMZF2noc9aas6s4Xa4yMgsMZp4jQMWCKGPcDmmzqTHuUZdDuX39v6UaBqSUUisHQMpyCMimvKkeAxOT0ABJ/SkMfSN90/SmrNG5wsik+meac33T9KAK1FFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABVaZbw3kLQSRLbgHzVdSS3PG3GMHrySfpVmigChOmnGKdwtqZAzAkBciTH/oX61sL9wfSsS40ey2SzGElwzTjLnAfB5Az7n862kAEagDAAGAKAGQ/K8kfo24fQ8/zzRNyYk/vOCfw5/pSSfJcRv2bKH+Y/l+tL967H+wn8z/8AWqvMnyJaKKKkoKKKKAK4kFuZEbOM7kA757D8f5ipIoyCXfmRuvsPQU8opZWKgsvQ46UtNsVhrIjjDqrD3GajMCqCULLjsGOPyqakb7p+lK47FaiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAx7jRYwJZvtEhHmtcbCB97B4z1/yK6BBhFA7AVjayJltVnjlZY4TulRTjevTH/wCvjnParcDyy28UguJlDoGCsq5GRnB4oAuTqXhYL94cr9RyKZbsJPMlHRjx9AP8c1Dib/n6k/75X/CqelztdWCyxSzRoWbCnYe556U76CtqbNFUsTf8/Un/AHyv+FVre5kmu7qATXSmBlBZ0UK2R/D8vIpDNaiqWJv+fqT/AL5X/Cqn2yT+1xY+bc7vJ83zNq7euMfd60AbFFUsTf8AP1J/3yv+FU729ktLiyiMty5uJvLBRUwvHU8dKANmkb7p+lU8Tf8AP1J/3yv+FVb+6lsrbzWe4lXOCqBM9CfTpxj8aALtFRW04ubWKcKVEihtp6jNS0AFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAFOGK9XVbiWWYNZsgEUeeVbjJPHf68YPrxcoooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD//Z</Thumbnail>
%}