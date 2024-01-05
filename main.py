from __future__ import annotations
import pygame
import asyncio
import string
from typing import List, Dict, Type
import random

class Game:
    def __init__(self, answer_object: AnswerObject, event_object: TextObject) -> None:
        self.answer = answer_object
        self.event = event_object
        self.freeze_input = False
        self.freeze_timeout = 400 # milliseconds
        self.word_list = []
        self.game_ended = False
        self.guessed_letters = []
        self.current_menu = None
        self.letter_buttons: List[LetterButton] = []
        self.menu_object_list: Dict[str, Dict[str, List[Type[LetterButton]]]] = {
            PLAY_MENU: {},
            MAIN_MENU: {}
            }

        self.add_object(PLAY_MENU, answer_object)
        self.add_object(PLAY_MENU, event_object)
        self.add_object(PLAY_MENU, answer_object.guesses_left_object)
        self.add_object(PLAY_MENU, answer_object.guessed_letters_object)

        self.create_letter_buttons()

    def reposition_objects(self, screen_size):
        self.reposition_menu_objects(screen_size)
        self.reposition_text_objects(screen_size)
        self.reposition_letter_buttons(screen_size)

    def reposition_text_objects(self, screen_size):
        screen_size_x, screen_size_y = screen_size
        self.answer.guesses_left_object.topleft = 30, 20
        self.answer.guessed_letters_object.center = screen_size_x // 2, screen_size_y * 0.3
        self.answer.center = screen_size_x // 2, screen_size_y * 0.4
        self.event.center = screen_size_x // 2, screen_size_y * 0.2

    def reposition_menu_objects(self, screen_size):
        screen_size_x, screen_size_y = screen_size
        for menu in self.menu_object_list.values():
            for object_list in menu.values():
                for object in object_list:
                    print(f"{object.id = }")
                    if object.id == START_BUTTON_ID:
                        object.rect.center = screen_size_x // 2, screen_size_y // 2 - 100
                        print(f"{object.rect.center = }")
                    if object.id == BACK_BUTTON_ID:
                        object.rect.topright = screen_size_x - 10, 20
                    if object.id == LOGO_ID:
                        logo_object.center = screen_size_x // 2, 100
        

    def create_letter_buttons(self):
        for letter in string.ascii_uppercase:
            new_letter = LetterButton(letter, letter, LETTER_BUTTON_FONT)
            self.add_object(PLAY_MENU, new_letter)
            self.letter_buttons.append(new_letter)

    def set_word_selection(self, word_list):
        self.word_list = word_list

    def get_objects(self, object_type = None):
        if object_type is None:
            return [object for values in self.menu_object_list[self.current_menu].values() for object in values]
        if object_type in self.menu_object_list[self.current_menu]:
            return [object for object in self.menu_object_list[self.current_menu][object_type]]
        return None

    def to_main_menu(self):
        self.current_menu = MAIN_MENU

    def start_new_game(self):
        self.game_ended = False
        self.current_menu = PLAY_MENU
        self.event.set_text('')
        self.answer.set_answer(random.choice(self.word_list))
        for object in self.letter_buttons:
            object.change_button_state(LETTER_BUTTON_UNPRESSED)

    def draw(self, screen):
        for object_list in self.menu_object_list[self.current_menu].values():
            for object in object_list:
                object.draw(screen)

    def get_letter_button(self, letter: str):
        letter = letter.upper()
        return [letter_button for letter_button in self.letter_buttons if letter_button.letter.upper() == letter][0]

    def reposition_letter_buttons(self, screen_size):
        keyboard_rect = create_keyboard_zone(screen_size)
        letter_counter = 0
        margin_y = 5
        background_image_size = letter_button_unpressed_scaled.get_size()
        margin_x = 5 + (background_image_size[0] / 2)
        letter_min_x_spacing = 5
        letters_per_row = (keyboard_rect.size[0] - margin_x * 2) // (max(background_image_size[0], letter_min_x_spacing))
        letter_row = 0
        letter_column = 0
        letter_x_spacing = (keyboard_rect.size[0] - margin_x * 2) / (letters_per_row - 1)
        letter_min_y_spacing = 5
        y_space = (keyboard_rect.size[1] - margin_y * 2)
        columns = y_space // (max(background_image_size[0], letter_min_y_spacing))
        letter_y_spacing = (keyboard_rect.size[1] - margin_y * 2) // columns
        print(f"{letter_y_spacing = }")

        for letter_button in self.letter_buttons:
            letter_button.rect.midtop = letter_column * letter_x_spacing + (keyboard_rect.topleft[0] + margin_x), letter_row * letter_y_spacing + (keyboard_rect.topleft[1] + margin_y)
            letter_counter += 1
            letter_column += 1
            if letter_counter % letters_per_row == 0:
                letter_row += 1
                letter_column = 0
                more_space_than_letters_left = len(self.letter_buttons) - letter_counter < letters_per_row
                if more_space_than_letters_left:
                    next_pos = (letters_per_row - (len(self.letter_buttons) - letter_counter)) // 2 # skip towards center
                    letter_column = next_pos

    def add_object(self, game_state, object: GameObject):
        if object.object_type not in self.menu_object_list[game_state]:
            self.menu_object_list[game_state][object.object_type] = []
        self.menu_object_list[game_state][object.object_type].append(object)

    def game_won(self):
        self.event.set_text("Game won!", CORRECT_COLOR)
        self.game_ended = True
        self.freeze_input = True
        pygame.time.set_timer(SHORT_PAUSE_AFTER_WINNING, self.freeze_timeout, 1)

    def game_lost(self):
        self.event.set_text("Game lost!", WRONG_COLOR)
        self.game_ended = True
        self.freeze_input = True
        pygame.time.set_timer(SHORT_PAUSE_AFTER_WINNING, self.freeze_timeout, 1)

