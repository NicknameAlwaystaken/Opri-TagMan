from __future__ import annotations
import pygame
import asyncio
import string
from typing import List, Dict, Type
import random

class Game:
    def __init__(self, answer_object: AnswerObject, event_object: TextObject, heart_object: HeartObject) -> None:
        self.answer = answer_object
        self.event = event_object
        self.heart_object = heart_object
        self.freeze_input = False
        self.freeze_timeout = 400 # milliseconds
        self.word_list = []
        self.game_ended = False
        self.guessed_letters = []
        self.current_menu = MAIN_MENU
        self.letter_buttons: List[LetterButton] = []
        self.menu_object_list: Dict[str, Dict[str, List[Type[LetterButton]]]] = {
            PLAY_MENU: {},
            MAIN_MENU: {}
            }
        self.transition_screen = None
        self.is_menu_transitioning = False
        self.transitioning_to = None
        self.transition_time = 1000 # milliseconds
        self.transition_start_time = 0 # milliseconds

        self.add_object(PLAY_MENU, answer_object)
        self.add_object(PLAY_MENU, event_object)
        self.add_object(PLAY_MENU, heart_object)
        self.add_object(PLAY_MENU, answer_object.guessed_letters_object)

        self.create_letter_buttons()

    def finish_transitioning(self):
        self.is_menu_transitioning = False
        self.freeze_input = False
        pygame.time.set_timer(PAUSE_AFTER_WIN_TIMER, 0, 1)
        self.current_menu = self.transitioning_to
        if self.current_menu == PLAY_MENU:
            self.start_new_game()

    def reposition_objects(self, screen_size):
        self.reposition_menu_objects(screen_size)
        self.reposition_text_objects(screen_size)
        self.reposition_letter_buttons(screen_size)

    def reposition_text_objects(self, screen_size):
        screen_size_x, screen_size_y = screen_size
        
        if screen_size_x >= screen_size_y: # landscape
            guessed_letters_pos = 0.33
            answer_pos = 0.35
            event_pos = answer_pos # left of answer_pos
        else: # portrait
            guessed_letters_pos = 0.23
            answer_pos = 0.25
            event_pos = guessed_letters_pos
        event_screen_x_pos = 0.2
        #self.answer.guessed_letters_object.center = screen_size_x // 2, screen_size_y * guessed_letters_pos
        self.answer.center = screen_size_x // 2, screen_size_y * answer_pos
        #self.event.center = screen_size_x * event_screen_x_pos, screen_size_y * event_pos 

    def reposition_menu_objects(self, screen_size):
        screen_size_x, screen_size_y = screen_size
        top_margin = 100
        for menu in self.menu_object_list.values():
            for object_list in menu.values():
                for object in object_list:
                    if object.id == START_BUTTON_ID:
                        object.rect.center = screen_size_x // 2, screen_size_y // 2
                    elif object.id == BACK_BUTTON_ID:
                        object.rect.topright = screen_size_x - 10, top_margin
                    elif object.id == LOGO_MAIN_ID:
                        object.center = screen_size_x // 2, 100
                    elif object.id == LOGO_GAME_ID:
                        object.topleft = 0, 0
                    elif object.id == HEART_ID:
                        object.topleft = 30, top_margin
        
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

    def go_to_menu(self, menu):
        self.start_menu_transition(menu)

    def go_to_main_menu(self):
        # this is to have a static function for buttons like back button, fine till I add more back buttons
        # If I plan to add more back buttons I should definitely give back button the menu as a variable in the class to point to the menu.
        self.go_to_menu(MAIN_MENU)

    def start_menu_transition(self, menu):
        self.transition_screen = pygame.Surface(screen.get_size())
        self.transition_screen.fill(BLACK_COLOR)
        pygame.time.set_timer(TRANSITION_TIMER, self.transition_time, 1)
        self.transition_start_time = pygame.time.get_ticks()
        game.freeze_input = True
        self.is_menu_transitioning = True
        self.transitioning_to = menu

    def start_new_game(self):
        self.game_ended = False
        self.event.set_text('')
        self.answer.set_answer(random.choice(self.word_list))
        self.heart_object.set_max_health(8)
        for object in self.letter_buttons:
            object.change_button_state(BUTTON_UNPRESSED)

    def draw(self, screen: pygame.Surface):
        if self.current_menu in self.menu_object_list:
            for object_list in self.menu_object_list[self.current_menu].values():
                for object in object_list:
                    object.draw(screen)

        if self.is_menu_transitioning and self.transition_screen is not None:
            ticks = (pygame.time.get_ticks() - self.transition_start_time)
            self.transition_screen.set_alpha(255 - (255 * ((self.transition_time - ticks) / self.transition_time)))
            screen.blit(self.transition_screen, self.transition_screen.get_rect())

    def update(self):
        if self.current_menu in self.menu_object_list:
            for object_list in self.menu_object_list[self.current_menu].values():
                for object in object_list:
                    object.update()

    def get_letter_button(self, letter: str):
        letter = letter.upper()
        return [letter_button for letter_button in self.letter_buttons if letter_button.letter.upper() == letter][0]

    def reposition_letter_buttons(self, screen_size):
        keyboard_rect = create_keyboard_zone(screen_size)
        background_image_size = letter_button_unpressed_scaled.get_size()
        # X spacing
        size_multiplier_x = 1.2
        margin_x = 0 
        letters_per_row = (keyboard_rect.size[0] - margin_x * 2) // (background_image_size[0] / size_multiplier_x)
        letter_row = 0
        letter_column = 0
        letter_x_spacing = (keyboard_rect.size[0] - margin_x * 2) / (letters_per_row - 1)
        print(f"{keyboard_rect.size[0] = } {background_image_size[0] = } {letters_per_row = }")
        print(f"{letter_x_spacing = }")

        # Y spacing
        size_multiplier_y = 1.05
        margin_y = 0
        y_space = (keyboard_rect.size[1] - margin_y * 2)
        columns = y_space // (background_image_size[0] / size_multiplier_y)
        letter_y_spacing = (keyboard_rect.size[1] - margin_y * 2) // columns

        letter_counter = 0
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
        pygame.time.set_timer(PAUSE_AFTER_WIN_TIMER, self.freeze_timeout, 1)

    def game_lost(self):
        self.event.set_text("Game lost!", WRONG_COLOR)
        self.game_ended = True
        self.freeze_input = True
        pygame.time.set_timer(PAUSE_AFTER_WIN_TIMER, self.freeze_timeout, 1)

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

    def update(self):
        pass

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

