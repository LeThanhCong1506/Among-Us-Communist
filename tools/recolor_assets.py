from pathlib import Path
import colorsys

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]

TARGETS = {
    "black": (45, 45, 50),
    "brown": (112, 68, 34),
    "pink": (238, 92, 164),
    "purple": (118, 72, 190),
    "white": (224, 226, 220),
}

FILES = [
    ("Assets/Images/Player/Red/red_ghost/step1_left.png", "Assets/Images/Player/{Title}/{lower}_ghost/step1_left.png"),
    ("Assets/Images/Player/Red/red_ghost/step1_right.png", "Assets/Images/Player/{Title}/{lower}_ghost/step1_right.png"),
    ("Assets/Images/Alerts/emergency_meeting_red.png", "Assets/Images/Alerts/emergency_meeting_{lower}.png"),
    ("Assets/Images/Alerts/report_dead_body_red.PNG", "Assets/Images/Alerts/report_dead_body_{lower}.png"),
]

# Walk-cycle frames per direction (the bot-only colours shipped with a single
# static frame each; players need the full cycle to animate).
WALK_DIRS = {
    "left_walk": 17,
    "right_walk": 17,
    "down_walk": 18,
    "up_walk": 17,
}


def red_body_mask(pixel):
    r, g, b, a = pixel
    if a == 0:
        return False
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return (h <= 0.06 or h >= 0.92) and s >= 0.32 and v >= 0.18 and r > g * 1.15 and r > b * 1.15


def recolor_pixel(pixel, target):
    r, g, b, a = pixel
    if not red_body_mask(pixel):
        return pixel
    tr, tg, tb = target
    _, _, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    shade = 0.55 + 0.75 * v
    nr = max(0, min(255, int(tr * shade)))
    ng = max(0, min(255, int(tg * shade)))
    nb = max(0, min(255, int(tb * shade)))
    return nr, ng, nb, a


def recolor_file(src_rel, dst_rel, lower, target):
    src = ROOT / src_rel
    dst = ROOT / dst_rel.format(lower=lower, Title=lower.title())
    dst.parent.mkdir(parents=True, exist_ok=True)
    img = Image.open(src).convert("RGBA")
    out = Image.new("RGBA", img.size)
    out.putdata([recolor_pixel(px, target) for px in img.getdata()])
    out.save(dst)
    print(dst.relative_to(ROOT))


def main():
    for lower, target in TARGETS.items():
        for src_rel, dst_rel in FILES:
            recolor_file(src_rel, dst_rel, lower, target)
        for direction, frames in WALK_DIRS.items():
            for i in range(1, frames + 1):
                recolor_file(
                    f"Assets/Images/Player/Red/red_{direction}/step{i}.png",
                    f"Assets/Images/Player/{{Title}}/{{lower}}_{direction}/step{i}.png",
                    lower, target,
                )


if __name__ == "__main__":
    main()
