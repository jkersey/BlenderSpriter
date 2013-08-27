BlenderSpriter (alpha 2)
============================

Homepage/Screenshots:
---------------------

[http://jameskersey.com/BlenderSpriter](http://jameskersey.com/BlenderSpriter)


Description:
-------------

This script turns character animations into sprite sheets.

For each .blend file in the blend_files directory with a camera set up to point at the target object, it will run through all of the animations and output the animation in the listed directions into a 1024x1024 .png file.



Setup:
------

I'm running this with the 2.68a version of Blender and the included Python on Windows.  I installed the Pillow image processing library in my installed version of Python3.3 and then copied the PIL and Pillow-2.1.0-py3.3.egg-info directories from the /Lib/site-packages directory to Blender's python/lib/site-packages directory

The config file has options for output path, anti-aliasing, and frame skipping

What you'll need to do in the .blend file:

* Create an empty object called "Grip"
* Set Grip as the parent of your camera
* Set Grip as the parent of all lamps
* Make sure the camera is set to Orthographic
* Position the camera so that the entire object is visible and is as close to the edge as possible (accounting for animations)
* Check the included player.blend file for examples






Running:
--------

    c:/Program Files/Blender Foundation/Blender/blender.exe --background --python RenderScript.py"

There is an ant script and .sh script included as well

I also had to do this:

    set PYTHONPATH=%PYTHONPATH%;.

To get it to see the Stitcher.py file.



Output:
-------

The output goes into the output directory, split into an images directory for the sprite sheets and a js directory for the JSON files with the animation lists.



Known Issues:
-------------
[ ] It only lets you fill one 1024x1024 page per .blend file

(Windows) I tried using an external version of Python 3.3, but I got the [cannot import name: MAXREPEAT](http://bugs.python.org/issue18050) exception and couldn't get past it.

Further Reading:
----------------

[http://www.blender.org/documentation/blender_python_api_2_61_0/info_tips_and_tricks.html](http://www.blender.org/documentation/blender_python_api_2_61_0/info_tips_and_tricks.html)

