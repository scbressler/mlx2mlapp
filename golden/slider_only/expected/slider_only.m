classdef slider_only < matlab.apps.App

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure     matlab.ui.Figure
        Slider       matlab.ui.control.Slider
        SliderLabel  matlab.ui.control.Label
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
            <Label name='SliderLabel'>
                <HorizontalAlignment>'right'</HorizontalAlignment>
                <Position>[25 421 36 22]</Position>
                <Text>'Slider'</Text>
            </Label>
            <Slider name='Slider' label='SliderLabel'>
                <Limits>[0 30]</Limits>
                <Position>[83 430 150 3]</Position>
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
    <Name>slider_only</Name>
    <Version>1.0</Version>
</AppDetails>
%}

%---
%[app:internalData]
%{
<?xml version='1.0' encoding='UTF-8'?>
<InternalData>
    <AppId>567381f4-63c6-4906-8c70-f93fed16268e</AppId>
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
<Thumbnail autoCapture='true'>data:image/jpg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAClANwDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3WmebH5nl+Ym/+7uGfyp9ZV5oFnfXb3MrTCRsZ2MAOBj05/GgDVBBAIOQehFQtdwLIUaQBgcYwaqaXolppBc2xlJcAEyPuwB2HpT5xm5+zo4O9TI0ZkAyQRz64/TigC55if31/MUeYn99fzFUmXbOkJRdz5IHnc4B5OMemKZKywMiyiJWbHDXGMdfUdM4H40AaHmJ/fX8xR5if31/MVnzkW4HmCNSegafHcDPI9T/AC9aLhktQDN5SBjgbp9uRkZPI7DmgDQ8xP76/mKPMT++v51nzMlvEJJfKVW6Znxnr0yPTBon2R23mSCLYwwuZ8ByRwASO9AGlRTY5EljWSN1dGGQynINOoAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKgNpCb1bsg+cqbAc8Y+nryfzqeigCF7WKS7iuWU+bECqnPY9aju9Otr5kadCSnAIYjj0q1RQBWvbC31BAtwhYAEcHHUgn+Qpt7p1vfiMT78R5K7XIwfX6jHBq3RQBUuNNtrqCKCRW8qLhVDcdMc+vFJNplrcWCWMisbdAoChiMgdATVyigCK3gS1gWGPdtXONxyTk5OT+NS0UUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQB//Z</Thumbnail>
%}