class GameObject:
    def __init__(self, id: str) -> None:
        self.id = id
        self.rect: pygame.Rect = None
        self.surface: pygame.Surface = None
        self.object_type = None

    def draw(self, screen: pygame.Surface):
        if self.surface is not None and self.rect is not None:
            screen.blit(self.surface, self.rect)

    def set_rect(self, rect: pygame.Rect):
        self.rect = rect

    def set_surface(self, surface: pygame.Surface):
        self.surface = surface

class NonInteractiveObject(GameObject):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.object_type = NON_INTERACTIVE_OBJECT_TYPE
        self.center = None
        self.topleft = None

class ImageObject(NonInteractiveObject):
    def __init__(self, id, image) -> None:
        super().__init__(id)
        self.surface = image

    def draw(self, screen):
        if self.surface is not None and self.center is not None:
            surface_rect = self.surface.get_rect()
            surface_rect.center = self.center
            screen.blit(self.surface, surface_rect)
        elif self.surface is not None and self.topleft is not None:
            surface_rect = self.surface.get_rect()
            surface_rect.topleft = self.topleft
            screen.blit(self.surface, surface_rect)

class TextObject(NonInteractiveObject):
    def __init__(self, id, font: pygame.font.Font, color = None) -> None:
        super().__init__(id)
        self.text = ''
        self.font = font
        self.color = color
        self.temp_color = None
        self.center = None
        self.topleft = None
        self.alpha = None

    def set_text(self, text, color = None):
        self.text = text
        self.temp_color = color

        self.surface = self.font.render(text, True, self.color)
        self.rect = self.surface.get_rect()
        self._update_surface()
        
    def change_color(self, color, alpha = None):
        self.color = color
        if alpha is not None:
            self.alpha = alpha
        self._update_surface()

    def _update_surface(self):
        color = self.temp_color if self.temp_color is not None else self.color
        self.surface = self.font.render(self.text, True, color)
        if self.alpha is not None:
            self.surface.set_alpha(self.alpha)

    def draw(self, screen):
        if self.surface is not None and self.center is not None:
            surface_rect = self.surface.get_rect()
            surface_rect.center = self.center
            screen.blit(self.surface, surface_rect)
        elif self.surface is not None and self.topleft is not None:
            surface_rect = self.surface.get_rect()
            surface_rect.topleft = self.topleft
            screen.blit(self.surface, surface_rect)

