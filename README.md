# Spriter

Render and compile sprite sheets for the as-yet-unavailable Adventur game engine. Renders Blender models to per-frame PNGs, then packs them into per-skin sprite sheets with Aseprite-compatible JSON metadata.

Working on plugins for Godot, Phaser, and Unity. They're just .json files with coordinates for .png images, how hard can it be? 

---

## Quickstart

### Prerequisites

- [Blender 3.x or 4.x](https://www.blender.org/download/) installed and accessible from the terminal (`blender --version` should work)
- Python 3.8+
- Pillow: `pip install Pillow` (required for the compiler step)
- A `.blend` file with at least one armature-driven animation

### Setup

1. Clone this repo:
   ```bash
   git clone https://github.com/jkersey/spriter.git
   cd spriter
   ```

2. Copy the example config and edit it for your project:
   ```bash
   cp config.ini.example config.ini
   ```
   Open `config.ini` and set:
   - `blender_file` — path to your `.blend` file
   - `output_path` under `[output]` — where rendered frames should be saved
   - `output_path` under `[compiler]` — where sprite sheets should be saved
   - `[directions]` section — each key is a direction name (e.g. `north`, `northeast`); move unused directions to `[unused]` to skip them

3. Render frames from Blender:
   ```bash
   python run.py
   ```
   Blender opens in background mode and renders each animation frame from each configured direction. Depending on model complexity and direction count, this may take several minutes.

4. Compile frames into a sprite sheet:
   ```bash
   python compiler.py
   ```
   Output: one `{skin}.json` and `{skin}.png` per skin in your `output_dir` (Aseprite format).

5. Import the output into Godot 4 using the [Godot Spriter Importer](https://github.com/jkersey/godot-spriter-importer) plugin.

---

## Advanced Usage

### Tools

| Script | Purpose |
|---|---|
| `render.py` | Blender automation script invoked by `run.py`. Do not call directly. |
| `compiler.py` | Pack rendered frames into sprite sheets + Aseprite JSON |
| `serve.py` | Local dev server for previewing renders and triggering builds |
| `wall_compiler.py` | Wall sprite compiler, still in progress but the math works. |

### Configuration

Still a little primitive, move the directions you're not interested in to the unused section. This is what the camera uses to render the model from different angles. Fallout 1 & 2 wouldn't have needed north or south, for example. I've left these formulas out in the open to give you the option of tweaking them if you need to.

```ini
[config]
blender_file = ./models/character.blend
ignore_actions = Action,ObAction,walkx

[output]
output_path = ./render
use_antialiasing = True
frame_step = 4

[compiler]
input_path = ./render
output_path = ./compiled

[directions]
north = 2 * pi / 4
south = 6 * pi / 4
east = pi
west = 0.0
northwest = pi / 4
southwest = 7 * pi / 4
southeast = 5 * pi / 4
northeast = 3 * pi / 4

[unused]
```

UI note: Directions listed under `[unused]` are skipped during rendering. The dev server's toggle UI moves directions between `[directions]` and `[unused]`.

### Preview with the dev server

```bash
python serve.py
```

Starts a local server at **http://localhost:8080/index.html**. Open that URL in a browser to preview renders and trigger builds from the UI.

#### API endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/renders` | Scan `render/` and return sprite inventory by skin/station/animation/direction |
| GET | `/api/config` | Return active and inactive directions from `config.ini` |
| POST | `/api/config/toggle` | Toggle a direction between active and inactive |
| POST | `/api/render` | Trigger rendering and return stdout/stderr |

Static files (including `index.html`) are served from the scripts directory.

---

## Tests

```bash
python -m pytest tests/ -v
```

## Support

If Spriter saves you time, consider supporting development:

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/YOUR_KOFI_USERNAME)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/jkersey?style=social)](https://github.com/sponsors/jkersey)
