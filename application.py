import pygame

import graphics
from graphics import Board, Button, Text, Clock, ScrollableText, ToggleButton
import pieces
from typing import Optional, Tuple, List

"""
Contains event and click handling.
"""

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
CURRENT_SCREEN = "Menu"

FPS = 60

pieces_group = pygame.sprite.Group()
is_white_on_turn = True
is_board_turned = False
selected_piece: Optional[pieces.Piece] = None
selected_piece_group = pygame.sprite.GroupSingle()
before_promotion_row, before_promotion_col = None, None
before_promotion_taken_piece: Optional[pieces.Piece] = None
last_move: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None  # [[from row, from col], [to row, to col]]
is_onturn_king_in_check = False

BACKGROUND_COLOR = (122, 104, 70)
board = Board((SCREEN_WIDTH // 2 - graphics.SQUARE_SIZE * 4), (SCREEN_HEIGHT // 2 - graphics.SQUARE_SIZE * 4))

game_buttons: List[Button] = []
game_texts: List[Text] = []
menu_buttons: List[Button] = []
menu_texts: List[Text] = []

# button = Button(50, 50, 200, 70, (0, 0, 0), "Valami", 25, (100, 100, 200), True, graphics.menu_onclick)
three_button = Button(100, 220, 150, 70, (72, 245, 66), "3 + 0", 25, (100, 100, 200), True, graphics.menu_onclick)
five_button = Button(300, 220, 150, 70, (72, 245, 66), "5 + 0", 25, (100, 100, 200), True, graphics.menu_onclick)
ten_button = Button(500, 220, 150, 70, (72, 245, 66), "10 + 0", 25, (100, 100, 200), True, graphics.menu_onclick)
white_button = Button(200, 350, 150, 70, (72, 245, 66), "White", 25, (100, 100, 200), True, graphics.menu_onclick)
black_button = Button(420, 350, 150, 70, (72, 245, 66), "Black", 25, (100, 100, 200), True, graphics.menu_onclick)
start_button = Button(300, 460, 150, 70, (72, 245, 66), "Start", 25, (100, 100, 200), True, graphics.menu_onclick)
menu_buttons = [three_button, five_button, ten_button, white_button, black_button, start_button]
selected_button = 180
print(selected_button)

time_buttons = [three_button, five_button, ten_button]  # idő csoport
color_buttons = [white_button, black_button]  # szín csoport
start_button.set_text("Start")


def initial_menu_buttons():
    for button in time_buttons:
        button.selected = False
        button.background_color = (72, 245, 66)
    time_buttons[0].selected = True
    time_buttons[0].background_color = (245, 215, 66)

    for button in color_buttons:
        button.selected = False
        button.background_color = (72, 245, 66)
    color_buttons[0].selected = True
    color_buttons[0].background_color = (245, 215, 66)

    # start_button.selected = True
    # start_button.background_color = (245, 215, 66)


welcome_text = Text(250, 150, "Welcome to our chess game!", 25, pygame.Color(0, 20, 20), True)
welcome_text.set_text("Welcome to our chess game!", 'Comic_sans')
menu_texts.append(welcome_text)

turn_board_button = Button(0, 0, 250, 65, pygame.Color(20, 150, 0),
                           "Tábla megfordítása", 28, pygame.Color(0, 0, 0), True, graphics.turn_board)
turn_board_button.set_text("Tábla megfordítása")
turn_board_button.is_visible = True
game_buttons.append(turn_board_button)

resign_button = Button(1150, 650, 250, 65, pygame.Color(20, 150, 0),
                       "Feladás", 28, pygame.Color(0, 0, 0), True, graphics.resign)
resign_button.set_text("Feladás")
resign_button.is_visible = True
game_buttons.append(resign_button)

white_clock = Clock(100, 450, 300, 100, selected_button, 36, bg_color=(200, 200, 200))
black_clock = Clock(100, 350, 300, 100, selected_button, 36, bg_color=(200, 200, 200))


def set_clocks(time: str):
    if not isinstance(time, str):
        raise TypeError(f"Parameter time should be the type of int not {type(time)}.")
    match time:
        case "3 + 0":
            return 180
        case "5 + 0":
            return 300
        case "10 + 0":
            return 600
        case _:
            raise ValueError(f"There is no such time control in our game {time}!")


def switch_clocks():
    global is_white_on_turn, white_clock, black_clock
    if is_white_on_turn:
        black_clock.stop()
        white_clock.start()
    else:
        white_clock.stop()
        black_clock.start()


move_list = ScrollableText(1200, 200, 150, 450, font_size=35, text_color=(0, 0, 0), bg_color=(200, 200, 200))
toggle_music_button = ToggleButton(300, 0, 200, 65, (200, 200, 200), "Turn music on/off", 25, (0, 0, 0), True,
                                   'music/Chess_Game.mp3')
toggle_music_button.set_text("Turn music on/off")

white_material_text = Text(900, 770, "0", 40, pygame.Color(255, 0, 0), True)
black_material_text = Text(900, 50, "0", 40, pygame.Color(255, 0, 0), True)


def application():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), vsync=True)
    pygame.display.set_caption('Chess game')
    screen.fill(BACKGROUND_COLOR)
    clock = pygame.time.Clock()
    setup_pieces()
    initial_menu_buttons()

    running = True
    while running:
        clock.tick(FPS)
        # pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            if CURRENT_SCREEN == "Menu":
                menu_event_handler(event)
            elif CURRENT_SCREEN == "Game":
                game_event_handler(event)

        if CURRENT_SCREEN == "Menu":
            menu_screen(screen)
        elif CURRENT_SCREEN == "Game":
            game_screen(screen)

        pygame.display.update()

    pygame.quit()
    exit()