class AnswerObject(TextObject):
    def __init__(self, id, font: pygame.font.Font, color, guesses_left_object: TextObject, guessed_letters_object: TextObject) -> None:
        super().__init__(id, font, color)
        self.guesses_left_object = guesses_left_object
        self.guessed_letters_object = guessed_letters_object
        self.draw_text = ''
        self.max_wrong_guesses = 9
        self.wrong_guesses = 0
        self.guesses_left_text = f"Wrong guesses left: "

    def set_answer(self, answer: str):
        self.text = answer
        self.draw_text = ''.join(['_' if letter in string.ascii_uppercase else letter for letter in answer.upper()])
        self.temp_color = None
        self.guessed_letters_object.set_text('')
        self.wrong_guesses = 0
        self.guesses_left_object.set_text(self.guesses_left_text + str(self.max_wrong_guesses - self.wrong_guesses))
        self._update_surface()

    def set_text(self, text, color=None):
        raise NotImplementedError("Setting text/answer to AnswerObject is used with set_answer")
        
    def _update_surface(self):
        color = self.temp_color if self.temp_color is not None else self.color
        self.surface = self.font.render(self.draw_text, True, color)
        

    def check_letter(self, letter: str): # Returns True if word is solved, False if not
        letter = letter.upper()
        guessed_string = ''
        correct_answer = self.text.upper()
        guessed_letters = self.guessed_letters_object.text

        if letter in guessed_letters:
            game.event.set_text(f"Already guessed '{letter}'")
            return
        self.guessed_letters_object.set_text(guessed_letters + letter)
        guessed_letters = self.guessed_letters_object.text
        letter_button = game.get_letter_button(letter)
        if letter not in correct_answer:
            color = WRONG_COLOR
            self.wrong_guesses += 1
            self.guesses_left_object.set_text(self.guesses_left_text + str(self.max_wrong_guesses - self.wrong_guesses))
            letter_button.change_button_state(LETTER_BUTTON_PRESSED_INCORRECT)
            game.event.set_text(f"'{letter}' was not found!", color)
            if self.wrong_guesses >= self.max_wrong_guesses:
                game.game_lost()
            return
        
        color = CORRECT_COLOR
        letter_button.change_button_state(LETTER_BUTTON_PRESSED_CORRECT)
        game.event.set_text(f"'{letter}' was found!", color)
    
        print(f"{correct_answer = }")
        for letter in correct_answer:
            if letter not in guessed_letters and letter in string.ascii_uppercase:
                guessed_string += '_'
            else:
                guessed_string += letter

        print(f"{guessed_string = }")
        self.draw_text = guessed_string

        if guessed_string == correct_answer:
            game.game_won()
            

        self._update_surface()

class ButtonObject(GameObject):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.object_type = BUTTON_OBJECT_TYPE
        self.button_function = None

    def activate(self):
        raise NotImplementedError

class MenuButton(ButtonObject):
    def __init__(self, id, surface, rect, button_function) -> None:
        super().__init__(id)
        self.surface = surface
        self.rect = rect
        self.button_function = button_function

    def activate(self):
        self.button_function()

class LetterButton(ButtonObject):
    def __init__(self, id, letter, font: pygame.font.Font) -> None:
        super().__init__(id)
        self.object_type = BUTTON_OBJECT_TYPE
        self.state = 0
        self.image_list = {
            LETTER_BUTTON_UNPRESSED: letter_button_unpressed_scaled.copy(),
            LETTER_BUTTON_PRESSED_CORRECT: letter_button_pressed_correct_scaled.copy(),
            LETTER_BUTTON_PRESSED_INCORRECT: letter_button_pressed_incorrect_scaled.copy()
            }
        self.background_image = self.image_list[self.state]
        self.letter: str = letter
        self.font = font
        self.color = BLACK_COLOR
        self.letter_surface = font.render(letter, True, self.color)
        self.rect = self.background_image.get_rect()
        self.surface = None
        self.pressed_alpha = {
            LETTER_BUTTON_UNPRESSED: 255,
            LETTER_BUTTON_PRESSED_CORRECT: 150,
            LETTER_BUTTON_PRESSED_INCORRECT: 100
            }

        self._update_surface()

    def change_button_state(self, state_number): # 0 for unpressed state, 1 for correct pressed, 2 for incorrect pressed
        self.state = state_number
        self._update_surface()

    def _update_surface(self):
        self.background_image = self.image_list[self.state]
        self.letter_surface = self.font.render(self.letter, True, self.color)
        letter_surface_rect = self.letter_surface.get_rect()
        letter_surface_rect.center = self.background_image.get_rect().center
        self.surface = self.background_image

        self.surface.blit(self.letter_surface, letter_surface_rect)

        self.surface.set_alpha(self.pressed_alpha[self.state])

    def activate(self):
        game.answer.check_letter(self.letter)

