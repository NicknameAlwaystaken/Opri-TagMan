from __future__ import annotations
import pygame
import asyncio
import string
from typing import List, Dict, Type
import random

from pygame.font import Font

class Game:
    def __init__(self, answer_object: AnswerObject, heart_object: HeartObject, score_object: Score) -> None:
        self.answer = answer_object
        self.heart_object = heart_object
        self.score_object = score_object
        self.input_frozen = False
        self.freeze_time = 400 # milliseconds
        self.freeze_time_start = 0
        self.word_list = []
        self.game_ended = NOT_ENDED
        self.guessed_letters = []
        self.current_menu = MAIN_MENU
        self.letter_buttons: List[LetterButton] = []
        self.menu_object_list: Dict[str, Dict[str, List[Type[LetterButton]]]] = {
            PLAY_MENU: {},
            MAIN_MENU: {},
            SCORE_MENU: {}
            }
        self.transition_screen = None
        self.menu_transitioning_state = NO_TRANSITION
        self.transitioning_to = None
        self.transition_in_time = 250 # milliseconds
        self.transition_out_time = 250 # milliseconds
        self.transition_in_start_time = 0 # milliseconds
        self.transition_out_start_time = 0 # milliseconds

        self.add_object(PLAY_MENU, answer_object)
        self.add_object(PLAY_MENU, heart_object)
        self.add_object(SCORE_MENU, score_object)

        self.create_letter_buttons()
        self.score_object.set_score(0)

    def reposition_objects(self, screen_size):
        self.reposition_menu_objects(screen_size)
        self.reposition_text_objects(screen_size)
        self.reposition_letter_buttons(screen_size)

    def reposition_text_objects(self, screen_size):
        screen_size_x, screen_size_y = screen_size
        
        if screen_size_x >= screen_size_y: # landscape
            answer_pos = 0.35
        else: # portrait
            answer_pos = 0.25
        self.answer.center = screen_size_x // 2, screen_size_y * answer_pos

    def reposition_menu_objects(self, screen_size):
        screen_size_x, screen_size_y = screen_size
        top_margin = 100
        for menu in self.menu_object_list.values():
            for object_list in menu.values():
                for object in object_list:
                    # SCORE_MENU
                    if object.id == NEXT_BUTTON_ID:
                        object.rect.center = screen_size_x // 2, screen_size_y // 3 * 2
                    elif object.id == GAME_OVER_ID:
                        object.center = screen_size_x // 2, screen_size_y // 3 * 1
                    elif object.id == YOU_WIN_ID:
                        object.center = screen_size_x // 2, screen_size_y // 3 * 1
                    elif object.id == SCORE_ID:
                        object.center = screen_size_x // 2, screen_size_y // 2
                    # START_MENU
                    elif object.id == START_BUTTON_ID:
                        object.rect.center = screen_size_x // 2, screen_size_y // 2
                    elif object.id == LOGO_MAIN_ID:
                        object.center = screen_size_x // 2, 100
                    # GAME_MENU
                    elif object.id == BACK_BUTTON_ID:
                        game_logo_surface = logo_game_object.surface
                        game_logo_rect = game_logo_surface.get_rect()
                        object.rect.midright = screen_size_x - 10, game_logo_rect.center[1] - 10
                    elif object.id == LOGO_GAME_ID:
                        object.topleft = 0, 0
                    elif object.id == HEART_ID:
                        game_logo_surface = logo_game_object.surface
                        game_logo_rect = game_logo_surface.get_rect()
                        object.center = game_logo_rect.center[0], game_logo_surface.get_size()[1] + object.surface.get_size()[1] / 2
        
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
        self.transitioning_to = menu
        self.menu_transitioning_state = TRANSITION_IN
        self.start_menu_transition()

    def transition_in_finish(self):
        self.transition_out_start_time = pygame.time.get_ticks()
        self.menu_transitioning_state = TRANSITION_OUT
        self.current_menu = self.transitioning_to
        if self.current_menu == PLAY_MENU:
            self.start_new_game()

    def transition_out_finish(self):
        self.menu_transitioning_state = NO_TRANSITION
        self.input_frozen = False

    def start_menu_transition(self):
        self.transition_screen = pygame.Surface(screen.get_size())
        self.transition_screen.fill(MAIN_OKRA_COLOR)
        self.transition_in_start_time = pygame.time.get_ticks()
        game.input_frozen = True

    def start_new_game(self):
        self.game_ended = NOT_ENDED
        self.answer.set_answer(random.choice(self.word_list))
        self.heart_object.set_max_health(8)
        for object in self.letter_buttons:
            object.change_button_state(BUTTON_UNPRESSED)

    def draw(self, screen: pygame.Surface):
        if self.current_menu in self.menu_object_list:
            for object_list in self.menu_object_list[self.current_menu].values():
                for object in object_list:
                    object.draw(screen)

        if (self.menu_transitioning_state == TRANSITION_IN or self.menu_transitioning_state == TRANSITION_OUT) and self.transition_screen is not None:
            ticks = (pygame.time.get_ticks() - self.transition_in_start_time)
            if self.menu_transitioning_state == TRANSITION_IN:
                alpha = 255 - (255 * ((self.transition_in_time - ticks) / self.transition_in_time))
            else:
                alpha = 255 + (255 * ((self.transition_out_time- ticks) / self.transition_out_time))
            self.transition_screen.set_alpha(alpha)
            screen.blit(self.transition_screen, self.transition_screen.get_rect())

    def update(self):
        ticks = pygame.time.get_ticks()
        if self.menu_transitioning_state != NO_TRANSITION:

            if self.menu_transitioning_state == TRANSITION_IN:
                elapsed_time = ticks - self.transition_in_start_time
                if elapsed_time >= self.transition_in_time:
                    self.transition_in_finish()

            elif self.menu_transitioning_state == TRANSITION_OUT:
                elapsed_time = ticks - self.transition_out_start_time
                if elapsed_time >= self.transition_in_time:
                    self.transition_out_finish()

        if self.current_menu in self.menu_object_list:
            for object_list in self.menu_object_list[self.current_menu].values():
                for object in object_list:
                    object.update()

        if self.input_frozen:
            elapsed_time = ticks - self.freeze_time_start
            if elapsed_time >= self.freeze_time:
                self.input_frozen = False
            
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

    def freeze_input(self):
        self.input_frozen = True
        self.freeze_time_start = pygame.time.get_ticks()

    def game_won(self):
        self.score_object.add_score(1)
        self.game_ended = GAME_WON
        self.freeze_input()
        self.go_to_menu(SCORE_MENU)

    def game_lost(self):
        self.game_ended = GAME_LOST
        self.freeze_input()
        self.go_to_menu(SCORE_MENU)

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
        if self.id == YOU_WIN_ID and game.game_ended != GAME_WON:
            return
        if self.id == GAME_OVER_ID and game.game_ended != GAME_LOST:
            return
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
    def __init__(self, id, font: pygame.font.Font, color) -> None:
        super().__init__(id, font, color)
        self.guessed_letters = []
        self.draw_text = ''
        self.previous_letter_guessed = ''
        self.animation_state = NO_LETTER_ANIMATION
        self.animation_start_time = 0
        self.wrong_letter_animation_time = 400
        self.correct_letter_animation_time = 250
        self.correct_letter_animation_scale = 0.3

    def set_answer(self, answer: str):
        self.text = answer.upper()
        self.draw_text = ''.join(['_' if letter in string.ascii_uppercase else letter for letter in answer.upper()])
        self.temp_color = None
        self.guessed_letters = []
        self._update_surface()

    def set_text(self, text, color=None):
        raise NotImplementedError("Setting text/answer to AnswerObject is used with set_answer")
        
    def _update_surface(self):
        letter_size_x, letter_size_y = self.font.size('_')
        letter_x_spacing = 0
        x_margin = (letter_size_x * (1 + self.correct_letter_animation_scale)) / 2
        letter_surface = pygame.Surface((x_margin * 2 + (letter_size_x + letter_x_spacing) * len(self.draw_text), letter_size_y * (1 + self.correct_letter_animation_scale)), pygame.SRCALPHA)
        if self.animation_state != NO_LETTER_ANIMATION:
            elapsed_time = pygame.time.get_ticks() - self.animation_start_time
            if self.animation_state == CORRECT_LETTER_ANIMATION:
                animation_fraction = min(elapsed_time / self.correct_letter_animation_time, 1)
            else:
                animation_fraction = min(elapsed_time / self.wrong_letter_animation_time, 1)

        for index, letter in enumerate(self.draw_text):
            if self.animation_state == WRONG_LETTER_ANIMATION:
                color = tuple([MAIN_GREY_COLOR[i] + (self.color[i] - MAIN_GREY_COLOR[i]) * animation_fraction for i in range(3)])
            else:
                if self.previous_letter_guessed == letter:
                    color = CORRECT_COLOR
                else:
                    color = self.temp_color if self.temp_color is not None else self.color

            letter_image = self.font.render(letter, True, color)

            if self.previous_letter_guessed == letter and self.animation_state == CORRECT_LETTER_ANIMATION:
                if animation_fraction <= 0.5:
                    letter_image = pygame.transform.rotozoom(letter_image, 0, 1 + self.correct_letter_animation_scale * animation_fraction)
                else:
                    letter_image = pygame.transform.rotozoom(letter_image, 0, 1 + self.correct_letter_animation_scale - self.correct_letter_animation_scale * animation_fraction)

            letter_rect = letter_image.get_rect()
            letter_rect.center = (x_margin + letter_size_x / 2 + letter_size_x * index, letter_surface.get_size()[1] / 2)
            letter_surface.blit(letter_image, letter_rect)

        self.surface = letter_surface
        
    def update(self):
        if self.animation_state != NO_LETTER_ANIMATION:
            self._update_surface()
            elapsed_time = pygame.time.get_ticks() - self.animation_start_time
            if (elapsed_time > self.wrong_letter_animation_time and self.animation_state == WRONG_LETTER_ANIMATION) or (
                    elapsed_time > self.correct_letter_animation_time and self.animation_state == CORRECT_LETTER_ANIMATION):
                self.animation_state = NO_LETTER_ANIMATION
                self._update_surface()

    def wrong_letter_animation(self):
        self.animation_state = WRONG_LETTER_ANIMATION
        self.animation_start_time = pygame.time.get_ticks()

    def correct_letter_animation(self):
        self.animation_state = CORRECT_LETTER_ANIMATION
        self.animation_start_time = pygame.time.get_ticks()

    def check_letter(self, letter: str): # Returns True if word is solved, False if not
        letter = letter.upper()
        guessed_string = ''
        correct_answer = self.text.upper()
        guessed_letters = self.guessed_letters
        self.previous_letter_guessed = letter
        if letter in guessed_letters:
            return
        
        self.guessed_letters.append(letter)
        guessed_letters = self.guessed_letters
        letter_button = game.get_letter_button(letter)

        if letter not in correct_answer:
            game.heart_object.remove_health(1)
            letter_button.change_button_state(BUTTON_PRESSED_INCORRECT)
            self.wrong_letter_animation()
            if game.heart_object.get_health() <= 0:
                game.game_lost()
            return
        
        self.correct_letter_animation()
        letter_button.change_button_state(BUTTON_PRESSED_CORRECT)
    
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

