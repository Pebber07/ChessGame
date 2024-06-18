import pygame
import application as app
import graphics
from abc import ABC, abstractmethod
from typing import List
from typing import Tuple
from typing import Optional

"""
Contains Piece related elements. (Piece mechanics.)
"""

pieces_list: List['Piece'] = []
white_king: 'King'
black_king: 'King'
en_passant_candidate: Optional['Pawn'] = None
promotion_piece: Optional[str] = None

piece_values = {
    'Pawn': 1,
    'Rook': 5,
    'Knight': 3,
    'Bishop': 3,
    'Queen': 9,
    'King': 1
}


def find_piece(row: int, col: int, pieces: List['Piece'] = None) -> Optional['Piece']:
    """
    Finds piece on the specified position.
    :param row: Row of the piece to find.
    :param col: Column of the piece to find.
    :param pieces: All pieces of a position. Optional: If not given, then the current position will be used.
    :return: Returns the Piece on the specified position. If there is not any Piece, then returns None.
    """
    if not isinstance(row, int) or not isinstance(col, int):
        raise TypeError(f"Parameter row and col must be integers.")

    if pieces is None:
        pieces = pieces_list

    for piece in pieces:
        if piece.row == row and piece.col == col:
            return piece
    return None


def is_square_under_attack(row, col):
    for piece in pieces_list:
        if piece.is_enemy(find_piece(row, col)) and piece.is_legal_move(row, col, handle_check=False):
            return True
    return False


def get_all_legal_moves(piece: 'Piece') -> List[Optional[Tuple[int, int]]]:
    return piece.get_all_legal_moves()


def calculate_piece_start_on_screen(piece: 'Piece', x=0, y=0) -> Tuple[int, int]:
    if not isinstance(piece, Piece):
        raise ValueError(f"Piece type required for piece, got {type(piece)}")

    piece_col = piece.col
    piece_row = piece.row

    start_x = x + piece_col * graphics.SQUARE_SIZE
    start_y = y + piece_row * graphics.SQUARE_SIZE
    return start_x, start_y


def same_squared_pieces(piece: 'Piece', piece_list: List) -> bool:
    """
    :param piece: The given piece that the other pieces getting compared to.
    :param piece_list: A list consisting of Pieces
    :return: The same typeof pieces are on the same color (True), or on different color (False).
    """
    if not isinstance(piece_list[0], Piece):
        raise ValueError(f"Piece type required for piece, got {type(piece_list)}")
    else:
        if len(piece_list) == 0 or len(piece_list) == 1:
            return True
        comparative = ((piece.row + piece.col) % 2, type(piece))
        for piece in piece_list:
            if isinstance(piece, comparative[1]) and piece.row + piece.col % 2 != comparative[0]:
                return False
        return True


def mating_force() -> bool:
    """
    Determines whether is there enough force to mate the opponents king.
    :return: True value, if there is enough force, False if the game cannot be decided in any way.
    """
    first_bishop = pieces_list[0]  # what?
    if len(pieces_list) > 3:
        if same_squared_pieces(first_bishop, pieces_list):
            return False
        return True
    if len(pieces_list) == 3:
        for piece in pieces_list:
            if isinstance(piece, (Bishop, Knight)):
                return False
        return True
    return False


# nincs még sehol se meghívva.


