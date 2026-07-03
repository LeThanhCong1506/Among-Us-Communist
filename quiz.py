"""Multiple-choice question bank + in-game quiz window for the deduction
mode ("Truy Tim Ke Tham Nhung"). This replaces the old per-task minigames
as what players do at task stations -- both crew and imposter answer (the
imposter blends in this way instead of being locked out of stations
entirely), and finishing a question grants the crewmate a temporary
tracking arrow to the imposter (see server.py's 'quiz result' handler and
game.py's tracking_crew) instead of a plain 8-tasks-done win.
"""
import json
import random

import pygame as pg

from settings import vn_font, WHITE, GREEN, RED, YELLOW, WIDTH, HEIGHT

QUESTIONS_PATH = "Assets/questions_vi.json"


class QuizBank:
    """Loads Assets/questions_vi.json and hands out questions without
    repeating one until the whole set has been seen once."""

    def __init__(self, path=QUESTIONS_PATH):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self.questions = data["questions"]
        self._unseen = []

    def next_question(self):
        if not self.questions:
            return None
        if not self._unseen:
            self._unseen = list(self.questions)
            random.shuffle(self._unseen)
        return self._unseen.pop()


class QuizWindow:
    """One open question at a station.

    Lifecycle: shown -> player clicks an option -> brief correct/incorrect
    flash (FLASH_MS) revealing the right answer -> ready_to_close() becomes
    True -> the caller (Game) reads is_correct, applies the result
    (missions_done, network message, station cooldown) and drops this
    object. This class only draws and tracks the click; it never mutates
    game state itself.
    """

    PANEL_RECT = pg.Rect(int(WIDTH / 2 - 320), int(HEIGHT / 2 - 260), 640, 520)
    FLASH_MS = 900
    # Tall enough for 2 wrapped lines of OPTION_FONT_SIZE text (see
    # option_rects/draw) -- long answer options were overflowing past the
    # button edge at the old fixed single-line height.
    OPTION_ROW_HEIGHT = 58
    OPTION_ROW_GAP = 8
    OPTION_FONT_SIZE = 15

    def __init__(self, question, station_key):
        self.question = question
        self.station_key = station_key
        self.selected = None
        self.selected_at = None

    @property
    def is_correct(self):
        return self.selected == self.question["answer"]

    def option_rects(self):
        rects = []
        top = self.PANEL_RECT.top + 180
        step = self.OPTION_ROW_HEIGHT + self.OPTION_ROW_GAP
        for i in range(len(self.question["options"])):
            rects.append(pg.Rect(self.PANEL_RECT.left + 40, top + i * step,
                                  self.PANEL_RECT.width - 80, self.OPTION_ROW_HEIGHT))
        return rects

    def handle_click(self, pos):
        """Register an option click. No-op once an option is already
        selected, so clicking during the flash can't change the answer."""
        if self.selected is not None:
            return
        for i, rect in enumerate(self.option_rects()):
            if rect.collidepoint(pos):
                self.selected = i
                self.selected_at = pg.time.get_ticks()
                return

    def ready_to_close(self):
        return self.selected is not None and pg.time.get_ticks() - self.selected_at >= self.FLASH_MS

    def draw(self, screen, board):
        panel = pg.Surface((self.PANEL_RECT.width, self.PANEL_RECT.height), pg.SRCALPHA)
        panel.fill((10, 10, 18, 235))
        screen.blit(panel, self.PANEL_RECT.topleft)
        pg.draw.rect(screen, WHITE, self.PANEL_RECT, width=2, border_radius=10)

        title_font = vn_font(20)
        title_surf = title_font.render("Câu hỏi minh bạch", True, YELLOW)
        screen.blit(title_surf, title_surf.get_rect(midtop=(self.PANEL_RECT.centerx, self.PANEL_RECT.top + 16)))

        q_font = vn_font(20)
        board.draw_wrapped_text(
            screen, self.question["text"], q_font, WHITE,
            pg.Rect(self.PANEL_RECT.left + 30, self.PANEL_RECT.top + 55, self.PANEL_RECT.width - 60, 120),
            line_spacing=6,
        )

        option_font = vn_font(self.OPTION_FONT_SIZE)
        for i, (rect, option_text) in enumerate(zip(self.option_rects(), self.question["options"])):
            if self.selected is None:
                colour = (50, 50, 65)
            elif i == self.question["answer"]:
                colour = (30, 110, 40)  # always reveal the correct one once answered
            elif i == self.selected:
                colour = (120, 30, 30)  # the wrong one the player picked
            else:
                colour = (50, 50, 65)
            pg.draw.rect(screen, colour, rect, border_radius=6)
            pg.draw.rect(screen, WHITE, rect, width=1, border_radius=6)
            # Wrap long options onto up to 2 lines instead of rendering as
            # one line that can overflow past the button edge -- stacked
            # lines are centered as a block within the row's height.
            lines = board.wrap_text_lines(option_text, option_font, rect.width - 28)[:2]
            line_height = option_font.get_height()
            block_height = len(lines) * line_height + (len(lines) - 1) * 2
            y = rect.centery - block_height / 2
            for line in lines:
                line_surf = option_font.render(line, True, WHITE)
                screen.blit(line_surf, (rect.left + 14, y))
                y += line_height + 2

        if self.selected is not None:
            result_font = vn_font(18)
            result_text = "Chính xác!" if self.is_correct else "Chưa đúng."
            result_colour = GREEN if self.is_correct else RED
            result_surf = result_font.render(result_text, True, result_colour)
            screen.blit(result_surf, result_surf.get_rect(midtop=(self.PANEL_RECT.centerx, self.PANEL_RECT.bottom - 40)))
