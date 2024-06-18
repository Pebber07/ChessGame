from datetime import datetime, timedelta

import pygame
import application as app
import pieces
from typing import List
import sys

"""
Contains visual/graphic elements and components.
"""

BOARD_START_X, BOARD_START_Y = 0, 0
SQUARE_SIZE = 85


class Board:
    def __init__(self, start_x=0, start_y=0):
        global BOARD_START_X, BOARD_START_Y

        self._start_x, self._start_y = start_x, start_y
        BOARD_START_X, BOARD_START_Y = start_x, start_y
        self._square_size = SQUARE_SIZE
        self.board_rows, self.board_cols = 8, 8

        self.white_color = pygame.Color(255, 255, 255)
        self.dark_color = pygame.Color(155, 182, 230)
        self.last_move_marker_color = pygame.Color(160, 230, 80)
        self.legal_move_marker_color = pygame.Color(255, 20, 0)
        self.selected_piece_square_color = pygame.Color(230, 230, 80)
        self.check_marker_color = pygame.Color(220, 30, 10)

        self.board = pygame.Surface((self.square_size * self.board_rows, self.square_size * self.board_cols))

        self.promotion_tab = PromotionTab()

        self.legal_move_marks = None

    def draw_board(self, screen):
        self.draw_squares()
        self.draw_board_marks()

        app.pieces_group.draw(self.board)

        if app.selected_piece is not None and app.selected_piece.is_white == app.is_white_on_turn:
            if self.legal_move_marks is None:
                self.legal_move_marks = pieces.get_all_legal_moves(app.selected_piece)
            self.draw_legal_moves_marks()
        else:
            self.legal_move_marks = None

        if self.promotion_tab.is_visible:
            self.promotion_tab.draw(self.board)

        screen.blit(self.board, (self.start_x, self.start_y))

        app.selected_piece_group.draw(screen)

    def draw_squares(self):
        square = pygame.Rect(0, 0, self.square_size, self.square_size)
        for i in range(self.board_cols):
            for j in range(self.board_rows):
                square.left, square.top = i * self.square_size, j * self.square_size
                pygame.draw.rect(self.board, self.white_color if (i + j) % 2 == 0 else self.dark_color, square)

        if app.selected_piece is not None and app.selected_piece.is_white == app.is_white_on_turn:
            square.left = app.selected_piece.col * self.square_size
            square.top = app.selected_piece.row * self.square_size
            pygame.draw.rect(self.board, self.selected_piece_square_color, square)

        if app.last_move is not None:
            square.left, square.top = app.last_move[0][1] * self.square_size, app.last_move[0][0] * self.square_size
            pygame.draw.rect(self.board, self.last_move_marker_color, square)

            square.left, square.top = app.last_move[1][1] * self.square_size, app.last_move[1][0] * self.square_size
            pygame.draw.rect(self.board, self.last_move_marker_color, square)

        # if app.is_onturn_king_in_check:
        #     if app.is_white_on_turn:
        #         square.left = pieces.white_king.col * self.square_size
        #         square.top = pieces.white_king.row * self.square_size
        #         pygame.draw.rect(self.board, self.check_marker_color, square, 3)
        #     else:
        #         square.left = pieces.black_king.col * self.square_size
        #         square.top = pieces.black_king.row * self.square_size
        #         pygame.draw.rect(self.board, self.check_marker_color, square, 3)

    def draw_board_marks(self):
        numbers_font = pygame.font.SysFont("arial", 24)
        letters_font = pygame.font.SysFont("arial", 26)

        j = 0
        iteration = range(8) if not app.is_board_turned else range(7, -1, -1)
        for i in iteration:
            rendered_text = numbers_font.render(chr(49 + (7 - i)), True, (50, 50, 50))
            self.board.blit(rendered_text, (2, j * self.square_size + self.square_size // 2))

            rendered_text = letters_font.render(chr(97 + i), True, (50, 50, 50))
            self.board.blit(rendered_text, (j * self.square_size + 71, 8 * self.square_size - 34))

            j += 1

    def draw_legal_moves_marks(self) -> None:
        for legal_move in self.legal_move_marks:
            move_row, move_col = legal_move[0], legal_move[1]

            pygame.draw.circle(self.board, self.legal_move_marker_color,
                               (move_col * self.square_size + self.square_size // 2,
                                move_row * self.square_size + self.square_size // 2), 13, 4)

    @property
    def square_size(self):
        return self._square_size

    @square_size.setter
    def square_size(self, value):
        global SQUARE_SIZE

        SQUARE_SIZE = value
        self._square_size = value

    @property
    def start_x(self):
        return self._start_x

    @start_x.setter
    def start_x(self, value):
        global BOARD_START_X

        BOARD_START_X = value
        self._start_x = value

    @property
    def start_y(self):
        return self._start_y

    @start_y.setter
    def start_y(self, value):
        global BOARD_START_Y

        BOARD_START_Y = value
        self._start_y = value


class PromotionTab:
    def __init__(self):
        self.start_x, self.start_y = 0, 0
        self.global_x, self.global_y = 0, 0

        self.tab = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE * 4))
        self.background_color = pygame.Color((10, 128, 10))

        self._visible = False

        self.white_images: List[pygame.image] = list()
        self.white_images.append(pygame.image.load('images/white/Queen.png'))
        self.white_images.append(pygame.image.load('images/white/Knight.png'))
        self.white_images.append(pygame.image.load('images/white/Rook.png'))
        self.white_images.append(pygame.image.load('images/white/Bishop.png'))

        self.black_images: List[pygame.image] = list()
        self.black_images.append(pygame.image.load('images/black/bishop.png'))
        self.black_images.append(pygame.image.load('images/black/rook.png'))
        self.black_images.append(pygame.image.load('images/black/knight.png'))
        self.black_images.append(pygame.image.load('images/black/queen.png'))

    @property
    def is_visible(self):
        return self._visible

    def set_visible(self, promotion_col: int):
        if not isinstance(promotion_col, int):
            raise TypeError(f"Parameter promotion_col must be integer.")

        self._visible = True

        self.start_x = promotion_col * SQUARE_SIZE
        self.global_x = BOARD_START_X + promotion_col * SQUARE_SIZE
        if app.is_white_on_turn is not app.is_board_turned:
            self.start_y = 0
            self.global_y = BOARD_START_Y + 0
        else:
            self.start_y = 4 * SQUARE_SIZE
            self.global_y = BOARD_START_Y + 4 * SQUARE_SIZE

        self.draw_content()

    def set_invisible(self):
        self._visible = False

    def get_clicked_piece_name(self) -> str:
        mouse_y = pygame.mouse.get_pos()[1]
        mouse_col = (mouse_y - self.global_y) // SQUARE_SIZE

        piece_order = [0, 1, 2, 3] if app.is_white_on_turn is not app.is_board_turned else [3, 2, 1, 0]
        if piece_order[0] == mouse_col:
            return "queen"
        if piece_order[1] == mouse_col:
            return "knight"
        if piece_order[2] == mouse_col:
            return "rook"
        if piece_order[3] == mouse_col:
            return "bishop"
        raise Exception("Something wrong happened in selecting promotion piece.")

    def draw_content(self):
        self.tab.fill(self.background_color)

        images = self.white_images if app.is_white_on_turn else self.black_images
        iteration = range(4) if not app.is_board_turned else range(3, -1, -1)
        position = 0
        for i in iteration:
            self.tab.blit(images[i], (0, position * SQUARE_SIZE))
            position += 1

    def draw(self, screen):
        if self.is_visible:
            screen.blit(self.tab, (self.start_x, self.start_y))


class Button:
    """Universal button with text."""

    def __init__(self, start_x, start_y, width, height, background_color, text, text_size, text_color, is_visible,
                 onclick):
        if not callable(onclick):
            raise TypeError(f"Onclick must be callable.")

        self.start_x, self.start_y = start_x, start_y
        self._width, self._height = width, height
        self._background_color = background_color

        self.button = pygame.Surface((width, height))
        self.is_visible = is_visible
        self.text = Text(0, 0, text, text_size, text_color, True)
        self.text.set_centered(self.button)
        self.set_text(text)

        self.onclick_method = onclick
        self.button.fill(self._background_color)
        self.selected = False

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, color):
        self._background_color = color
        self.button.fill(self._background_color)
        self.set_text(self.text.text)

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        if not isinstance(value, int):
            raise TypeError(f"Parameter width must be integer. Got {type(value)}.")
        self._width = value
        self.button = pygame.Surface((self._width, self._height))
        self.text.set_centered(self.button)

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        if not isinstance(value, int):
            raise TypeError(f"Parameter height must be integer. Got {type(value)}.")
        self._height = value
        self.button = pygame.Surface((self._width, self._height))
        self.text.set_centered(self.button)

    def get_end_pos(self):
        return self.start_x + self.width, self.start_y + self.height

    def set_text(self, text):
        self.button.fill(self.background_color)

        self.text.set_text(text)
        self.button.blit(self.text.rendered_text, (self.text.start_x, self.text.start_y))

    def draw(self, screen):
        if self.is_visible:
            screen.blit(self.button, (self.start_x, self.start_y))

    def onclick(self):
        if self.is_visible:
            self.onclick_method(self)


class Text:
    def __init__(self, start_x: int, start_y: int, text: str, text_size: int, text_color: pygame.Color, is_visible):
        self.start_x, self.start_y = start_x, start_y
        self.width, self.height = 0, 0

        self.text = text
        self.text_size = text_size
        self.text_color = text_color

        self.is_visible = is_visible

        self.rendered_text: pygame.Surface = pygame.Surface((0, 0))
        self.set_text(text)
        # self.style

    def set_text(self, text, font_style='arial'):
        if not isinstance(text, str):
            raise ValueError("Text must be a string type")
        self.text = text
        font_style = pygame.font.SysFont(font_style, self.text_size)
        self.rendered_text = font_style.render(self.text, True, self.text_color)

        self.width, self.height = self.rendered_text.get_width(), self.rendered_text.get_height()

    def set_centered(self, screen: pygame.Surface):
        self.start_x = (screen.get_width() - self.width) // 2
        self.start_y = (screen.get_height() - self.height) // 2

    def draw(self, screen: pygame.Surface):
        if self.is_visible:
            screen.blit(self.rendered_text, (self.start_x, self.start_y))


class Clock(object):
    """
    a grafikai kinézetét fogja tartalamazni.
    """

    def __init__(self, x, y, width, height, initial_time, font_size=20, bg_color=(200, 200, 200), text_color=(0, 0, 0)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.initial_time = initial_time
        self.remaining_time = self.initial_time
        self.font = pygame.font.SysFont('arial', font_size)
        self.bg_color = bg_color
        self.text_color = text_color
        self.rect = pygame.Rect(x, y, width, height)
        self.active = False

    def set_time(self, new_time):
        self.initial_time = new_time
        self.remaining_time = new_time

    def start(self):
        self.active = True

    def stop(self):
        self.active = False

    def update(self, dt):
        if self.active:
            self.remaining_time -= dt
            if self.remaining_time <= 0:
                self.remaining_time = 0
                self.active = False

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect)

        minutes = int(self.remaining_time // 60)
        seconds = int(self.remaining_time % 60)
        time_str = f"{minutes:02}:{seconds:02}"
        text_surface = self.font.render(time_str, True, self.text_color)
        if text_surface.get_width() > self.width - 10:
            raise ValueError(f"Too long text ({text_surface.get_width()}) for clock width {self.width}.")

        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)  # Todo: változtatás


def turn_board(button: Button):
    if button.is_visible:
        app.is_board_turned = not app.is_board_turned

        for piece in pieces.pieces_list:
            piece.row, piece.col = 7 - piece.row, 7 - piece.col
            piece.update_rect()

        if app.before_promotion_taken_piece is not None:
            app.before_promotion_taken_piece.row = 7 - app.before_promotion_taken_piece.row
            app.before_promotion_taken_piece.col = 7 - app.before_promotion_taken_piece.col
            app.before_promotion_row = 7 - app.before_promotion_row
            app.before_promotion_col = 7 - app.before_promotion_col

        if app.last_move is not None:
            app.last_move = ((7 - app.last_move[0][0], 7 - app.last_move[0][1]),
                             (7 - app.last_move[1][0], 7 - app.last_move[1][1]))

        app.board.legal_move_marks = None


def menu_onclick(button: Button):
    button.selected = not button.selected
    button.background_color = (245, 215, 66) if button.selected else (72, 245, 66)


class ScrollableText:
    def __init__(self, x, y, width, height, font_size=20, text_color=(255, 255, 255), bg_color=(0, 0, 0)):
        self.area = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(None, font_size)
        self.text_color = text_color
        self.bg_color = bg_color
        self.texts = []
        self.offset = 0
        self.line_height = font_size + 5
        self.first_addition = True  # felirat törléséhez.

    def add_text(self, text):
        if self.first_addition:
            app.game_texts.clear()  # Üríti a listát, ha ez az első hozzáadás
            self.first_addition = False  # Frissíti a flaget
        text_surface = self.font.render(text, True, self.text_color)
        self.texts.append((text, text_surface))

    def scroll(self, delta):
        if delta < 0 and self.offset > 0:
            self.offset += delta
        elif delta > 0 and self.texts and (self.offset < len(self.texts) * self.line_height - self.area.height):
            self.offset += delta

    def draw(self, screen):
        screen.fill(self.bg_color, self.area)
        for i, (text, text_surf) in enumerate(self.texts):
            y = self.area.top + i * self.line_height - self.offset
            if self.area.top <= y <= self.area.bottom:
                screen.blit(text_surf, (self.area.left, y))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.scroll(-self.line_height)
            elif event.button == 5:  # Scroll down
                self.scroll(self.line_height)


class ToggleButton:
    def __init__(self, start_x, start_y, width, height, background_color, text, text_size, text_color, is_visible,
                 sound_file):
        self.start_x, self.start_y = start_x, start_y
        self.width, self.height = width, height
        self.background_color = background_color
        self.text = Text(0, 0, text, text_size, text_color, is_visible)
        self.is_visible = is_visible
        self.sound_file = sound_file
        self.sound = pygame.mixer.Sound(sound_file)
        self.is_playing = False
        self.button = pygame.Surface((self.width, self.height))
        self.button.fill(self.background_color)
        self.text.set_centered(self.button)

    def toggle_sound(self):
        if self.is_playing:
            pygame.mixer.Sound.stop(self.sound)
            self.is_playing = False
            print("Sound stopped.")
        else:
            pygame.mixer.Sound.play(self.sound, loops=-1)
            self.is_playing = True
            print("Sound playing.")

    def set_text(self, new_text):
        """Set the text displayed on the button."""
        self.text.set_text(new_text)
        self.text.set_centered(self.button)
        self.button.fill(self.background_color)  # ez remélem jól működik
        self.button.blit(self.text.rendered_text, (self.text.start_x, self.text.start_y))

    def draw(self, screen):
        if self.is_visible:
            screen.blit(self.button, (self.start_x, self.start_y))

    def onclick(self):
        if self.is_visible:
            self.toggle_sound()


def resign(button: Button):
    app.white_clock.stop()
    app.black_clock.stop()

    app.setup_pieces()

    if app.is_white_on_turn:
        app.lose()
    else:
        app.lose()