class Piece(ABC, pygame.sprite.Sprite):
    def __init__(self, row: int, col: int, is_white: bool):
        super().__init__()
        self.row = row
        self.col = col
        self._is_white = None
        self.is_white = is_white
        self.image = pygame.image.load(f"images/{'white' if self.is_white else 'black'}/{self}.png")
        self.image = pygame.transform.scale(self.image, (graphics.SQUARE_SIZE, graphics.SQUARE_SIZE))
        start_on_screen = calculate_piece_start_on_screen(self)
        self.rect = self.image.get_rect(left=start_on_screen[0], top=start_on_screen[1])
        self.is_dragged = False

    def is_legal_move(self, where_row: int, where_col: int, pieces=None, handle_check: bool = True) -> bool:
        """
            Could this piece move to the specified place legally? Only check if it is legal but never performs the move!
            Args:
                where_row (int): The row of the specified position. Expected values from 0 to 7.
                where_col (int): The column of the specified position. Expected values from 0 to 7.
                handle_check (bool): Take care with check or ignore?
                pieces (list): All pieces of a position. Optional: If not given, then the current position will be used.
            Return:
                bool: Is the specified place a legal move?
        """
        if not isinstance(where_row, int) or not isinstance(where_col, int):
            raise TypeError(f"Parameter where_row ({where_row}) and where_col ({where_col}) must be integers.")
        if not isinstance(handle_check, bool):
            raise TypeError(f"Parameter handle_check ({handle_check}) must be bool.")

        if handle_check:
            if pieces is None:
                pieces = pieces_list

            piece_copy: Piece = self.__class__(where_row, where_col, self.is_white)
            simulated_pieces: List[Piece] = []
            simulated_own_king: Optional[King] = None

            for piece in pieces:
                simulated_piece_copy = piece.__copy__()
                if not piece.is_equal(self) and not piece.is_equal(piece_copy):
                    simulated_pieces.append(simulated_piece_copy)
                    if isinstance(simulated_piece_copy, King) and piece.is_friend(piece_copy):
                        simulated_own_king = simulated_piece_copy

            simulated_pieces.append(piece_copy)

            if simulated_own_king is None:
                if isinstance(piece_copy, King):
                    simulated_own_king = piece_copy
                else:
                    return False  # Nincs királyunk

            for piece in simulated_pieces:
                if piece_copy.is_enemy(piece) and \
                        piece.is_legal_move(simulated_own_king.row, simulated_own_king.col, simulated_pieces, False):
                    return False  # Az ellenfél le tudná venni a királyunk, sakkban vagyunk
        return True

    def put(self, where_row: int, where_col: int) -> None:
        """
        :param where_row:
        :param where_col:
        :return: Puts a given piece to the designed square.
        """
        self.row = where_row
        self.col = where_col

        self.update_rect()

    def move_to(self, where_row: int, where_col: int) -> None:
        """
        Moves the piece to the specific position if it is a legal move.
        :param where_row: The row of the specified position. Expected values from 0 to 7.
        :param where_col: The column of the specified position. Expected values from 0 to 7.
        :return:
        """
        global en_passant_candidate

        if self.is_white != app.is_white_on_turn:
            raise ValueError(f"Not your turn!")

        if not self.is_legal_move(where_row, where_col):
            raise ValueError(f"Invalid move: ({where_row}, {where_col}) with {self.info()}")

        where_to_piece = find_piece(where_row, where_col)
        if where_to_piece is not None:
            print(f"Takes {where_to_piece} on {where_row}, {where_col}.")
            where_to_piece.taken()
        else:
            print(f"Moved to {where_row}, {where_col} empty square.")

        en_passant_candidate = None

        self.row = where_row
        self.col = where_col

        self.update_rect()

    def get_all_legal_moves(self) -> List[Optional[Tuple[int, int]]]:
        return [(row, col) for col in range(8) for row in range(8)
                if (find_piece(row, col) is None or self.is_enemy(find_piece(row, col))) and
                self.is_legal_move(row, col)]

    def is_equal(self, other: 'Piece') -> bool:
        """
        Checks whether the self and another Piece are the same objects.
        :param other: The other Piece object.
        :return: True if they are the same. False if they are different ones.
        """
        return (self.row == other.row) and (self.col == other.col)

    @property
    def row(self) -> int:
        return self._row

    @row.setter
    def row(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"Row must be integer!")
        else:
            if value > 7:
                print(f"Max value for line must be 7, got {value}")
            if value < 0:
                print(f"Min value for line must be 0, got {value}")
            self._row = min(7, max(0, value))

    @property
    def col(self) -> int:
        return self._col

    @col.setter
    def col(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"Col must be integer, got {value} with type {type(value)}!")
        else:
            if value > 7:
                print(f"Max value for col must be 7, got {value}")
            if value < 0:
                print(f"Min value for col must be 0, got {value}")
            self._col = min(7, max(0, value))

    @property
    def is_white(self) -> bool:
        return self._is_white

    @is_white.setter
    def is_white(self, value: Optional[bool]):
        if self._is_white is not None:
            raise ValueError("You are not allowed to change the color!")
        else:
            if not isinstance(value, bool) and value is not None:
                raise TypeError(f"Is_white must be boolean or None, got {value} with type {type(value)}")
            self._is_white = value

    def is_friend(self, other_piece: 'Piece') -> bool:
        if not isinstance(other_piece, Piece):
            raise TypeError(f"Piece required, but given {other_piece}")
        return other_piece.is_white == self.is_white

    def is_enemy(self, other_piece: 'Piece') -> bool:
        if not isinstance(other_piece, Piece):
            raise TypeError(f"Piece required, but given {other_piece}")
        return not other_piece.is_white == self.is_white

    def taken(self):
        pieces_list.remove(self)
        app.pieces_group.remove(self)
        print(f"Piece ({self}) taken from {self.row}, {self.col}.")

        del self

    def add_to_list(self) -> None:
        pieces_list.append(self)
        app.pieces_group.add(self)

    def remove_from_list(self):
        pieces_list.remove(self)
        app.pieces_group.remove(self)

    def update(self):
        if self.is_dragged:
            self.rect.center = pygame.mouse.get_pos()

    def start_drag(self):
        self.is_dragged = True
        app.pieces_group.remove(self)
        app.selected_piece_group.add(self)

    def end_drag(self):
        self.is_dragged = False
        app.selected_piece_group.remove(self)
        app.pieces_group.add(self)
        self.update_rect()

    def update_rect(self):
        self.rect.x, self.rect.y = calculate_piece_start_on_screen(self)

    def info(self) -> str:
        name = f"{self}"[0].upper() + f"{self}"[1:]
        return f"{name}: color: {'white' if self.is_white else 'black'}, row: {self.row}, column: {self.col}."

    def __copy__(self):
        return self.__class__(self.row, self.col, self.is_white)

    @abstractmethod
    def __str__(self) -> str:
        """
        Returns the string representation of the Piece.
        :return: The piece's name. If white start with uppercase letter, else start with lowercase letter.
        """
        pass