def menu_screen(screen):
    for button in menu_buttons:
        button.draw(screen)

    for text in menu_texts:
        text.draw(screen)


def menu_event_handler(event):
    global selected_button
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mouse_pos = pygame.mouse.get_pos()
        for btn in menu_buttons:
            if btn.start_x <= mouse_pos[0] <= btn.start_x + btn.width and \
                    btn.start_y <= mouse_pos[1] <= btn.start_y + btn.height:
                btn.onclick()
                if btn in time_buttons:
                    selected_button = set_clocks(btn.text.text)
                    new_time = set_clocks(btn.text.text)
                    white_clock.set_time(new_time)
                    black_clock.set_time(new_time)
                    for other_btn in time_buttons:
                        if other_btn != btn:
                            other_btn.selected = False
                            other_btn.background_color = (72, 245, 66)
                elif btn in color_buttons:
                    for other_btn in color_buttons:
                        if other_btn != btn:
                            other_btn.selected = False
                            other_btn.background_color = (72, 245, 66)
                if btn == start_button:
                    global CURRENT_SCREEN
                    CURRENT_SCREEN = "Game"
                    white_clock.start()
                break


def game_screen(screen):
    pieces_group.update()
    selected_piece_group.update()

    screen.fill(BACKGROUND_COLOR)

    for button in game_buttons:
        button.draw(screen)

    for text in game_texts:
        text.draw(screen)

    board.draw_board(screen)

    move_list.draw(screen)
    toggle_music_button.draw(screen)

    # teszt
    balance = calculate_material_balance()
    white_material_text.set_text(f"Piece Evaluation: {max(balance, 0)}")  # Pozitív értékek, ha fehér előnyben
    black_material_text.set_text(f"Piece Evaluation: {-min(balance, 0)}")  # Negatív értékek, ha fekete előnyben

    white_material_text.draw(screen)  # Minden képkockafrissítéskor meghívandó
    black_material_text.draw(screen)
    # teszt

    if CURRENT_SCREEN == "Game":
        delta_time = pygame.time.Clock().tick(FPS) / 1000
        white_clock.update(delta_time)
        black_clock.update(delta_time)
        white_clock.draw(screen)
        black_clock.draw(screen)


