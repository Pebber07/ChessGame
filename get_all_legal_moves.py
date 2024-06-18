def get_all_legal_moves_pawn(x, y, color=True):
    legal_moves_list = []

    if color:
        legal_moves_list.append((x - 1, y - 1))
        legal_moves_list.append((x - 1, y))
        legal_moves_list.append((x - 2, y))
        legal_moves_list.append((x - 1, y + 1))
    else:
        legal_moves_list.append((x + 1, y))
        legal_moves_list.append((x + 2, y))
        legal_moves_list.append((x + 1, y - 1))
        legal_moves_list.append((x + 1, y + 1))

    return legal_moves_list


def get_all_legal_moves_rook(x, y):
    legal_moves_list = []

    for a in range(0, 8):
        legal_moves_list.append((x, a))
    for b in range(0, 8):
        legal_moves_list.append((b, y))

    while (x, y) in legal_moves_list:
        legal_moves_list.remove((x, y))
    return legal_moves_list


def get_all_legal_moves_knight(x, y):
    legal_moves_list = []

    legal_moves_list.append((x - 2, y - 1))
    legal_moves_list.append((x - 1, y - 2))
    legal_moves_list.append((x + 1, y - 2))
    legal_moves_list.append((x + 2, y - 1))
    legal_moves_list.append((x - 2, y + 1))
    legal_moves_list.append((x - 1, y + 2))
    legal_moves_list.append((x + 1, y + 2))
    legal_moves_list.append((x + 2, y + 1))

    return legal_moves_list


def get_all_legal_moves_bishop(x, y):
    legal_moves_list = []

    a = x
    b = y
    # bal felső sarok
    while a > 0 and b > 0:
        a -= 1
        b -= 1
        legal_moves_list.append((a, b))

    a = x
    b = y
    # jobb felső sarok
    while a > 0 and b < 7:
        a -= 1
        b += 1
        legal_moves_list.append((a, b))

    a = x
    b = y
    # bal alsó sarok
    while a < 7 and b > 0:
        a += 1
        b -= 1
        legal_moves_list.append((a, b))

    a = x
    b = y
    # jobb alsó sarok
    while a < 7 and b < 7:
        a += 1
        b += 1
        legal_moves_list.append((a, b))
    return legal_moves_list


def get_all_legal_moves_queen(x, y):
    legal_moves_list = []

    # bastya
    for a in range(0, 8):
        legal_moves_list.append((x, a))
    for b in range(0, 8):
        legal_moves_list.append((b, y))

    # futo
    a = x
    b = y
    # bal felső sarok
    while a > 0 and b > 0:
        a -= 1
        b -= 1
        legal_moves_list.append((a, b))

    a = x
    b = y
    # jobb felső sarok
    while a > 0 and b < 7:
        a -= 1
        b += 1
        legal_moves_list.append((a, b))

    a = x
    b = y
    # bal alsó sarok
    while a < 7 and b > 0:
        a += 1
        b -= 1
        legal_moves_list.append((a, b))

    a = x
    b = y
    # jobb alsó sarok
    while a < 7 and b < 7:
        a += 1
        b += 1
        legal_moves_list.append((a, b))

    a = x
    b = y
    while (x, y) in legal_moves_list:
        legal_moves_list.remove((x, y))

    return legal_moves_list


def get_all_legal_moves_king(x, y):
    legal_moves_list = []

    legal_moves_list.append((x - 1, y - 1))
    legal_moves_list.append((x - 1, y))
    legal_moves_list.append((x - 1, y + 1))
    legal_moves_list.append((x, y - 1))
    legal_moves_list.append((x, y + 1))
    legal_moves_list.append((x + 1, y - 1))
    legal_moves_list.append((x + 1, y))
    legal_moves_list.append((x + 1, y + 1))

    return legal_moves_list

# Test
# print("Gyalog tesztelése: (5,5)")
# print(get_all_legal_moves_pawn(5, 5))
# print(get_all_legal_moves_pawn(1, 2, False))
# print("Bástya tesztelése: (5,5)")
# print(get_all_legal_moves_rook(5, 5))
# print("Huszár tesztelése: (4,2)")
# print(get_all_legal_moves_knight(4, 2))
# print("Futó tesztelése: (4,2)")
# print(get_all_legal_moves_bishop(4, 2))
# print("Vezér tesztelése: (4,2)")
# print(get_all_legal_moves_queen(4, 2))
# print("Király tesztelése: (4,2)")
# print(get_all_legal_moves_king(4, 2))
# print("Na még egy teszt királyra: (7,0) (értelmezésre szorul)")
# print(get_all_legal_moves_king(7, 0))

# print("Na még egy teszt vezérre: (7,0)")
# print(get_all_legal_moves_queen(7, 0))
