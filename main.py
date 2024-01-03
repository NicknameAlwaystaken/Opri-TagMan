from __future__ import annotations
import pygame
import asyncio
import string
from typing import List, Dict, Type
import random

class Game:
    def __init__(self, answer_object: AnswerObject, event_object: EventObject) -> None:
        self.answer = answer_object
        self.event = event_object
        self.freeze_input = False
        self.word_list = []
        self.won = False
        self.guessed_letters = []
        self.current_menu = None
        self.game_state_object_list: Dict[str, Dict[str, List[Type[LetterButton]]]] = {
            PLAY_MENU_STATE: {},
            MAIN_MENU_STATE: {}
            }

        self.add_object(PLAY_MENU_STATE, answer_object)
        self.add_object(PLAY_MENU_STATE, event_object)

    def word_selection(self, word_list):
        self.word_list = word_list

    def get_objects(self, object_type = None):
        if object_type is None:
            return [object for values in self.game_state_object_list[self.current_menu].values() for object in values]
        if object_type in self.game_state_object_list[self.current_menu]:
            return [object for object in self.game_state_object_list[self.current_menu][object_type]]
        return None

    def start_new_game(self):
        self.won = False
        self.current_menu = PLAY_MENU_STATE
        self.event.set_text('')
        self.answer.set_answer(random.choice(self.word_list))
        self.guessed_letters = []
        for object in self.game_state_object_list[PLAY_MENU_STATE][BUTTON_OBJECT_TYPE]:
            object.change_color(BLACK_COLOR, RESET_ALPHA)

    def draw(self, screen):
        for object_list in self.game_state_object_list[self.current_menu].values():
            for object in object_list:
                object.draw(screen)

    def initialize(self):
        pass

    def position_letter_buttons(self, keyboard_rect: pygame.Rect):
        letter_counter = 0
        margin_y = 20
        margin_x = margin_y + (DEFAULT_FONT.size('A')[0] / 2)
        letters_per_row = 9
        letter_row = 0
        letter_column = 0
        letter_x_spacing = (keyboard_rect.size[0] - margin_x * 2) / (letters_per_row - 1)
        letter_y_spacing = (keyboard_rect.size[1] - DEFAULT_FONT.size('A')[1] * 1.5) / 3

        for letter in string.ascii_uppercase:
            new_letter = LetterButton(letter, DEFAULT_FONT)
            self.add_object(PLAY_MENU_STATE, new_letter)
            new_letter.rect.midtop = letter_column * letter_x_spacing + (keyboard_rect.topleft[0] + margin_x), letter_row * letter_y_spacing + (keyboard_rect.topleft[1] + margin_y)
            letter_counter += 1
            letter_column += 1
            if letter_counter % letters_per_row == 0:
                letter_row += 1
                letter_column = 0
                if len(string.ascii_uppercase) - letter_counter < letters_per_row:
                    next_pos = (letters_per_row - (len(string.ascii_uppercase) - letter_counter)) // 2
                    letter_column = next_pos

    def add_object(self, game_state, object: GameObject):
        if object.object_type not in self.game_state_object_list[game_state]:
            self.game_state_object_list[game_state][object.object_type] = []
        self.game_state_object_list[game_state][object.object_type].append(object)

    def game_won(self):
        self.event.set_text("Game won!")
        self.won = True
        self.freeze_input = True
        pygame.time.set_timer(SHORT_PAUSE_AFTER_WINNING, 250, 1)

class GameObject:
    def __init__(self) -> None:
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
    def __init__(self) -> None:
        super().__init__()
        self.object_type = NON_INTERACTIVE_OBJECT_TYPE

