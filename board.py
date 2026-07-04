import pygame as pg
import pygame.font

from settings import *
from settings import *


# Board surface on screen to draw menus
class Board:

    def __init__(self, width: int, height: int, game):
        self.surface = pg.display.set_mode((width, height), 0, 32)
        pg.display.set_caption('Among Us')
        self.width = width
        self.height = height
        self.game = game
        self.intro_bg = pg.image.load("Assets/Images/Menu/back.png").convert_alpha()
        self.intro_bg2 = pg.image.load("Assets/Images/Menu/back2.png").convert_alpha()
        self.intro_title = pg.image.load("Assets/Images/Menu/title.png").convert_alpha()
        self.intro_menu1 = pg.image.load("Assets/Images/Menu/freeplay.png").convert_alpha()
        self.intro_menu2 = pg.image.load("Assets/Images/Menu/online.png").convert_alpha()
        self.intro_menu3 = pg.image.load("Assets/Images/Menu/help.png").convert_alpha()
        self.intro_menu4 = pg.image.load("Assets/Images/Menu/credits.png").convert_alpha()
        self.intro_menu5 = pg.image.load("Assets/Images/Menu/quit.png").convert_alpha()
        self.intro_color1 = pg.image.load("Assets/Images/Menu/blue.png").convert_alpha()
        self.intro_color2 = pg.image.load("Assets/Images/Menu/green.png").convert_alpha()
        self.intro_color3 = pg.image.load("Assets/Images/Menu/yellow.png").convert_alpha()
        self.intro_color4 = pg.image.load("Assets/Images/Menu/red.png").convert_alpha()
        self.intro_color5 = pg.image.load("Assets/Images/Menu/orange.png").convert_alpha()
        self.intro_choosecolour = pg.image.load("Assets/Images/Menu/choosecolour.png").convert_alpha()
        self.intro_return = pg.image.load("Assets/Images/Menu/return.png").convert_alpha()
        self.intro_entername = pg.image.load("Assets/Images/Menu/entername.png").convert_alpha()
        self.intro_enteraddress = pg.image.load("Assets/Images/Menu/enteraddress.png").convert_alpha()
        self.intro_input = pg.image.load("Assets/Images/Menu/input.png").convert_alpha()
        self.intro_help = []
        for i in range(0, 9):
            self.intro_help.append(pygame.image.load('Assets/Images/help/'+'help'+str(i+1)+'.png'))
        self.intro_credits = pg.image.load("Assets/Images/credits/credits.png")
        self.lobby_ship_img = pg.image.load("Assets/Maps/lobby_ship.png").convert_alpha()
        self.lobby_flame_imgs = [pg.image.load(f"Assets/Maps/engine_flame_{i}.png").convert_alpha() for i in range(1, 7)]
        # Left engine uses its own "- Copy" frames (only 1/2/4/5/6 exist -- no frame 3)
        self.lobby_flame_imgs_left = [
            pg.image.load(f"Assets/Maps/engine_flame_{i} - Copy.png").convert_alpha()
            for i in (1, 2, 4, 5, 6)
        ]
        # anchor points for the engine exhaust, in lobby_ship.png's own pixel
        # space -- placed to overlap into the turbine housing so the flame
        # reads as coming out of it rather than floating below with a gap
        self.lobby_left_engine_anchor = (130, 730)
        self.lobby_right_engine_anchor = (1100, 730)

        self.menu_font = vn_font(35)
        self.bonus_font = vn_font(28)
        self.title_font = vn_font(72)
        self.game_over_font = vn_font(52)
        self.game_left_font = vn_font(60)

    # Draw Main Menu - Intro Menu
    def draw_menu(self, *args):
        self.intro_bg = pg.transform.smoothscale(self.intro_bg, (self.width, self.height))
        self.surface.blit(self.intro_bg, (0, 0), (0, 0, self.width, self.height))
        self.intro_title = pg.transform.smoothscale(self.intro_title, (int(self.width / 2), int(self.height * 0.2)))
        self.surface.blit(self.intro_title, (self.width / 4, self.height * 0.1), (0, 0, self.width, self.height))
        self.intro_menu1 = pg.transform.smoothscale(self.intro_menu1, (int(self.width / 5), int(self.height * 0.1)))
        self.surface.blit(self.intro_menu1, (self.width / 2.5, self.height * 0.39), (0, 0, self.width, self.height))
        self.intro_menu2 = pg.transform.smoothscale(self.intro_menu2, (int(self.width / 5), int(self.height * 0.1)))
        self.surface.blit(self.intro_menu2, (self.width / 2.5, self.height * 0.51), (0, 0, self.width, self.height))
        self.intro_menu3 = pg.transform.smoothscale(self.intro_menu3, (int(self.width / 5), int(self.height * 0.1)))
        self.surface.blit(self.intro_menu3, (self.width / 2.5, self.height * 0.63), (0, 0, self.width, self.height))
        self.intro_menu4 = pg.transform.smoothscale(self.intro_menu4, (int(self.width / 5), int(self.height * 0.1)))
        self.surface.blit(self.intro_menu4, (self.width / 2.5, self.height * 0.75), (0, 0, self.width, self.height))
        self.intro_menu5 = pg.transform.smoothscale(self.intro_menu5, (int(self.width / 5), int(self.height * 0.1)))
        self.surface.blit(self.intro_menu5, (self.width / 2.5, self.height * 0.87), (0, 0, self.width, self.height))

        for drawable in args:
            drawable.draw_on(self.surface)
        pg.display.update()

    # Draw Choose Color/Character Menu
    def draw_choose_character(self, *args):
        self.intro_bg2 = pg.transform.smoothscale(self.intro_bg2, (self.width, self.height))
        self.surface.blit(self.intro_bg2, (0, 0), (0, 0, self.width, self.height))
        self.intro_choosecolour = pg.transform.smoothscale(self.intro_choosecolour, (int(self.width / 2), int(self.height * 0.1)))
        self.surface.blit(self.intro_choosecolour, (self.width / 3.9, self.height * 0.05), (0, 0, self.width, self.height))
        self.intro_color1 = pg.transform.smoothscale(self.intro_color1, (int(self.width / 4), int(self.height * 0.1)))
        self.surface.blit(self.intro_color4, (self.width / 2.6, self.height * 0.2), (0, 0, self.width, self.height))
        self.intro_color2 = pg.transform.smoothscale(self.intro_color2, (int(self.width / 4), int(self.height * 0.1)))
        self.surface.blit(self.intro_color1, (self.width / 2.6, self.height * 0.33), (0, 0, self.width, self.height))
        self.intro_color3 = pg.transform.smoothscale(self.intro_color3, (int(self.width / 4), int(self.height * 0.1)))
        self.surface.blit(self.intro_color5, (self.width / 2.6, self.height * 0.46), (0, 0, self.width, self.height))
        self.intro_color4 = pg.transform.smoothscale(self.intro_color4, (int(self.width / 4), int(self.height * 0.1)))
        self.surface.blit(self.intro_color3, (self.width / 2.6, self.height * 0.59), (0, 0, self.width, self.height))
        self.intro_color5 = pg.transform.smoothscale(self.intro_color5, (int(self.width / 4), int(self.height * 0.1)))
        self.surface.blit(self.intro_color2, (self.width / 2.6, self.height * 0.72), (0, 0, self.width, self.height))
        self.intro_return = pg.transform.smoothscale(self.intro_return, (int(self.width / 4), int(self.height * 0.1)))
        self.surface.blit(self.intro_return, (self.width / 2.6, self.height * 0.85), (0, 0, self.width, self.height))

        for drawable in args:
            drawable.draw_on(self.surface)
        pg.display.update()

    # Dim band behind the title/subtitle so the Vietnamese overlay stays
    # readable on top of the text baked into the victory/defeat art.
    def _draw_game_over_backdrop(self):
        band = pg.Surface((self.width, int(self.height * 0.24)), pg.SRCALPHA)
        band.fill((0, 0, 0, 170))
        self.surface.blit(band, (0, int(self.height * 0.09)))

    # Draw Gameover Menu
    def draw_game_over(self, scoreboard: list, message: str, subtitle='', lesson='', *args):
        background = pg.image.load("Assets/Images/Alerts/victory.PNG")
        #self.surface.fill(background)
        self.surface.blit(background,(0,0))
        self._draw_game_over_backdrop()
        self.draw_text(self.surface, message, self.width / 2, self.height * 0.16, self.game_over_font)
        if subtitle:
            self.draw_wrapped_text(self.surface, subtitle, vn_font(28), MENU_FONT_COLOR,
                                   pg.Rect(90, self.height * 0.23, self.width - 180, 90))
        pos = 0.42
        for player in scoreboard:
            self.draw_text(self.surface, player[0], self.width / 3, self.height * pos, self.bonus_font)
            self.draw_text(self.surface, player[1], self.width * 2 / 3, self.height * pos, self.bonus_font)
            pos += 0.08
        if lesson:
            self.draw_wrapped_text(self.surface, lesson, vn_font(22), MENU_FONT_COLOR,
                                   pg.Rect(110, self.height * 0.8, self.width - 220, 120), line_spacing=8)
        for drawable in args:
            drawable.draw_on(self.surface)
        pg.display.update()

    def draw_game_over_imposter(self, scoreboard: list, message: str, subtitle='', lesson='', *args):
        background = pg.image.load("Assets/Images/Alerts/defeat.PNG")
        #self.surface.fill(background)
        self.surface.blit(background,(0,0))
        self._draw_game_over_backdrop()
        self.draw_text(self.surface, message, self.width / 2, self.height * 0.16, self.game_over_font)
        if subtitle:
            self.draw_wrapped_text(self.surface, subtitle, vn_font(28), MENU_FONT_COLOR,
                                   pg.Rect(90, self.height * 0.23, self.width - 180, 90))
        pos = 0.42
        for player in scoreboard:
            self.draw_text(self.surface, player[0], self.width / 3, self.height * pos, self.bonus_font)
            self.draw_text(self.surface, player[1], self.width * 2 / 3, self.height * pos, self.bonus_font)
            pos += 0.08
        if lesson:
            self.draw_wrapped_text(self.surface, lesson, vn_font(22), MENU_FONT_COLOR,
                                   pg.Rect(110, self.height * 0.8, self.width - 220, 120), line_spacing=8)
        for drawable in args:
            drawable.draw_on(self.surface)
        pg.display.update()

    def draw_game_left(self, scoreboard: list, message: str, *args):
        background = (0, 0, 0)
        self.surface.fill(background)
        self.draw_text(self.surface, message, self.width / 2, self.height * 0.2, self.game_left_font)
        pos = 0.5
        for player in scoreboard:
            self.draw_text(self.surface, player[0], self.width / 3, self.height * pos, self.bonus_font)
            self.draw_text(self.surface, player[1], self.width * 2 / 3, self.height * pos, self.bonus_font)
            pos += 0.08
        for drawable in args:
            drawable.draw_on(self.surface)
        pg.display.update()

    #Draw Input Name field Menu
    def draw_input(self, word: str, x: int, y: int):
        self.intro_bg2 = pg.transform.scale(self.intro_bg2, (self.width, self.height))
        self.surface.blit(self.intro_bg2, (0, 0), (0, 0, self.width, self.height))
        self.intro_entername = pg.transform.smoothscale(self.intro_entername, (int(self.width / 2), int(self.height * 0.1)))
        self.surface.blit(self.intro_entername, (self.width / 3.9, self.height * 0.05), (0, 0, self.width, self.height))
        self.intro_input = pg.transform.smoothscale(self.intro_input, (int(self.width / 3), int(self.height * 0.2)))
        self.surface.blit(self.intro_input, (self.width / 3.0, self.height * 0.4), (0, 0, self.width, self.height))
        text = self.menu_font.render("{}".format(word), True, MENU_FONT_COLOR)
        rect = text.get_rect()
        rect.center = x, y
        result = self.surface.blit(text, rect)
        pg.display.update()
        return result

    def draw_input_address(self, word: str, x: int, y: int, suggested_ip: str = None):
        self.intro_bg2 = pg.transform.smoothscale(self.intro_bg2, (self.width, self.height))
        self.surface.blit(self.intro_bg2, (0, 0), (0, 0, self.width, self.height))
        self.intro_enteraddress = pg.transform.smoothscale(self.intro_enteraddress, (int(self.width / 2), int(self.height * 0.1)))
        self.surface.blit(self.intro_enteraddress, (self.width / 3.9, self.height * 0.05), (0, 0, self.width, self.height))
        self.intro_input = pg.transform.smoothscale(self.intro_input, (int(self.width / 3), int(self.height * 0.2)))
        self.surface.blit(self.intro_input, (self.width / 3.0, self.height * 0.4), (0, 0, self.width, self.height))
        text = self.menu_font.render("{}".format(word), True, MENU_FONT_COLOR)
        rect = text.get_rect()
        rect.center = x, y
        result = self.surface.blit(text, rect)
        if suggested_ip:
            hint = f"Để trống rồi nhấn Enter để dùng IP máy này: {suggested_ip}"
            self.draw_text(self.surface, hint, self.width / 2, self.height * 0.68, vn_font(18))
        pg.display.update()
        return result

    # Layout for the lobby ship image: where it's placed/scaled on screen, and
    # the walkable interior room, in lobby_ship.png's own 1222x1008 pixel space.
    LOBBY_SHIP_HEIGHT_FRAC = 0.88
    LOBBY_SHIP_TOP_FRAC = 0.10
    LOBBY_INTERIOR_BOX = (345, 300, 875, 955)  # x0, y0, x1, y1

    def get_lobby_ship_layout(self):
        ship_h = int(self.height * self.LOBBY_SHIP_HEIGHT_FRAC)
        scale = ship_h / self.lobby_ship_img.get_height()
        ship_w = int(self.lobby_ship_img.get_width() * scale)
        ship_x = self.width / 2 - ship_w / 2
        ship_y = self.height * self.LOBBY_SHIP_TOP_FRAC
        return ship_x, ship_y, scale, ship_w, ship_h

    # Screen-space (xmin, xmax, ymin, ymax) the player can walk around in,
    # matching the ship's interior room so they can't wander out past the hull.
    def get_lobby_interior_bounds(self):
        ship_x, ship_y, scale, _, _ = self.get_lobby_ship_layout()
        x0, y0, x1, y1 = self.LOBBY_INTERIOR_BOX
        return (ship_x + x0 * scale, ship_x + x1 * scale,
                ship_y + y0 * scale, ship_y + y1 * scale)

    # Draw Multiplayer Lobby - waiting for enough players before the match starts.
    # target_players is the room's confirmed player-count target (the same
    # number the countdown waits for), separate from room_max_players below
    # which is what the settings panel shows the host editing.
    def draw_lobby(self, player_count, target_players, seconds_left, player_image, player_pos, flame_frame,
                    other_players=(), is_host=False, room_max_players=9, room_imposter_count=1, settings_dirty=False):
        self.surface.fill((10, 12, 20))

        if seconds_left is not None:
            status_text = f"BẮT ĐẦU SAU {seconds_left} GIÂY"
        else:
            status_text = f"ĐANG CHỜ CÁN BỘ... {player_count}/{target_players}"
        self.draw_text(self.surface, status_text, self.width / 2, self.height * 0.06, self.menu_font)

        ship_x, ship_y, scale, ship_w, ship_h = self.get_lobby_ship_layout()
        ship = pg.transform.smoothscale(self.lobby_ship_img, (ship_w, ship_h))
        self.surface.blit(ship, (ship_x, ship_y))

        # Animated engine flames, anchored so they overlap into the turbine
        # housing rather than floating below it with a visible gap. Left and
        # right use separate image lists so they can be tuned independently.
        flame_sets = (
            (self.lobby_flame_imgs_left, self.lobby_left_engine_anchor),
            (self.lobby_flame_imgs, self.lobby_right_engine_anchor),
        )
        for flame_imgs, (anchor_x, anchor_y) in flame_sets:
            flame_img = flame_imgs[flame_frame % len(flame_imgs)]
            flame_w = max(1, int(flame_img.get_width() * scale))
            flame_h = max(1, int(flame_img.get_height() * scale))
            flame_scaled = pg.transform.smoothscale(flame_img, (flame_w, flame_h))
            rect = flame_scaled.get_rect()
            rect.midtop = (ship_x + anchor_x * scale, ship_y + anchor_y * scale)
            self.surface.blit(flame_scaled, rect)

        # Everyone else waiting in the lobby, at the position they reported
        for other_x, other_y, other_image in other_players:
            other_scaled = pg.transform.smoothscale(other_image, (32, 32))
            other_rect = other_scaled.get_rect(center=(other_x, other_y))
            self.surface.blit(other_scaled, other_rect)

        # Local player, walking around the lobby interior while waiting
        player_scaled = pg.transform.smoothscale(player_image, (32, 32))
        player_rect = player_scaled.get_rect(center=(player_pos.x, player_pos.y))
        self.surface.blit(player_scaled, player_rect)

        self.draw_lobby_room_settings(is_host, room_max_players, room_imposter_count, settings_dirty)

        pg.display.update()

    # Clickable +/- rects for the host-only room setup panel. Sits in the
    # left margin beside the ship art, which is empty at every screen size
    # since the ship is centered and only ~half the screen wide.
    def get_lobby_room_setting_rects(self):
        bx = 34
        bw = 28
        return {
            'max_minus': pg.Rect(bx, 134, bw, bw),
            'max_plus': pg.Rect(bx + 156, 134, bw, bw),
            'apply': pg.Rect(bx, 192, 190, 36),
        }

    def draw_lobby_room_settings(self, is_host, room_max_players, room_imposter_count, settings_dirty=False):
        # room_imposter_count is always 1 -- "Truy Tim Ke Tham Nhung" is a
        # fixed 5-crew/1-imposter deduction game, so only room size (which
        # controls when the countdown fires) is still host-configurable.
        panel_h = 250 if is_host else 150
        panel = pg.Surface((240, panel_h), pg.SRCALPHA)
        panel.fill((0, 0, 0, 140))
        self.surface.blit(panel, (20, 76))

        title = "Thiết lập phòng (Chủ phòng)" if is_host else "Thiết lập phòng"
        self.draw_text(self.surface, title, 140, 92, vn_font(16))

        rects = self.get_lobby_room_setting_rects()
        label_font = vn_font(15)
        value_font = vn_font(18)
        minus_rect, plus_rect = rects['max_minus'], rects['max_plus']
        label = label_font.render("Số người tối đa", True, MENU_FONT_COLOR)
        self.surface.blit(label, (minus_rect.x, minus_rect.y - 20))
        value_surf = value_font.render(str(room_max_players), True, MENU_FONT_COLOR)
        value_centre = ((minus_rect.right + plus_rect.left) // 2, minus_rect.centery)
        self.surface.blit(value_surf, value_surf.get_rect(center=value_centre))
        if is_host:
            for rect, sign in ((minus_rect, "-"), (plus_rect, "+")):
                pg.draw.rect(self.surface, (60, 60, 70), rect, border_radius=6)
                pg.draw.rect(self.surface, MENU_FONT_COLOR, rect, width=2, border_radius=6)
                sign_surf = value_font.render(sign, True, MENU_FONT_COLOR)
                self.surface.blit(sign_surf, sign_surf.get_rect(center=rect.center))

        role_hint = vn_font(13).render("5 cán bộ liêm chính, 1 cán bộ tham nhũng", True, (200, 200, 140))
        self.surface.blit(role_hint, (minus_rect.x, plus_rect.bottom + 8))

        if is_host:
            apply_rect = rects['apply']
            fill_colour = (200, 130, 20) if settings_dirty else (60, 60, 70)
            pg.draw.rect(self.surface, fill_colour, apply_rect, border_radius=8)
            pg.draw.rect(self.surface, MENU_FONT_COLOR, apply_rect, width=2, border_radius=8)
            apply_label = "Cập nhật *" if settings_dirty else "Cập nhật"
            apply_surf = value_font.render(apply_label, True, MENU_FONT_COLOR)
            self.surface.blit(apply_surf, apply_surf.get_rect(center=apply_rect.center))

    # Rect of the clickable "RETURN" button shown on Help/Credits screens.
    # compact=True gives a small bottom-left button for the Help screen,
    # whose baked-in illustrations use nearly the whole frame -- the larger
    # bottom-center spot (used on Credits, matching the choose-character
    # screen's own return button) would overlap that artwork/captions.
    def get_return_button_rect(self, compact=False):
        if compact:
            w, h = 150, 46
            x, y = 24, self.height - h - 20
        else:
            w = int(self.width / 4)
            h = int(self.height * 0.1)
            x = self.width / 2.6
            y = self.height * 0.85
        return pg.Rect(x, y, w, h)

    def draw_return_button(self, compact=False):
        rect = self.get_return_button_rect(compact)
        btn = pg.transform.smoothscale(self.intro_return, (rect.width, rect.height))
        self.surface.blit(btn, rect)

    def draw_help(self, i):
        #self.intro_help[i] = pg.transform.smoothscale(self.intro_help[i], (self.width, self.height))
        self.intro_help[i] = pg.transform.scale(self.intro_help[i], (self.width, self.height))
        self.surface.blit(self.intro_help[i], (0, 0), (0, 0, self.width, self.height))
        self.draw_return_button(compact=True)
        pg.display.update()

    CREDIT_NAMES = [
        "Lê Thành Công - SE183504",
        "Lê Quốc Khánh - SE171151",
        "Dương Thành Phát - SE183374",
    ]

    def draw_credits(self):
        #self.intro_credits = pg.transform.smoothscale(self.intro_credits, (self.width, self.height))
        self.intro_credits = pg.transform.scale(self.intro_credits, (self.width, self.height))
        self.surface.blit(self.intro_credits, (0, 0), (0, 0, self.width, self.height))
        pos_y = self.height * 0.45
        for name in self.CREDIT_NAMES:
            text = self.bonus_font.render(name, True, BLACK)
            self.surface.blit(text, text.get_rect(center=(self.width / 2, pos_y)))
            pos_y += self.height * 0.1
        self.draw_return_button()
        pg.display.update()

    def draw_pause(self):
        self.draw_text(self.surface, "Tạm dừng", self.width / 2, self.height / 2, self.title_font)

    def draw_bots_left(self, left: int, text_size):
        self.bots_left_font = vn_font(text_size)
        self.draw_text(self.surface, "Đầu mối còn lại: {}".format(left), 135, 25, self.bots_left_font)

    def draw_player_name(self, player_name, text_color, text_size):
        self.player_name_font = vn_font(text_size)
        text_surface = self.player_name_font.render(player_name + " - " + ROLE_IMPOSTER, True, text_color)
        text_surface2 = self.player_name_font.render(player_name + " - " + ROLE_CREW, True, text_color)
        if self.game.player.imposter:
            return text_surface
        else:
            return text_surface2

    def draw_ejected_text(self, colour, role_text=None):
        display_colour = COLOR_DISPLAY_NAMES.get(colour, colour)
        headline = f"{display_colour} đã bị đình chỉ công tác sau phiên biểu quyết."
        self.draw_wrapped_text(self.surface, headline, vn_font(30), MENU_FONT_COLOR,
                               pg.Rect(180, self.height / 2 - 72, self.width - 360, 80))
        if role_text:
            self.draw_wrapped_text(self.surface, role_text, vn_font(23), MENU_FONT_COLOR,
                                   pg.Rect(200, self.height / 2 + 5, self.width - 400, 105), line_spacing=6)

    def draw_light_timer_text(self, left: int, text_color, text_size):
        timer_font = vn_font(text_size)
        text_surface = timer_font.render("{} ".format(left), True, text_color)
        return text_surface

    def draw_kill_timer_text(self, left: int, text_color, text_size):
        timer_font = vn_font(text_size)
        text_surface = timer_font.render("{} ".format(left), True, text_color)
        return text_surface

    def draw_reactor_timer_imposter_text(self, left: int, text_color, text_size):
        timer_font = vn_font(text_size)
        text_surface = timer_font.render("{} ".format(left), True, text_color)
        return text_surface

    def draw_reactor_timer_text(self, left: int, text_color, text_size):
        timer_font = vn_font(text_size)
        text_surface = timer_font.render("Khủng hoảng niềm tin sau: {} giây".format(left), True, text_color)
        return text_surface

    def draw_meeting_timer_text(self, left: int, text_color, text_size):
        timer_font = vn_font(text_size)
        text_surface = timer_font.render("Biểu quyết kết thúc sau: {} ".format(left), True, text_color)
        return text_surface

    @staticmethod
    def wrap_text_lines(text, font, max_width):
        lines = []
        for raw_line in str(text).splitlines():
            words = raw_line.split()
            if not words:
                lines.append("")
                continue
            current = words[0]
            for word in words[1:]:
                trial = current + " " + word
                if font.size(trial)[0] <= max_width:
                    current = trial
                else:
                    lines.append(current)
                    current = word
            lines.append(current)
        return lines

    def draw_wrapped_text(self, surface, text, font, color, rect, line_spacing=6, center=True):
        rect = pg.Rect(rect)
        y = rect.top
        for line in self.wrap_text_lines(text, font, rect.width):
            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect()
            if center:
                text_rect.centerx = rect.centerx
            else:
                text_rect.x = rect.x
            text_rect.y = y
            surface.blit(text_surface, text_rect)
            y += text_surface.get_height() + line_spacing
            if y > rect.bottom:
                break

    @staticmethod
    def draw_adds(surface, x, y, image, amount=1):
        for i in range(amount):
            img_rect = image.get_rect()
            img_rect.x = x + 30 * i
            img_rect.y = y
            surface.blit(image, img_rect)

    @staticmethod

    def draw_text(surface, text, x, y, font):
        if text is not None:
            text = font.render(text, True, MENU_FONT_COLOR)
            rect = text.get_rect()
            rect.center = x, y
            surface.blit(text, rect)
