function finalize_mlapp(mlapp_in, mat_out)
% FINALIZE_MLAPP  Generate a proper appModel.mat from a Python-generated .mlapp.
%
% Usage
% -----
%   finalize_mlapp('output/MyApp.mlapp', '/tmp/appModel.mat')
%
% What it does
% ------------
% 1. Extracts the classdef string from document.xml inside mlapp_in
% 2. Writes it to a temp .m file with a no-op startupFcn and instantiates
%    the app -- this runs createComponents() and builds live matlab.ui.* objects
% 3. Injects DesignTimeProperties.CodeName onto every component so App
%    Designer can map component objects back to property names
% 4. Saves appModel.mat using App Designer's MLAPPSerializer pipeline (which
%    runs pre-save component adjusters and includes the required appData struct)
%    but writing only the MAT data -- NOT the full .mlapp
%
% The caller (run_finalize.py) patches the .mlapp ZIP using Python's zipfile,
% which preserves all entry paths correctly.
%
% Prerequisites
% -------------
%   MATLAB R2018a or later with App Designer toolbox.

    % ── 1. Extract classdef ──────────────────────────────────────────────
    fprintf('Reading classdef from %s\n', mlapp_in);
    code_text = read_classdef(mlapp_in);

    % ── 2. Identify class name ───────────────────────────────────────────
    tok = regexp(code_text, 'classdef\s+(\w+)', 'tokens', 'once');
    if isempty(tok)
        error('finalize_mlapp: could not find classdef name in document.xml');
    end
    class_name = tok{1};
    fprintf('Class name: %s\n', class_name);

    % ── 3. Write no-op classdef to temp dir and instantiate ──────────────
    tmp_dir = [tempname '_finalize'];
    mkdir(tmp_dir);
    m_file  = fullfile(tmp_dir, [class_name '.m']);

    fid = fopen(m_file, 'w', 'n', 'UTF-8');
    fprintf(fid, '%s', noop_startup(code_text));
    fclose(fid);

    addpath(tmp_dir);
    cleanup = onCleanup(@() safe_cleanup(tmp_dir, class_name));

    fprintf('Instantiating %s ...\n', class_name);
    app = feval(class_name);

    if ~isvalid(app) || ~isprop(app, 'UIFigure') || ~isvalid(app.UIFigure)
        error('finalize_mlapp: app.UIFigure is not a valid UI object.');
    end
    fprintf('UIFigure created: %s  Position=[%d %d %d %d]\n', ...
        class(app.UIFigure), app.UIFigure.Position);

    % ── 4. Inject DesignTimeProperties onto every component ──────────────
    inject_design_time_properties(app);

    % ── 5. Set Visible=off (required by App Designer serializer) ─────────
    app.UIFigure.Visible = 'off';

    % ── 6. Build appModel.mat using App Designer's internal save pipeline ─
    % Use MLAPPSerializer internals to build the correctly-structured MAT
    % data (with appData.MinimumSupportedVersion and pre-save adjusters)
    % then save only the MAT file -- NOT the full .mlapp.
    fprintf('Building appModel.mat -> %s\n', mat_out);
    write_appmodel_mat(app.UIFigure, code_text, class_name, mat_out);

    % ── 7. Close the live app ────────────────────────────────────────────
    try
        delete(app);
    catch
    end

    fprintf('Done.\n');
end


% =========================================================================
% Write a properly-structured appModel.mat using App Designer internals.
%
% Replicates the data preparation that MLAPPSerializer.save() does before
% calling save(), so that the resulting MAT file matches what App Designer
% produces -- including the appData struct required for R2018a compatibility.
% =========================================================================
function write_appmodel_mat(uifigure, code_text, class_name, mat_out)
    import appdesigner.internal.serialization.save.*
    import appdesigner.internal.serialization.app.*

    % -- components struct ------------------------------------------------
    components = struct();
    components.UIFigure = uifigure;

    % Run App Designer's pre-save component data adjusters
    % (removes CreateFcns, handles aliased properties, etc.)
    factory = ComponentDataAdjusterFactory();
    adjuster = factory.createComponentDataAdjuster(components);
    components = adjuster.adjustComponentDataPreSave();

    % -- code struct -------------------------------------------------------
    code = parse_code_struct(code_text, class_name);

    % -- appData struct (required for R2018a+ compatibility) ---------------
    appData = AppData([], [], []);
    appData.MinimumSupportedVersion = 'R2018a';

    % -- save --------------------------------------------------------------
    % Variable names must match exactly what App Designer expects:
    %   components, code, appData
    save(mat_out, 'components', 'code', 'appData');