class Knight(Piece):
    def __init__(self, row: int, col: int, is_white: bool):
        super().__init__(row, col, is_white)

    def is_legal_move(self, where_row: int, where_col: int, pieces=None, handle_check: bool = True) -> bool:
        handle_check_result = super().is_legal_move(where_row, where_col, handle_check=handle_check)

        if not handle_check_result:
            return False

        if pieces is None:
            pieces = pieces_list

        where_to_square = find_piece(where_row, where_col, pieces)
        if (where_to_square is None or self.is_enemy(where_to_square)) and \
                ((abs(where_row - self.row) == 2 and abs(where_col - self.col) == 1) or
                 (abs(where_row - self.row) == 1 and abs(where_col - self.col) == 2)):
            return True

        return False

    def get_all_legal_moves(self) -> List[Tuple[int, int]]:
        moves = [(self.row - 2, self.col - 1), (self.row - 1, self.col - 2), (self.row + 1, self.col - 2),
                 (self.row + 2, self.col - 1), (self.row - 2, self.col + 1), (self.row - 1, self.col + 2),
                 (self.row + 1, self.col + 2), (self.row + 2, self.col + 1)]

        return [move for move in moves if self.is_legal_move(move[0], move[1])]

    def __str__(self) -> str:
        return f"Knight" if self._is_white else f"knight"


