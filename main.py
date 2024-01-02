from __future__ import annotations
import pygame
import asyncio
import string
from typing import List
import random

"""

Create rect for regions in window for aligning objects


def button_function(letter):


for event in events:
    if event == keydown
        key = event.key
            if key in string.ascii
                button_function(key)

    if event == mousedown
        mousepos = getmousepos
        for button in buttons:
            if button.collide(mousepos):
                    button_function(button.letter)


"""

class Game:
    def __init__(self) -> None:
        self.answer = ''
        self.word_list = []
        self.guessed_letters = []
        self.objects: List[GameObject] = []

    def word_selection(self, word_list):
        self.word_list = word_list

    def new_game(self):
        self.answer = random.choice(self.word_list)
        self.guessed_letters = []

    def draw(self, screen):
        for object in self.objects:
            object.draw(screen)

    def add_object(self, object):
        self.objects.append(object)

    def check_letter(self, letter):
        letter = letter.upper()
        if letter not in self.guessed_letters:
            self.guessed_letters.append(letter)
            print(f"Guessed letter '{letter}'")
            game_won = True
            for letter in self.answer.upper():
                if letter not in self.guessed_letters:
                    game_won = False
            
            if game_won:
                self.game_won()
        else:
            print(f"Already guessed '{letter}'")

    def game_won(self):
        print("Game won!")
        self.new_game()


class GameObject:
    def __init__(self) -> None:
        self.rect: pygame.Rect = None
        self.surface: pygame.Surface = None

    def draw(self, screen):
        if self.surface is not None and self.rect is not None:
            screen.blit(self.surface, self.rect)

class LetterButton(GameObject):
    def __init__(self, letter, font: pygame.font.Font) -> None:
        super().__init__()
        self.letter = letter
        self.font = font
        self.surface = font.render(letter, True, (0, 0, 0))
        self.rect = self.surface.get_rect()

    def set_position(self, rect):
        self.rect = rect

async def main():


    random_words = ['potato', 'peruna', 'glass', 'bottle']
    game.word_selection(random_words)

    game.new_game()

    screen_size = screen.get_size()
    letter_counter = 0
    margin = 100
    for letter in string.ascii_uppercase:
        new_letter = LetterButton(letter, DEFAULT_FONT)
        game.add_object(new_letter)
        new_letter.rect.center = ((screen_size[0] - margin / 2) / len(string.ascii_uppercase)) * letter_counter + margin, screen_size[1] * 0.90
        letter_counter += 1

    running = True

    while running:
        events = pygame.event.get()
        mousepos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                key = chr(event.key).upper()
                if key in string.ascii_uppercase:
                    game.check_letter(key)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                for object in game.objects:
                    if object.rect.collidepoint(mousepos):
                        game.check_letter(object.letter)

        screen.fill(LIGHT_BLUE_COLOR)


        font_surface = DEFAULT_FONT.render(game.answer, True, BLACK_COLOR)
        font_surface_rect = font_surface.get_rect()
        font_surface_rect.center = screen_size[0] // 2, screen_size[1] // 2

        screen.blit(font_surface, font_surface_rect)

        game.draw(screen)

        pygame.display.flip()

        clock.tick(TICK_SPEED)

        await asyncio.sleep(0)


if __name__ == "__main__":
    pygame.init()
    
    SCREEN_WIDTH = 1024
    SCREEN_HEIGHT = 768

    TICK_SPEED = 60

    LIGHT_BLUE_COLOR = (138, 160, 242)
    BLACK_COLOR = (0, 0, 0)

    DEFAULT_FONT_SIZE = 50

    FONT_FILE_NAME = "MartianMono-VariableFont_wdth,wght.ttf"

    DEFAULT_FONT = pygame.font.Font(FONT_FILE_NAME, DEFAULT_FONT_SIZE)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    clock = pygame.time.Clock()

    game = Game()


    # game variables
    game.answer = 'glass'

    asyncio.run(main())