def game_event_handler(event):
    global selected_piece
    mouse_x, mouse_y = pygame.mouse.get_pos()

    mouse_row = (mouse_y - board.start_y) // board.square_size
    mouse_col = (mouse_x - board.start_x) // board.square_size
    move_list.handle_event(event)  # hozzáadott, nem biztos, hogy jó.

    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == pygame.BUTTON_LEFT:
            if board.start_x <= mouse_x <= board.start_x + board.board.get_width() and \
                    board.start_y <= mouse_y <= board.start_y + board.board.get_height():
                mouse_button_down_on_board(mouse_row, mouse_col)
            else:
                if before_promotion_row is not None:
                    cancel_promotion()

            turn_board_button_end_x, turn_board_button_end_y = turn_board_button.get_end_pos()
            if (turn_board_button.start_x <= mouse_x <= turn_board_button_end_x
                    and turn_board_button.start_y <= mouse_y <= turn_board_button_end_y):
                turn_board_button.onclick()

            mouse_pos = pygame.mouse.get_pos()
            if toggle_music_button.start_x <= mouse_pos[
                0] <= toggle_music_button.start_x + toggle_music_button.width and \
                    toggle_music_button.start_y <= mouse_pos[
                1] <= toggle_music_button.start_y + toggle_music_button.height:
                toggle_music_button.onclick()

            if resign_button.start_x <= mouse_pos[0] <= resign_button.start_x + resign_button.width and \
                    resign_button.start_y <= mouse_pos[
                1] <= resign_button.start_y + resign_button.height:
                resign_button.onclick()

        if event.button == pygame.BUTTON_RIGHT:
            if selected_piece is not None:
                if selected_piece.is_dragged:
                    selected_piece.end_drag()

                if before_promotion_row is not None:
                    cancel_promotion()

                selected_piece = None
                board.legal_move_marks = None

    if event.type == pygame.MOUSEBUTTONUP and event.button == pygame.BUTTON_LEFT:
        if selected_piece is not None:
            mouse_button_up_on_board(mouse_row, mouse_col)


def mouse_button_down_on_board(mouse_row, mouse_col):
    global selected_piece
    global before_promotion_row, before_promotion_col

    if 0 <= mouse_row <= 7 and 0 <= mouse_col <= 7:
        if selected_piece is None:
            select_piece(mouse_row, mouse_col)
        else:
            if board.promotion_tab.is_visible:
                promotion_tab_click_control()
            else:
                try:
                    move_with_selected_piece(mouse_row, mouse_col)
                except ValueError as e:
                    print(e)
                    try:
                        select_piece(mouse_row, mouse_col)
                    except ValueError as e:
                        print(e)
                        selected_piece = None
                        board.legal_move_marks = None
    else:
        if before_promotion_row is not None:
            cancel_promotion()
        selected_piece = None
        board.legal_move_marks = None


def mouse_button_up_on_board(mouse_row, mouse_col):
    global selected_piece
    global before_promotion_row, before_promotion_col

    if selected_piece is not None and selected_piece.is_dragged:
        if selected_piece.row != mouse_row or selected_piece.col != mouse_col:
            try:
                selected_piece.end_drag()
                move_with_selected_piece(mouse_row, mouse_col)
            except ValueError as e:
                print(e)
                before_promotion_row, before_promotion_col = None, None
                board.promotion_tab.set_invisible()
        else:
            selected_piece.end_drag()


def select_piece(mouse_row, mouse_col) -> None:
    global selected_piece

    selected_piece = pieces.find_piece(mouse_row, mouse_col)
    if selected_piece is not None:
        selected_piece.start_drag()
        board.legal_move_marks = None


