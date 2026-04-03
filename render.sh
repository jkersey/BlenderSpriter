#!/bin/sh

# /opt/blender/blender ./blend_files/wall_1.blend --background --python RenderScript.py
# /opt/blender/blender ./blend_files/shadow_person.blend --background --python RenderScript.py

BLENDER_EXE="/opt/blender4/blender"

BASEDIR="./models"
OPTS="--log-file log.txt --verbose 0 --background --python render.py"

"$BLENDER_EXE" $BASEDIR/walls/desert_tech/wall_desert_tech.blend $OPTS
"$BLENDER_EXE" $BASEDIR/characters/npc_default/npc_default.blend $OPTS
"$BLENDER_EXE" $BASEDIR/objects/container_cryo/container_cryo.blend $OPTS

# Experimental
# "$BLENDER_EXE" $BASEDIR/characters/npc_default/npc_default_no_grip.blend $OPTS
# "$BLENDER_EXE" $BASEDIR/characters/npc_default/npc_default_b4.blend $OPTS
