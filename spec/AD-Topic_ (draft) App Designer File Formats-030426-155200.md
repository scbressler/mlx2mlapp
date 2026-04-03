Topic: (draft) App Designer File Formats

References

To replace:  Compatibility Between Different Releases of App Designer - MATLAB & Simulin

k

Live Code File Format (.mlx) - MATLAB & Simulink

Live Code File Format (.m) - MATLAB & Simulink

Plain Text Beta Documentation

check rules for guibutton/label/menuitem

App Designer File Formats

There are two file formats for storing apps in App Designer. By default, App Designer stores

apps using a .mlapp extension. This type of app can only be edited in App Designer.

You can also save apps using a plain text file format that consists of two files (.m and .xml). The

plain text format is useful for apps that are managed with source control, or that you would like

to edit outside of App Designer (since R2026b).

Choose App File Format

For the most part, apps saved in the plain text format and the binary format have the same

behavior. This table summarizes the main considerations when choosing a file format for your

app.

Use Case

File Format

Share app with users

binary (.mlapp)

across multiple MATLAB

releases

Use source control

plain text (.m + .xml)

Simulink apps

binary (.mlapp)

User authored

components

binary (.mlapp)

Plain Text Apps (since R2026b)

Binary Apps

File

.m and .xml

.mlapp

Extensio

ns

Editors

App Designer

App Designer

MATLAB Editor

External editors

Source

Control

MATLAB Comparison Tool

MATLAB Comparison Tool (link to:  Com

Source Control Integration in MA

pare and Merge Apps - MATLAB & Simulin

TLAB - MATLAB & Simulink

k )

Limitatio

Not compatible with:

Not compatible with:

ns

Simulink apps

MATLAB Editor

User authored components

External editors

External control tools

Modify Default App File Format

By default, new apps created in App Designer are stored with an .mlapp extension. You can

change the default app file format.

Convert App File Format

You can convert existing apps into a different file type by creating a copy of your app.

Binary Apps

The default app file format consists of one file with a  .mlapp  extension. This app format uses

Open Packaging Conventions technology, which is an extension of the zip file format.

Apps stored with a  .mlapp  extension can only be edited in App Designer.

Plain Text Apps

The plain text app file format consists of two files:

A MATLAB® code file ( .m ) that contains all the app code you write, such as callbacks and

properties.

An XML file ( .xml ) that contains the app configuration, which includes the app components,

layout, and metadata.

App code and app configuration files can be opened in both App Designer and external editors.

App Code File (.m)

The MATLAB code file ( .m ) associated with your app stores the app code. This code includes:

Properties, including both App Designer-generated properties for each UI component in your

app and any properties you create to share data in your app.

Callback functions

Helper functions

The file also contains a property,  AppConfigFilename , that stores the path to the XML file

with your app layout.

The recommended way to edit this file is in App Designer Code View. If you open the code file

from the MATLAB Files pane, it will automatically open into App Designer Code View.

Alternatively, you can open the code file in other editors. For example, to open the file in the

MATLAB Editor, right-click the file in the Files pane and select Open as Text. However, if you

edit this file outside of App Designer, you might lose code when you load the app in App

Designer in the future.

You can use other editors for these tasks:

Viewing the app code outside of App Designer

Adding code to sections of the file that are editable in App Designer Code View. For example,

you can make changes to the code in your callback functions or in property blocks you

manage.

Using other editors for these tasks may result in losing code when you load the app in App

Designer in the future:

Making changes to the app layout

Adding a new callback function

Adding a new property to the UI components block

App Configuration File (.xml)

The XML file associated with your app stores the app configuration. This configuration includes:

App layout and UI components

Component configuration, such as any properties you set on a UI component in your app

App details, such as the app name and author

Internal App Designer data used to load and run your app

App Designer is the recommended environment for editing apps. When you interactively

develop your app in App Designer, for example by adding a new component or updating the

properties of a component, App Designer updates the XML file to reflect the changes.

Compatibility Between Different Releases of App Designer

If you develop apps over multiple releases of MATLAB, or if you edit or run a shared App

Designer app in a different release than it was saved in, App Designer makes updates to your

app to provide compatibility between the releases. If you encounter errors, you can open the

app in App Designer to help resolve them.

You can now save apps using a plain text app format that consists of two files (.m and .xml). To

run these apps in earlier versions of MATLAB, convert to the binary app format (.mlapp).

Edit and Run Apps in Later Releases

(same)

Edit and Run Apps in Earlier Releases

If you have an existing  .mlapp  app that was created in one MATLAB release and you are using

an earlier MATLAB release, you can open the app in App Designer for editing.

App Designer removes any functionality that is unsupported in the release you are using and

provides an option to see the differences in the updated app. This removal might impact the app

functionality. For example, if you load an app with a UI component in a release before the

component was introduced, App Designer removes the component from the app.

If you try to run an app in an earlier release, you might encounter errors if the app uses

functionality that is not supported in your release. To resolve the errors, open the app in App

Designer and view the changes App Designer makes to the app.

Existing apps stored in the plain text file format will not open in App Designer in MATLAB

releases before R2026b. If you try to open the app code file or app configuration file, then it will

open in the MATLAB Editor. You will not be able to run your app unless you switch to a

supported release.

Save Copy of App

App Designer provides two options to create copies of your app: Save Copy As and Save As.

