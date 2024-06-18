import pygame

import application

pygame.init()


class Button:
    """Universal button with text."""

    def __init__(self, start_x, start_y, width, height, background_color, text, text_size, text_color, is_visible,
                 onclick):
        if not callable(onclick):
            raise TypeError(f"Onclick must be callable.")

        self.start_x, self.start_y = start_x, start_y
        self.width, self.height = width, height
        self._background_color = background_color

        self.button = pygame.Surface((width, height))
        self.is_visible = is_visible
        self.text = text
        self.text_color = text_color
        self.text_size = text_size
        self.set_text(text)

        self.onclick_method = onclick
        self.button.fill(self._background_color)
        self.set_text(text)
        self.selected = False  # kijelölés miatt fog kelleni

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, color):
        self._background_color = color
        self.button.fill(self._background_color)
        self.set_text(self.text)

    def get_end_pos(self):
        return self.start_x + self.width, self.start_y + self.height

    def set_text(self, text):
        self.button.fill(self.background_color)
        self.button.fill(self._background_color)
        font_style = pygame.font.SysFont("arial", self.text_size)
        rendered_text = font_style.render(str(text), True, self.text_color)
        text_start_x = (self.width - rendered_text.get_width()) // 2
        text_start_y = (self.height - rendered_text.get_height()) // 2

        self.button.blit(rendered_text, (text_start_x, text_start_y))

    def draw(self, screen):
        if self.is_visible:
            screen.blit(self.button, (self.start_x, self.start_y))

    def onclick(self):
        if self.is_visible:
            self.selected = not self.selected  # váltogatás
            self.background_color = (245, 215, 66) if self.selected else (72, 245, 66)  # háttérszín váltása
            self.onclick_method(self)


pygame.display.set_caption("Multiple screens prototype")

actual_screen = "menu"
screen = pygame.display.set_mode((800, 600))

font = pygame.font.SysFont("Comic-sans", 36)
welcome_text = font.render('Welcome to our chess game!', True, (255, 255, 255))  # renderelés


def event_handler(button):
    group = time_buttons if button in time_buttons else color_buttons if button in color_buttons else None  # uj, None nem biztos, hogy kell
    if group:
        for butn in group:
            if butn != button:
                butn.selected = False
                butn.background_color = (72, 245, 66)


button = Button(50, 50, 200, 70, (0, 0, 0), "Valami", 25, (100, 100, 200), True, event_handler)
three_button = Button(100, 220, 150, 70, (72, 245, 66), "3 + 0", 25, (100, 100, 200), True, event_handler)
five_button = Button(300, 220, 150, 70, (72, 245, 66), "5 + 0", 25, (100, 100, 200), True, event_handler)
ten_button = Button(500, 220, 150, 70, (72, 245, 66), "10 + 0", 25, (100, 100, 200), True, event_handler)
white_button = Button(200, 350, 150, 70, (72, 245, 66), "White", 25, (100, 100, 200), True, event_handler)
black_button = Button(420, 350, 150, 70, (72, 245, 66), "Black", 25, (100, 100, 200), True, event_handler)
start_button = Button(300, 460, 150, 70, (72, 245, 66), "Start", 25, (100, 100, 200), True, event_handler)

time_buttons = [three_button, five_button, ten_button]  # idő csoport
color_buttons = [white_button, black_button]  # szín csoport

# első gomb legyen kijelölve
time_buttons[0].selected = True  # uj
color_buttons[0].selected = True  # uj
time_buttons[0].background_color = (245, 215, 66)  # uj
color_buttons[0].background_color = (245, 215, 66)  # uj

buttons = [button, three_button, five_button, ten_button, white_button, black_button, start_button]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

        if actual_screen == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for btn in buttons:
                    if btn.start_x <= mouse_pos[0] <= btn.start_x + btn.width and \
                            btn.start_y <= mouse_pos[1] <= btn.start_y + btn.height:
                        btn.onclick()

    if actual_screen == "menu":
        screen.fill((245, 102, 66))
        button.draw(screen)
        three_button.draw(screen)
        five_button.draw(screen)
        ten_button.draw(screen)
        white_button.draw(screen)
        black_button.draw(screen)
        start_button.draw(screen)
        screen.blit(welcome_text,
                    (400 - welcome_text.get_width() // 2, 180 - welcome_text.get_height() // 2))  # szöveg kirajzolása
    elif actual_screen == "game":
        screen.fill((20, 240, 50))

    pygame.display.update()