class HeartObject(ImageObject):
    def __init__(self, id, heart_full: pygame.Surface, heart_half: pygame.Surface, heart_empty: pygame.Surface) -> None:
        super().__init__(id, heart_empty)
        self.image_list = {
            HEART_FULL: heart_full.copy(),
            HEART_HALF: heart_half.copy(),
            HEART_EMPTY: heart_empty.copy()
            }
        self.heart_surface = None
        self.health = 0

    def set_max_health(self, max_health):
        self.number_of_hearts = int((max_health / 2) + 0.5)
        self.health = max_health

        self._update_heart_surface()

    def remove_health(self, number):
        self.health -= number
        self._update_heart_surface()

    def get_health(self):
        return self.health

    def _update_heart_surface(self):
        heart_x_spacing = 5
        heart_x_size, heart_y_size = self.image_list[HEART_FULL].get_size()
        self.heart_surface = pygame.Surface(((heart_x_size + heart_x_spacing) * self.number_of_hearts, heart_y_size), pygame.SRCALPHA)
        health = self.health
        heart_index = 0
        heart_type = HEART_EMPTY
        for _ in range(self.number_of_hearts):
            if health >= HEART_FULL:
                health -= HEART_FULL
                heart_type = HEART_FULL

            elif health >= HEART_HALF:
                health -= HEART_HALF
                heart_type = HEART_HALF

            else:
                heart_type = HEART_EMPTY

            heart_image = self.image_list[heart_type]
            heart_image_rect = heart_image.get_rect()
            heart_image_rect.topleft = ((heart_x_size + heart_x_spacing) * heart_index, 0)
            self.heart_surface.blit(heart_image, heart_image_rect)
            heart_index += 1

        self.surface = self.heart_surface

