
PLAYER = 1
NPC = 2
CRYO_BED = 3
MINITRON = 4

IDLE = 1
WALK = 2
RUN = 3
PUNCH = 4

ACTIVATE = 5
ACTIVATED = 6
DEACTIVATE = 7

EMPTY = 9
EXPIRED = 10

NORTH = 0
NORTHEAST = 1
EAST = 2
SOUTHEAST = 3
SOUTH = 4
SOUTHWEST = 5
WEST = 6
NORTHWEST = 7

skin_encoding = {
    'player': PLAYER,
    'shadow_person': PLAYER,
    'npc_default_default': PLAYER,
    'npc_default_yellow': NPC,
    'container_cryo_default': CRYO_BED,
    'npc_default_default_minitron': MINITRON,
}

animation_encoding = {
    'idle': IDLE,
    'walk': WALK,
    'run': RUN,
    'punch': PUNCH,
    'activate': ACTIVATE,
    'activated': ACTIVATED,
    'deactivate': DEACTIVATE,
    'empty': EMPTY,
    'expired': EXPIRED,
}
direction_encoding = {
    'north': NORTH,
    'northeast': NORTHEAST,
    'east': EAST,
    'southeast': SOUTHEAST,
    'south': SOUTH,
    'southwest': SOUTHWEST,
    'west': WEST,
    'northwest': NORTHWEST,
}