end


% =========================================================================
% Helper: inject DesignTimeProperties.CodeName onto every UI component
% =========================================================================
function inject_design_time_properties(app)
    pub = properties(app);
    for k = 1:numel(pub)
        prop_name = pub{k};
        try
            comp = app.(prop_name);
        catch
            continue
        end
        if ~isgraphics(comp)
            continue
        end
        if ~isprop(comp, 'DesignTimeProperties')
            try
                addprop(comp, 'DesignTimeProperties');
            catch
                continue
            end
        end
        comp.DesignTimeProperties = struct( ...
            'CodeName',          prop_name, ...
            'GroupId',           '', ...
            'ComponentCode',     {{}}, ...
            'ImageRelativePath', '', ...
            'DirtyProps',        struct());
    end
end


% =========================================================================
% Helper: replace startupFcn body with a no-op
% =========================================================================
function out = noop_startup(code_text)
    out = regexprep(code_text, ...
        '(function\s+startupFcn\s*\(app\)).*?(^\s*end\b)', ...
        '$1\n        end', ...
        'dotexceptnewline', 'lineanchors');
end


% =========================================================================
% Helper: read classdef CDATA from document.xml inside a .mlapp ZIP
% =========================================================================
function code_text = read_classdef(mlapp_path)
    tmp_dir = [tempname '_readxml'];
    unzip(mlapp_path, tmp_dir);
    cleanup = onCleanup(@() rmdir(tmp_dir, 's'));

    xml_file = fullfile(tmp_dir, 'matlab', 'document.xml');
    if ~exist(xml_file, 'file')
        error('finalize_mlapp:noDocXML', ...
            'matlab/document.xml not found in %s', mlapp_path);
    end

    tree      = xmlread(xml_file);
    code_text = extract_cdata(tree);
    if isempty(code_text)
        error('finalize_mlapp:noCDATA', ...
            'Could not extract classdef text from document.xml');
    end
end


% =========================================================================
% Helper: walk XML DOM and return first text/CDATA node containing "classdef"
% =========================================================================
function text = extract_cdata(node)
    text = '';
    nt = node.getNodeType();
    if nt == node.TEXT_NODE || nt == node.CDATA_SECTION_NODE
        val = char(node.getNodeValue());
        if contains(val, 'classdef')
            text = val;
            return
        end
    end
    children = node.getChildNodes();
    for i = 0 : children.getLength() - 1
        text = extract_cdata(children.item(i));
        if ~isempty(text)
            return
        end
    end
end


% =========================================================================
% Helper: parse classdef text and extract code struct fields
% =========================================================================
function code = parse_code_struct(code_text, class_name)
    code = struct();
    code.ClassName   = class_name;
    code.AppTypeData = struct();

    % EditableSectionCode: private properties block
    priv = regexp(code_text, ...
        'properties\s*\(Access\s*=\s*private\)(.*?)end', ...
        'tokens', 'once', 'dotexceptnewline');
    if ~isempty(priv)
        lines = strsplit(priv{1}, newline());
        code.EditableSectionCode = lines(:)';
    else
        code.EditableSectionCode = {'    '};
    end

    % StartupCallback
    sc = regexp(code_text, ...
        'function\s+(startupFcn|StartupFcn)\s*\(app\)(.*?)end', ...
        'tokens', 'once', 'dotexceptnewline');
    if ~isempty(sc)
        lines = strsplit(sc{2}, newline());
        code.StartupCallback = struct('Name', sc{1}, 'Code', {lines(:)'});
    end

    % Callbacks (function Xxx(app, event))
    cb_pat = 'function\s+(\w+)\s*\(app\s*,\s*event\)(.*?)end';
    [names, bodies] = regexp(code_text, cb_pat, 'tokens', 'match', ...
        'dotexceptnewline');
    if ~isempty(names)
        cb_names = cellfun(@(t) t{1}, names, 'UniformOutput', false);
        cb_codes = cellfun(@(t) strsplit(t{2}, newline()), bodies, ...
                            'UniformOutput', false);
        code.Callbacks = struct('Name', cb_names, 'Code', cb_codes);
    end
end


% =========================================================================
% Cleanup helper
% =========================================================================
function safe_cleanup(tmp_dir, class_name)
    rmpath(tmp_dir);
    try
        rmdir(tmp_dir, 's');
    catch
    end
    try
        clear(class_name);
    catch
    end
end