class TextObject(NonInteractiveObject):
    def __init__(self, id, font: pygame.font.Font, color = None) -> None:
        super().__init__(id)
        self.text = ''
        self.font = font
        self.color = color
        self.temp_color = None
        self.center = None
        self.topleft = None
        self.bottomleft = None
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
        elif self.surface is not None and self.bottomleft is not None:
            surface_rect = self.surface.get_rect()
            surface_rect.bottomleft = self.bottomleft
            screen.blit(self.surface, surface_rect)

class AnswerObject(TextObject):
    def __init__(self, id, font: pygame.font.Font, color, guessed_letters_object: TextObject) -> None:
        super().__init__(id, font, color)
        self.guessed_letters_object = guessed_letters_object
        self.draw_text = ''

    def set_answer(self, answer: str):
        self.text = answer
        self.draw_text = ''.join(['_' if letter in string.ascii_uppercase else letter for letter in answer.upper()])
        self.temp_color = None
        self.guessed_letters_object.set_text('')
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
            game.heart_object.remove_health(1)
            letter_button.change_button_state(BUTTON_PRESSED_INCORRECT)
            game.event.set_text(f"'{letter}' not found!", color)
            if game.heart_object.get_health() <= 0:
                game.game_lost()
            return
        
        color = CORRECT_COLOR
        letter_button.change_button_state(BUTTON_PRESSED_CORRECT)
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
        self.state = 0

    def activate(self):
        raise NotImplementedError

class MenuButton(ButtonObject):
    def __init__(self, id, surface_pressed: pygame.Surface, surface_unpressed: pygame.Surface, rect, button_function, button_menu_pointer) -> None:
        super().__init__(id)
        self.rect = rect
        self.button_function = button_function
        self.button_menu_pointer = button_menu_pointer
        self.button_pressed_timer = 500
        self.button_pressed_last_tick = 0
        self.image_list = {
            BUTTON_UNPRESSED: surface_unpressed.copy(),
            BUTTON_PRESSED: surface_pressed.copy()
            }
        self.surface = self.image_list[self.state]

    def update(self):
        if self.state == BUTTON_PRESSED:
            ticks = pygame.time.get_ticks() - self.button_pressed_last_tick
            if ticks >= self.button_pressed_timer:
                self.state = BUTTON_UNPRESSED
                self._update_surface()

    def activate(self):
        self.button_function(self.button_menu_pointer)
        self.state = BUTTON_PRESSED
        self.button_pressed_last_tick = pygame.time.get_ticks()
        self._update_surface()
        
    def _update_surface(self):
        self.surface = self.image_list[self.state]
        
    def change_button_state(self, state_number): # 0 for unpressed state, 1 for correct pressed, 2 for incorrect pressed
        self.state = state_number

