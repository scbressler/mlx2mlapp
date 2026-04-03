@Jasmine Poppick

@Laura Rosado

Created:  08 Nov 2023

Last Updated:  02 Apr 2026

Draft in progress

R2026b

Doc R: Plaintext .m App File Format

What is doc requirements analysis and why do we do it?

Author (@username)

Date

Doc R status

Target Release (i.e. R20NNx)

Table of Contents

Summarize the Feature

Gather Resources and Identify Reviewers

Understand User Roles and Goals

Define Workflows for Goals

Design Doc Plan

Design Category Page if Needed

Notes

Summarize the Feature

The App Designer team will be introducing a new file format for apps. The current MLAPP file

format has been meeting the needs of many users, but for users creating large apps and

collaborating with other contributors over source control, the lack of editing flexibility, app

running performance, and binary file format causes a lot of pain. The feature is a new, dual

M+XML file format, where the M file contains user code, such as callbacks and properties, and

the XML contains App Designer-managed code, such as the app layout and metadata. This two-

file format provides better source control integration, better performance, and more flexibility in

the app building process.

Gather Resources

How do I do this?

Resources

RFA: File Format Preferences

F: Multi-File M App

RFA: matlab.apps.App

F: Plain Text App Editor Integration and Open Behaviors

FA: Metadata Serialization for Plain-Text File Format

RFA: Appendix Debugging

24a - Usability Test Plan for Plain Text Apps

Plain Text Format WG

Type of resource?

RF spec

RF spec

RF spec

RF spec

RF spec

RF spec

Usability study

notes

Meeting notes and

timeline

http://p4db.mathworks.com/cgi-bin/depotTreeBrowser.cgi?

Location for PDF 1-

FSPC=//doc/Bdoc/matlab/doc/src/nonrelease/matlab/26aPlaintextApps&HI

pager for 26a

DEDEL=YES

Preliminary Interview Data - Plain-Text Study

Understand User Roles and Goals

How do I do this?

prerelease

plaintext customer

engagement (see

26aPlaintextApps_

book.xml)

UX Preliminary

Interview notes

(see

Documentation

column)

User background

PRIS

User role

Goal

(what does this user

M

or

already know?)

persona

user

type

MATLAB user familiar

Power

User

Use App Designer to build new apps and edit

with general App

User

building

previously built apps

Designer workflows

an app

for

personal

use

Power

User

Diff and merge changes to an app built in App

User/

collabora

Designer

Devel

ting on

oper

an app

with

others

Power

User

Share an app built in App Designer that all app users

User/

building

can run

Devel

an app

oper

as a tool

for others

Power

User

Make quick edits to app code or layout without

User/

building

launching MATLAB or App Designer

Devel

an app

oper

for

personal

use

Define Workflows for Goals

How do I do this?

Workflows...

Use App Designer to build new apps and edit previously built apps

Workflow Steps

1. Open new or existing app for editing

Question

Answer

Where this information will be covered

What file format is my app?

MLAPP by

All existing doc - no changes.

How do I know whether I should

If the

default

switch my file format?

MLAPP

file format

is working

for you,

there is no

need to

switch.

If you use

your file

with

source

control or

want to

edit your

code in

the

MATLAB

desktop

or a

different

IDE,

consider

using the

dual file

format.

How do I convert an existing app

Save As or

to use M+XML?

Save Copy

As

How can I change the default file

MATLAB

format?

settings

panel

Share an app that all app users can run

Workflow Steps

1. Develop an app using your preferred file format.

Question

Answer

Where this information will be covered

I know I want to share my app

broadly. Should that impact my

choice of file format?

M+XML

apps will

not run

in

release

before

R2026a.

If you

want to

share

with

users on

older

releases,

you will

either

need to

save a

copy of

your app

as an

MLAPP

file or

develop

your app

using the

MLAPP

format

from the

start.

How do I choose my file format?

Set your

default

format in

MATLAB

settings.

Open

App

Designer,

click

New

Blank

App

