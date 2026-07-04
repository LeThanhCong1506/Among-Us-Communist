import socket
import pygame


def get_local_lan_ip():
    """Best-effort detection of this machine's current LAN IP.

    Opens a UDP socket "connected" to a public address without sending
    any packets -- the OS just picks the outbound interface for that
    route, which is normally the LAN adapter. Falls back to localhost
    if the machine has no network route (e.g. no cable/Wi-Fi).
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKYBLUE = (135, 206, 235)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
Orange = (255, 165, 0)
Brown = (106, 55, 5)
Transparent_Black = (0, 0, 0, 1)
MENU_FONT_COLOR = (255, 255, 255)

# game settings
WIDTH = 1280   # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 640  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
MULTIPLAYER_SERVER_IP = get_local_lan_ip()  # auto-detected each run; only correct when client + server run on this same machine
TITLE = "Multi Player Game"
BGCOLOR = Brown
NO_OF_MISSIONS = 8
NO_OF_BOTS = 9
# Quiz stations (Phase 3): how long a station stays unusable after being
# answered, so a player can't stand in one spot and farm the same station.
STATION_COOLDOWN_MS = 20000
# A wrong answer only locks that station for a short retry window instead of
# the full cooldown above, since a wrong answer earns nothing (no tracking
# arrow, no idle-timer reset) and the player should be able to try again soon.
WRONG_ANSWER_RETRY_MS = 5000
# Fund withdrawal (Phase 5): imposter-only, Multiplayer-only channel time in
# Phòng Tài chính, plus a client-side cooldown estimate (the server enforces
# its own copy of this and has final say -- see server.py's WITHDRAW_COOLDOWN_SECONDS).
WITHDRAW_CHANNEL_MS = 8000
WITHDRAW_COOLDOWN_MS = 90000
WITHDRAW_WIN_COUNT = 3  # must match server.py's own copy

# Vent hide/reentry limits: imposter can only stay hidden in a vent for
# VENT_HIDE_DURATION_MS before being auto-ejected, then can't enter any
# vent again for VENT_REENTRY_COOLDOWN_MS. Purely local/client-enforced
# (like the old random-teleport version) since there's no other player to
# cheat against here -- only the imposter's own client cares.
VENT_HIDE_DURATION_MS = 10000
VENT_REENTRY_COOLDOWN_MS = 20000

# Deduction-mode meeting pacing ("Truy Tim Ke Tham Nhung"): a full discussion
# window before voting opens, then a shorter vote window than the classic
# Among Us timing -- Freeplay keeps its original short chat + 30s vote
# pacing untouched (see game.py's meeting state machine).
DISCUSSION_DURATION_MS = 30000
VOTE_DURATION_MS_DEDUCTION = 15000

TILESIZE = 32
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE
FONT = 'Assets/Fonts/Rubik-ExtraBold.TTF'
VN_FONT_NAME = 'segoeui'


def vn_font(size, bold=True):
    return pygame.font.SysFont(VN_FONT_NAME, size, bold=bold)


ROLE_CREW = "Cán bộ liêm chính"
ROLE_IMPOSTER = "Cán bộ tham nhũng"

COLOR_DISPLAY_NAMES = {
    "Red": "Đỏ",
    "Blue": "Xanh dương",
    "Orange": "Cam",
    "Yellow": "Vàng",
    "Green": "Xanh lá",
    "Black": "Đen",
    "Brown": "Nâu",
    "Pink": "Hồng",
    "Purple": "Tím",
    "White": "Trắng",
}

SERVER_COLOURS = ["Red", "Blue", "Orange", "Yellow", "Green", "Black", "Brown", "Pink", "Purple", "White"]

TASK_DIALOGS = {
    "stabilize": (
        "Bắt đầu định hướng quy trình thanh tra: hãy đưa mục tiêu về đúng trọng tâm.",
        "Hoàn thành: quy trình thanh tra đã được định hướng rõ ràng, tránh né không còn chỗ đứng.",
    ),
    "garbage": (
        "Bắt đầu loại bỏ hồ sơ sai lệch: kéo cần để tách bỏ thông tin bị thao túng.",
        "Hoàn thành: hồ sơ sai lệch đã bị loại bỏ khỏi hệ thống.",
    ),
    "wifi": (
        "Bắt đầu khôi phục cổng công khai minh bạch: kết nối lại kênh thông tin cho nhân dân giám sát.",
        "Hoàn thành: cổng công khai minh bạch đã hoạt động trở lại.",
    ),
    "wires": (
        "Bắt đầu kết nối hệ thống giám sát: nối đủ các đường kiểm tra để dữ liệu không bị cắt xén.",
        "Hoàn thành: hệ thống giám sát đã được kết nối đầy đủ.",
    ),
    "power": (
        "Bắt đầu kích hoạt cơ chế kiểm soát quyền lực: đẩy nguồn lực vào đúng kênh giám sát.",
        "Hoàn thành: cơ chế kiểm soát quyền lực đã được kích hoạt.",
    ),
    "engine": (
        "Bắt đầu chuẩn hóa quy trình xử lý tố cáo: căn chỉnh từng bước để tránh oan sai và bỏ lọt sai phạm.",
        "Hoàn thành: quy trình xử lý tố cáo đã được chuẩn hóa.",
    ),
    "fuel": (
        "Bắt đầu bổ sung nguồn lực cho kiểm toán: cần có đủ dữ liệu và phương tiện để kiểm tra đến cùng.",
        "Hoàn thành: nguồn lực kiểm toán đã được bổ sung.",
    ),
    "asteroids": (
        "Bắt đầu ngăn chặn tin giả và lợi ích nhóm: bắn hạ các nguồn gây nhiễu thông tin.",
        "Hoàn thành: tin giả và lợi ích nhóm đã bị đẩy lùi.",
    ),
}

SYSTEM_DIALOGS = {
    "lights_off": "Thông tin minh bạch bị che mờ. Hãy khôi phục hệ thống công khai tại phòng điện.",
    "lights_on": "Thông tin minh bạch đã được khôi phục. Tập thể có thêm căn cứ để giám sát.",
    "reactor_on": "Khủng hoảng niềm tin đang lan rộng. Cần kích hoạt lại cơ chế kiểm soát trước khi quá muộn.",
    "reactor_off": "Khủng hoảng niềm tin đã được kiểm soát. Quyền lực cần tiếp tục được giám sát.",
    "report": "Một đầu mối bất thường đã được báo cáo. Hãy biểu quyết dựa trên bằng chứng.",
    "no_eject": "Không ai bị đình chỉ. Phiếu biểu quyết chưa đủ căn cứ.",
    "quiz_correct": "Chính xác!",
    # Countdown suffix (" Thử lại sau Ns.") is appended live by
    # update_wrong_retry_notice() in game.py -- keep this base text short.
    "quiz_wrong": "Chưa đúng.",
    # Crew-only wrong-answer message (deduction mode) -- only a correct
    # answer grants the tracking arrow, so this clarifies why nothing
    # happened, unlike the imposter's copy of "quiz_wrong" (they still earn
    # a withdraw credit either way, so the generic message stays accurate).
    "quiz_wrong_crew": "Chưa đúng -- không nhận được mũi tên chỉ hướng lần này.",
    # Public/anonymous -- everyone sees this, nobody learns who did it.
    "withdraw_alert": "CẢNH BÁO: Quỹ vừa bị rút!",
    "eject_time_penalty": "Đình chỉ nhầm cán bộ liêm chính: mất 60 giây điều tra.",
    # Personal/local -- only the idle player sees these (see idle_ids in
    # game.py's draw()/check_state_dialogs).
    "idle_dark": "Bạn đã không làm nhiệm vụ quá lâu. Hãy đến trạm gần nhất và trả lời ĐÚNG để mở lại đèn!",
    "idle_bright": "Đèn đã sáng trở lại.",
    # Tracking arrows (replaces the old evidence-board mechanic) -- only the
    # crewmate who just gained one, and only the imposter being warned, see
    # these (see game.py's check_state_dialogs).
    "crew_tracking_gained": "Bạn đã xác định được hướng của kẻ tham nhũng! Hãy đuổi theo mũi tên.",
    "imposter_spotted": "Có cán bộ liêm chính đang lần theo dấu vết của bạn. Hãy tìm chỗ trốn!",
}

CASE_BRIEF = (
    "Vụ việc: Một số cán bộ đang lợi dụng chức vụ để che giấu sai phạm, làm nhiễu thông tin và gây suy giảm niềm tin xã hội.\n"
    "Mục tiêu: Cán bộ liêm chính hoàn thành nhiệm vụ minh bạch hóa hệ thống; cán bộ tham nhũng tìm cách bịt đầu mối và phá hoại giám sát."
)

# Multiplayer ("Truy Tim Ke Tham Nhung" deduction mode) has different rules
# from Freeplay's classic kill/sabotage, so it gets its own brief: quiz
# stations instead of minigames, tracking arrows instead of an evidence
# board, and the imposter's fund-withdrawal win condition instead of kills.
CASE_BRIEF_DEDUCTION = (
    "Vụ việc: 5 cán bộ, 1 người trong số đó tham nhũng. Trả lời câu hỏi tại các trạm (la bàn góc phải chỉ đường).\n"
    "Cán bộ liêm chính: mỗi câu trả lời ĐÚNG sẽ mở lại đèn của bạn và hiện mũi tên chỉ hướng kẻ tham nhũng trong ít giây; trả lời sai thì không được gì và phải chờ 5 giây mới thử lại trạm đó. Bỏ phiếu đình chỉ đúng người để thắng.\n"
    "Cán bộ tham nhũng: cũng phải trả lời câu hỏi để không bị nghi ngờ -- nhưng mỗi lần cán bộ liêm chính có mũi tên, bạn cũng sẽ thấy mũi tên chỉ về phía họ để né tránh. Mỗi câu trả lời xong mở khóa 1 lượt rút quỹ tại Phòng Tài chính; thắng bằng cách rút đủ 3 lần hoặc trụ vững đến hết giờ."
)

# In-game controls/how-to-play reference, toggled with F1 (see
# game.py draw_help_overlay). Two separate lists since Freeplay's classic
# kill/sabotage and deduction mode's quiz/tracking-arrow/withdraw rules
# share almost no controls in common. Each entry is (key_label, description).
HELP_LINES_FREEPLAY = [
    ("WASD / Mũi tên", "Di chuyển"),
    ("Space", "Làm nhiệm vụ tại trạm, hoặc ẩn hình khi đứng trên cống"),
    ("Khi đang ẩn trong cống", "Mũi tên chọn cống tự hiện, bấm 1/2/3 để dịch chuyển"),
    ("Enter", "Giết cán bộ liêm chính gần đó (tham nhũng) / báo cáo xác"),
    ("Ctrl", "Phá hoại đèn (tham nhũng)"),
    ("Shift", "Phá hoại lò phản ứng (tham nhũng)"),
    ("Tab", "Xem minimap"),
    ("P / Esc", "Tạm dừng"),
    ("F1", "Đóng/mở bảng hướng dẫn này"),
]

HELP_LINES_DEDUCTION = [
    ("WASD / Mũi tên", "Di chuyển"),
    ("Space (tại trạm nhiệm vụ)", "Trả lời câu hỏi -- cả cán bộ liêm chính lẫn tham nhũng"),
    ("Space (đứng trên cống)", "Ẩn hình vào cống (chỉ cán bộ tham nhũng)"),
    ("Khi đang ẩn trong cống", "Mũi tên chọn cống tự hiện, bấm 1/2/3 để dịch chuyển"),
    ("Enter (trong Phòng Tài chính)", "Giữ để rút quỹ (chỉ tham nhũng, cần đủ lượt từ nhiệm vụ)"),
    ("Space (nút khẩn cấp) / Click xác", "Gọi họp bỏ phiếu"),
    ("Tab", "Xem minimap -- chấm xanh: trạm sẵn dùng, chấm xám: đang hồi"),
    ("La bàn góc phải trên", "Chỉ hướng trạm nhiệm vụ gần nhất chưa dùng"),
    ("Mũi tên đỏ quanh bạn", "Trả lời ĐÚNG câu hỏi sẽ chỉ hướng kẻ tham nhũng trong ít giây"),
    ("Mũi tên xanh quanh bạn", "Có người đang theo dấu bạn (chỉ cán bộ tham nhũng thấy)"),
    ("P / Esc", "Tạm dừng"),
    ("F1", "Đóng/mở bảng hướng dẫn này"),
]

HELP_WIN_CONDITIONS_DEDUCTION = (
    "Cán bộ liêm chính thắng: bỏ phiếu đình chỉ đúng cán bộ tham nhũng.\n"
    "Cán bộ tham nhũng thắng: rút quỹ thành công 3 lần, hoặc trụ vững đến hết giờ."
)

WIN_TEXTS = {
    "crew_tasks": (
        "Cán bộ liêm chính chiến thắng",
        "Hệ thống minh bạch đã được khôi phục.",
        "Bài học: Minh bạch thông tin, kiểm soát quyền lực và xử lý tố cáo đúng quy trình là nền tảng quan trọng để phòng chống tham nhũng.",
    ),
    "crew_eject": (
        "Cán bộ liêm chính chiến thắng",
        "Cán bộ tham nhũng đã bị phát hiện và đình chỉ.",
        "Bài học: Chống tham nhũng cần bằng chứng, sự quan sát và trách nhiệm của tập thể.",
    ),
    "imposter_kill": (
        "Cán bộ tham nhũng chiến thắng",
        "Sai phạm đã bị che giấu và niềm tin xã hội suy giảm.",
        "Bài học: Khi thông tin bị che mờ, hồ sơ bị thao túng và quyền lực thiếu kiểm soát, tham nhũng có thể tiếp tục tồn tại.",
    ),
    "imposter_crisis": (
        "Cán bộ tham nhũng chiến thắng",
        "Niềm tin xã hội đã sụp đổ. Cán bộ tham nhũng đã che giấu sai phạm thành công.",
        "Bài học: Khi thông tin bị che mờ, hồ sơ bị thao túng và quyền lực thiếu kiểm soát, tham nhũng có thể tiếp tục tồn tại.",
    ),
    # Deduction mode ("Truy Tim Ke Tham Nhung") win conditions -- Phase 2/5.
    "imposter_time": (
        "Cán bộ tham nhũng chiến thắng",
        "Hết thời gian điều tra. Cán bộ tham nhũng đã trụ vững đến phút cuối.",
        "Bài học: Nếu tập thể không kịp thu thập đủ bằng chứng và hành động, sai phạm có thể trôi qua trong im lặng.",
    ),
    "imposter_withdraw": (
        "Cán bộ tham nhũng chiến thắng",
        "Quỹ đã bị rút trót lọt hai lần trước khi bị phát hiện.",
        "Bài học: Thiếu giám sát tài chính chặt chẽ tạo cơ hội cho hành vi tham nhũng lặp lại.",
    ),
    # The imposter's connection dropped mid-match -- crew wins by default
    # since there's no one left to withdraw funds or run out the clock.
    "imposter_left": (
        "Cán bộ liêm chính chiến thắng",
        "Cán bộ tham nhũng đã rời khỏi phiên làm việc.",
        "Bài học: Rời bỏ trách nhiệm giữa chừng cũng là một hình thức trốn tránh giám sát.",
    ),
}

# Neutral (non-victory) end-of-match message when too few players remain to
# continue -- shown via menu.game_left, not the win/lose screens above.
NOT_ENOUGH_PLAYERS_MESSAGE = "Không đủ người chơi để tiếp tục phiên làm việc."


# Menu setting
INTRO_SPRITE_WIDTH = 40
INTRO_SPRITE_HEIGHT = 40
INTRO_SPRITE_POS_X = 0.37
OPTIONS_SPRITE_WIDTH = 45
OPTIONS_SPRITE_HEIGHT = 45
OPTIONS_SPRITE_POS_X = 0.3


# Player settings
PLAYER_SPEED = 400

# Walls setting
WALL_IMG = 'wall.png'

# Sprite Layers
WALL_LAYER = 1
PLAYER_LAYER = 2
BOT_LAYER = 1
EFFECTS_LAYER = 3
ITEM_LAYER = 1

# Sound Effects
#BG_MUSIC1 = 'Background/background.wav'
#BG_MUSIC2 = 'Background/espionage.ogg'
BG_MUSIC3 = 'Ambience/AMB_Main.ogg'

CAFETERIA_AMBIENT_DETECT_RADIUS = 750
MEDBAY_AMBIENT_DETECT_RADIUS = 450
SECURITY_ROOM_AMBIENT_DETECT_RADIUS = 350
REACTOR_ROOM_AMBIENT_DETECT_RADIUS = 450
ENGINE_ROOM_AMBIENT_DETECT_RADIUS = 400
ELECTRICAL_ROOM_AMBIENT_DETECT_RADIUS = 570
STORAGE_ROOM_AMBIENT_DETECT_RADIUS = 580
ADMIN_ROOM_AMBIENT_DETECT_RADIUS = 400
COMMUNICATION_ROOM_AMBIENT_DETECT_RADIUS = 370
OXYGEN_ROOM_AMBIENT_DETECT_RADIUS = 250
COCKPIT_ROOM_AMBIENT_DETECT_RADIUS = 300
WEAPON_ROOM_AMBIENT_DETECT_RADIUS = 400

stepping_rate = 230  # the time interval between each footstep sound played in milisecs
FOOTSTEP_SOUNDS = ['Footsteps/Footstep01.ogg',
                   'Footsteps/Footstep02.ogg',
                   'Footsteps/Footstep03.ogg',
                   'Footsteps/Footstep04.ogg',
                   'Footsteps/Footstep05.ogg',
                   'Footsteps/Footstep06.ogg',
                   'Footsteps/Footstep07.ogg',
                   'Footsteps/Footstep08.ogg'
                   ]

EFFECT_SOUNDS = {'main_menu_music': 'Background/main_menu_music.mp3',
                 'start_game': 'General/roundstart.ogg',
                 'emergency_alarm': 'General/alarm_emergencymeeting.ogg',
                 'dead_body_found': 'General/report_Bodyfound.ogg',
                 'crises_alarm': 'General/crises.ogg',
                 'invisible': 'General/swap.ogg',
                 'vent': 'General/vent.ogg',
                 'victory_crew': 'General/victory_crew.ogg',
                 'victory_imposter': 'General/victory_impostor.ogg',
                 'game_left': 'General/victory_disconnect.ogg',
                 'fill_gas_can': 'General/gas_can_fill.ogg',
                 'pick_gas_can': 'General/pick_up_gas_can.ogg',
                 'menu_sel': 'UI/select.ogg',
                 'go_back': 'UI/back2.ogg',
                 'selected': 'UI/selected2.ogg',
                 'pause': 'UI/pause.ogg',
                 'backspace': 'UI/backspace.ogg',
                 'keypress': 'UI/keypress.ogg',
                 'map_click': 'UI/map_btn_click.ogg',
                 'map_click2': 'UI/pause.ogg',
                 'task_completed': 'General/task_complete.ogg',
                 'imposter_kill_sound': 'Kill/imposter_kill.ogg',
                 'imposter_kill_cooldown_sound': 'Kill/imposter_kill_cooldown.ogg',
                 'imposter_kill_victim_sound': 'Kill/imposter_kill_victim.ogg',
                 'vote_sound': 'UI/votescreen_locking.ogg',
                 'fix_electric_wires_BG': 'Tasks Backgrounds/AMB_Electrical.ogg',
                 'fixed_electric_wires_BG': 'Tasks Backgrounds/AMB_ElectricRoom.ogg',
                 'stabilize_nav_BG': 'Tasks Backgrounds/AMB_Admin.ogg',
                 'emtpy_garbage_BG': 'Tasks Backgrounds/AMB_DecontaminationHall.ogg',
                 'reboot_wifi_BG': 'Tasks Backgrounds/AMB_Laboratory.ogg',
                 'rebooted_wifi_BG': 'Tasks Backgrounds/AMB_comms #16940.ogg',
                 }

ELECTRIC_SHOCK_SOUNDS = ['Electric Shock/AMB_Electricshock1.ogg',
                         'Electric Shock/AMB_Electricshock2.ogg',
                         'Electric Shock/AMB_Electricshock3.ogg',
                         'Electric Shock/AMB_Electricshock4.ogg'
                         ]

COMMS_RADIO_SOUNDS = ['Comms Radio/AMB_comms #16940.ogg',
                      'Comms Radio/AMB_Comms.ogg',
                      'Comms Radio/AMB_CommsRoom.ogg',
                      ]

AMBIENT_SOUNDS = {'admin_room': 'Ambience/AMB_Admin.ogg',
                  'cafeteria': 'Ambience/AMB_Cafeteria.ogg',
                  'cockpit': 'Ambience/AMB_Cockpit.ogg',
                  'comms1': 'Ambience/AMB_comms #16940.ogg',
                  'comms2': 'Ambience/AMB_Comms.ogg',
                  'comms3': 'Ambience/AMB_CommsRoom.ogg',
                  'electrical1': 'Ambience/AMB_Electrical.ogg',
                  'medbay_room': 'Ambience/AMB_MedbayRoom.ogg',
                  'electrical_room': 'Ambience/AMB_ElectricRoom.ogg',
                  'u_engine_room': 'Ambience/AMB_EngineRoom.ogg',
                  'l_engine_room': 'Ambience/AMB_EngineRoom.ogg',
                  'reactor_room': 'Ambience/AMB_ReactorRoom.ogg',
                  'security_room': 'Ambience/AMB_SecurityRoom.ogg',
                  'storage_room': 'Ambience/AMB_Storage.ogg',
                  'oxygen_room': 'Ambience/AMB_Oxygen.ogg',
                  'launchpad': 'Ambience/AMB_Launchpad.ogg',
                  'main': 'Ambience/AMB_Main.ogg',
                  'weapons': 'Ambience/AMB_Weapons.ogg',
                  }

# Visual Effects
LIGHT_MASK = 'light_350_med.png'
LIGHT_MASK_REACTOR = 'light_350_med_reactor.png'
NIGHT_COLOR = (20, 20, 20)
NIGHT_COLOR_REACTOR = (200, 20, 20)
LIGHT_RADIUS = (500, 500)
LIGHT_RADIUS_REACTOR = (500, 500)

# Bots Position
BOT_POS = [(5401, 1530), (3686, 1857), (3733, 2626), (2325, 1814),
           (1718, 1282), (1288, 2418), (1249, 506), (2513, 1286)
           ]


# Mini Map
MAP_BUTTON = "UI/map_button.png"

# ITEMS-------------------

ITEM_IMAGES = {'health': 'health_pack.png',
               'weapon': 'shotgun.png',
               'vent': 'ventilation.png',
               'emerg_btn': 'emergency_icon_inv.png',
               'destroy_asteroids': 'destroy_asteroids.png',
               'nav': 'nav.png',
               'nav_highlight': 'nav_highlight.png'

               }

CLEAR_ASTEROIDS_IMAGES = ['Assets/Images/Tasks/Clear Asteroids/asteroid1.png',
                          'Assets/Images/Tasks/Clear Asteroids/asteroid2.png',
                          'Assets/Images/Tasks/Clear Asteroids/asteroid3.png',
                          'Assets/Images/Tasks/Clear Asteroids/asteroid4.png'

                          ]


# Tasks Setting
DETECT_RADIUS = 250
DETECT_RADIUS_SABOTAGE_FIX = 50
STABILIZE_NAV_RADIUS = 140
EMPTY_GARBAGE_RADIUS = 70
REBOOT_WIFI_RADIUS = 50
FIX_ELECTRICITY_WIRES_RADIUS = 50
VIEW_ADMIN_MAP_CONTROL_RADIUS = 85
VIEW_SECURITY_MONITOR_RADIUS = 170
DIVERT_POWER_TOP_REACTOR_RADIUS = 50
ALIGN_ENGINE_OUTPUT = 50
PICK_STORAGE_GAS_CAN_RADIUS = 50
FUEL_ENGINE = 50

# Pygame Mouse Button Codes
LEFT_MOUSE_BUTTON = 1
MIDDLE_MOUSE_BUTTON = 2
RIGHT_MOUSE_BUTTON = 3


# PLAYER SPRITES MOVEMENTS ----------------------------
# Red Player Movements
# Player left movement
red_player_imgs_left = []
# loops 1 to N-1
for i in range(1, 18):
    red_player_imgs_left.append(pygame.image.load('Assets/Images/Player/Red/red_left_walk/'+'step'+str(i)+'.png'))
# loops 1 to N-1
for i in range(0, 17):
    red_player_imgs_left[i] = pygame.transform.smoothscale(red_player_imgs_left[i], (64, 86))

# Player right movement
red_player_imgs_right = []
# loops 1 to 17
for i in range(1, 18):
    red_player_imgs_right.append(pygame.image.load('Assets/Images/Player/Red/red_right_walk/'+'step'+str(i)+'.png'))
# loops 1 to 16
for i in range(0, 17):
    red_player_imgs_right[i] = pygame.transform.smoothscale(red_player_imgs_right[i], (64, 86))


# Player down movement
red_player_imgs_down = []
for i in range(1, 19):
    red_player_imgs_down.append(pygame.image.load('Assets/Images/Player/Red/red_down_walk/'+'step'+str(i)+'.png'))
# loops 1 to 16
for i in range(0, 18):
    red_player_imgs_down[i] = pygame.transform.smoothscale(red_player_imgs_down[i], (64, 86))

# Player Up movement
red_player_imgs_up = []
# loops 1 to 16
for i in range(1, 18):
    red_player_imgs_up.append(pygame.image.load('Assets/Images/Player/Red/red_up_walk/'+'step'+str(i)+'.png'))
# loops 1 to 16
for i in range(0, 17):
    red_player_imgs_up[i] = pygame.transform.smoothscale(red_player_imgs_up[i], (64, 86))

red_player_imgs_dead = pygame.image.load('Assets/Images/Player/Dead/Deadred.png')

red_player_imgs_ghost_left = pygame.image.load('Assets/Images/Player/Red/red_ghost/step1_left.png')
red_player_imgs_ghost_left = pygame.transform.smoothscale(red_player_imgs_ghost_left, (64, 86))

red_player_imgs_ghost_right = pygame.image.load('Assets/Images/Player/Red/red_ghost/step1_right.png')
red_player_imgs_ghost_right = pygame.transform.smoothscale(red_player_imgs_ghost_right, (64, 86))

red_player_emergency_meeting = pygame.image.load('Assets/Images/Alerts/emergency_meeting_red.png')
red_player_emergency_meeting_report = pygame.image.load('Assets/Images/Alerts/report_dead_body_red.png')

# Blue Player Movements-----------------
# Player left movement
blue_player_imgs_left = []
# loops 1 to N-1
for i in range(1, 18):
    blue_player_imgs_left.append(pygame.image.load('Assets/Images/Player/Blue/blue_left_walk/'+'step'+str(i)+'.png'))
# loops 1 to N-1
for i in range(0, 17):
    blue_player_imgs_left[i] = pygame.transform.smoothscale(blue_player_imgs_left[i], (64, 86))


# Player right movement
blue_player_imgs_right = []
# loops 1 to 17
for i in range(1, 18):
    blue_player_imgs_right.append(pygame.image.load('Assets/Images/Player/Blue/blue_right_walk/'+'step'+str(i)+'.png'))
# loops 1 to 16
for i in range(0, 17):
    blue_player_imgs_right[i] = pygame.transform.smoothscale(blue_player_imgs_right[i], (64, 86))


# Player down movement
blue_player_imgs_down = []
for i in range(1, 19):
    blue_player_imgs_down.append(pygame.image.load('Assets/Images/Player/Blue/blue_down_walk/'+'step'+str(i)+'.png'))
# loops 1 to 16
for i in range(0, 18):
    blue_player_imgs_down[i] = pygame.transform.smoothscale(blue_player_imgs_down[i], (64, 86))

# Player Up movement
blue_player_imgs_up = []
# loops 1 to 16
for i in range(1, 18):
    blue_player_imgs_up.append(pygame.image.load('Assets/Images/Player/Blue/blue_up_walk/'+'step'+str(i)+'.png'))
# loops 1 to 16
for i in range(0, 17):
    blue_player_imgs_up[i] = pygame.transform.smoothscale(blue_player_imgs_up[i], (64, 86))

blue_player_imgs_dead = pygame.image.load('Assets/Images/Player/Dead/Deadblue.png')

blue_player_imgs_ghost_left = pygame.image.load('Assets/Images/Player/Blue/blue_ghost/step1_left.png')
blue_player_imgs_ghost_left = pygame.transform.smoothscale(blue_player_imgs_ghost_left, (64, 86))

blue_player_imgs_ghost_right = pygame.image.load('Assets/Images/Player/Blue/blue_ghost/step1_right.png')
blue_player_imgs_ghost_right = pygame.transform.smoothscale(blue_player_imgs_ghost_right, (64, 86))

blue_player_emergency_meeting = pygame.image.load('Assets/Images/Alerts/emergency_meeting_blue.png')
blue_player_emergency_meeting_report = pygame.image.load('Assets/Images/Alerts/report_dead_body_blue.png')

# Green Player Movements-----------------
# Player left movement
green_player_imgs_left = []
# loops 1 to N-1
for i in range(1, 18):
    green_player_imgs_left.append(pygame.image.load('Assets/Images/Player/Green/green_left_walk/'+'step'+str(i)+'.png'))
# loops 1 to N-1
for i in range(0, 17):
    green_player_imgs_left[i] = pygame.transform.smoothscale(green_player_imgs_left[i], (64, 86))


# Player right movement
green_player_imgs_right = []
# loops 1 to 17
for i in range(1, 18):
    green_player_imgs_right.append(pygame.image.load('Assets/Images/Player/Green/green_right_walk/'+'step'+str(i)+'.png'))
# loops 1 to 16
for i in range(0, 17):
    green_player_imgs_right[i] = pygame.transform.smoothscale(green_player_imgs_right[i], (64, 86))


# Player down movement
green_player_imgs_down = []
for i in range(1, 19):
    green_player_imgs_down.append(pygame.image.load('Assets/Images/Player/Green/green_down_walk/'+'step'+str(i)+'.png'))
# loops 1 to 16
for i in range(0, 18):
    green_player_imgs_down[i] = pygame.transform.smoothscale(green_player_imgs_down[i], (64, 86))

# Player Up movement
green_player_imgs_up = []
# loops 1 to 16
for i in range(1, 18):
    green_player_imgs_up.append(pygame.image.load('Assets/Images/Player/Green/green_up_walk/'+'step'+str(i)+'.png'))
# loops 1 to 16
for i in range(0, 17):
    green_player_imgs_up[i] = pygame.transform.smoothscale(green_player_imgs_up[i], (64, 86))

green_player_imgs_dead = pygame.image.load('Assets/Images/Player/Dead/Deadgreen.png')

green_player_imgs_ghost_left = pygame.image.load('Assets/Images/Player/Green/green_ghost/step1_left.png')
green_player_imgs_ghost_left = pygame.transform.smoothscale(green_player_imgs_ghost_left, (64, 86))

green_player_imgs_ghost_right = pygame.image.load('Assets/Images/Player/Green/green_ghost/step1_right.png')
green_player_imgs_ghost_right = pygame.transform.smoothscale(green_player_imgs_ghost_right, (64, 86))

green_player_emergency_meeting = pygame.image.load('Assets/Images/Alerts/emergency_meeting_green.png')
green_player_emergency_meeting_report = pygame.image.load('Assets/Images/Alerts/report_dead_body_green.png')

# Orange Player Movements-----------------
# Player left movement
orange_player_imgs_left = []
# loops 1 to N-1
for i in range(1, 18):
    orange_player_imgs_left.append(pygame.image.load('Assets/Images/Player/Orange/orange_left_walk/'+'step'+str(i)+'.png'))
# loops 1 to N-1
for i in range(0, 17):
    orange_player_imgs_left[i] = pygame.transform.smoothscale(orange_player_imgs_left[i], (64, 86))


# Player right movement
orange_player_imgs_right = []
# loops 1 to 17
for i in range(1, 18):
    orange_player_imgs_right.append(pygame.image.load('Assets/Images/Player/Orange/orange_right_walk/'+'step'+str(i)+'.png'))
# loops 1 to 16
for i in range(0, 17):
    orange_player_imgs_right[i] = pygame.transform.smoothscale(orange_player_imgs_right[i], (64, 86))


# Player down movement
orange_player_imgs_down = []
for i in range(1, 19):
    orange_player_imgs_down.append(pygame.image.load('Assets/Images/Player/Orange/orange_down_walk/'+'step'+str(i)+'.png'))
# loops 1 to 16
for i in range(0, 18):
    orange_player_imgs_down[i] = pygame.transform.smoothscale(orange_player_imgs_down[i], (64, 86))

# Player Up movement
orange_player_imgs_up = []
# loops 1 to 16
for i in range(1, 18):
    orange_player_imgs_up.append(pygame.image.load('Assets/Images/Player/Orange/orange_up_walk/'+'step'+str(i)+'.png'))
# loops 1 to 16
for i in range(0, 17):
    orange_player_imgs_up[i] = pygame.transform.smoothscale(orange_player_imgs_up[i], (64, 86))

orange_player_imgs_dead = pygame.image.load('Assets/Images/Player/Dead/Deadorange.png')

orange_player_imgs_ghost_left = pygame.image.load('Assets/Images/Player/Orange/orange_ghost/step1_left.png')
orange_player_imgs_ghost_left = pygame.transform.smoothscale(orange_player_imgs_ghost_left, (64, 86))

orange_player_imgs_ghost_right = pygame.image.load('Assets/Images/Player/Orange/orange_ghost/step1_right.png')
orange_player_imgs_ghost_right = pygame.transform.smoothscale(orange_player_imgs_ghost_right, (64, 86))

orange_player_emergency_meeting = pygame.image.load('Assets/Images/Alerts/emergency_meeting_orange.png')
orange_player_emergency_meeting_report = pygame.image.load('Assets/Images/Alerts/report_dead_body_orange.png')

# Yellow Player Movements-----------------
# Player left movement
yellow_player_imgs_left = []
# loops 1 to N-1
for i in range(1, 18):
    yellow_player_imgs_left.append(pygame.image.load('Assets/Images/Player/Yellow/yellow_left_walk/'+'step'+str(i)+'.png'))
# loops 1 to N-1
for i in range(0, 17):
    yellow_player_imgs_left[i] = pygame.transform.smoothscale(yellow_player_imgs_left[i], (64, 86))


# Player right movement
yellow_player_imgs_right = []
# loops 1 to 17
for i in range(1, 18):
    yellow_player_imgs_right.append(pygame.image.load('Assets/Images/Player/Yellow/yellow_right_walk/'+'step'+str(i)+'.png'))
# loops 1 to 16
for i in range(0, 17):
    yellow_player_imgs_right[i] = pygame.transform.smoothscale(yellow_player_imgs_right[i], (64, 86))


# Player down movement
yellow_player_imgs_down = []
for i in range(1, 19):
    yellow_player_imgs_down.append(pygame.image.load('Assets/Images/Player/Yellow/yellow_down_walk/'+'step'+str(i)+'.png'))
# loops 1 to 16
for i in range(0, 18):
    yellow_player_imgs_down[i] = pygame.transform.smoothscale(yellow_player_imgs_down[i], (64, 86))

# Player Up movement
yellow_player_imgs_up = []
# loops 1 to 16
for i in range(1, 18):
    yellow_player_imgs_up.append(pygame.image.load('Assets/Images/Player/Yellow/yellow_up_walk/'+'step'+str(i)+'.png'))
# loops 1 to 16
for i in range(0, 17):
    yellow_player_imgs_up[i] = pygame.transform.smoothscale(yellow_player_imgs_up[i], (64, 86))
    
yellow_player_imgs_dead = pygame.image.load('Assets/Images/Player/Dead/Deadyellow.png')

yellow_player_imgs_ghost_left = pygame.image.load('Assets/Images/Player/Yellow/yellow_ghost/step1_left.png')
yellow_player_imgs_ghost_left = pygame.transform.smoothscale(yellow_player_imgs_ghost_left, (64, 86))

yellow_player_imgs_ghost_right = pygame.image.load('Assets/Images/Player/Yellow/yellow_ghost/step1_right.png')
yellow_player_imgs_ghost_right = pygame.transform.smoothscale(yellow_player_imgs_ghost_right, (64, 86))

yellow_player_emergency_meeting = pygame.image.load('Assets/Images/Alerts/emergency_meeting_yellow.png')
yellow_player_emergency_meeting_report = pygame.image.load('Assets/Images/Alerts/report_dead_body_yellow.png')


def _load_walk(colour_dir, colour_slug, direction, frames):
    imgs = []
    for i in range(1, frames + 1):
        img = pygame.image.load(f'Assets/Images/Player/{colour_dir}/{colour_slug}_{direction}/step{i}.png')
        imgs.append(pygame.transform.smoothscale(img, (64, 86)))
    return imgs


# Black Player Movements-----------------
black_player_imgs_left = _load_walk('Black', 'black', 'left_walk', 17)
black_player_imgs_right = _load_walk('Black', 'black', 'right_walk', 17)
black_player_imgs_down = _load_walk('Black', 'black', 'down_walk', 18)
black_player_imgs_up = _load_walk('Black', 'black', 'up_walk', 17)
black_player_imgs_dead = pygame.image.load('Assets/Images/Player/Dead/Deadblack.png')


# Brown Player Movements-----------------
brown_player_imgs_left = _load_walk('Brown', 'brown', 'left_walk', 17)
brown_player_imgs_right = _load_walk('Brown', 'brown', 'right_walk', 17)
brown_player_imgs_down = _load_walk('Brown', 'brown', 'down_walk', 18)
brown_player_imgs_up = _load_walk('Brown', 'brown', 'up_walk', 17)
brown_player_imgs_dead = pygame.image.load('Assets/Images/Player/Dead/Deadbrown.png')


# Pink Player Movements-----------------
pink_player_imgs_left = _load_walk('Pink', 'pink', 'left_walk', 17)
pink_player_imgs_right = _load_walk('Pink', 'pink', 'right_walk', 17)
pink_player_imgs_down = _load_walk('Pink', 'pink', 'down_walk', 18)
pink_player_imgs_up = _load_walk('Pink', 'pink', 'up_walk', 17)
pink_player_imgs_dead = pygame.image.load('Assets/Images/Player/Dead/Deadpink.png')


# Purple Player Movements-----------------
purple_player_imgs_left = _load_walk('Purple', 'purple', 'left_walk', 17)
purple_player_imgs_right = _load_walk('Purple', 'purple', 'right_walk', 17)
purple_player_imgs_down = _load_walk('Purple', 'purple', 'down_walk', 18)
purple_player_imgs_up = _load_walk('Purple', 'purple', 'up_walk', 17)
purple_player_imgs_dead = pygame.image.load('Assets/Images/Player/Dead/DeadPurple.png')


# White Player Movements-----------------
white_player_imgs_left = _load_walk('White', 'white', 'left_walk', 17)
white_player_imgs_right = _load_walk('White', 'white', 'right_walk', 17)
white_player_imgs_down = _load_walk('White', 'white', 'down_walk', 18)
white_player_imgs_up = _load_walk('White', 'white', 'up_walk', 17)
white_player_imgs_dead = pygame.image.load('Assets/Images/Player/Dead/DeadWhite.png')


def _load_ghost(colour_dir, colour_slug):
    ghost_left = pygame.image.load(f'Assets/Images/Player/{colour_dir}/{colour_slug}_ghost/step1_left.png')
    ghost_right = pygame.image.load(f'Assets/Images/Player/{colour_dir}/{colour_slug}_ghost/step1_right.png')
    return (
        pygame.transform.smoothscale(ghost_left, (64, 86)),
        pygame.transform.smoothscale(ghost_right, (64, 86)),
    )


black_player_imgs_ghost_left, black_player_imgs_ghost_right = _load_ghost('Black', 'black')
brown_player_imgs_ghost_left, brown_player_imgs_ghost_right = _load_ghost('Brown', 'brown')
pink_player_imgs_ghost_left, pink_player_imgs_ghost_right = _load_ghost('Pink', 'pink')
purple_player_imgs_ghost_left, purple_player_imgs_ghost_right = _load_ghost('Purple', 'purple')
white_player_imgs_ghost_left, white_player_imgs_ghost_right = _load_ghost('White', 'white')

black_player_emergency_meeting = pygame.image.load('Assets/Images/Alerts/emergency_meeting_black.png')
black_player_emergency_meeting_report = pygame.image.load('Assets/Images/Alerts/report_dead_body_black.png')
brown_player_emergency_meeting = pygame.image.load('Assets/Images/Alerts/emergency_meeting_brown.png')
brown_player_emergency_meeting_report = pygame.image.load('Assets/Images/Alerts/report_dead_body_brown.png')
pink_player_emergency_meeting = pygame.image.load('Assets/Images/Alerts/emergency_meeting_pink.png')
pink_player_emergency_meeting_report = pygame.image.load('Assets/Images/Alerts/report_dead_body_pink.png')
purple_player_emergency_meeting = pygame.image.load('Assets/Images/Alerts/emergency_meeting_purple.png')
purple_player_emergency_meeting_report = pygame.image.load('Assets/Images/Alerts/report_dead_body_purple.png')
white_player_emergency_meeting = pygame.image.load('Assets/Images/Alerts/emergency_meeting_white.png')
white_player_emergency_meeting_report = pygame.image.load('Assets/Images/Alerts/report_dead_body_white.png')


def _colour_set(left, right, down, up, dead, ghost_left, ghost_right,
                meeting, meeting_report, slug, eject_index):
    return {
        "left": left,
        "right": right,
        "down": down,
        "up": up,
        "dead": dead,
        "ghost_left": ghost_left,
        "ghost_right": ghost_right,
        "meeting": meeting,
        "meeting_report": meeting_report,
        "meeting_ref": f"{slug}_player_emergency_meeting",
        "meeting_report_ref": f"{slug}_player_emergency_meeting_report",
        "eject_ref": f"{slug}_player_imgs_right[{eject_index}]",
    }


COLOUR_SETS = {
    "Red": _colour_set(red_player_imgs_left, red_player_imgs_right, red_player_imgs_down, red_player_imgs_up,
                       red_player_imgs_dead, red_player_imgs_ghost_left, red_player_imgs_ghost_right,
                       red_player_emergency_meeting, red_player_emergency_meeting_report, "red", 9),
    "Blue": _colour_set(blue_player_imgs_left, blue_player_imgs_right, blue_player_imgs_down, blue_player_imgs_up,
                        blue_player_imgs_dead, blue_player_imgs_ghost_left, blue_player_imgs_ghost_right,
                        blue_player_emergency_meeting, blue_player_emergency_meeting_report, "blue", 9),
    "Orange": _colour_set(orange_player_imgs_left, orange_player_imgs_right, orange_player_imgs_down, orange_player_imgs_up,
                          orange_player_imgs_dead, orange_player_imgs_ghost_left, orange_player_imgs_ghost_right,
                          orange_player_emergency_meeting, orange_player_emergency_meeting_report, "orange", 9),
    "Yellow": _colour_set(yellow_player_imgs_left, yellow_player_imgs_right, yellow_player_imgs_down, yellow_player_imgs_up,
                          yellow_player_imgs_dead, yellow_player_imgs_ghost_left, yellow_player_imgs_ghost_right,
                          yellow_player_emergency_meeting, yellow_player_emergency_meeting_report, "yellow", 9),
    "Green": _colour_set(green_player_imgs_left, green_player_imgs_right, green_player_imgs_down, green_player_imgs_up,
                         green_player_imgs_dead, green_player_imgs_ghost_left, green_player_imgs_ghost_right,
                         green_player_emergency_meeting, green_player_emergency_meeting_report, "green", 9),
    "Black": _colour_set(black_player_imgs_left, black_player_imgs_right, black_player_imgs_down, black_player_imgs_up,
                         black_player_imgs_dead, black_player_imgs_ghost_left, black_player_imgs_ghost_right,
                         black_player_emergency_meeting, black_player_emergency_meeting_report, "black", 0),
    "Brown": _colour_set(brown_player_imgs_left, brown_player_imgs_right, brown_player_imgs_down, brown_player_imgs_up,
                         brown_player_imgs_dead, brown_player_imgs_ghost_left, brown_player_imgs_ghost_right,
                         brown_player_emergency_meeting, brown_player_emergency_meeting_report, "brown", 0),
    "Pink": _colour_set(pink_player_imgs_left, pink_player_imgs_right, pink_player_imgs_down, pink_player_imgs_up,
                        pink_player_imgs_dead, pink_player_imgs_ghost_left, pink_player_imgs_ghost_right,
                        pink_player_emergency_meeting, pink_player_emergency_meeting_report, "pink", 0),
    "Purple": _colour_set(purple_player_imgs_left, purple_player_imgs_right, purple_player_imgs_down, purple_player_imgs_up,
                          purple_player_imgs_dead, purple_player_imgs_ghost_left, purple_player_imgs_ghost_right,
                          purple_player_emergency_meeting, purple_player_emergency_meeting_report, "purple", 0),
    "White": _colour_set(white_player_imgs_left, white_player_imgs_right, white_player_imgs_down, white_player_imgs_up,
                         white_player_imgs_dead, white_player_imgs_ghost_left, white_player_imgs_ghost_right,
                         white_player_emergency_meeting, white_player_emergency_meeting_report, "white", 0),
}