class LetterButton(ButtonObject):
    def __init__(self, id, letter, font: pygame.font.Font) -> None:
        super().__init__(id)
        self.object_type = BUTTON_OBJECT_TYPE
        self.image_list = {
            BUTTON_UNPRESSED: letter_button_unpressed_scaled.copy(),
            BUTTON_PRESSED_CORRECT: letter_button_pressed_correct_scaled.copy(),
            BUTTON_PRESSED_INCORRECT: letter_button_pressed_incorrect_scaled.copy()
            }
        self.background_image = self.image_list[self.state]
        self.letter: str = letter
        self.font = font
        self.color = LETTER_BUTTON_COLOR
        self.letter_surface = font.render(letter, True, self.color)
        self.rect = self.background_image.get_rect()
        self.surface = None
        self.pressed_alpha = {
            BUTTON_UNPRESSED: 255,
            BUTTON_PRESSED_CORRECT: 150,
            BUTTON_PRESSED_INCORRECT: 100
            }

        self._update_surface()

    def change_button_state(self, state_number): # 0 for unpressed state, 1 for correct pressed, 2 for incorrect pressed
        self.state = state_number
        self._update_surface()

    def _update_surface(self):
        self.background_image = self.image_list[self.state]
        self.letter_surface = self.font.render(self.letter, True, self.color)
        letter_surface_rect = self.letter_surface.get_rect()
        background_image_center = self.background_image.get_rect().center
        letter_surface_rect.center = (background_image_center[0], background_image_center[1] - 2) # It looks like letters are bit off center, lifting them up by few pixels
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
    maximum_portrait_keyboard_x_size = minimum_landscape_keyboard_x_size
    rotate_to_portrait = screen_size_x < screen_size_y
    if rotate_to_portrait:
        keyboard_width = min(max(screen_size_x * 0.75, minimum_portrait_keyboard_x_size), maximum_portrait_keyboard_x_size)
        keyboard_height = screen_size_y * 0.5
        bot_y_margin = 50
        rect_size = keyboard_width, keyboard_height
        keyboard_rect = pygame.Rect(0, 0, *rect_size)
        keyboard_rect.midbottom = screen_size_x // 2, screen_size_y - bot_y_margin
    else:
        keyboard_width = min(max(screen_size_x * 0.75, minimum_landscape_keyboard_x_size), maximum_landscape_keyboard_x_size)
        keyboard_height = screen_size_y * 0.4
        bot_y_margin = 50
        rect_size = keyboard_width, keyboard_height
        keyboard_rect = pygame.Rect(0, 0, *rect_size)
        keyboard_rect.midbottom = screen_size_x // 2, screen_size_y - bot_y_margin

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
        game.go_to_menu(game_state)
        return True
    if event_key == pygame.K_RETURN and game_state == MAIN_MENU:
        game.go_to_menu(game_state)
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

            if event.type == TRANSITION_TIMER:
                game.finish_transitioning()

            if game.game_ended and event.type == PAUSE_AFTER_WIN_TIMER:
                game.freeze_input = False

            if game.freeze_input: # I want to introduce short pause so people don't accidentally continue after pressing multiple buttons at end of the game
                continue

            if event.type == pygame.KEYDOWN:
                event_key = event.key
                if game.game_ended: # make game continue after winning only once user gives input
                    game.go_to_menu(PLAY_MENU)
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
                    game.go_to_menu(PLAY_MENU)
                    continue

                list_of_objects = game.get_objects(BUTTON_OBJECT_TYPE)
                if list_of_objects is not None:
                    for object in game.get_objects(BUTTON_OBJECT_TYPE):
                        if object.rect.collidepoint(mousepos):
                            object.activate()

        screen.fill(BACKGROUND_COLOR)

        game.update()
        game.draw(screen)

        pygame.display.flip()

        clock.tick(TICK_SPEED)

        await asyncio.sleep(0)