2. When the app is ready to be shared, save a copy using the MLAPP file format

Question

Answer Where this information will be covered

How do I save an app in a

different file format?

Save As

or Save

Copy As

options

in the

toolstrip

3. Share the MLAPP file with users running MATLAB in previous releases

Question

Answer

Where this

information will be

covered

What will an app user in an older

They will get an error that the app

release see if I share an M+XML

can't run, and have an option to

file instead of an MLAPP file?

download a tool to convert the file.

Workflow Context

Question

Answer

Where this information will be

covered

What alternative approaches

Users can still

should users know about?

develop their

apps using the

MLAPP file

format to

conserve

compatibility

What prerequisites do users

need?

How will users apply the

App users will be

results?

able to run the

app in older

releases

When should users not apply

When an app

this workflow?

author will need

to develop their

app in previous

releases, it might

be easier to use

the MLAPP

format rather

than keep track

of two copies of

the same app

What measures of success

Being able to see

should users look for?

inside their app

file outside of

App Designer/in

their source

control system

What default behavior in the

N/A

workflow can users modify?

What limitations should users

Editing the file

consider?

outside of App

Designer can

lead to the app

becoming

corrupted/unable

to open or run

Diff and merge changes to an app

Workflow Steps

1. Create an app that's compatible with source control.

Question

Answer

What App Designer

Apps using the M+XML file format.

apps are compatible

with source control?

What is the M+XML file

A new dual-file plaintext file format for apps

format and why would

created in App Designer, that's easier to diff

I want to use it?

and merge using source control.

How do I create a new

Update your default file format in MATLAB

app using the M+XML

serttings. Then, open App Designer and click

file format?

New Blank App

How do I convert an

Open your app in App Designer. Use Save As

existing app to the

or Save Copy As in the toolstrip to save a

M+XML file format?

copy of your app in the new format.

How can I confirm that

File extension of app in App Designer is .m

my app is using the

Where this

information will

be covered

M+XML file format?

You have two files associated with the

app: appname.m and appname.xml.

In Code View, only your code is visible

(not the App Designer generated code)

You can open both files in any editor and

view their contents

2. View changes to the app that a collaborator has made.

Question

Answer

How do I view changes

Using the same workflow as

to my app file in source

diffing/merging any other plaintext files

control?

in source control.

What do the two files

M file:

consist of?

App callbacks and properties,

stored as MATLAB code

XML file:

App components and layout

App metadata, such as author and

version

Internal data managed by App

Designer

Where this

information will be

covered

3. Decide whether to accept or reject the changes to the app

Question

Answer

Where this

information will be

covered

How do I determine if a change

Run the updated file in MATLAB

will break the app?

or visually identify if the changes

make sense.

What part of the app

In the M file: callbacks and app

(component, callback code, etc.)

behavior

does the change relate to?

In the XML file: app component

creation and configuration and

app layout

4. Merge some of the changes into the app

Question

Answer

Are there parts of

The XML appendix can be fragile, so if you're

the file that I

merging code there, it's a good practice to

shouldn't merge?

verify that the app still loads runs after the

merge.

Avoid editing content in the XML file that

represents the internal data managed by App

Designer.

5. Verify that the app runs and behaves as expected after the merge

Question

Answer

How do I run the app?

From MATLAB (command line or from

the Editor with the M file open) or

App Designer

What can I do if the app

Revert the merge, or troubleshoot by

doesn't run or behave as

editing the app code by hand.

expected?

Workflow Context

Question

Answer

Where this

information will be

covered

Where this

information will be

covered

Where this

information will be

covered

What alternative

Users can still use the MLAPP file

approaches should

format and the built-in MATLAB

users know about?

diff/merge too.

What prerequisites do

Users need an existing app in a source

users need?

control system

How will users apply the

Diff/merge app files in the same way

results?

they diff/merge any other code file

When should users not

When the user needs their app to run in

apply this workflow?

previous versions of MATLAB

What measures of

Being able to see inside their app file

success should users