class TextObject(NonInteractiveObject):
    def __init__(self, font: pygame.font.Font) -> None:
        super().__init__()
        self.text = ''
        self.font = font
        self.color = None
        self.center = None
        self.topleft = None
        self.alpha = None

    def set_text(self, text, color = None):
        self.text = text
        if color is not None:
            self.color = color
        self.surface = self.font.render(text, True, self.color)
        self.rect = self.surface.get_rect()
        self._update_surface()
        
    def change_color(self, color, alpha = None):
        self.color = color
        if alpha is not None:
            self.alpha = alpha
        self._update_surface()

    def _update_surface(self):
        self.surface = self.font.render(self.text, True, self.color)
        if self.alpha is not None:
            self.surface.set_alpha(self.alpha)

    def draw(self, screen):
        if self.surface is not None and self.center is not None:
            surface_rect = self.surface.get_rect()
            surface_rect.center = self.center
            screen.blit(self.surface, surface_rect)

class AnswerObject(TextObject):
    def __init__(self, font: pygame.font.Font) -> None:
        super().__init__(font)
        self.guessed_letters = []
        self.draw_text = ''

    def set_answer(self, answer: str):
        self.text = answer
        self.draw_text = ''.join(['_' if letter in string.ascii_uppercase else letter for letter in answer.upper()])
        self._update_surface()
        
    def _update_surface(self):
        self.surface = self.font.render(self.draw_text, True, self.color)
        

    def check_letter(self, letter: str): # Returns True if word is solved, False if not
        letter = letter.upper()
        if letter not in self.guessed_letters:
            self.guessed_letters.append(letter)
            game.event.set_text(f"You guessed '{letter}'")
        else:
            game.event.set_text(f"Already guessed '{letter}'")
            return
        guessed_string = ''
        correct_answer = self.text.upper()
        print(f"{correct_answer = }")
        for letter in correct_answer:
            if letter not in self.guessed_letters and letter in string.ascii_uppercase:
                guessed_string += '_'
            else:
                guessed_string += letter

        print(f"{guessed_string = }")
        self.draw_text = guessed_string
        self._update_surface()

        if guessed_string == correct_answer:
            game.game_won()

class EventObject(TextObject):
    def __init__(self, font: pygame.font.Font) -> None:
        super().__init__(font)

class ButtonObject(GameObject):
    def __init__(self) -> None:
        super().__init__()
        self.object_type = BUTTON_OBJECT_TYPE
        self.button_function = None

    def activate(self):
        raise NotImplementedError

class MenuButton(ButtonObject):
    def __init__(self, surface, rect, button_function) -> None:
        super().__init__()
        self.surface = surface
        self.rect = rect
        self.button_function = button_function

    def activate(self):
        self.button_function()

class LetterButton(ButtonObject):
    def __init__(self, letter, font: pygame.font.Font) -> None:
        super().__init__()
        self.object_type = BUTTON_OBJECT_TYPE
        self.letter = letter
        self.font = font
        self.color = BLACK_COLOR
        self.surface = font.render(letter, True, self.color)
        self.rect = self.surface.get_rect()

    def change_color(self, color, alpha = None):
        self.color = color
        self._update_surface(alpha)

    def _update_surface(self, alpha):
        self.surface = self.font.render(self.letter, True, self.color)
        if alpha is not None:
            self.surface.set_alpha(alpha)

    def activate(self):
        game.answer.check_letter(self.letter)


def create_keyboard_zone():
    keyboard_width = min(max(SCREEN_WIDTH * 0.75, 450), 600)
    keyboard_height = SCREEN_HEIGHT * 0.4
    bot_y_margin = 50
    rect_size = keyboard_width, keyboard_height
    keyboard_rect = pygame.Rect(0, 0, *rect_size)
    keyboard_surface = pygame.Surface(keyboard_rect.size, pygame.SRCALPHA)
    keyboard_surface_rect = keyboard_surface.get_rect()
    keyboard_surface_rect.midbottom = SCREEN_WIDTH // 2, SCREEN_HEIGHT - bot_y_margin
    pygame.draw.rect(keyboard_surface, WRONG_COLOR, keyboard_rect)
    keyboard_surface.set_alpha(100)

    return keyboard_surface, keyboard_surface_rect

