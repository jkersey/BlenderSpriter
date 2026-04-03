# BlenderSpriter

Generate sprite sheets from Blender 3D animation files — one sheet per action, one sheet per skin.

> Featured on [BlenderNation](https://www.blendernation.com/2013/08/29/blenderspriter/). Works with Blender 4.x.

---

## What it does

BlenderSpriter renders every action in a `.blend` file into a single sprite sheet, with frames laid out in row-major order. If you define multiple skins (texture swaps), it generates a separate sheet for each one — same layout, different look.

Output includes:
- PNG sprite sheet per action (and per skin)
- Aseprite-compatible JSON metadata with frame coordinates and animation tags

This makes it straightforward to drop the output directly into Godot, Phaser, Unity (via the Aseprite importer), or any engine that reads Aseprite's JSON format.

---

## Requirements

- [Blender](https://www.blender.org/) 2.x – 4.x
- No additional Python dependencies — uses Blender's built-in Python environment

---

## Usage

```bash
blender --background your_character.blend --python blenderspriter.py -- \
  --output ./sprites \
  --width 64 \
  --height 64
```

### With skins

```bash
blender --background your_character.blend --python blenderspriter.py -- \
  --output ./sprites \
  --width 64 \
  --height 64 \
  --skins skin_default skin_red skin_blue
```

This produces one sprite sheet per skin per action:

```
sprites/
  walk_skin_default.png
  walk_skin_default.json
  walk_skin_red.png
  walk_skin_red.json
  idle_skin_default.png
  idle_skin_default.json
  ...
```

---

## Aseprite JSON output

Each sprite sheet is accompanied by a `.json` file compatible with Aseprite's array export format. This includes:

- Frame coordinates (`x`, `y`, `w`, `h`) for every frame
- Frame duration derived from the Blender scene FPS
- `frameTags` mapping each Blender action name to its frame range

Example:

```json
{
  "frames": [
    {
      "filename": "walk_00.png",
      "frame": { "x": 0, "y": 0, "w": 64, "h": 64 },
      "rotated": false,
      "trimmed": false,
      "spriteSourceSize": { "x": 0, "y": 0, "w": 64, "h": 64 },
      "sourceSize": { "w": 64, "h": 64 },
      "duration": 100
    }
  ],
  "meta": {
    "app": "https://www.aseprite.org/",
    "version": "1.2.25",
    "image": "walk_skin_default.png",
    "format": "RGBA8888",
    "size": { "w": 512, "h": 64 },
    "scale": "1",
    "frameTags": [
      { "name": "walk", "from": 0, "to": 7, "direction": "forward" }
    ],
    "slices": []
  }
}
```

Godot's Aseprite importer, Phaser's `Loader.aseprite()`, and Unity's Aseprite importer (2021.2+) all read this format directly.

---

## Workflow example

1. Build and rig your character in Blender
2. Create actions (`walk`, `run`, `idle`, `attack`, etc.) in the Action Editor
3. Set up skin materials as needed
4. Run BlenderSpriter from the command line
5. Import the PNG + JSON directly into your engine

---

## Tips

- Action names become the `frameTags` names in the JSON — name them clearly (`walk`, `run_fast`, `jump_start`)
- Frame size should match your target tile size in-engine
- Skins are swapped at render time, so any material or texture can be used

---

## Background

BlenderSpriter started in 2013 as a weekend script to avoid manually stitching rendered frames together. It's been quietly used and forked since then and still runs on current Blender without modification.

---

## License

MIT
