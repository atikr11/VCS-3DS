#include <3ds.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>

static uint32_t little32(const unsigned char *p) {
    return p[0] | ((uint32_t)p[1]<<8) | ((uint32_t)p[2]<<16) | ((uint32_t)p[3]<<24);
}

static void inspect(void) {
    unsigned char sector[2048];
    FILE *iso = fopen("sdmc:/3ds/vcs/game.iso", "rb");
    if (!iso) {
        puts("Place your unpacked PSP disc image at\nsdmc:/3ds/vcs/game.iso");
        return;
    }
    if (fseek(iso, 16 * 2048, SEEK_SET) ||
        fread(sector, 1, sizeof sector, iso) != sizeof sector ||
        sector[0] != 1 || memcmp(sector+1,"CD001",5) || sector[6] != 1) {
        puts("Could not read ISO volume header.");
    } else {
        printf("Volume: %.32s\n", (char *)sector+40);
        printf("Root directory sector: %lu\n", (unsigned long)little32(sector+158));
    }
    fclose(iso);
}

int main(void) {
    gfxInitDefault();
    consoleInit(GFX_TOP, NULL);
    puts("Vice City Stories port experiment\nPSP disc reader\n");
    inspect();
    puts("\nA: read again    START: exit");
    while (aptMainLoop()) {
        hidScanInput();
        u32 pressed = hidKeysDown();
        if (pressed & KEY_START) break;
        if (pressed & KEY_A) inspect();
        gspWaitForVBlank();
    }
    gfxExit();
    return 0;
}