def promotion_tab_click_control() -> None:
    global is_white_on_turn
    global selected_piece
    global before_promotion_row, before_promotion_col, before_promotion_taken_piece
    global last_move

    mouse_x, mouse_y = pygame.mouse.get_pos()
    if board.promotion_tab.global_x <= mouse_x <= board.promotion_tab.global_x + board.square_size and \
            board.promotion_tab.global_y <= mouse_y <= board.promotion_tab.global_y + 4 * board.square_size and \
            isinstance(selected_piece, pieces.Pawn):
        selected_piece.promote(board.promotion_tab.get_clicked_piece_name())

        last_move = ((before_promotion_row, before_promotion_col), (selected_piece.row, selected_piece.col))

        before_promotion_row, before_promotion_col = None, None
        before_promotion_taken_piece = None

        is_white_on_turn = not is_white_on_turn
        if is_mate(get_king()):
            lose()
        if not pieces.mating_force():
            draw()
    else:
        cancel_promotion()

    board.promotion_tab.set_invisible()
    selected_piece = None
    board.legal_move_marks = None


def move_with_selected_piece(mouse_row, mouse_col) -> None:
    global is_white_on_turn
    global selected_piece
    global last_move

    before_move_row, before_move_col = selected_piece.row, selected_piece.col
    before_take_piece = pieces.find_piece(mouse_row, mouse_col)

    splitted_info = selected_piece.info().split(":")
    selected_piece.move_to(mouse_row, mouse_col)
    move_list.add_text(f"{splitted_info[0]}. {mouse_row}, {mouse_col}")
    if isinstance(selected_piece, pieces.Pawn) and selected_piece.row == selected_piece.last_row():
        begin_promotion(mouse_col, before_move_row, before_move_col, before_take_piece)
    elif isinstance(selected_piece, pieces.King):
        bal_bastya = pieces.find_piece(selected_piece.row, 0)
        jobb_bastya = pieces.find_piece(selected_piece.row, 7)
        if isinstance(jobb_bastya, pieces.Rook) and selected_piece.row == before_move_row and (
                selected_piece.col == before_move_col + 2):
            jobb_bastya.put(jobb_bastya.row, jobb_bastya.col - 2)
            jobb_bastya.moved = True
        if isinstance(bal_bastya, pieces.Rook) and selected_piece.row == before_move_row and (
                selected_piece.col == before_move_col - 2):
            bal_bastya.put(bal_bastya.row, bal_bastya.col + 3)
            selected_piece.moved = True
        if isinstance(selected_piece, pieces.Rook):
            selected_piece.moved = True
        selected_piece.moved = True
        is_white_on_turn = not is_white_on_turn
        if is_mate(get_king()):
            lose()
        if not pieces.mating_force():
            draw()
    else:
        last_move = ((before_move_row, before_move_col), (mouse_row, mouse_col))
        selected_piece = None
        board.legal_move_marks = None
        is_white_on_turn = not is_white_on_turn
        if is_mate(get_king()):
            lose()
        if not pieces.mating_force():
            draw()
        switch_clocks()


def begin_promotion(promotion_col, before_move_row, before_move_col, before_take_piece: Optional[pieces.Pawn]) -> None:
    global before_promotion_row, before_promotion_col, before_promotion_taken_piece

    before_promotion_row, before_promotion_col = before_move_row, before_move_col

    before_promotion_taken_piece = before_take_piece
    board.promotion_tab.set_visible(promotion_col)


def cancel_promotion() -> None:
    global selected_piece
    global before_promotion_row, before_promotion_col, before_promotion_taken_piece

    if selected_piece is None:
        raise TypeError("There must be a selected piece while promoting!")

    selected_piece.row, selected_piece.col = before_promotion_row, before_promotion_col
    selected_piece.update_rect()
    before_promotion_row, before_promotion_col = None, None

    if before_promotion_taken_piece is not None:
        add_piece_to_list(before_promotion_taken_piece)
        before_promotion_taken_piece = None

    board.promotion_tab.set_invisible()
    selected_piece = None
    board.legal_move_marks = None


def add_piece_to_list(piece: pieces.Piece) -> None:
    if not isinstance(piece, pieces.Piece):
        raise TypeError(f"Added piece must be a piece, got {piece} with type of {type(piece)}.")

    piece.add_to_list()


def remove_piece_from_list(piece: pieces.Piece) -> None:
    if not isinstance(piece, pieces.Piece):
        raise TypeError(f"Added piece must be a piece, got {piece} with type of {type(piece)}.")

    piece.remove_from_list()