class Pawn(Piece):
    def __init__(self, row: int, col: int, is_white: bool):
        super().__init__(row, col, is_white)

    def move_to(self, where_row: int, where_col: int) -> None:
        global en_passant_candidate
        previous_row, previous_col = self.row, self.col
        previous_en_passant_candidate = en_passant_candidate

        super().move_to(where_row, where_col)

        if self.col == previous_col and self.row == previous_row - 2 * self.color_modifier():
            en_passant_candidate = self

        if previous_en_passant_candidate is not None and previous_en_passant_candidate.col == self.col and \
                previous_en_passant_candidate.row == self.row + 1 * self.color_modifier():
            previous_en_passant_candidate.taken()

    def is_legal_move(self, where_row: int, where_col: int, pieces=None, handle_check: bool = True) -> bool:
        handle_check_result = super().is_legal_move(where_row, where_col, handle_check=handle_check)

        if not handle_check_result:
            return False

        if pieces is None:
            pieces = pieces_list

        if where_col == self.col:
            if find_piece(self.row - 1 * self.color_modifier(), self.col, pieces) is None:
                if where_row == self.row - 1 * self.color_modifier():
                    return True

                is_starting_position = self.row == (6 if self.is_white is not app.is_board_turned else 1)
                if is_starting_position and where_row == self.row - 2 * self.color_modifier() and \
                        find_piece(self.row - 2 * self.color_modifier(), self.col, pieces) is None:
                    return True

        where_to_piece: Optional[Piece] = find_piece(where_row, where_col, pieces)
        if (where_col == self.col - 1 or where_col == self.col + 1) and \
                where_row == self.row - 1 * self.color_modifier():
            if where_to_piece is not None and self.is_enemy(where_to_piece):
                return True
            if en_passant_candidate is not None and en_passant_candidate.col == where_col and \
                    en_passant_candidate.row == where_row + 1 * self.color_modifier():
                return True

        return False

    def get_all_legal_moves(self) -> List[Tuple[int, int]]:
        moves = [(self.row - 1 * self.color_modifier(), self.col - 1), (self.row - 1 * self.color_modifier(), self.col),
                 (self.row - 1 * self.color_modifier(), self.col + 1), (self.row - 2 * self.color_modifier(), self.col)]

        return [move for move in moves if self.is_legal_move(move[0], move[1])]

    def promote(self, promote_to: str) -> None:
        """
        Performs the promotion sequence. Creates the new Piece then delete self.
        param promote_to: Piece name to be promoted. (Must be 'queen' | 'knight' | 'rook' | 'bishop')
        """
        if not isinstance(promote_to, str):
            raise TypeError(f"Promoted_to parameter must be string, got {promote_to} with {type(promote_to)}.")

        promoted_piece: Piece
        match promote_to:
            case None:
                raise ValueError(f"Must select a promotion piece before promotion.")
            case "queen":
                promoted_piece = Queen(self.row, self.col, self.is_white)
            case "knight":
                promoted_piece = Knight(self.row, self.col, self.is_white)
            case "rook":
                promoted_piece = Rook(self.row, self.col, self.is_white)
            case "bishop":
                promoted_piece = Bishop(self.row, self.col, self.is_white)
            case _:
                raise ValueError(f"Promotion class not found. Got {promote_to}.")

        app.pieces_group.add(promoted_piece)
        pieces_list.append(promoted_piece)
        app.selected_piece = promoted_piece

        self.taken()

    def color_modifier(self):
        return 1 if self.is_white is not app.is_board_turned else -1

    def last_row(self) -> int:
        return 0 if self.is_white is not app.is_board_turned else 7

    def __str__(self) -> str:
        return f"Pawn" if self._is_white else f"pawn"


