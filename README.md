# Adventur Scripts

Render and compile sprite sheets for the Adventur game engine. Renders Blender models to per-frame PNGs, then packs them into per-skin sprite sheets with Aseprite-compatible JSON metadata.

---

## Tools

| Script | Purpose |
|---|---|
| `render.sh` | Render all `.blend` files to PNG frames via Blender |
| `compiler.py` | Pack rendered frames into sprite sheets + Aseprite JSON |
| `serve.py` | Local dev server for previewing renders and triggering builds |
| `wall_compiler.py` | Legacy wall sprite compiler |

---

## Requirements

- [Blender](https://www.blender.org/) 4.x (path configured in `render.sh`)
- Python 3.x with Pillow: `pip install Pillow`

---

## Workflow

### 1. Render

```bash
./render.sh
```

Runs Blender in background mode against each `.blend` file listed in `render.sh`. Output lands in `render/` with this structure:

```
render/
  {skin}/
    {station}/
      {animation}/
        {direction}/
          frame_0000.png
          frame_0001.png
          ...
```

Blender executable path is set at the top of `render.sh`:

```sh
BLENDER_EXE="/opt/blender4/blender"
```

### 2. Compile

```bash
python compiler.py
```

Reads rendered frames from the path set in `config.ini` (`compiler.input_path`) and writes one `{skin}.png` + `{skin}.json` pair per skin to `compiler.output_path`.

The JSON is in Aseprite hash format with `frameTags` per animation+direction (e.g. `idle_north`, `walk_south`). Compatible with Godot's Aseprite importer, Phaser's `Loader.aseprite()`, and Unity's Aseprite importer.

#### Legacy format

```bash
python compiler.py --format json
```

Produces `spritesheet_N.png` + `file.json` + `file.bin` + `file.csv` (old packed-sheet format).

### 3. Preview with the dev server

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
| POST | `/api/render` | Trigger `render.sh` and return stdout/stderr |

Static files (including `index.html`) are served from the scripts directory.

---

## Configuration

`config.ini` is not committed to git. Create one locally:

```ini
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

Directions listed under `[unused]` are skipped during rendering. The dev server's toggle UI moves directions between `[directions]` and `[unused]`.

---

## Tests

```bash
python -m pytest tests/ -v
```