def setup_pieces() -> None:
    global selected_piece
    global pieces_group
    global selected_piece_group
    global before_promotion_row, before_promotion_col
    global before_promotion_taken_piece
    global last_move
    global is_onturn_king_in_check
    global is_white_on_turn

    pieces_group = pygame.sprite.Group()
    pieces.pieces_list = []

    is_white_on_turn = True
    selected_piece = None
    selected_piece_group = pygame.sprite.GroupSingle()
    before_promotion_row, before_promotion_col = None, None
    before_promotion_taken_piece = None
    last_move = None  # [[from row, from col], [to row, to col]]
    is_onturn_king_in_check = False

    for i in range(8):
        add_piece_to_list(pieces.Pawn(1, i, False))
        add_piece_to_list(pieces.Pawn(6, i, True))

    add_piece_to_list(pieces.Knight(0, 1, False))
    add_piece_to_list(pieces.Knight(0, 6, False))
    add_piece_to_list(pieces.Knight(7, 1, True))
    add_piece_to_list(pieces.Knight(7, 6, True))

    add_piece_to_list(pieces.Bishop(0, 2, False))
    add_piece_to_list(pieces.Bishop(0, 5, False))
    add_piece_to_list(pieces.Bishop(7, 2, True))
    add_piece_to_list(pieces.Bishop(7, 5, True))

    add_piece_to_list(pieces.Rook(0, 0, False))
    add_piece_to_list(pieces.Rook(0, 7, False))
    add_piece_to_list(pieces.Rook(7, 0, True))
    add_piece_to_list(pieces.Rook(7, 7, True))

    pieces.white_king = pieces.King(7, 4, True)
    pieces.black_king = pieces.King(0, 4, False)
    add_piece_to_list(pieces.white_king)
    add_piece_to_list(pieces.black_king)

    add_piece_to_list(pieces.Queen(0, 3, False))
    add_piece_to_list(pieces.Queen(7, 3, True))


def is_mate(king: Optional[pieces.King]) -> bool:
    if king is None:
        print("No king found.")
        return False
    in_check = king.is_in_check()
    no_moves = len(
        king.get_all_legal_moves()) == 0
    print("összes legális lépés.", king.get_all_legal_moves())
    print(f"Checking mate: in_check={in_check}, no_moves={no_moves}")
    return in_check and no_moves


def get_king() -> Optional[pieces.King]:
    for piece in pieces.pieces_list:
        if isinstance(piece, pieces.King) and (piece.is_white == is_white_on_turn):
            print(f"King found: {piece}")
            return piece
    print("No king matched the criteria.")
    return None


win_text = Text(135, 150, "You won the game!", 25, pygame.Color(0, 20, 20), True)


def lose():
    print("Nyertél!")
    result_text = "White won the game!" if not is_white_on_turn else "Black won the game!"
    save_game_result(result_text)
    if not is_white_on_turn:
        win_text.set_text("White won the game!", 'Comic_sans')
        game_texts.append(win_text)
    else:
        win_text.set_text("Black won the game!", 'Comic_sans')
        win_text.start_y = 650
        game_texts.append(win_text)


draw_text = Text(750, 50, "Draw!", 25, pygame.Color(0, 20, 20), True)


def draw():
    print("Döntetlen!")
    white_clock.stop()
    black_clock.stop()
    draw_text.set_text("Draw!", 'Comic_sans')
    game_texts.append(draw_text)
    save_game_result("Draw!")


game_count = 0


def save_game_result(result_message):
    global game_count
    filename = f'games/game_result_{game_count}.txt'
    with open(filename, 'w', encoding='utf-8') as file:
        for text, surface in move_list.texts:
            file.write(text + '\n')
        file.write(result_message + '\n')

    move_list.texts.clear()
    move_list.first_addition = True

    game_count += 1


def calculate_material_balance():
    white_score = 0
    black_score = 0
    for piece in pieces.pieces_list:
        piece_value = pieces.piece_values[type(piece).__name__]
        if piece.is_white:
            white_score += piece_value
        else:
            black_score += piece_value
    return white_score - black_score