You can access both options from the Save button in the App Designer toolstrip. These options

serve different purposes, and their behavior is also different.

To save a copy of your app to edit or share later, use Save Copy As. When you use this

option, App Designer saves the copy of the app in the specified folder, but it does not replace

the app in your current session.

To save a copy of your app and continue editing it, use Save As. When you use this option,

App Designer saves the copy of the app in the specified folder and replaces the app in your

current session.

You can convert an existing MLAPP app to the plain text format, and vice versa, by creating a

copy and selecting either  MATLAB APP (*.m)  or  MATLAB APP (*.mlapp)  when prompted.

First Draft
App Designer File Formats

notes

Overview of M+XML and MLAPP files

Breakdown of how user code vs. generated code is represented

Decision-making support about when to use each, including what isnʼt

supported (e.g. UAC? Simulink apps?)

need to draft subtitle?

live script pages donʼt have subtitles; they are listed as bullet points under “what

is a live script?” page

By default, App Designer stores apps using a binary file format with a .mlapp extension. The

binary file format consists of one file and can only be edited in App Designer. This binary app

format uses Open Packing Conventions technology, which is an extension of the zip file

format.

You can also save apps using a plain text app file format (.m and .xml). The plain text format

is useful for apps that you use with source control or that have code that you would like to

edit outside of App Designer (Since R2026b).

The plain text app format is not compatible with Simulink apps or user authored components.

Both app file formats have the same behavior in App Designer. For information on creating

app layouts interactively, see Lay out Apps in App Designer Design View. For information on

editing app code, see Manage Code in App Designer Code View.

MLAPP

notes

MLAPP: How code is represented

All code in MLAPP file

User code writeable, layout and data read-only

Worth mentioning OPC(?), like .mlx file page does?

Live Code File Format (.mlx) -

MATLAB & Simulink

maybe nix this section? not much to say unless itʼs in comparison to the plain text

format (table? list?)

The binary file format consists of one file (.mlapp) and can only be edited in App Designer.

This binary app format uses Open Packaging Conventions technology, which is an extension

of the zip file format.

M+XML

notes

M+XML: How code is represented

The plain text file format consists of two files:

A MATLAB code file (.m) that contains all of the app code you write, such as callbacks and

properties.

An XML file (.xml) that contains the app configuration, which includes the app

components, layout, and metadata.

MATLAB Code File (.m)

notes

User code in M file

Note needed about the warning that pops up?

The MATLAB code file (.m) associated with your app stores the app code. This code

includes:

Properties, including both App Designer-generated properties for each UI component in

your app and any properties you create to share data in your app.

Callback functions

Helper functions

The file also contains a property, AppConfigFilename, that stores the path to the XML file

with your app layout.

The recommended way to edit this file is in App Designer Code View. If you select the code

file from the MATLAB file tree, it will automatically open into App Designer Code View.

Alternatively, you can open the file in other editors. For example, to open the file in the

MATLAB Editor, right-click the file in the Files pane and select Open as Text. However, if you

edit this file outside App Designer, you might lose code when you load the app in App

Designer in the future.

You can use other editors for these tasks:

Viewing the app code outside of App Designer

Adding code to sections of the file that are editable in App Designer Code View. For

example, you can make changes to the code in your callback functions or in property

blocks that you manage.

Using other editors for these tasks may result in losing code when you load the app in App

Designer in the future:

Making changes to the app layout

Adding a new callback function

Adding a new property to the UI components properties block

XML File

notes

Layout and data in XML file

Component and properties as elements

Design-time data as attributes

Metadata

The XML file associated with your app stores the app configuration. This configuration

includes:

App layout and UI components

Component configuration, such as any properties you set on a UI component in your app

App details, such as the app name and author

Internal App Designer data used to load and run your app

App Designer is the recommended environment for editing apps. When you interactively

develop your app in App Designer, for example by adding a new component or updating the

properties of a component, App Designer updates the XML file to reflect the changes.

Modify Default App File Format

notes

How to modify your default file format

is there a way to do this from the command line?

rewrite to be more general

In MATLAB, on the Home tab, in the Environment section, click Settings. Select App

Designer in the left pane. Under Create new apps as:, select M. Then, select Blank App

from the App Designer Start Page to create a new app with the plain text file format.

By default, new apps created in App Designer will be stored with an .mlapp extension. You

can change the default app file format.

1. In MATLAB, on the Home tab, in the Environment section, click Settings.

2. Select App Designer in the left panel.

3. Under Create new apps as:, select either M or MLAPP.

Convert App File Type

notes

How to convert apps between formats

Preferences → what does this mean

Save As

A note about shadowing?

combine this with Save Copy of App → add note about changing file type

You can convert an existing MLAPP file to the plain text format, and vice versa.

1. Open the app in App Designer.

2. In the Designer tab, select Save > Save As or Save a Copy As.

3. Rename the app, and then under Save as type:, select either MATLAB APP (*.m) or

MATLAB APP (*.mlapp).

4. Click save to create a copy of your app with the chosen format.

Compatibility Between Different Releases of App Designer

notes

Compatibility of different App Designer files

Running/editing/sharing MLAPP files between releases → same info as before

Running/editing/sharing M+XML files between releases → earlier versions

recognize app code (.m) as a class, can be opened in MATLAB but will not run

