rem @echo off
set BLENDER_EXE=C:\Program Files\Blender Foundation\Blender_2.79b\blender.exe
set BASEDIR=%HOME%\Projects\Adventur\models
set OPTS=--background --python  render.py

echo =====================================================================
echo Starting render...
echo Blender is: %BLENDER_EXE%
echo Base dir is: %BASEDIR%
echo =====================================================================
"%BLENDER_EXE%" %BASEDIR%\walls\desert_tech\wall_desert_tech.blend %OPTS%
"%BLENDER_EXE%" %BASEDIR%\characters\npc_default\npc_default.blend %OPTS%
"%BLENDER_EXE%" %BASEDIR%\objects\container_cryo\container_cryo.blend %OPTS%