async def main():

    random_words = ['potato', 'peruna', 'glass', 'bottle']
    game.word_selection(random_words)

    screen_size = screen.get_size()

    keyboard_surface, keyboard_surface_rect = create_keyboard_zone()

    game.freeze_input = False

    game.position_letter_buttons(keyboard_surface_rect)

    running = True

    while running:
        events = pygame.event.get()
        mousepos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

            if game.freeze_input and event.type == SHORT_PAUSE_AFTER_WINNING:
                game.freeze_input = False
                print(f"Freeze is done!")

            if game.freeze_input: # I want to introduce short pause so people don't accidentally continue after pressing multiple buttons at end of the game
                continue

            if event.type == pygame.KEYDOWN:
                if game.won: # make game continue after winning only once user gives input
                    game.start_new_game()
                    continue
                try:
                    key = chr(event.key).upper()
                    print(f"{key = }")
                    if key in string.ascii_uppercase:
                        game.answer.check_letter(key)
                except:
                    print(f"Invalid {event.key = }")
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.won: # make game continue after winning only once user gives input
                    game.start_new_game()
                    continue

                list_of_objects = game.get_objects(BUTTON_OBJECT_TYPE)
                if list_of_objects is not None:
                    for object in game.get_objects(BUTTON_OBJECT_TYPE):
                        if object.rect.collidepoint(mousepos):
                            print(f"{object = }")
                            object.activate()

        screen.fill(LIGHT_BLUE_COLOR)

        screen.blit(keyboard_surface, keyboard_surface_rect)

        game.draw(screen)

        pygame.display.flip()

        clock.tick(TICK_SPEED)

        await asyncio.sleep(0)

if __name__ == "__main__":
    pygame.init()
    
    SCREEN_WIDTH = 1024
    SCREEN_HEIGHT = 768

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    TICK_SPEED = 60

    # gamestates
    PLAY_MENU_STATE = 'play_menu_state'
    MAIN_MENU_STATE = 'main_menu_state'

    LIGHT_BLUE_COLOR = (138, 160, 242)
    CORRECT_COLOR = (16, 140, 40)
    WRONG_COLOR = (200, 50, 25)
    BLACK_COLOR = (0, 0, 0)
    
    RESET_ALPHA = 255
    WRONG_LETTER_ALPHA = 100

    BUTTON_OBJECT_TYPE = "button"
    NON_INTERACTIVE_OBJECT_TYPE = "non_interactive"

    DEFAULT_FONT_SIZE = 50
    ANSWER_FONT_SIZE = 40
    EVENT_FONT_SIZE = 30

    FONT_FILE_NAME = "MartianMono-VariableFont_wdth,wght.ttf"

    DEFAULT_FONT = pygame.font.Font(FONT_FILE_NAME, DEFAULT_FONT_SIZE)
    ANSWER_FONT = pygame.font.Font(FONT_FILE_NAME, ANSWER_FONT_SIZE)
    EVENT_FONT = pygame.font.Font(FONT_FILE_NAME, EVENT_FONT_SIZE)
    
    start_game = pygame.image.load("temp_start.png").convert_alpha()
    start_game_scaled = pygame.transform.smoothscale(start_game, (175, 90))


    clock = pygame.time.Clock()
    
    SHORT_PAUSE_AFTER_WINNING = pygame.USEREVENT

    answer_object = AnswerObject(ANSWER_FONT)
    answer_object.color = BLACK_COLOR
    answer_object.center = SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.4

    event_object = EventObject(EVENT_FONT)
    event_object.color = BLACK_COLOR
    event_object.center = SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.3


    game = Game(answer_object, event_object)

    start_game_scaled_rect = start_game_scaled.get_rect()
    start_game_scaled_rect.center = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100
    start_button_function = game.start_new_game
    start_button = MenuButton(start_game_scaled, start_game_scaled_rect, start_button_function)

    game.add_object(MAIN_MENU_STATE, start_button)

    game.current_menu = MAIN_MENU_STATE

    asyncio.run(main())