outside of App Designer/in their source

look for?

control system

What default behavior in

N/A

the workflow can users

modify?

What limitations should

Editing the file outside of App Designer

users consider?

can lead to the app becoming

corrupted/unable to open or run

Make quick edits to app code or layout without launching App Designer

Workflow Steps

1. Open the M and/or XML file outside of App Designer

Question

Answer

Where this information will be

covered

What programs can I open the

Any. The M file

file in?

is all MATLAB

code, so the

best

experience will

be to open it in

MATLAB.

How do I interpret what I'm

seeing?

The M file

consists of

all of the app

logic that

you have

written

The XML file

consists of

configuration

data that

App

Designer

manages,

such as

component

creation and

layout

2. Edit the callback code.

Question

Answer

Where this information will be

covered

How do I edit my callback code? Using your

normal MATLAB

code editing

practices.

What sorts of changes are safe?

Really any. This

is just M code,

you can edit it

like any other M

code.

3. Make small tweaks to property values

Question

Answer

Where this information will be

covered

How do a change a property

Find the

value?

element that

represents the

property on

the component

and update the

value.

What sorts of changes are

safe?

Editing a

property

What sorts of changes should I

Editing App

avoid making outside of App

Designer?

Designer-

managed

data

Large layout

changes

(deleting or

adding

components,

etc) – edit at

your own

risk.

4. Confirm that the app opens and runs as expected

Question

Answer

Where this information will be

covered

How do I run the app after making

Same as any

changes outside of App Designer?

app: open

the file in AD

and run it

there, or run

it from

MATLAB at

the

Command

Window or

What happens if I made edits that

aren't compatible with the file

structure?

from the

CFB

On run:

You'll see

an error

On load:

Either App

Designer

will try to

recover

and

update

the code,

OR the

app will

fail to load

with an

error

How do I recover from a file that App

Make sure

Designer can't load?

the code

in the

XML file

matches

the format

that App

Designer

expects

(todo: will

we have

an XSD

for

customers

to validate

against?)

Documenting the Appendix

Click here to expand...

Reviewer Comments for IDR

Expect file format to be documented - explain concept of canvasGroup, for instance

(Michelle)

Need to be told what parts of the file should I be editing, not editing. Esp if it can break my

app loading back into AD (Michelle)

Need to be taught to ignore the file hash (Michelle)

Can users do the merge if it is non trivial? How does the users reason on it when there are

many changes. (John G)

At some point if I wanted to see what was fully going on, I might want to see all of the

code.  For example, the information in the Inspector... where is Balloons and Fish.  Its not

here anywhere in this file.  At some point I would start wondering, but hadn't yet. (Vadim)

Should I be modifying / allowed to modify [file hash, UUID, other metadata ... ]? (Multiple

reviewers)

Reviewers also expressed that the XML content was easy to read/reason on just by looking

at.

When will users interact with the appendix?

Task

Information needed

Interpret a diff to decide whether to

Understanding of how XML elements and attributes

accept changes to an app

map to App Designer concepts

The ComponentName attribute changed. What

will this look like if I open or run the app?

Understanding whether the changes result in an

artifact that "works" (successfully runs/loads in App

Designer)

The diff shows that a callback function was

deleted. Will this result in errors if I try to run the

Perform a merge of an app file

In addition to the info needed to interpret a diff...

app?

Know if the resulting XML is well-formed

I merged a lot of different elements and

attributes. Is the end result something that App

Designer will be able to open?

Understanding of which parts of the file can be

edited and any risks associated with manual editing

There's a merge conflict in the file hash. Which

edit should I accept?

Check that an action in the design

Information about how to view appendix

environment had the intended effect

Where is the code that controls how my app is

laid out?

Understanding of how XML elements and attributes

map to App Designer concepts

I changed the icon of my button. Where can I see

this change reflected in the code?

Make quick edits to component

Understanding of which parts of the file can be

configuration

edited and any risks associated with manual editing

I want to quickly change the color of a panel. Can

