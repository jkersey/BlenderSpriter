BlenderSpriter (alpha 2)
============================

I'm writing this script to turn Blender character animations into sprite sheets.

For each .blend file in the blend_files directory with a camera set up to point at the target object, it will run through all of the animations and output the animation in the listed directions into a 1024x1024 .png file.

Setup:
------

I'm running this with the 2.68a version of Blender and the included Python on Windows.  I installed the Pillow image processing library in my installed version of Python3.3 and then copied the PIL and Pillow-2.1.0-py3.3.egg-info directories from the /Lib/site-packages directory to Blender's python/lib/site-packages directory

The config file has options for output path, anti-aliasing, and frame skipping

Running:
--------

    c:/Program Files/Blender Foundation/Blender/blender.exe --background --python RenderScript.py"

There is an ant script and .sh script included as well


Output:
-------

The output goes into the output directory, split into an images directory for the sprite sheets and a js directory for the JSON files with the animation lists.

Issues:
-------

[ ] It only lets you fill one 1024x1024 page per .blend file
[ ] 