def create_keyboard_zone(screen_size):
    screen_size_x, screen_size_y = screen_size
    minimum_landscape_keyboard_x_size = 450
    maximum_landscape_keyboard_x_size = 600
    minimum_portrait_keyboard_x_size = 300
    maximum_portrait_keyboard_x_size = 450
    rotate_to_portrait = screen_size_x < screen_size_y
    if rotate_to_portrait:
        keyboard_width = min(max(screen_size_x * 0.75, minimum_portrait_keyboard_x_size), maximum_portrait_keyboard_x_size)
        keyboard_height = screen_size_y * 0.5
        bot_y_margin = 50
        rect_size = keyboard_width, keyboard_height
        keyboard_rect = pygame.Rect(0, 0, *rect_size)
        keyboard_rect.midbottom = screen_size_x // 2, screen_size_y - bot_y_margin
        print(f"Portrait: {screen_size = }")
    else:
        keyboard_width = min(max(screen_size_x * 0.75, minimum_landscape_keyboard_x_size), maximum_landscape_keyboard_x_size)
        keyboard_height = screen_size_y * 0.4
        bot_y_margin = 50
        rect_size = keyboard_width, keyboard_height
        keyboard_rect = pygame.Rect(0, 0, *rect_size)
        keyboard_rect.midbottom = screen_size_x // 2, screen_size_y - bot_y_margin
        print(f"Landscape: {screen_size = }")

    return keyboard_rect

def read_wordlist(file_name):
    wordlist = []
    with open(file_name, "r") as openfile:
        for line in openfile:
            word = line.rstrip()
            wordlist.append(word)

    return wordlist

def menu_action(event, game_state):
    event_key = event.key
    if event_key == pygame.K_ESCAPE and game_state == PLAY_MENU:
        game.to_main_menu()
        return True
    if event_key == pygame.K_RETURN and game_state == MAIN_MENU:
        game.start_new_game()
        return True
    
    return False

async def main():
    list_of_words = read_wordlist(wordlist_file)
    game.set_word_selection(list_of_words)

    game.freeze_input = False

    running = True

    while running:
        events = pygame.event.get()
        mousepos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.VIDEORESIZE:
                game.reposition_objects(screen.get_size())

            if game.freeze_input and event.type == SHORT_PAUSE_AFTER_WINNING:
                game.freeze_input = False
                game.answer.guesses_left_object.set_text("Continue...")

            if game.freeze_input: # I want to introduce short pause so people don't accidentally continue after pressing multiple buttons at end of the game
                continue

            if event.type == pygame.KEYDOWN:
                event_key = event.key
                if game.game_ended: # make game continue after winning only once user gives input
                    game.start_new_game()
                    continue

                if not menu_action(event, game.current_menu):
                    if game.current_menu == PLAY_MENU:
                        try:
                            key_upper = chr(event_key).upper()
                            if key_upper in string.ascii_uppercase:
                                    letter_button = game.get_letter_button(key_upper)
                                    if letter_button is not None:
                                        letter_button.activate()
                        except:
                            print(f"Invalid {event_key = }")

            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.game_ended: # make game continue after winning only once user gives input
                    game.start_new_game()
                    continue

                list_of_objects = game.get_objects(BUTTON_OBJECT_TYPE)
                if list_of_objects is not None:
                    for object in game.get_objects(BUTTON_OBJECT_TYPE):
                        if object.rect.collidepoint(mousepos):
                            object.activate()

        screen.fill(LIGHT_BLUE_COLOR)

        game.draw(screen)

        pygame.display.flip()

        clock.tick(TICK_SPEED)

        await asyncio.sleep(0)