make that change in VS Code? Is it possible I can

corrupt my app if I enter the color format

incorrectly?

Recover from an issue in the

Know if the resulting XML is well-formed

appendix code

What part of the document is causing the issue?

Know the format that App Designer needs to read

the data

If I delete this element entirely, what will happen

when I try to open the app in App Designer?

Design Doc Plan

How do I do this?

Release Notes

Products

Compatibility

Feature

Title

note?

highlight?

MATLAB

No

TBD, but likely

App Designer: Use new plaintext MAPP file

format for better source control integration

and performance

Reference

New or update?

Type

Title

Purpose

(function/class/o

bject...)

Update

Tool

App Designer

Update file format references

and screenshots

Update

settings API

matlab.appdesign

New settings group under

er settings

appdesigner (see A section of

this RFA spec:

RFA: File Format

Preferences

)

Re

quir

ed

for

26

b

pre

rele

ase

?

N

N

Update

Settings

App Designer

Include file format preferences N

Settings

New

Abstract class

matlab.apps.App

Provide a breadcrumb that

Y

advanced/curious users can

use to learn more about the

base class for plaintext apps

Document the

lifecycle/execution order of

an app, including:

When the XML file is

accessed.

Which class accesses it.

How the data flows from

XML to UI Components.

Make it clear that this is a

class that App Designer uses

to create apps, and isnʼt

meant to be something that a

user subclasses

See

Discussion: Reference P

ages for AppBase and App Cla

sses

 for proposal, mockups,

and discussion notes.

New

Abstract class

matlab.apps.App

Provide a breadcrumb that

Y

Base

advanced/curious users can

use to learn more about the

base class for plaintext apps

Provide a breadcrumb for

some of the back-box

methods that users have

asked about (e.g. g2732146)

Make it clear that this is a

class that App Designer uses

to create apps, and isnʼt

meant to be something that a

user subclasses

See

Discussion: Reference P

ages for AppBase and App Cla

sses

 for proposal, mockups,

and discussion notes.

Re

quir

ed

by

26

b

pre

rele

ase

?

Y

Topics

New or

Title

Overview of Content

update?

New

App Designer

Overview of M+XML and MLAPP files

File Formats

Breakdown of how user code vs. generated code is

represented

Decision-making support about when to use each,

including what isnʼt supported (e.g. UAC? Simulink

apps?) → represented as a table for quick decision

making

How to modify your default file format

Preferences

How to convert apps between formats

Save As

Convert M+XML to MLAPP for backwards compatibility

New

MATLAB App

Similar to live code page:

Live Code File Format (.m) -

Y?

File Format (.m

MATLAB & Simulink

+ .xml)

Proposing after 4/2/26 xml schema overview meeting:

Doc R: Plaintext .m App File Format | 4/2/2026

M: How code is represented

User code in M file

Layout and data in XML file

Component and properties as elements

Design-time data as attributes

Metadata

What is required to run/what will be automatically

assumed default

Update

Compatibility

Compatibility of different App Designer files

Between

Different

Releases of

App Designer

Running/editing/sharing MLAPP files between releases

Running/editing/sharing M+XML files between releases

Convert M+XML to MLAPP for backwards compatibility

Update

Compare and

KEEP information on merging MLAPP file

Merge Apps

ADD a section to describe merging M+XML files

Y

Y

What the diff/merge workflow looks like in the MATLAB

comparison tool (workflow to be designed)

High-level overview of how data is represented in the

appendix, with a link to the App Designer File Formats

topic for more info

Best practices for merging

General "edit at your own risk" note

Warning not to edit data managed by App Designer,

and info about how to identify that data in the

appendix

Update

Manage Code

Add callout about M+XML file format, with a link to more

N

in App Designer

info about the different file formats.

Code View

Update

Startup Tasks

Add information about when the StartupFcn executes

N

and Input

w/r/t the rest of app startup, since this isnʼt self-

Arguments in

documenting in the M+XML file.

App Designer

New?

TBD – any

troubleshooting