if __name__ == "__main__":
    pygame.init()
    
    screen_size_x, screen_size_y = (1024, 768)

    display_info = pygame.display.Info()
    if screen_size_x <= display_info.current_w and screen_size_y <= display_info.current_h:
        screen = pygame.display.set_mode((screen_size_x, screen_size_y), pygame.RESIZABLE)
    else:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.RESIZABLE)


    TICK_SPEED = 60

    # gamestates
    PLAY_MENU = 'play_menu_state'
    MAIN_MENU = 'main_menu_state'

    LIGHT_BLUE_COLOR = (138, 160, 242)
    CORRECT_COLOR = (16, 140, 40)
    WRONG_COLOR = (200, 50, 25)
    BLACK_COLOR = (0, 0, 0)
    WHITE_COLOR = (255, 255, 255)
    CREAM_COLOR = (255, 253, 208)

    # Main game colors
    MAIN_GOLD_BROWN_COLOR = (178, 134, 54)
    MAIN_PURPLE_COLOR = (84, 37, 90)

    ANSWER_FONT_COLOR = CREAM_COLOR
    ANSWER_FONT_COLOR = MAIN_PURPLE_COLOR
    LETTER_BUTTON_COLOR = CREAM_COLOR

    BACKGROUND_COLOR = WHITE_COLOR

    
    RESET_ALPHA = 255
    WRONG_LETTER_ALPHA = 100

    BUTTON_OBJECT_TYPE = "button"
    NON_INTERACTIVE_OBJECT_TYPE = "non_interactive"

    DEFAULT_FONT_SIZE = 50
    LETTER_BUTTON_FONT_SIZE = 40
    ANSWER_FONT_SIZE = 75
    EVENT_FONT_SIZE = 20
    GUESSED_LETTERS_SIZE = 20

    FONT_FILE = "MartianMono-VariableFont_wdth,wght.ttf"

    ARIAL_BLACK = 'arialblack'

    DEFAULT_FONT = pygame.font.Font(FONT_FILE, DEFAULT_FONT_SIZE)
    LETTER_BUTTON_FONT = pygame.font.SysFont(ARIAL_BLACK, LETTER_BUTTON_FONT_SIZE)
    ANSWER_FONT = pygame.font.Font(FONT_FILE, ANSWER_FONT_SIZE)
    EVENT_FONT = pygame.font.Font(FONT_FILE, EVENT_FONT_SIZE)
    GUESSED_LETTERS_FONT = pygame.font.Font(FONT_FILE, GUESSED_LETTERS_SIZE)

    oprimagazine_logo_original = pygame.image.load("oprimagazine_logo.png").convert_alpha()
    oprimagazine_logo_smallest = pygame.image.load("logo_y_100.png").convert_alpha()

    GAME_TOP_MARGIN = 100
    
    main_menu_logo_scaled = pygame.transform.rotozoom(oprimagazine_logo_original, 0, 0.4)
    logo_y_size = oprimagazine_logo_smallest.get_size()[1]
    game_menu_y_size = 100
    game_menu_scale = 1 / (logo_y_size / game_menu_y_size)
    print(game_menu_scale)
    game_menu_logo_scaled = pygame.transform.rotozoom(oprimagazine_logo_smallest, 0, game_menu_scale)
    
    HEART_FULL = 2
    HEART_HALF = 1
    HEART_EMPTY = 0

    heart_size = (50, 50)
    heart_full = pygame.image.load("full_heart.png").convert_alpha()
    heart_full_scaled = pygame.transform.smoothscale(heart_full, heart_size)
    heart_half = pygame.image.load("half_heart.png").convert_alpha()
    heart_half_scaled = pygame.transform.smoothscale(heart_half, heart_size)
    heart_empty = pygame.image.load("empty_heart.png").convert_alpha()
    heart_empty_scaled = pygame.transform.smoothscale(heart_empty, heart_size)
    
    start_button_size = (800, 500)
    start_button_scale = 3
    start_game_unpressed = pygame.image.load("start_button_unpressed.png").convert_alpha()
    start_game_unpressed_scaled = pygame.transform.smoothscale(start_game_unpressed, (int(start_button_size[0] / start_button_scale), int(start_button_size[1] / start_button_scale)))
    start_game_pressed = pygame.image.load("start_button_pressed.png").convert_alpha()
    start_game_pressed_scaled = pygame.transform.smoothscale(start_game_pressed, (int(start_button_size[0] / start_button_scale), int(start_button_size[1] / start_button_scale)))

    back_button_size = (800, 500)
    back_button_scale = 5
    back_button_unpressed = pygame.image.load("back_button_unpressed.png").convert_alpha()
    back_button_unpressed_scaled = pygame.transform.smoothscale(back_button_unpressed, (int(back_button_size[0] / back_button_scale), int(back_button_size[1] / back_button_scale)))
    back_button_pressed = pygame.image.load("back_button_pressed.png").convert_alpha()
    back_button_pressed_scaled = pygame.transform.smoothscale(back_button_pressed, (int(back_button_size[0] / back_button_scale), int(back_button_size[1] / back_button_scale)))

    letter_button_size = LETTER_BUTTON_FONT_SIZE * 2

    BUTTON_UNPRESSED = 0
    BUTTON_PRESSED_CORRECT = 1 # for letter buttons
    BUTTON_PRESSED_INCORRECT = 2 # for letter buttons
    BUTTON_PRESSED = 3

    letter_button_unpressed = pygame.image.load("letter_button_unpressed.png").convert_alpha()
    letter_button_unpressed_scaled = pygame.transform.smoothscale(letter_button_unpressed, (letter_button_size, letter_button_size))

    letter_button_pressed_incorrect = pygame.image.load("letter_button_pressed_incorrect.png").convert_alpha()
    letter_button_pressed_incorrect_scaled = pygame.transform.smoothscale(letter_button_pressed_incorrect, (letter_button_size, letter_button_size))

    letter_button_pressed_correct = pygame.image.load("letter_button_pressed_correct.png").convert_alpha()
    letter_button_pressed_correct_scaled = pygame.transform.smoothscale(letter_button_pressed_correct, (letter_button_size, letter_button_size))


    wordlist_file = "wordlist.txt"

    clock = pygame.time.Clock()
    
    PAUSE_AFTER_WIN_TIMER = pygame.USEREVENT

    TRANSITION_TIMER = pygame.USEREVENT

    HEART_ID = 'heart'
    ANSWER_ID = 'answer'
    EVENT_ID = 'event'

    guessed_letters_object = TextObject("guessed_letters", GUESSED_LETTERS_FONT, BLACK_COLOR)

    answer_object = AnswerObject(ANSWER_ID, ANSWER_FONT, ANSWER_FONT_COLOR, guessed_letters_object)

    event_object = TextObject(EVENT_ID, EVENT_FONT, BLACK_COLOR)

    heart_object = HeartObject(HEART_ID, heart_full_scaled, heart_half_scaled, heart_empty_scaled)

    game = Game(answer_object, event_object, heart_object)

    START_BUTTON_ID = 'start_button'
    BACK_BUTTON_ID = 'back_button'
    LOGO_MAIN_ID = 'logo_main'
    LOGO_GAME_ID = 'logo_game'

    start_game_scaled_rect = start_game_unpressed_scaled.get_rect()
    start_button_function = game.go_to_menu
    start_button_menu_pointer = PLAY_MENU
    start_button = MenuButton(START_BUTTON_ID, start_game_pressed_scaled, start_game_unpressed_scaled, start_game_scaled_rect, start_button_function, start_button_menu_pointer)
    
    back_button_scaled_rect = back_button_unpressed_scaled.get_rect()
    back_button_function = game.go_to_menu
    back_button_menu_pointer = MAIN_MENU
    back_button_unpressed = MenuButton(BACK_BUTTON_ID, back_button_pressed_scaled, back_button_unpressed_scaled, back_button_scaled_rect, back_button_function, back_button_menu_pointer)
    
    logo_main_object = ImageObject(LOGO_MAIN_ID, main_menu_logo_scaled)
    logo_game_object = ImageObject(LOGO_GAME_ID, game_menu_logo_scaled)

    game.add_object(MAIN_MENU, start_button)
    game.add_object(MAIN_MENU, logo_main_object)
    game.add_object(PLAY_MENU, logo_game_object)
    game.add_object(PLAY_MENU, back_button_unpressed)

    game.reposition_objects((screen_size_x, screen_size_y))

    #print(pygame.font.get_fonts())

    asyncio.run(main())