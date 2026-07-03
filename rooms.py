"""Named rooms for the "Truy Tim Ke Tham Nhung" deduction mode.

No pygame import here -- server.py needs this too (to check whether the
imposter is in Phòng Tài chính for the fund-withdrawal mechanic) and it
must not depend on a display.

Anchors reuse the same map coordinates already used for task-station glow
detection in gamefunctions.py, so a room name lines up with the station
players already recognize by walking there. Radii are a first pass; verify
in-game with the K_h debug overlay (game.py) by walking to each station and
checking room_at(player.pos.x, player.pos.y) matches, then adjust here.
"""

ROOMS = {
    # Admin Control buttons (~3815/4070, 1804) -- doubles as the Finance
    # Room where the imposter withdraws funds (Phase 5).
    "Phòng Tài chính": ((3940, 1804), 300),
    "Phòng Điều hành": ((3060, 385), 260),       # Cafeteria / admin computer
    "Phòng Định hướng": ((5610, 1290), 260),     # Navigation / stabilize task
    "Phòng Kiểm soát quyền lực": ((889, 999), 260),   # Reactor
    "Phòng Công khai minh bạch": ((3700, 1554), 220),  # Wifi
    "Phòng Giám sát": ((3166, 1846), 220),       # Electricity wires
    "Phòng Hồ sơ": ((3940, 321), 220),           # Garbage
    "Phòng Kiểm toán": ((1127, 2318), 260),      # Lower engine
    "Phòng Tố cáo": ((1117, 837), 260),          # Upper engine / align output
    "Phòng An ninh": ((1756, 1056), 220),        # Security monitor
}

FALLBACK_ROOM = "Hành lang"

FINANCE_ROOM = "Phòng Tài chính"


def room_at(x, y):
    """Return the name of the nearest room whose radius contains (x, y).

    Falls back to FALLBACK_ROOM ("Hành lang") for corridors between
    stations instead of None -- used to check whether the imposter is
    standing in Phòng Tài chính for the fund-withdrawal mechanic.
    """
    best_name = None
    best_dist = None
    for name, (center, radius) in ROOMS.items():
        dx = x - center[0]
        dy = y - center[1]
        dist = (dx * dx + dy * dy) ** 0.5
        if dist <= radius and (best_dist is None or dist < best_dist):
            best_name = name
            best_dist = dist
    return best_name if best_name is not None else FALLBACK_ROOM