if __name__ == "__main__":
    pygame.init()
    """
    screen_size_x = 1024
    screen_size_y = 768
    """
    
    screen_size_x = 1024
    screen_size_y = 768

    screen = pygame.display.set_mode((screen_size_x, screen_size_y), pygame.RESIZABLE)

    """
    display_info = pygame.display.Info()
    if screen_size_x <= display_info.current_w and screen_size_y <= display_info.current_h:
        screen = pygame.display.set_mode((screen_size_x, screen_size_y), pygame.RESIZABLE)
    else:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.RESIZABLE)

    screen_size_x, screen_size_y = screen.get_size()
    """


    TICK_SPEED = 60

    # gamestates
    PLAY_MENU = 'play_menu_state'
    MAIN_MENU = 'main_menu_state'

    LIGHT_BLUE_COLOR = (138, 160, 242)
    CORRECT_COLOR = (16, 140, 40)
    WRONG_COLOR = (200, 50, 25)
    BLACK_COLOR = (0, 0, 0)

    # Main game colors
    MAIN_GOLD_BROWN_COLOR = (178, 134, 54)
    MAIN_PURPLE_COLOR = (84, 37, 90)
    
    RESET_ALPHA = 255
    WRONG_LETTER_ALPHA = 100

    BUTTON_OBJECT_TYPE = "button"
    NON_INTERACTIVE_OBJECT_TYPE = "non_interactive"

    LOGO_FONT_SIZE = 100
    DEFAULT_FONT_SIZE = 50
    LETTER_BUTTON_FONT_SIZE = 40
    ANSWER_FONT_SIZE = 40
    EVENT_FONT_SIZE = 20
    GUESSES_LEFT_SIZE = 20
    GUESSED_LETTERS_SIZE = 20

    FONT_FILE = "MartianMono-VariableFont_wdth,wght.ttf"
    LOGO_FONT_FILE = "Poppins-Medium.ttf"

    ARIAL_BLACK = 'arialblack'

    LOGO_FONT = pygame.font.Font(LOGO_FONT_FILE, LOGO_FONT_SIZE)
    DEFAULT_FONT = pygame.font.Font(FONT_FILE, DEFAULT_FONT_SIZE)
    LETTER_BUTTON_FONT = pygame.font.SysFont(ARIAL_BLACK, LETTER_BUTTON_FONT_SIZE)
    ANSWER_FONT = pygame.font.Font(FONT_FILE, ANSWER_FONT_SIZE)
    EVENT_FONT = pygame.font.Font(FONT_FILE, EVENT_FONT_SIZE)
    GUESSES_LEFT_FONT = pygame.font.Font(FONT_FILE, GUESSES_LEFT_SIZE)
    GUESSED_LETTERS_FONT = pygame.font.Font(FONT_FILE, GUESSED_LETTERS_SIZE)

    oprim_logo = pygame.image.load("OpriM_logo.jpg").convert_alpha()
    oprim_logo_scaled = pygame.transform.rotozoom(oprim_logo, 0, 0.5)
    
    start_game = pygame.image.load("temp_start.png").convert_alpha()
    start_game_scaled = pygame.transform.smoothscale(start_game, (200, 100))

    back_button = pygame.image.load("temp_back.png").convert_alpha()
    back_button_scaled = pygame.transform.smoothscale(back_button, (150, 75))

    letter_button_size = LETTER_BUTTON_FONT_SIZE * 1.75

    LETTER_BUTTON_UNPRESSED = 0
    LETTER_BUTTON_PRESSED_CORRECT = 1
    LETTER_BUTTON_PRESSED_INCORRECT = 2

    letter_button_unpressed = pygame.image.load("letter_button_unpressed.png").convert_alpha()
    letter_button_unpressed_scaled = pygame.transform.smoothscale(letter_button_unpressed, (letter_button_size, letter_button_size))

    letter_button_pressed_incorrect = pygame.image.load("letter_button_pressed_incorrect.png").convert_alpha()
    letter_button_pressed_incorrect_scaled = pygame.transform.smoothscale(letter_button_pressed_incorrect, (letter_button_size, letter_button_size))

    letter_button_pressed_correct = pygame.image.load("letter_button_pressed_correct.png").convert_alpha()
    letter_button_pressed_correct_scaled = pygame.transform.smoothscale(letter_button_pressed_correct, (letter_button_size, letter_button_size))


    wordlist_file = "wordlist.txt"

    clock = pygame.time.Clock()
    
    SHORT_PAUSE_AFTER_WINNING = pygame.USEREVENT

    guesses_left_object = TextObject("guesses_left", GUESSES_LEFT_FONT, BLACK_COLOR)

    guessed_letters_object = TextObject("guessed_letters", GUESSED_LETTERS_FONT, BLACK_COLOR)

    answer_object = AnswerObject("answer", ANSWER_FONT, BLACK_COLOR, guesses_left_object, guessed_letters_object)

    event_object = TextObject("event", EVENT_FONT, BLACK_COLOR)

    game = Game(answer_object, event_object)

    START_BUTTON_ID = 'start_button'
    BACK_BUTTON_ID = 'back_button'
    LOGO_ID = 'logo'

    start_game_scaled_rect = start_game_scaled.get_rect()
    start_game_scaled_rect.center = screen_size_x // 2, screen_size_y // 2 - 100
    start_button_function = game.start_new_game
    start_button = MenuButton(START_BUTTON_ID, start_game_scaled, start_game_scaled_rect, start_button_function)
    
    back_button_scaled_rect = back_button_scaled.get_rect()
    back_button_scaled_rect.topright = screen_size_x - 10, 20
    back_button_function = game.to_main_menu
    back_button = MenuButton(BACK_BUTTON_ID, back_button_scaled, back_button_scaled_rect, back_button_function)
    
    logo_object = ImageObject(LOGO_ID, oprim_logo_scaled)

    game.add_object(MAIN_MENU, start_button)
    game.add_object(MAIN_MENU, logo_object)
    game.add_object(PLAY_MENU, back_button)

    game.reposition_objects((screen_size_x, screen_size_y))

    game.current_menu = MAIN_MENU

    asyncio.run(main())