class Rook(Piece):
    def __init__(self, row: int, col: int, is_white: bool):
        super().__init__(row, col, is_white)
        self.moved = False

    def is_legal_move(self, where_row: int, where_col: int, pieces=None, handle_check: bool = True) -> bool:
        handle_check_result = super().is_legal_move(where_row, where_col, handle_check=handle_check)

        if not handle_check_result:
            return False

        if pieces is None:
            pieces = pieces_list

        # 2 reszbol all: 1. el tudok-e jutni addig a pzicioig ahova el akarok jutni, 2. a pozicioba lephetek-e
        # sor: eljutas a pozicioig
        if where_row == self.row and 0 <= where_col <= 7:
            if self.col == where_col:
                # print("Ugyanaz a row és oszlop is.")
                return False

            squares = []
            col_tmp = self.col
            if self.col < where_col:
                while col_tmp < where_col:
                    col_tmp += 1
                    squares.append(col_tmp)
            if self.col > where_col:
                while col_tmp > where_col:
                    col_tmp -= 1
                    squares.append(col_tmp)
            squares.pop()

            for square in squares:
                where_to_piece = find_piece(self.row, square, pieces)
                if where_to_piece is not None and not self.is_equal(where_to_piece):
                    # print("square-nel akadtam el.")
                    return False

            # pozicio
            piece = find_piece(where_row, where_col, pieces)
            if piece is not None and not self.is_enemy(piece):
                # print("Nem mukodik a konkret mezo vizsgalat.")
                return False
            else:
                return True

        # oszlop: eljutas a pozicioig
        if where_col == self.col and 0 <= where_row <= 7:
            if self.row == where_row:
                return False

            squares = []
            row_tmp = self.row
            if self.row < where_row:
                while row_tmp < where_row:
                    row_tmp += 1
                    squares.append(row_tmp)
            if self.row > where_row:
                while row_tmp > where_row:
                    row_tmp -= 1
                    squares.append(row_tmp)
                    print("Ez a squares tartalma:", squares)
            squares.pop()
            print("Ez a squares tartalma pop után:", squares)

            for square in squares:
                # print(f"kulso iteráció : {square}")
                where_to_piece = find_piece(square, self.col, pieces)
                if where_to_piece is not None and not self.is_equal(where_to_piece):
                    # print("Ez a where_to_piece", where_to_piece)
                    # print(f"If-belül ahol elakadok : {square}")
                    # print("square-nel akadtam el.")
                    return False  # itt van egy ideiglenes logikai változtatás

                # pozicio
            piece = find_piece(where_row, where_col, pieces)
            if piece is not None and not self.is_enemy(piece):
                # print("Nem mukodik a konkret mezo vizsgalat.")
                return False
            else:
                return True

    def get_all_legal_moves(self) -> List[Optional[Tuple[int, int]]]:
        legal_moves_list = [(self.row, i) for i in range(8) if self.is_legal_move(self.row, i)]
        legal_moves_list.extend([(i, self.col) for i in range(8) if self.is_legal_move(i, self.col)])

        return legal_moves_list

    def __str__(self) -> str:
        return f"Rook" if self._is_white else f"rook"


class Bishop(Piece):
    def __init__(self, row: int, col: int, is_white: bool):
        super().__init__(row, col, is_white)

    def is_legal_move(self, where_row: int, where_col: int, pieces=None, handle_check: bool = True) -> bool:
        handle_check_result = super().is_legal_move(where_row, where_col, handle_check=handle_check)

        if not handle_check_result:
            return False

        if pieces is None:
            pieces = pieces_list

        if abs(where_row - self.row) != abs(where_col - self.col):
            return False
        if where_row > self.row:
            next_row = 1
        else:
            next_row = -1
        if where_col > self.col:
            next_col = 1
        else:
            next_col = -1
        copy_row = self.row
        copy_col = self.col
        where_to_square = find_piece(where_row, where_col, pieces)
        while (copy_row != where_row and copy_col != where_col):
            copy_row += next_row
            copy_col += next_col
            if copy_row == where_row and copy_col == where_col:
                if where_to_square is None or self.is_enemy(where_to_square):
                    return True
                else:
                    return False
            if find_piece(copy_row, copy_col, pieces) is not None:
                return False

    def __str__(self) -> str:
        return f"Bishop" if self._is_white else f"bishop"


