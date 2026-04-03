#include <stdint.h>
#include <stdio.h>

typedef struct {
    uint8_t skin;
    uint8_t anim;
    uint8_t direction;
    uint8_t sheet_id;
    unsigned short x;
    unsigned short y;
    uint8_t width;
    uint8_t height;
} anim_info;

int main() {

    anim_info info;

    FILE *f = fopen("file.bin", "rb");
    if (!f) {
        printf("Error in reading file. Abort.\n");
        return -3;
    }
    while (fread(&info, sizeof(anim_info), 1, f)) {
        // printf("(%d, %d)\n", info.x, info.y);
        printf("ok:skin: %d,  anim:%d, direction: %d, sheet_id:  %d, loc: "
               "(%d,%d), w:%d, h: %d\n",
               info.skin, info.anim, info.direction, info.sheet_id, info.x,
               info.y, info.width, info.height);
    }
    fclose(f);

    return 0;
}
