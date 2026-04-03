Using Live Editor API to convert MLX example to XML

Problem: For beta doc, we want to ship an example. But Example Manager ships examples in

the  matlab/examples  directory, and beta doc is only supplied as a PDF. We have to write

these examples in XML so that they can be a part of the beta doc PDF.

Idea: Can we use the generated XML from example manager?

Example Manager usually creates an XML file from your example and puts it in

matlab/derived/glnxa64/examples/<toolbox>  for the most part, this is valid XML that

plays nice with our Oxygen Projects, although it lacks much of the markup we use (product

names,  guilabel , etc.).

Itʼs not that clear how we create these XML files. But I found this page:

https://mathworks.atlassian.net/wiki/spaces/EXINFRA/pages/41682721/External+Dependencies

+for+Examples+Tooling+code+base

It seems like we use the API  matlab.internal.liveeditor.openAndConvert(src,

xmlFileName, additionalArgs{:});  to create the MLX files.

I tried it with this API call:

>>

matlab.internal.liveeditor.openAndConvert('PredictBOCUsingLiteRTBlock.ml

x','PredictBOCUsingLiteRTBlock.xml','examplePath',pwd)

This seemed to create valid XML… The XML is wrapped in  cellscriptwrapper , and it also

has some elements like  procedure  that are specific to examples. It took some manual

intervention to make it into a topic example, but it wasnʼt too bad.

The XML doesnʼt include the images though. I had to manually copy images from the live script

and then insert the images into Oxygen. This is fine.

Update: I noticed after the fact that the API actually dumps the image files as PNGs in the

current working directory. I just added these to the example instead of copying and pasting.

