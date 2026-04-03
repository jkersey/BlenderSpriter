import json
from unittest.mock import patch
from PIL import Image
from constants import SHEET_WIDTH, SHEET_HEIGHT

# Patch process_images so Compiler.__init__ doesn't try to read disk
def make_compiler(format='aseprite', input_dir='/tmp/in', output_dir='/tmp/out'):
    with patch.object(__import__('compiler', fromlist=['Compiler']).Compiler, 'process_images'):
        from compiler import Compiler
        return Compiler(input_dir, output_dir, format=format)


def test_format_defaults_to_aseprite():
    c = make_compiler()
    assert c.format == 'aseprite'


def test_format_json_stored():
    c = make_compiler(format='json')
    assert c.format == 'json'


def test_store_aseprite_single_frame():
    c = make_compiler()
    c.store_aseprite('player', 'idle', 'north', 0, 0, 16, 16)

    assert 'player' in c.aseprite_data
    frames = c.aseprite_data['player']['frames']
    assert 'player_idle_north_0' in frames
    frame = frames['player_idle_north_0']
    assert frame['frame'] == {'x': 0, 'y': 0, 'w': 16, 'h': 16}
    assert frame['rotated'] == False
    assert frame['trimmed'] == False
    assert frame['spriteSourceSize'] == {'x': 0, 'y': 0, 'w': 16, 'h': 16}
    assert frame['sourceSize'] == {'w': 16, 'h': 16}
    assert frame['duration'] == 100


def test_store_aseprite_frame_counter_increments():
    c = make_compiler()
    c.store_aseprite('player', 'idle', 'north', 0, 0, 16, 16)
    c.store_aseprite('player', 'idle', 'north', 16, 0, 16, 16)

    frames = c.aseprite_data['player']['frames']
    assert 'player_idle_north_0' in frames
    assert 'player_idle_north_1' in frames


def test_store_aseprite_frametag_opens_on_first_frame():
    c = make_compiler()
    c.store_aseprite('player', 'idle', 'north', 0, 0, 16, 16)

    data = c.aseprite_data['player']
    assert data['current_tag_name'] == 'idle_north'
    assert data['current_tag_from'] == 0


def test_store_aseprite_frametag_closes_on_direction_change():
    c = make_compiler()
    c.store_aseprite('player', 'idle', 'north', 0, 0, 16, 16)
    c.store_aseprite('player', 'idle', 'north', 16, 0, 16, 16)
    c.store_aseprite('player', 'idle', 'south', 32, 0, 16, 16)  # new direction

    data = c.aseprite_data['player']
    assert len(data['tags']) == 1
    assert data['tags'][0] == {'name': 'idle_north', 'from': 0, 'to': 1, 'direction': 'forward'}
    assert data['current_tag_name'] == 'idle_south'
    assert data['current_tag_from'] == 2


def test_store_aseprite_multiple_skins_independent():
    c = make_compiler()
    c.store_aseprite('player', 'idle', 'north', 0, 0, 16, 16)
    c.store_aseprite('npc_default_yellow', 'idle', 'north', 0, 0, 16, 16)

    assert c.aseprite_data['player']['frame_count'] == 1
    assert c.aseprite_data['npc_default_yellow']['frame_count'] == 1


def test_save_aseprite_writes_json_file(tmp_path):
    c = make_compiler(output_dir=str(tmp_path))
    c.store_aseprite('player', 'idle', 'north', 0, 0, 16, 16)
    c.store_aseprite('player', 'idle', 'north', 16, 0, 16, 16)
    c.save_aseprite()

    out = tmp_path / 'player.json'
    assert out.exists()
    data = json.loads(out.read_text())
    assert 'frames' in data
    assert 'meta' in data


def test_save_aseprite_meta_image_matches_skin(tmp_path):
    c = make_compiler(output_dir=str(tmp_path))
    c.store_aseprite('npc_default_yellow', 'idle', 'north', 0, 0, 16, 16)
    c.save_aseprite()

    data = json.loads((tmp_path / 'npc_default_yellow.json').read_text())
    assert data['meta']['image'] == 'npc_default_yellow.png'


def test_save_aseprite_closes_final_frametag(tmp_path):
    c = make_compiler(output_dir=str(tmp_path))
    c.store_aseprite('player', 'idle', 'north', 0, 0, 16, 16)
    c.store_aseprite('player', 'idle', 'north', 16, 0, 16, 16)
    c.store_aseprite('player', 'walk', 'north', 32, 0, 16, 16)
    c.save_aseprite()

    data = json.loads((tmp_path / 'player.json').read_text())
    tags = data['meta']['frameTags']
    assert len(tags) == 2
    assert tags[0] == {'name': 'idle_north', 'from': 0, 'to': 1, 'direction': 'forward'}
    assert tags[1] == {'name': 'walk_north', 'from': 2, 'to': 2, 'direction': 'forward'}


def test_save_aseprite_meta_fields(tmp_path):
    c = make_compiler(output_dir=str(tmp_path))
    c.store_aseprite('player', 'idle', 'north', 0, 0, 16, 16)
    c.save_aseprite()

    data = json.loads((tmp_path / 'player.json').read_text())
    meta = data['meta']
    assert meta['format'] == 'RGBA8888'
    assert meta['scale'] == '1'
    assert meta['size'] == {'w': SHEET_WIDTH, 'h': SHEET_HEIGHT}
    assert meta['layers'] == []
    assert meta['slices'] == []


def test_aseprite_produces_per_skin_png_and_json(tmp_path):
    # Build a minimal synthetic input directory:
    # input/player/station1/idle/north/frame_0.png
    skin_dir = tmp_path / 'input' / 'player' / 'station1' / 'idle' / 'north'
    skin_dir.mkdir(parents=True)
    img = Image.new('RGBA', (16, 16), color=(255, 0, 0, 255))
    img.save(str(skin_dir / 'frame_0.png'))

    out_dir = tmp_path / 'output'
    out_dir.mkdir()

    from compiler import Compiler
    Compiler(str(tmp_path / 'input'), str(out_dir), format='aseprite')

    assert (out_dir / 'player.png').exists()
    assert (out_dir / 'player.json').exists()

    data = json.loads((out_dir / 'player.json').read_text())
    assert 'player_idle_north_0' in data['frames']
    assert data['meta']['image'] == 'player.png'