info needed?

Potentially a

new debugging

topic that

covers both

files? Probably

N

not needed, but

something to

keep on the

radar

New?

Binary App File

To parallel page on plain text app format

N

Format

Live Code File Format (.mlx) - MATLAB & Simulink

MLAPP: How code is represented

All code in MLAPP file

User code writeable, layout and data read-only

Example Apps

Most existing MLAPP examples will not be converted for R2026a, since MLAPP is still the

default file format and the task the examples are demonstrating arenʼt dependent on the file

format.

The examples that will be converted to M+XML are:

Example

Rationale for Conversion

Organize App Data

This example is meant for a similar audience as the plaintext file format:

Using MATLAB

Customers will large apps who might be collaborating on them with

Classes

others.

Notes

4/2/2026

Plain Text App XML Schema Overview (26b)

XML schema info needs to be accessible to users in the first release (see first comment)

PROPOSE: A topic page for the plain text file format

AD Check-in, 3/20/2026

Discussion: App Designer File Formats topic pages

Compare and Merge Apps – Updates/Questions

Cannot compare binary and plain text app code

Is Compare To the recommended way to compare .m files for plain text apps? Can .xml files b

compared/is there any reason to do so?

Is App Designer-managed code identified in the same way as .mlapp apps (gray background)?

AD Check-in, 02/10/2026

We decided not to document the base classes matlab.apps.App and matlab.apps.AppBase becau

they are not designed in a way to be used outside of App Designer (see Jyotiʼs comments above)

This is in contrast to the documented base classes for authoring components and charts:

https://www.mathworks.com/help/matlab/ref/matlab.ui.componentcontainer.componentcontai

class.html

https://www.mathworks.com/help/matlab/ref/matlab.graphics.chartcontainer.chartcontainer-

class.html

There should also be further discussions on how much of the xml structure to document, as this

design may evolve in future releases.

Next Steps:

Review gecks involving base classes and execution order. What questions are they asking and can they be addressed elsewhere
the doc?

AD Check-in, 7/01/2025

Without the generated code of the MLAPP file, IDR reviewers gave the feedback that how the ap

executes (e.g. when and how components are created using the XML data) feels like magic. To

mitigate this, the team decided to add additional comments in the M file, and also to document th

execution order of the plaintext app file somewhere in the doc. For more info, see F: XML Process

Transparency.

In follow-up conversations with the team, we decided to just make it more clear on the topic that

talks about the StartupFcn what the execution order is (since with the plaintext format there isnʼt

self-documenting generated code). If we need more, it can probably be in the matlab.apps.App

reference page.

AD Check-in, 4/22/2025

As of today, if users write any custom code in their M file that doesn't conform to the way AD

expects the code to look (e.g. different order of properties/callbacks, added local function...), AD

delete that code when the app is loaded. There are discussions about addressing this before

shipping plain-text, but if that doesn't converge, we will definitely need something in the doc to w

users of pitfalls.

AD Check-in, 1/28/2024

Alex's internal API for determining plaintext or not proposes not explicitly supporting indirect

inheritance for matlab.apps.App (both creating and running). We might want to call this out

somewhere in the doc when we talk about programmatically working with app files – likely on the

matlab.apps.App reference page.

Re: RF: API to Identify if M File is Plain Text App

Doc Design Review, 4/2/2024

Agenda:

Review Understand User Roles and Goals,  and Design Doc Plan sections (skip the workflow

sections)

Discuss doc plan. A couple topics for conversation:

Level of support for editing code outside of App Designer (user goal that we're explicitly

targeting? or side effect of merge workflows?)

Implications of documenting appendix (what's an incompatibility? possibility of users coding

against anything we document?)

Comfort/priority of updating doc examples to use MAPP (maybe bring this as a future topic,

not sure we're ready to answer this at this point in the design)

Leave Feedback for Doc R Templates

Related Information

Research Doc Requirements

Research Doc Requirements for a Feature

Sample Feature Doc Requirements

Customer-Focused Questions