class King(Piece):
    def __init__(self, row: int, col: int, is_white: bool):
        super().__init__(row, col, is_white)
        self.moved = False

    def is_legal_move(self, where_row: int, where_col: int, pieces=None, handle_check: bool = True) -> bool:
        handle_check_result = super().is_legal_move(where_row, where_col, handle_check=handle_check)

        if not handle_check_result:
            return False

        if pieces is None:
            pieces = pieces_list

        if where_row == self.row and where_col == self.col:
            return False

        rook1 = find_piece(self.row, 0)
        rook2 = find_piece(self.row, 7)
        where_to_square = find_piece(where_row, where_col, pieces)
        if (-1 <= (where_row - self.row) <= 1 and -1 <= (where_col - self.col) <= 1) or (
                where_col + 2 and where_row == self.row) or (
                where_col - 2 and where_row == self.row) and (
                (isinstance(rook1, Rook) and not rook1.moved) or (isinstance(rook2, Rook) and not rook2.moved) and (
                self.is_able_to_castle(rook1) or self.is_able_to_castle(rook2))):
            # print("Első if megvan")
            if where_to_square is None or self.is_enemy(where_to_square):
                # print("Na ez itt a kerdes.")
                return True
        # print("Nem megyek be az if-be sajnos.")
        return False

    def get_all_legal_moves(self) -> List[Optional[Tuple[int, int]]]:
        moves = [(self.row - 1, self.col - 1), (self.row - 1, self.col), (self.row - 1, self.col + 1),
                 (self.row, self.col - 1), (self.row, self.col + 1), (self.row + 1, self.col - 1),
                 (self.row + 1, self.col), (self.row + 1, self.col + 1), (self.row, self.col + 2),
                 (self.row, self.col - 2)]

        for move in moves:
            if (move[0] < 0 or move[0] > 7) or (move[1] < 0 or move[1] > 7):
                moves.remove(move)  # todo: remélem ez megoldja a gondokat.(megoldotta)

        return [move for move in moves if self.is_legal_move(move[0], move[1])]

    def is_in_check(self, pieces=None):
        if pieces is None:
            pieces = pieces_list

        for piece in pieces:
            if self.is_enemy(piece) and piece.is_legal_move(self.row, self.col):
                return True

        return False

    def is_able_to_castle(self, rook: 'Rook'):
        if self.moved or rook.moved:
            return False

        if self.is_in_check():
            return False

        if is_square_under_attack(self.row, self.col + 1):
            return False
        if is_square_under_attack(self.row, self.col + 2):
            return False
        if is_square_under_attack(self.row, self.col - 1):
            return False
        if is_square_under_attack(self.row, self.col - 2):
            return False

        start_col = min(self.col, rook.col) + 1
        end_col = max(self.col, rook.col)

        # Ellenőrzés, hogy az összes mező üres-e és nincs-e támadás alatt közöttük
        for col in range(start_col, end_col):
            if find_piece(self.row, col) or is_square_under_attack(self.row, col):
                return False

        return True

    def __str__(self) -> str:
        return f"King" if self._is_white else f"king"


class Queen(Piece):
    def __init__(self, row: int, col: int, is_white: bool):
        super().__init__(row, col, is_white)

    def is_legal_move(self, where_row: int, where_col: int, pieces=None, handle_check: bool = True) -> bool:
        handle_check_result = super().is_legal_move(where_row, where_col, handle_check=handle_check)

        if not handle_check_result:
            return False

        if pieces is None:
            pieces = pieces_list

        if (abs(where_row - self.row) == abs(where_col - self.col)) or (where_row == self.row or where_col == self.col):
            if where_row > self.row:
                next_row = 1
            elif where_row == self.row:
                next_row = 0
            else:
                next_row = -1
            if where_col > self.col:
                next_col = 1
            elif where_col == self.col:
                next_col = 0
            else:
                next_col = -1

            copy_row = self.row
            copy_col = self.col

            where_to_square = find_piece(where_row, where_col, pieces)

            while (copy_row != where_row or copy_col != where_col):
                copy_row += next_row
                copy_col += next_col
                if copy_row == where_row and copy_col == where_col:
                    if where_to_square is None or self.is_enemy(where_to_square):
                        return True
                    else:
                        return False
                if find_piece(copy_row, copy_col, pieces) is not None:
                    return False

        return False

    def __str__(self) -> str:
        return f"Queen" if self._is_white else f"queen"
