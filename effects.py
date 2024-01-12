import pygame
import random

class Effect:
    def __init__(self) -> None:
        pass
    

def create_fireworks_effect(screen: pygame.Surface):
    color_list = [(0, 0, 0)]
    firework_size = 2
    firework_rect = pygame.Rect(0, 0, firework_size, firework_size)
    pygame.draw.rect(screen, random.choice(color_list), firework_rect)

if __name__ == "__main__":
    pass