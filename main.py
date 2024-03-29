from __future__ import annotations
import pygame
import asyncio
import string
from typing import List, Dict, Type
import random
random.seed()
import os
from effects import Fireworks, EffectController
import webbrowser
from pygame.font import Font

class Game:
    def __init__(self, screen: pygame.Surface, answer_object: AnswerObject, heart_object: HeartObject, score_object: ScoreObject) -> None:
        self.screen = screen
        self.answer_object = answer_object
        self.heart_object = heart_object
        self.score_object = score_object
        self.input_frozen = False
        self.difficulty_mode = None
        self.default_freeze_time = 400
        self.freeze_time = 400 # milliseconds
        self.freeze_time_start = 0
        self.word_list: List[str] = []
        self.game_ended = NOT_ENDED
        self.guessed_letters = []
        self.current_menu = START_MENU
        self.letter_buttons: List[LetterButton] = []
        self.start_menu_objects: Dict[str, List[Type[GameObject]]] = {} # Dic, {object_type, [list of objects]}
        self.play_menu_objects: Dict[str, List[Type[GameObject]]] = {}
        self.score_menu_objects: Dict[str, List[Type[GameObject]]] = {}
        
        self.transition_screen = None
        self.menu_transitioning_state = NO_TRANSITION
        self.transitioning_to = None
        self.transition_in_time = 200 # milliseconds
        self.transition_out_time = 200 # milliseconds
        self.transition_in_start_time = 0 # milliseconds
        self.transition_out_start_time = 0 # milliseconds
        self.transition_screen = pygame.Surface(screen.get_size())

        self.scorescreen_delay_time = 1000
        self.scorescreen_delay_start_time = 0

        self.add_object(PLAY_MENU, answer_object)
        self.add_object(PLAY_MENU, heart_object)
        self.add_object(SCORE_MENU, score_object)

        list_of_words = read_wordlist(wordlist_file)
        self.set_word_selection(list_of_words)

        self.create_letter_buttons()
        self.score_object.reset_streak("")
        self.heart_object.set_max_health(8)
        self.answer_object.set_answer(random.choice(self.word_list))

    def start_easy_game(self):
        self.difficulty_mode = EASY_MODE
        self.go_to_menu(PLAY_MENU)

    def start_hard_game(self):
        self.difficulty_mode = HARD_MODE
        self.go_to_menu(PLAY_MENU)

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
        self.answer_object.update_rect_center((screen_size_x // 2, screen_size_y * answer_pos))

    def reposition_menu_objects(self, screen_size):
        screen_size_x, screen_size_y = screen_size
        for object_list in self.score_menu_objects.values(): # SCORE_MENU
            for object in object_list:
                if object.id == NEXT_BUTTON_ID:
                    object.rect.center = screen_size_x // 2, screen_size_y // 3 * 2
                elif object.id == TRY_AGAIN_BUTTON_ID:
                    object.rect.center = screen_size_x // 2, screen_size_y // 3 * 2
                elif object.id == GAME_OVER_ID:
                    object.update_rect_center((screen_size_x // 2, screen_size_y // 3 * 1))
                elif object.id == YOU_WIN_ID:
                    object.update_rect_center((screen_size_x // 2, screen_size_y // 3 * 1))
                elif object.id == SCORE_ID:
                    object.update_rect_center((screen_size_x // 2, screen_size_y // 2))

        for object_list in self.start_menu_objects.values(): # START_MENU
            for object in object_list:
                if object.id == START_EASY_BUTTON_ID:
                    object.rect.center = screen_size_x // 2 - (start_easy_game_pressed_scaled.get_size()[0] / 2) - (BUTTON_SEPARATION_AMOUNT / 2), screen_size_y // 3 * 2
                elif object.id == START_HARD_BUTTON_ID:
                    object.rect.center = screen_size_x // 2 + (start_hard_game_pressed_scaled.get_size()[0] / 2) + (BUTTON_SEPARATION_AMOUNT / 2), screen_size_y // 3 * 2
                elif object.id == LOGO_MAIN_ID:
                    object.update_rect_center((screen_size_x // 2, screen_size_y // 3 * 1))

        for object_list in self.play_menu_objects.values(): # PLAY_MENU
            for object in object_list:
                if object.id == BACK_BUTTON_ID:
                    game_logo_surface = logo_game_button.surface
                    game_logo_rect = game_logo_surface.get_rect()
                    object.rect.midright = screen_size_x - 10, game_logo_rect.center[1] - 10
                elif object.id == LOGO_GAME_ID:
                    object.update_rect_topleft((0, 0))
                elif object.id == LOGO_BACKGROUND_ID:
                    object.update_rect_center((screen_size_x // 2, screen_size_y // 2))
                elif object.id == HEART_ID:
                    game_logo_surface = logo_game_button.surface
                    game_logo_rect = game_logo_surface.get_rect()
                    object.update_rect_center((game_logo_rect.center[0], game_logo_surface.get_size()[1] + object.surface.get_size()[1] / 2))
        
    def create_letter_buttons(self):
        for letter in string.ascii_uppercase:
            new_letter = LetterButton(letter, letter, LETTER_BUTTON_FONT)
            self.add_object(PLAY_MENU, new_letter)
            self.letter_buttons.append(new_letter)

    def set_word_selection(self, word_list):
        self.word_list = word_list

    def get_objects(self, object_type = None):
        if self.current_menu == PLAY_MENU:
            menu_dict = self.play_menu_objects
        elif self.current_menu == START_MENU:
            menu_dict = self.start_menu_objects
        elif self.current_menu == SCORE_MENU:
            menu_dict = self.score_menu_objects
        else:
            return None

        if object_type is None:
            return [object for values in menu_dict.values() for object in values]
        
        if object_type in menu_dict:
            return [object for object in menu_dict[object_type]]
        return None

    def go_to_menu(self, menu):
        if menu == START_MENU:
            self.score_object.reset_streak(self.difficulty_mode)

        self.freeze_input()
        self.transitioning_to = menu
        self.menu_transitioning_state = TRANSITION_IN
        self.start_menu_transition()
        score_menu_effects.deactivate_effects()

    def go_to_website(self, link):
        webbrowser.open(link)

    def transition_in_finish(self):
        self.transition_out_start_time = pygame.time.get_ticks()
        self.menu_transitioning_state = TRANSITION_OUT
        self.current_menu = self.transitioning_to
        self.unfreeze_input()
        if self.current_menu == PLAY_MENU:
            self.start_new_game()

    def transition_out_finish(self):
        self.menu_transitioning_state = NO_TRANSITION
        if self.game_ended == GAME_WON and self.current_menu == SCORE_MENU:
            score_menu_effects.activate_effects()
            
    def score_screen_delay_finish(self):
        self.go_to_menu(SCORE_MENU)

    def start_menu_transition(self):
        self.transition_screen.fill(TRANSITION_SCREEN_COLOR)
        self.transition_in_start_time = pygame.time.get_ticks()
        game.input_frozen = True

    def start_new_game(self):
        self.game_ended = NOT_ENDED
        new_word = random.choice(self.word_list)
        self.answer_object.set_answer(new_word)
        self.heart_object.set_max_health(8)
        for object in self.letter_buttons:
            object.change_button_state(BUTTON_UNPRESSED)

        if self.difficulty_mode == EASY_MODE:
            random_letter = random.choice(new_word)
            for object in self.letter_buttons:
                if object.letter.upper() == random_letter.upper():
                    object.activate()


    def draw(self, screen: pygame.Surface):
        menu_dict = {}
        if self.current_menu == PLAY_MENU:
            menu_dict = self.play_menu_objects
        elif self.current_menu == START_MENU:
            menu_dict = self.start_menu_objects
        elif self.current_menu == SCORE_MENU:
            menu_dict = self.score_menu_objects
        
        if menu_dict:
            for object_list in menu_dict.values():
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

            elif self.menu_transitioning_state == SCORE_SCREEN_DELAY:
                elapsed_time = ticks - self.scorescreen_delay_start_time
                if elapsed_time >= self.scorescreen_delay_time:
                    self.score_screen_delay_finish()

        menu_dict = {}
        if self.current_menu == PLAY_MENU:
            menu_dict = self.play_menu_objects
        elif self.current_menu == START_MENU:
            menu_dict = self.start_menu_objects
        elif self.current_menu == SCORE_MENU:
            menu_dict = self.score_menu_objects
        
        
        if menu_dict:
            for object_list in menu_dict.values():
                for object in object_list:
                    object.update()

        if self.input_frozen:
            elapsed_time = ticks - self.freeze_time_start
            if elapsed_time >= self.freeze_time:
                self.unfreeze_input()
            
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
        menu_dict = {}
        if game_state == PLAY_MENU:
            menu_dict = self.play_menu_objects
        elif game_state == START_MENU:
            menu_dict = self.start_menu_objects
        elif game_state == SCORE_MENU:
            menu_dict = self.score_menu_objects
        
        if object.object_type not in menu_dict:
            menu_dict[object.object_type] = []
            
        menu_dict[object.object_type].append(object)

    def unfreeze_input(self):
        self.input_frozen = False
        self.freeze_time = self.default_freeze_time

    def freeze_input(self, delay=None):
        self.input_frozen = True
        self.freeze_time_start = pygame.time.get_ticks()
        if delay:
            self.freeze_time = delay

    def game_won(self):
        self.score_object.add_streak(self.difficulty_mode)
        self.game_ended = GAME_WON
        self.freeze_input(self.scorescreen_delay_time + 250)
        self.scorescreen_delay_start_time = pygame.time.get_ticks()
        self.menu_transitioning_state = SCORE_SCREEN_DELAY

    def game_lost(self):
        self.score_object.reset_streak(self.difficulty_mode)
        self.game_ended = GAME_LOST
        self.freeze_input(self.scorescreen_delay_time + 250)
        self.scorescreen_delay_start_time = pygame.time.get_ticks()
        self.menu_transitioning_state = SCORE_SCREEN_DELAY

class GameObject:
    def __init__(self, id: str) -> None:
        self.id = id
        self.rect: pygame.Rect = None
        self.surface: pygame.Surface = None
        self.object_type = None

    def draw(self, screen: pygame.Surface):
        if self.surface is not None and self.rect is not None:
            screen.blit(self.surface, self.rect)

    def update_rect_center(self, center):
        self.rect = self.surface.get_rect()
        self.rect.center = center

    def update_rect_topleft(self, topleft):
        self.rect = self.surface.get_rect()
        self.rect.topleft = topleft

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
        if self.surface is not None and self.rect is not None:
            screen.blit(self.surface, self.rect)

class HeartObject(ImageObject):
    def __init__(self, id, heart_full: pygame.Surface, heart_half: pygame.Surface, heart_empty: pygame.Surface) -> None:
        super().__init__(id, heart_empty)
        self.image_list = {
            HEART_FULL: heart_full.copy(),
            HEART_HALF: heart_half.copy(),
            HEART_EMPTY: heart_empty.copy()
        }
        self.number_of_hearts = 0
        self.previous_hearts = 0
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

        if not self.heart_surface or self.previous_hearts != self.number_of_hearts:
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

        temp_rect = self.heart_surface.get_rect()
        temp_rect.center = self.rect.center if self.rect else (0, 0)
        self.rect = temp_rect
        self.surface = self.heart_surface

class TextObject(NonInteractiveObject):
    def __init__(self, id, font: Font, color = None) -> None:
        super().__init__(id)
        self.text = ''
        self.font = font
        self.color = color
        self.temp_color = None
        self.alpha = None

    def set_text(self, text, color = None):
        self.text = text
        self.temp_color = color
        self._update_surface()
        
    def change_color(self, color, alpha = None):
        self.color = color
        if alpha is not None:
            self.alpha = alpha
        self._update_surface()

    def _update_surface(self):
        color = self.temp_color if self.temp_color is not None else self.color
        self.surface = Font.render(self.font, self.text, True, color)
        temp_rect = self.surface.get_rect()
        temp_rect.center = self.rect.center if self.rect else (0, 0)
        self.rect = temp_rect
        if self.alpha is not None and self.alpha != self.surface.get_alpha():
            self.surface.set_alpha(self.alpha)

    def draw(self, screen):
        if self.surface is not None and self.rect is not None:
            screen.blit(self.surface, self.rect)

class AnswerObject(TextObject):
    def __init__(self, id, font: Font, color) -> None:
        super().__init__(id, font, color)
        self.guessed_letters = []
        self.draw_text = ''
        self.previous_letter_guessed = ''
        self.animation_state = NO_LETTER_ANIMATION
        self.animation_start_time = 0
        self.animation_start_delay = 0
        self.wrong_letter_animation_time = 400
        self.correct_letter_animation_time = 250
        self.correct_letter_animation_scale = 0.3
        self.letter_dict: Dict[str, Dict[str, pygame.Surface, str, str, str, tuple[int, int, int]]] = {}
        self.last_letter_colored = None

    def set_answer(self, answer: str):
        self.text = answer.upper()
        self.draw_text = ''.join(['_' if letter in string.ascii_uppercase else letter for letter in answer.upper()])
        self.temp_color = None
        self.guessed_letters = []
        self.letter_dict = {}
        for index, character in enumerate(self.draw_text):
            self.letter_dict[str(index)] = {'letter': character, 'color': self.color}
        self._update_surface()

    def set_text(self, text, color=None):
        raise NotImplementedError("Setting text/answer to AnswerObject is used with set_answer")
        
    def _update_surface(self):
        letter_size_x, letter_size_y = self.font.size('_')
        letter_x_spacing = 8
        x_margin = (letter_size_x * (1 + self.correct_letter_animation_scale)) / 2
        word_surface = pygame.Surface((x_margin * 2 + (letter_size_x + letter_x_spacing) * len(self.draw_text), letter_size_y * (1 + self.correct_letter_animation_scale)), pygame.SRCALPHA)
        elapsed_time = 0
        if self.animation_state != NO_LETTER_ANIMATION:
            elapsed_time = pygame.time.get_ticks() - self.animation_start_time
            if elapsed_time >= self.animation_start_delay:
                animation_start_time = elapsed_time - self.animation_start_delay
                if self.animation_state == CORRECT_LETTER_ANIMATION:
                    animation_fraction = min(animation_start_time / self.correct_letter_animation_time, 1)
                else:
                    animation_fraction = min(animation_start_time / self.wrong_letter_animation_time, 1)

        color = self.temp_color if self.temp_color is not None else self.color
        for letter_values in self.letter_dict.values():
            if letter_values['letter'] != self.previous_letter_guessed and letter_values['color'] != color:
                letter_image = Font.render(self.font, letter_values['letter'], True, color)
                letter_values['surface'] = letter_image

        for index, letter in enumerate(self.draw_text):
            if self.animation_state == WRONG_LETTER_ANIMATION and elapsed_time >= self.animation_start_delay:
                color = tuple([MAIN_GREY_COLOR[i] + (self.color[i] - MAIN_GREY_COLOR[i]) * animation_fraction for i in range(3)])
            else:
                if self.previous_letter_guessed == letter:
                    color = CORRECT_COLOR
                    self.last_letter_colored = letter
                else:
                    color = self.temp_color if self.temp_color is not None else self.color

            if self.letter_dict[str(index)]['letter'] == '_':
                letter_image = Font.render(self.font, letter, True, color)
                self.letter_dict[str(index)]['surface'] = letter_image
                self.letter_dict[str(index)]['letter'] = letter
                self.letter_dict[str(index)]['color'] = color
            scaled_image = None
            if elapsed_time >= self.animation_start_delay:
                if self.previous_letter_guessed == letter and self.animation_state == CORRECT_LETTER_ANIMATION:
                    if animation_fraction <= 0.5:
                        scaled_image = pygame.transform.smoothscale_by(self.letter_dict[str(index)]['surface'], 1 + self.correct_letter_animation_scale * animation_fraction)
                    else:
                        scaled_image = pygame.transform.smoothscale_by(self.letter_dict[str(index)]['surface'], 1 + self.correct_letter_animation_scale - self.correct_letter_animation_scale * animation_fraction)
            
            finished_image = scaled_image if scaled_image else self.letter_dict[str(index)]['surface']
            finished_image_rect = finished_image.get_rect()
            finished_image_rect.center = (x_margin + letter_size_x / 2 + (letter_size_x + letter_x_spacing) * index, word_surface.get_size()[1] / 2)
            word_surface.blit(finished_image, finished_image_rect)

        temp_rect = word_surface.get_rect()
        temp_rect.center = self.rect.center if self.rect else (0, 0)
        self.rect = temp_rect
        self.surface = word_surface
        
    def update(self):
        if self.animation_state != NO_LETTER_ANIMATION:
            elapsed_time = pygame.time.get_ticks() - self.animation_start_time
            if elapsed_time >= self.animation_start_delay:
                if (elapsed_time > self.wrong_letter_animation_time and self.animation_state == WRONG_LETTER_ANIMATION) or (
                        elapsed_time > self.correct_letter_animation_time and self.animation_state == CORRECT_LETTER_ANIMATION):
                    self.animation_state = NO_LETTER_ANIMATION
                
            self._update_surface()

    def wrong_letter_animation(self):
        self.animation_state = WRONG_LETTER_ANIMATION
        self.animation_start_time = pygame.time.get_ticks() + self.animation_start_delay

    def correct_letter_animation(self):
        self.animation_state = CORRECT_LETTER_ANIMATION
        self.animation_start_time = pygame.time.get_ticks() + self.animation_start_delay

    def check_letter(self, letter: str): # Returns True if word is solved, False if not
        letter = letter.upper()
        guessed_string = ''
        correct_answer = self.text.upper()
        guessed_letters = self.guessed_letters
        self.previous_letter_guessed = letter
        if letter in guessed_letters:
            return
        
        self.animation_state == NO_LETTER_ANIMATION
        
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
    
        for letter in correct_answer:
            if letter not in guessed_letters and letter in string.ascii_uppercase:
                guessed_string += '_'
            else:
                guessed_string += letter

        self.draw_text = guessed_string

        if guessed_string == correct_answer:
            game.game_won()
            
        self._update_surface()

class ButtonObject(GameObject):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.object_type = BUTTON_OBJECT_TYPE
        self.button_function = None
        self.button_state = BUTTON_UNPRESSED
        self.previous_state = BUTTON_UNPRESSED
        self.is_animating = False
        self.animate_center = None
        self.animate_step = 0
        self.animate_time = 50
        self.max_animate_steps = 60 * (self.animate_time / 1000)
        self.surface_min_scale = 0.9

    def activate(self):
        raise NotImplementedError
    
    def update(self):
        if self.is_animating:
            self._update_surface()
            pressed_animation(self)
    
    def draw(self, screen):
        if self.surface is not None and self.rect is not None:
            screen.blit(self.surface, self.rect)
            
    def _update_surface(self):
        raise NotImplementedError


class MenuButton(ButtonObject):
    def __init__(self, id, surface_pressed: pygame.Surface, surface_unpressed: pygame.Surface, rect, button_function, button_menu_pointer = None) -> None:
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
        self.surface = self.image_list[self.button_state]

    def update(self):
        if self.button_state == BUTTON_PRESSED:
            ticks = pygame.time.get_ticks() - self.button_pressed_last_tick
            if ticks >= self.button_pressed_timer:
                self.button_state = BUTTON_UNPRESSED
                self._update_surface()
        super().update()

    def activate(self):
        if self.button_menu_pointer:
            self.button_function(self.button_menu_pointer)
        else:
            self.button_function()
        self.button_state = BUTTON_PRESSED
        self.is_animating = True
        self.animate_step = 0
        self.button_pressed_last_tick = pygame.time.get_ticks()
        self._update_surface()
        
    def _update_surface(self):
        self.surface = self.image_list[self.button_state]
        
    def change_button_state(self, state_number): # 0 for unpressed state, 1 for correct pressed, 2 for incorrect pressed
        self.button_state = state_number

    def draw(self, screen: pygame.Surface):
        if self.id == NEXT_BUTTON_ID and game.game_ended != GAME_WON:
            return
        if self.id == TRY_AGAIN_BUTTON_ID and game.game_ended != GAME_LOST:
            return
        super().draw(screen)

class LetterButton(ButtonObject):
    def __init__(self, id, letter, font: Font) -> None:
        super().__init__(id)
        self.object_type = BUTTON_OBJECT_TYPE
        self.image_list = {
            BUTTON_UNPRESSED: letter_button_unpressed_scaled.copy(),
            BUTTON_PRESSED_CORRECT: letter_button_pressed_correct_scaled.copy(),
            BUTTON_PRESSED_INCORRECT: letter_button_pressed_incorrect_scaled.copy()
            }
        self.background_image = self.image_list[self.button_state]
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
        self.button_state = state_number
        self.is_animating = True
        self.animate_step = 0
        self._update_surface()

    def _update_surface(self):
        self.background_image = self.image_list[self.button_state]
        letter_surface_rect = self.letter_surface.get_rect()
        background_image_center = self.background_image.get_rect().center
        letter_surface_rect.center = (background_image_center[0], background_image_center[1])
        self.surface = self.background_image

        self.surface.blit(self.letter_surface, letter_surface_rect)
        self.surface.set_alpha(self.pressed_alpha[self.button_state])

    def activate(self):
        game.answer_object.check_letter(self.letter)

class ScoreObject(TextObject):
    def __init__(self, id, font: Font, color=None) -> None:
        super().__init__(id, font, color)
        self.streak = 0
        self.text_template = f" STREAK: "

    def reset_streak(self, difficulty_name: str):
        self.streak = 0
        self.set_text(f"{difficulty_name.upper()}" + self.text_template + str(self.streak))

    def add_streak(self, difficulty_name: str):
        self.streak += 1
        self.set_text(f"{difficulty_name.upper()}" + self.text_template + str(self.streak))

def pressed_animation(self: ButtonObject):
    scale_amount = (1 - self.surface_min_scale) / self.max_animate_steps
    self.surface = pygame.transform.smoothscale_by(self.surface, 1 - scale_amount * self.animate_step)
    temp_center = self.rect.center
    self.rect = self.surface.get_rect()
    self.rect.center = temp_center
    self.animate_step += 1
    if self.animate_step > self.max_animate_steps:
        self.is_animating = False
        self._update_surface()
        self.rect = self.surface.get_rect()
        self.rect.center = temp_center

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
    if event_key == pygame.K_ESCAPE: # Like back button
        if game_state == PLAY_MENU or game_state == SCORE_MENU:
            back_button.activate()
            return True
    elif (event_key == pygame.K_RETURN or event_key == pygame.K_SPACE): # Like continue button
        if game_state == START_MENU:
            start_easy_button.activate()
            return True
        if game_state == SCORE_MENU and game.game_ended == GAME_WON:
            next_button.activate()
            return True
        if game_state == SCORE_MENU and game.game_ended == GAME_LOST:
            try_again_button.activate()
            return True
    
    return False


async def main():

    game.unfreeze_input()

    running = 1

    while running:
        events = pygame.event.get()
        for event in events:

            if event.type == pygame.QUIT:
                running = 0

            if game.input_frozen: # inputs frozen during transition
                continue


            elif event.type == pygame.KEYDOWN:
                if not menu_action(event, game.current_menu):
                    event_key = event.key
                    if game.current_menu == PLAY_MENU:
                        try:
                            key_upper = chr(event_key).upper()
                            letter_button = game.get_letter_button(key_upper)
                            if letter_button is not None:
                                letter_button.activate()
                        except:
                            pass

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mousepos = pygame.mouse.get_pos()
                    list_of_objects = game.get_objects(BUTTON_OBJECT_TYPE)
                    if list_of_objects is not None:
                        for object in list_of_objects:
                            if object.rect.collidepoint(mousepos):
                                object.activate()

        screen.fill(BACKGROUND_COLOR)

        score_menu_effects.update()
        score_menu_effects.draw(screen)

        game.update()
        game.draw(screen)

        pygame.display.flip()
    
        clock.tick(TICK_SPEED)
        
        await asyncio.sleep(0)

if __name__ == "__main__":
    pygame.init()
    
    screen_size_x, screen_size_y = (1024, 768)

    screen = pygame.display.set_mode((screen_size_x, screen_size_y), pygame.DOUBLEBUF | pygame.SCALED)

    game_name = 'TagMan'

    pygame.display.set_caption(f"Play {game_name}")

    IMAGE_FOLDER = 'images'
    icon_image = pygame.image.load("favicon.png").convert()
    pygame.display.set_icon(icon_image)

    # Game states
    PLAY_MENU = 'play_menu_state'
    START_MENU = 'main_menu_state'
    SCORE_MENU = 'score_menu_state'

    LIGHT_BLUE_COLOR = (138, 160, 242)
    CORRECT_COLOR = (0, 93, 69)
    WRONG_COLOR = (200, 50, 25)
    BLACK_COLOR = (0, 0, 0)
    WHITE_COLOR = (255, 255, 255)
    CREAM_COLOR = (255, 253, 208)

    # Main game colors
    MAIN_GREY_COLOR = (96, 96, 96)
    MAIN_OKRA_COLOR = (178, 134, 54)
    MAIN_PURPLE_COLOR = (84, 37, 90)

    TRANSITION_SCREEN_COLOR = WHITE_COLOR
    SCORE_FONT_COLOR = BLACK_COLOR
    ANSWER_FONT_COLOR = MAIN_PURPLE_COLOR
    LETTER_BUTTON_COLOR = CREAM_COLOR

    BACKGROUND_COLOR = WHITE_COLOR

    
    RESET_ALPHA = 255
    WRONG_LETTER_ALPHA = 100

    BUTTON_OBJECT_TYPE = "button"
    NON_INTERACTIVE_OBJECT_TYPE = "non_interactive"

    LETTER_BUTTON_FONT_SIZE = 40
    ANSWER_FONT_SIZE = 75
    SCORE_FONT_SIZE = 50

    FONT_FOLDER = 'fonts'

    RUBIKMONO_FONT = os.path.join(FONT_FOLDER, 'RubikMonoOne-Regular.ttf')
    LIBERATIONMONO_FONT = os.path.join(FONT_FOLDER, "LiberationMono-Bold.ttf")

    LETTER_BUTTON_FONT = Font(RUBIKMONO_FONT, LETTER_BUTTON_FONT_SIZE)
    ANSWER_FONT = Font(LIBERATIONMONO_FONT, ANSWER_FONT_SIZE)
    ANSWER_FONT.set_bold(True)
    SCORE_FONT = Font(RUBIKMONO_FONT, SCORE_FONT_SIZE)

    game_logo_no_text = pygame.image.load(os.path.join(IMAGE_FOLDER, "game_logo_no_text.png")).convert_alpha()
    scale_amount = (screen_size_x / 1.6) / game_logo_no_text.get_size()[0]
    game_logo_no_text_scaled = pygame.transform.smoothscale_by(game_logo_no_text, scale_amount)

    game_logo = pygame.image.load(os.path.join(IMAGE_FOLDER, "game_logo.png")).convert_alpha()
    main_menu_logo_scaled = pygame.transform.smoothscale_by(game_logo, 0.5)

    oprimagazine_logo_smallest = pygame.image.load(os.path.join(IMAGE_FOLDER, "logo_y_100.png")).convert_alpha()
    logo_y_size = oprimagazine_logo_smallest.get_size()[1]
    game_menu_y_size = 100
    game_menu_scale = 1 / (logo_y_size / game_menu_y_size)
    game_menu_logo_scaled = pygame.transform.smoothscale_by(oprimagazine_logo_smallest, game_menu_scale)
    
    score_screen_text_scale = 0.7

    game_over_text = pygame.image.load(os.path.join(IMAGE_FOLDER, "game_over_text.png")).convert_alpha()
    game_over_text_scaled = pygame.transform.smoothscale_by(game_over_text, score_screen_text_scale)

    you_win_text = pygame.image.load(os.path.join(IMAGE_FOLDER, "you_win_text.png")).convert_alpha()
    you_win_text_scaled = pygame.transform.smoothscale_by(you_win_text, score_screen_text_scale)
    
    HEART_FULL = 2
    HEART_HALF = 1
    HEART_EMPTY = 0

    heart_size = (50, 50)
    heart_full = pygame.image.load(os.path.join(IMAGE_FOLDER, "full_heart.png")).convert_alpha()
    heart_full_scaled = pygame.transform.smoothscale(heart_full, heart_size)
    heart_half = pygame.image.load(os.path.join(IMAGE_FOLDER, "half_heart.png")).convert_alpha()
    heart_half_scaled = pygame.transform.smoothscale(heart_half, heart_size)
    heart_empty = pygame.image.load(os.path.join(IMAGE_FOLDER, "empty_heart.png")).convert_alpha()
    heart_empty_scaled = pygame.transform.smoothscale(heart_empty, heart_size)
    
    start_easy_game_unpressed = pygame.image.load(os.path.join(IMAGE_FOLDER, "easy_button_unpressed.png")).convert_alpha()
    start_easy_button_size = start_easy_game_unpressed.get_size()
    start_easy_button_scale = 5
    start_easy_game_unpressed_scaled = pygame.transform.smoothscale(start_easy_game_unpressed, (int(start_easy_button_size[0] / start_easy_button_scale), int(start_easy_button_size[1] / start_easy_button_scale)))
    start_easy_game_pressed = pygame.image.load(os.path.join(IMAGE_FOLDER, "easy_button_pressed.png")).convert_alpha()
    start_easy_game_pressed_scaled = pygame.transform.smoothscale(start_easy_game_pressed, (int(start_easy_button_size[0] / start_easy_button_scale), int(start_easy_button_size[1] / start_easy_button_scale)))

    start_hard_game_unpressed = pygame.image.load(os.path.join(IMAGE_FOLDER, "hard_button_unpressed.png")).convert_alpha()
    start_hard_button_size = start_hard_game_unpressed.get_size()
    start_hard_button_scale = 5
    start_hard_game_unpressed_scaled = pygame.transform.smoothscale(start_hard_game_unpressed, (int(start_hard_button_size[0] / start_hard_button_scale), int(start_hard_button_size[1] / start_hard_button_scale)))
    start_hard_game_pressed = pygame.image.load(os.path.join(IMAGE_FOLDER, "hard_button_pressed.png")).convert_alpha()
    start_hard_game_pressed_scaled = pygame.transform.smoothscale(start_hard_game_pressed, (int(start_hard_button_size[0] / start_hard_button_scale), int(start_hard_button_size[1] / start_hard_button_scale)))

    back_button_unpressed = pygame.image.load(os.path.join(IMAGE_FOLDER, "x_back_button_unpressed.png")).convert_alpha()
    back_button_size = back_button_unpressed.get_size()
    back_button_scale = 8
    back_button_unpressed_scaled = pygame.transform.smoothscale(back_button_unpressed, (int(back_button_size[0] / back_button_scale), int(back_button_size[1] / back_button_scale)))
    back_button_pressed = pygame.image.load(os.path.join(IMAGE_FOLDER, "x_back_button_pressed.png")).convert_alpha()
    back_button_pressed_scaled = pygame.transform.smoothscale(back_button_pressed, (int(back_button_size[0] / back_button_scale), int(back_button_size[1] / back_button_scale)))

    next_button_unpressed = pygame.image.load(os.path.join(IMAGE_FOLDER, "next_button_unpressed.png")).convert_alpha()
    next_button_size = next_button_unpressed.get_size()
    next_button_scale = 1 / (start_easy_game_unpressed_scaled.get_size()[1] / next_button_size[1])
    next_button_unpressed_scaled = pygame.transform.smoothscale(next_button_unpressed, (int(next_button_size[0] / next_button_scale), int(next_button_size[1] / next_button_scale)))

    next_button_pressed = pygame.image.load(os.path.join(IMAGE_FOLDER, "next_button_pressed.png")).convert_alpha()
    next_button_pressed_scaled = pygame.transform.smoothscale(next_button_pressed, (int(next_button_size[0] / next_button_scale), int(next_button_size[1] / next_button_scale)))

    try_again_button_unpressed = pygame.image.load(os.path.join(IMAGE_FOLDER, "try_again_button_unpressed.png")).convert_alpha()
    try_again_button_size = try_again_button_unpressed.get_size()
    try_again_button_scale = 1 / (start_easy_game_unpressed_scaled.get_size()[1] / try_again_button_size[1])
    try_again_button_unpressed_scaled = pygame.transform.smoothscale(try_again_button_unpressed, (int(try_again_button_size[0] / try_again_button_scale), int(try_again_button_size[1] / try_again_button_scale)))
    
    try_again_button_pressed = pygame.image.load(os.path.join(IMAGE_FOLDER, "try_again_button_pressed.png")).convert_alpha()
    try_again_button_pressed_scaled = pygame.transform.smoothscale(try_again_button_pressed, (int(try_again_button_size[0] / try_again_button_scale), int(try_again_button_size[1] / try_again_button_scale)))

    letter_button_size = LETTER_BUTTON_FONT_SIZE * 2

    BUTTON_UNPRESSED = 0
    BUTTON_PRESSED_CORRECT = 1 # for letter buttons
    BUTTON_PRESSED_INCORRECT = 2 # for letter buttons
    BUTTON_PRESSED = 3

    letter_button_unpressed = pygame.image.load(os.path.join(IMAGE_FOLDER, "letter_button_unpressed.png")).convert_alpha()
    letter_button_unpressed_scaled = pygame.transform.smoothscale(letter_button_unpressed, (letter_button_size, letter_button_size))

    letter_button_pressed_incorrect = pygame.image.load(os.path.join(IMAGE_FOLDER, "letter_button_pressed_incorrect.png")).convert_alpha()
    letter_button_pressed_incorrect_scaled = pygame.transform.smoothscale(letter_button_pressed_incorrect, (letter_button_size, letter_button_size))

    letter_button_pressed_correct = pygame.image.load(os.path.join(IMAGE_FOLDER, "letter_button_pressed_correct.png")).convert_alpha()
    letter_button_pressed_correct_scaled = pygame.transform.smoothscale(letter_button_pressed_correct, (letter_button_size, letter_button_size))


    wordlist_file = "wordlist.txt"

    TICK_SPEED = 60
    clock = pygame.time.Clock()
    
    PAUSE_AFTER_WIN_TIMER = pygame.USEREVENT + 1

    TRANSITION_IN_TIMER = pygame.USEREVENT + 2
    TRANSITION_OUT_TIMER = pygame.USEREVENT + 3

    NO_TRANSITION = -1
    TRANSITION_IN = 0
    TRANSITION_OUT = 1
    SCORE_SCREEN_DELAY = 2

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
    score_object = ScoreObject(SCORE_ID, SCORE_FONT, SCORE_FONT_COLOR)

    heart_object = HeartObject(HEART_ID, heart_full_scaled, heart_half_scaled, heart_empty_scaled)

    EASY_MODE = "easy"
    HARD_MODE = "hard"

    game = Game(screen, answer_object, heart_object, score_object)

    START_EASY_BUTTON_ID = 'start_easy_button'
    START_HARD_BUTTON_ID = 'start_hard_button'
    BACK_BUTTON_ID = 'back_button'
    NEXT_BUTTON_ID = 'next_button'
    TRY_AGAIN_BUTTON_ID = 'try_again_button'
    LOGO_MAIN_ID = 'logo_main'
    LOGO_GAME_ID = 'logo_game'
    LOGO_BACKGROUND_ID = 'logo_background'
    GAME_OVER_ID = 'game_over'
    YOU_WIN_ID = 'you_win'

    BUTTON_SEPARATION_AMOUNT = 50

    start_easy_game_scaled_rect = start_easy_game_unpressed_scaled.get_rect()
    start_easy_button_function = game.start_easy_game
    start_easy_button = MenuButton(START_EASY_BUTTON_ID, start_easy_game_pressed_scaled, start_easy_game_unpressed_scaled, start_easy_game_scaled_rect, start_easy_button_function)
    
    start_hard_game_scaled_rect = start_hard_game_unpressed_scaled.get_rect()
    start_hard_button_function = game.start_hard_game
    start_hard_button = MenuButton(START_HARD_BUTTON_ID, start_hard_game_pressed_scaled, start_hard_game_unpressed_scaled, start_hard_game_scaled_rect, start_hard_button_function)
    
    back_button_scaled_rect = back_button_unpressed_scaled.get_rect()
    back_button_function = game.go_to_menu
    back_button_menu_pointer = START_MENU
    back_button = MenuButton(BACK_BUTTON_ID, back_button_pressed_scaled, back_button_unpressed_scaled, back_button_scaled_rect, back_button_function, back_button_menu_pointer)
    
    next_button_scaled_rect = next_button_unpressed_scaled.get_rect()
    next_button_function = game.go_to_menu
    next_button_menu_pointer = PLAY_MENU
    next_button = MenuButton(NEXT_BUTTON_ID, next_button_pressed_scaled, next_button_unpressed_scaled, next_button_scaled_rect, next_button_function, next_button_menu_pointer)
    
    try_again_button_scaled_rect = try_again_button_unpressed_scaled.get_rect()
    try_again_button_function = game.go_to_menu
    try_again_button_menu_pointer = PLAY_MENU
    try_again_button = MenuButton(TRY_AGAIN_BUTTON_ID, try_again_button_pressed_scaled, try_again_button_unpressed_scaled, try_again_button_scaled_rect, try_again_button_function, try_again_button_menu_pointer)

    logo_main_image = ImageObject(LOGO_MAIN_ID, main_menu_logo_scaled)
    
    logo_game_button_scaled_rect = game_menu_logo_scaled.get_rect()
    logo_game_button_function = game.go_to_website
    logo_game_button_menu_pointer = r"https://www.oprimagazine.com/"
    logo_game_button = MenuButton(LOGO_GAME_ID, game_menu_logo_scaled, game_menu_logo_scaled, logo_game_button_scaled_rect, logo_game_button_function, logo_game_button_menu_pointer)
    
    game_logo_no_text_scaled.set_alpha(10)
    game_logo_no_text_object = ImageObject(LOGO_BACKGROUND_ID, game_logo_no_text_scaled)

    game_over_object = ImageObject(GAME_OVER_ID, game_over_text_scaled)
    you_win_object = ImageObject(YOU_WIN_ID, you_win_text_scaled)


    game.add_object(START_MENU, start_easy_button)
    game.add_object(START_MENU, start_hard_button)
    game.add_object(START_MENU, logo_main_image)
    game.add_object(START_MENU, logo_game_button)

    game.add_object(PLAY_MENU, logo_game_button)
    game.add_object(PLAY_MENU, back_button)
    game.add_object(PLAY_MENU, game_logo_no_text_object)

    game.add_object(SCORE_MENU, next_button)
    game.add_object(SCORE_MENU, try_again_button)
    game.add_object(SCORE_MENU, game_over_object)
    game.add_object(SCORE_MENU, you_win_object)
    game.add_object(SCORE_MENU, back_button)

    game.reposition_objects((screen_size_x, screen_size_y))

    score_menu_effects = EffectController()
    score_menu_effects.add_effect(Fireworks(screen))

    pygame.event.set_allowed([
        pygame.MOUSEBUTTONDOWN,
        pygame.MOUSEBUTTONUP,
        pygame.KEYDOWN,
        pygame.KEYUP,
        pygame.QUIT]
        )

    asyncio.run(main())