class Score(TextObject):
    def __init__(self, id, font: Font, color=None) -> None:
        super().__init__(id, font, color)
        self.score = 0
        self.text_template = f"SCORE: "

    def set_score(self, amount):
        self.score = amount
        self.set_text(self.text_template + str(self.score))

    def add_score(self, amount):
        self.score += amount
        self.set_text(self.text_template + str(self.score))

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
        back_button.activate()
        return True
    if event_key == pygame.K_RETURN and game_state == MAIN_MENU:
        start_button.activate()
        return True
    if event_key == pygame.K_RETURN and game_state == SCORE_MENU:
        next_button.activate()
        return True
    
    return False

async def main():
    list_of_words = read_wordlist(wordlist_file)
    game.set_word_selection(list_of_words)

    game.input_frozen = False

    running = True

    while running:
        events = pygame.event.get()
        mousepos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.VIDEORESIZE:
                game.reposition_objects(screen.get_size())

            if game.input_frozen: # I want to introduce short pause so people don't accidentally continue after pressing multiple buttons at end of the game
                continue

            if event.type == pygame.KEYDOWN:
                event_key = event.key

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

    screen = pygame.display.set_mode((screen_size_x, screen_size_y), pygame.RESIZABLE)

    # display_info = pygame.display.Info()
    # if screen_size_x <= display_info.current_w and screen_size_y <= display_info.current_h:
    #     screen = pygame.display.set_mode((screen_size_x, screen_size_y), pygame.RESIZABLE)
    # else:
    #     screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.RESIZABLE)


    TICK_SPEED = 60

    # gamestates
    PLAY_MENU = 'play_menu_state'
    MAIN_MENU = 'main_menu_state'
    SCORE_MENU = 'score_menu_state'

    LIGHT_BLUE_COLOR = (138, 160, 242)
    #CORRECT_COLOR = (16, 140, 40)
    CORRECT_COLOR = (0, 93, 69)
    WRONG_COLOR = (200, 50, 25)
    BLACK_COLOR = (0, 0, 0)
    WHITE_COLOR = (255, 255, 255)
    CREAM_COLOR = (255, 253, 208)

    # Main game colors
    MAIN_GREY_COLOR = (96, 96, 96)
    MAIN_OKRA_COLOR = (178, 134, 54)
    MAIN_PURPLE_COLOR = (84, 37, 90)

    SCORE_FONT_COLOR = BLACK_COLOR
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
    SCORE_FONT_SIZE = 50

    FONT_FILE = "MartianMono-VariableFont_wdth,wght.ttf"

    ARIAL_BLACK = 'ariblk.ttf'
    CONSOLAS_BOLD = 'consolab.ttf'

    DEFAULT_FONT = pygame.font.Font(FONT_FILE, DEFAULT_FONT_SIZE)
    LETTER_BUTTON_FONT = pygame.font.Font(ARIAL_BLACK, LETTER_BUTTON_FONT_SIZE)
    ANSWER_FONT = pygame.font.Font(CONSOLAS_BOLD, ANSWER_FONT_SIZE)
    ANSWER_FONT.set_bold(True)
    SCORE_FONT = pygame.font.Font(ARIAL_BLACK, SCORE_FONT_SIZE)

    oprimagazine_logo_original = pygame.image.load("oprimagazine_logo.png").convert_alpha()
    oprimagazine_logo_smallest = pygame.image.load("logo_y_100.png").convert_alpha()

    GAME_TOP_MARGIN = 100
    
    main_menu_logo_scaled = pygame.transform.rotozoom(oprimagazine_logo_original, 0, 0.4)
    logo_y_size = oprimagazine_logo_smallest.get_size()[1]
    game_menu_y_size = 100
    game_menu_scale = 1 / (logo_y_size / game_menu_y_size)
    game_menu_logo_scaled = pygame.transform.rotozoom(oprimagazine_logo_smallest, 0, game_menu_scale)

    
    game_over_text = pygame.image.load("game_over_text.png").convert_alpha()
    game_over_text_scaled = pygame.transform.smoothscale(game_over_text, game_over_text.get_size())

    you_win_text = pygame.image.load("you_win_text.png").convert_alpha()
    you_win_text_scaled = pygame.transform.smoothscale(you_win_text, you_win_text.get_size())
    
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
    
    start_game_unpressed = pygame.image.load("start_button_unpressed.png").convert_alpha()
    start_button_size = start_game_unpressed.get_size()
    start_button_scale = 3
    start_game_unpressed_scaled = pygame.transform.smoothscale(start_game_unpressed, (int(start_button_size[0] / start_button_scale), int(start_button_size[1] / start_button_scale)))
    start_game_pressed = pygame.image.load("start_button_pressed.png").convert_alpha()
    start_game_pressed_scaled = pygame.transform.smoothscale(start_game_pressed, (int(start_button_size[0] / start_button_scale), int(start_button_size[1] / start_button_scale)))

    back_button_unpressed = pygame.image.load("x_back_button_unpressed.png").convert_alpha()
    back_button_size = back_button_unpressed.get_size()
    back_button_scale = 8
    back_button_unpressed_scaled = pygame.transform.smoothscale(back_button_unpressed, (int(back_button_size[0] / back_button_scale), int(back_button_size[1] / back_button_scale)))
    back_button_pressed = pygame.image.load("x_back_button_pressed.png").convert_alpha()
    back_button_pressed_scaled = pygame.transform.smoothscale(back_button_pressed, (int(back_button_size[0] / back_button_scale), int(back_button_size[1] / back_button_scale)))

    next_button_unpressed = pygame.image.load("next_button_unpressed.png").convert_alpha()
    next_button_size = next_button_unpressed.get_size()
    next_button_size = (280, 130)
    next_button_scale = 1
    next_button_unpressed_scaled = pygame.transform.smoothscale(next_button_unpressed, (int(next_button_size[0] / next_button_scale), int(next_button_size[1] / next_button_scale)))
    next_button_pressed = pygame.image.load("next_button_pressed.png").convert_alpha()
    next_button_pressed_scaled = pygame.transform.smoothscale(next_button_pressed, (int(next_button_size[0] / next_button_scale), int(next_button_size[1] / next_button_scale)))

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
    
    PAUSE_AFTER_WIN_TIMER = pygame.USEREVENT + 1

    TRANSITION_IN_TIMER = pygame.USEREVENT + 2
    TRANSITION_OUT_TIMER = pygame.USEREVENT + 3

    TRANSITION_IN = 0
    TRANSITION_OUT = 1
    NO_TRANSITION = -1

    NO_LETTER_ANIMATION = -1
    CORRECT_LETTER_ANIMATION = 0
    WRONG_LETTER_ANIMATION = 1

    NOT_ENDED = -1
    GAME_LOST = 0
    GAME_WON = 1

    HEART_ID = 'heart'
    ANSWER_ID = 'answer'
    SCORE_ID = 'score'

    answer_object = AnswerObject(ANSWER_ID, ANSWER_FONT, ANSWER_FONT_COLOR)
    score_object = Score(SCORE_ID, SCORE_FONT, SCORE_FONT_COLOR)

    heart_object = HeartObject(HEART_ID, heart_full_scaled, heart_half_scaled, heart_empty_scaled)

    game = Game(answer_object, heart_object, score_object)

    START_BUTTON_ID = 'start_button'
    BACK_BUTTON_ID = 'back_button'
    NEXT_BUTTON_ID = 'next_button'
    LOGO_MAIN_ID = 'logo_main'
    LOGO_GAME_ID = 'logo_game'
    GAME_OVER_ID = 'game_over'
    YOU_WIN_ID = 'you_win'

    start_game_scaled_rect = start_game_unpressed_scaled.get_rect()
    start_button_function = game.go_to_menu
    start_button_menu_pointer = PLAY_MENU
    start_button = MenuButton(START_BUTTON_ID, start_game_pressed_scaled, start_game_unpressed_scaled, start_game_scaled_rect, start_button_function, start_button_menu_pointer)
    
    back_button_scaled_rect = back_button_unpressed_scaled.get_rect()
    back_button_function = game.go_to_menu
    back_button_menu_pointer = MAIN_MENU
    back_button = MenuButton(BACK_BUTTON_ID, back_button_pressed_scaled, back_button_unpressed_scaled, back_button_scaled_rect, back_button_function, back_button_menu_pointer)
    
    next_button_scaled_rect = next_button_unpressed_scaled.get_rect()
    next_button_function = game.go_to_menu
    next_button_menu_pointer = PLAY_MENU
    next_button = MenuButton(NEXT_BUTTON_ID, next_button_pressed_scaled, next_button_unpressed_scaled, next_button_scaled_rect, next_button_function, next_button_menu_pointer)
    
    logo_main_object = ImageObject(LOGO_MAIN_ID, main_menu_logo_scaled)
    logo_game_object = ImageObject(LOGO_GAME_ID, game_menu_logo_scaled)

    game_over_object = ImageObject(GAME_OVER_ID, game_over_text_scaled)
    you_win_object = ImageObject(YOU_WIN_ID, you_win_text_scaled)

    game.add_object(MAIN_MENU, start_button)
    game.add_object(MAIN_MENU, logo_main_object)
    game.add_object(PLAY_MENU, logo_game_object)
    game.add_object(PLAY_MENU, back_button)
    game.add_object(SCORE_MENU, next_button)
    game.add_object(SCORE_MENU, game_over_object)
    game.add_object(SCORE_MENU, you_win_object)

    game.reposition_objects((screen_size_x, screen_size_y))

    #print(pygame.font.get_fonts())

    asyncio.run(main())