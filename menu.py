from os import path
from drawable import Drawable
import pygame as pg
import sys
from settings import *
from pygame import mixer

#player_colour = None


pg.mixer.init()
class MenuCursor(Drawable, pg.sprite.Sprite):

    def __init__(self, game, x, y, width=20, height=20):
        # Init the Sprite base first: in pygame-ce 2.5+ Sprite.__init__ resets
        # self.rect/self.image to None, which would otherwise wipe the rect that
        # Drawable.__init__ builds. Running Drawable second keeps a valid rect.
        pg.sprite.Sprite.__init__(self)
        super(MenuCursor, self).__init__(width, height, x, y)
        self.image = self.surface
        self.game = game
        self.width = width
        self.height = height
        self.pic = None


    def animate(self, destination, area):
        self.pic = pg.image.load(path.join(self.game.Menu_folder, "sel.png"))
        self.pic = pg.transform.smoothscale(self.pic, (self.width, self.height))
        self.surface.blit(self.pic, destination, area)

def quit_game():
    pg.quit()
    sys.exit()


class Menu:

    def __init__(self, game):
        self.game = game
        self.pos_x = 0
        self.pos_y = 0
        self.i = 0
        self.word_count_ip = 17
        self.word_count_name = 11
        self.music_playing = False

    # Menu select cursor position
    def game_intro(self):
        # If music is already not playing then Play main_menu_music in Main Menu
        if not self.music_playing:
            self.game.effect_sounds['main_menu_music'].play(-1)
            self.music_playing = not self.music_playing
        else:
            pass
        self.i = 0.41
        # min_click_y=225 keeps stray clicks above the Freeplay item (e.g. on
        # the logo) from falling through to the "else: quit_game()" branch.
        self.set_menu_cursor_limit(0.12, 300, 500, INTRO_SPRITE_POS_X, self.game.board.draw_menu, self.game_help, 40, min_click_y=225)
        if 225 < self.pos_y < 300:
            self.game.gamemode = "Freeplay"
            self.game_choose_character()
            self.game.effect_sounds['main_menu_music'].stop()
            self.music_playing = False
            return
        elif 300 < self.pos_y < 385:
            self.game.gamemode = "Multiplayer"
            self.game_choose_character()
            self.game.effect_sounds['main_menu_music'].stop()
            self.music_playing = False
            return
        elif 385 < self.pos_y < 457:
            print(self.pos_y)
            self.game_help()
        elif 457 < self.pos_y < 520:
            print(self.pos_y)
            self.game_credits()
        else:
            quit_game()


    # menu option position
    #def game_options(self):
    #    self.i = 0.31
    #    self.set_menu_cursor_limit(0.15, 196, 366, OPTIONS_SPRITE_POS_X, self.game.board.draw_options, self.game_intro)
    #    if 185 < self.pos_y < 187:
    #        # controls
    #        pass
    #    elif 275 < self.pos_y < 277:
    #        pass
    #        # audio
    #    else:
    #        self.game_intro()
    
    def game_help(self):
        i = 0
        while True:
            pg.display.flip()
            return_rect = self.game.board.get_return_button_rect(compact=True)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quit_game()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.game.effect_sounds['go_back'].play()
                        self.game_intro()
                    elif event.key == pg.K_RIGHT or event.key == pg.K_d or event.key == pg.K_DOWN or event.key == pg.K_s or event.key == pg.K_RETURN:
                        if i < 8:
                            i += 1
                    elif event.key == pg.K_LEFT or event.key == pg.K_a or event.key == pg.K_UP or event.key == pg.K_w:
                        if i > 0:
                            i -= 1
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if return_rect.collidepoint(event.pos):
                        self.game.effect_sounds['go_back'].play()
                        self.game_intro()
            self.game.board.draw_help(i)

    def game_credits(self):
        while True:
            pg.display.flip()
            return_rect = self.game.board.get_return_button_rect()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quit_game()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE or event.key == pg.K_RETURN:
                        self.game.effect_sounds['go_back'].play()
                        self.game_intro()
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if return_rect.collidepoint(event.pos):
                        self.game.effect_sounds['go_back'].play()
                        self.game_intro()
            self.game.board.draw_credits()


    def game_choose_character(self):

        self.i = 0.21
        self.set_menu_cursor_limit(0.13, 200, 500, OPTIONS_SPRITE_POS_X, self.game.board.draw_choose_character, self.game_intro)

        if 100 < self.pos_y < 200:  # when option is Red
             self.game.player_colour = "Red"
             self.game_input()
             return
        elif 200 < self.pos_y < 300:  # when option is Blue
             self.game.player_colour = "Blue"
             self.game_input()
             return
        elif 300 < self.pos_y < 350:  # when option is Orange
            self.game.player_colour = "Orange"
            self.game_input()
            return
        elif 350 < self.pos_y < 400:  # when option is Yellow
            self.game.player_colour = "Yellow"
            self.game_input()
            return
        elif 400 < self.pos_y < 500:  # when option is Green
            self.game.player_colour = "Green"
            self.game_input()
            return
        else:   # when return option move step back
            self.game_intro()

    # To input player name
    def game_input(self):
        self.word = ""
        while True:
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quit_game()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.game.effect_sounds['go_back'].play()
                        self.game_intro()
                    elif event.key == pg.K_BACKSPACE:
                        self.game.effect_sounds['backspace'].play()
                        self.word = self.word[:-1]
                    elif event.key == pg.K_RETURN:
                        if len(self.word) > 0:   # if name is not nulls
                            #self.game.missions_done = 1   # Reset mission count on game completion
                            #self.game.invisible_play_count = 0
                            if self.game.gamemode == "Freeplay":
                                # stop main menu music before entering game
                                self.game.effect_sounds['main_menu_music'].stop()
                                self.game.new()
                                self.game.runfreeplay()
                                return
                            elif self.game.gamemode == "Multiplayer":
                                # Ask for the server's address -- this machine's own
                                # auto-detected IP is only correct when client and
                                # server run on the SAME machine, so it can't be
                                # used blindly for a real cross-machine connection.
                                self.game.effect_sounds['main_menu_music'].stop()
                                self.game_input_address()
                                return
                    elif len(self.word) < self.word_count_name:
                        self.word += event.unicode
                        self.game.effect_sounds['keypress'].play()
                self.game.board.draw_input(self.word, WIDTH / 2, HEIGHT / 2)
 
    def game_input_address(self):
        word_ip = ""
        # If left blank, Enter connects to this machine's own LAN IP -- correct
        # only when the server also runs on this machine (same-PC testing).
        # For a real cross-machine connection, type the host's actual address.
        suggested_ip = MULTIPLAYER_SERVER_IP
        while True:
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quit_game()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.game.effect_sounds['go_back'].play()
                        self.game_intro()
                    elif event.key == pg.K_BACKSPACE:
                        self.game.effect_sounds['backspace'].play()
                        word_ip = word_ip[:-1]
                    elif event.key == pg.K_RETURN:
                        address = word_ip if len(word_ip) > 0 else suggested_ip
                        # stop main menu music before entering game
                        self.game.effect_sounds['main_menu_music'].stop()
                        #self.game.missions_done = 1   # Reset mission count on game completion
                        #self.game.invisible_play_count = 0
                        self.game.new()
                        self.game.serveraddress = address
                        self.game.runmultiplayer()
                        return
                    elif len(word_ip) < self.word_count_ip:
                        word_ip += event.unicode
                        self.game.effect_sounds['keypress'].play()
                self.game.board.draw_input_address(word_ip, WIDTH / 2, HEIGHT / 2, suggested_ip)

    def game_over(self, scoreboard, message, subtitle='', lesson=''):
        while True:
            self.game.board.draw_game_over(scoreboard, message, subtitle, lesson)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quit_game()
                confirmed = (event.type == pg.KEYDOWN and event.key in (pg.K_SPACE, pg.K_RETURN)) or \
                    (event.type == pg.MOUSEBUTTONDOWN and event.button == 1)
                if confirmed:
                    self.game.effect_sounds['main_menu_music'].play(-1)
                    # Stop winning sound effect before returning to main menu
                    self.game.effect_sounds["victory_crew"].stop()
                    if self.game.pause_quit_button_status and self.game.paused:
                        self.game.quit()
                    else:
                        return
    def game_over_imposter(self, scoreboard, message, subtitle='', lesson=''):
        while True:
            self.game.board.draw_game_over_imposter(scoreboard, message, subtitle, lesson)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quit_game()
                confirmed = (event.type == pg.KEYDOWN and event.key in (pg.K_SPACE, pg.K_RETURN)) or \
                    (event.type == pg.MOUSEBUTTONDOWN and event.button == 1)
                if confirmed:
                    self.game.effect_sounds['main_menu_music'].play(-1)
                    # Stop winning sound effect before returning to main menu
                    self.game.effect_sounds["victory_imposter"].stop()
                    if self.game.pause_quit_button_status and self.game.paused:
                        self.game.quit()
                    else:
                        return

    def game_left(self, scoreboard, message):
        while True:
            self.game.board.draw_game_left(scoreboard, message)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quit_game()
                confirmed = (event.type == pg.KEYDOWN and event.key in (pg.K_SPACE, pg.K_RETURN)) or \
                    (event.type == pg.MOUSEBUTTONDOWN and event.button == 1)
                if confirmed:
                    self.game.effect_sounds['main_menu_music'].play(-1)
                    # Stop winning sound effect before returning to main menu
                    self.game.effect_sounds["victory_crew"].stop()
                    if self.game.pause_quit_button_status and self.game.paused:
                        self.game.quit()
                    else:
                        return

    # min_click_y guards screens whose out-of-range fallback is destructive
    # (the main menu's "else: quit_game()") -- clicks above it are ignored so
    # a stray click near the logo can't be misread as picking the last item.
    def set_menu_cursor_limit(self, i_value, top, bottom, pos, draw, previous, size=50, min_click_y=0):
        while True:
            self.set_position(pos)
            draw(self.set_menu_cursor(size))
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quit_game()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE or event.key == pg.K_BACKSPACE:
                        self.game.effect_sounds['go_back'].play()
                        previous()
                    if event.key == pg.K_UP or event.key == pg.K_w:
                        if self.pos_y > top:
                            self.i -= i_value
                            self.game.effect_sounds['menu_sel'].play()
                    if event.key == pg.K_DOWN or event.key == pg.K_s:
                        if self.pos_y < bottom:
                            self.i += i_value
                            self.game.effect_sounds['menu_sel'].play()
                    if event.key == pg.K_SPACE or event.key == pg.K_RETURN:
                        self.game.effect_sounds['selected'].play()
                        return False
                elif event.type == pg.MOUSEMOTION:
                    if event.pos[1] >= min_click_y:
                        self.i = event.pos[1] / HEIGHT
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if event.pos[1] >= min_click_y:
                        self.i = event.pos[1] / HEIGHT
                        self.game.effect_sounds['selected'].play()
                        return False

    def set_position(self, x):
        self.pos_y = HEIGHT * self.i
        self.pos_x = WIDTH * x

    def set_menu_cursor(self, size=50):
        intro_object = MenuCursor(self.game, self.pos_x, self.pos_y, size, size)
        intro_object.animate((0, 0), (0, 0, self.pos_x, self.pos_y))
        return intro_object

