from __future__ import annotations
import pygame
import pygame.gfxdraw
import random
from typing import List, Dict
import math

PARTICLE_SURFACES = 'particle_surfaces'
PARTICLE_RECTS = 'particle_rects'

MAIN_GREY_COLOR = (96, 96, 96)
MAIN_OKRA_COLOR = (178, 134, 54)
MAIN_PURPLE_COLOR = (84, 37, 90)

BLACK_COLOR = (0, 0, 0)
WHITE_COLOR = (255, 255, 255)
RED_COLOR = (255, 0, 0)
GREEN_COLOR = (0, 255, 0)
BLUE_COLOR = (0, 0, 255)

class EffectController:
    def __init__(self) -> None:
        self.managed_effects: List[Effect] = []
        self.effects_active = False

    def add_effect(self, effect: Effect):
        self.managed_effects.append(effect)

    def clear_effects(self):
        self.managed_effects = []

    def activate_effects(self):
        self.effects_active = True

    def deactivate_effects(self):
        self.effects_active = False
        for effect in self.managed_effects:
            effect.reset_effects()

    def update(self):
        if self.effects_active:
            for effect in self.managed_effects:
                effect.update()

    def draw(self, screen):
        if self.effects_active:
            for effect in self.managed_effects:
                effect.draw(screen)

class Effect:
    next_particle_index = 0

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.instances: List[EffectInstance] = []

    def update(self):
        self.instances = [instance for instance in self.instances if not instance.is_expired()]
        for instance in self.instances:
            instance.update()

    def draw(self, screen):
        for instance in self.instances:
            instance.draw(screen)

    def reset_effects(self):
        self.instances = []
            
    @classmethod
    def get_next_particle_index(cls): # in string so it can be used in dict
        index = cls.next_particle_index
        cls.next_particle_index += 1
        return str(index)


class Fireworks(Effect):
    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen)
        self.firework_colors = [BLACK_COLOR, MAIN_OKRA_COLOR, MAIN_PURPLE_COLOR]
        self.flash_colors = [MAIN_OKRA_COLOR, MAIN_PURPLE_COLOR, RED_COLOR, GREEN_COLOR, BLUE_COLOR]
        self.flash_start_alpha = 25
        self.max_speed = 9
        self.min_speed = 6
        self.max_effects = 3
        self.max_lifetime = 1250
        self.min_lifetime = 750
        self.max_launch_delay = 1250
        self.min_launch_delay = 750
        self.next_launch = 0
        self.last_launch = 0
        self.flash_lifetime = 200
        self.flash_list: List[tuple[pygame.Surface, int]] = [] # flash surface and flash start tick
        self.explosion_lifetime = 1000
        self.explosion_list: List[Explosion] = []

    def new_instance(self):
        x_padding = 50
        screen_x, screen_y = self.screen.get_size()
        random_x = random.randrange(x_padding, screen_x - x_padding)
        lifetime = random.randrange(self.min_lifetime, self.max_lifetime)
        speed = random.randrange(self.min_speed * 10, self.max_speed * 10) / 10
        new_firework = FireworkInstance(lifetime, (random_x, screen_y + 5), random.choice(self.firework_colors), speed)
        self.instances.append(new_firework)

    def update(self):
        ticks = pygame.time.get_ticks()
        if ticks - self.last_launch >= self.next_launch and len(self.instances) < self.max_effects:
            self.new_instance()
            self.next_launch = ticks + random.randrange(self.min_launch_delay, self.max_launch_delay)
        for instance in self.instances:
            instance.update()

        for instance in self.instances:
            if instance.is_expired():
                self.firework_explosion(random.choice(self.flash_colors), instance.rect)
        
        self.instances = [instance for instance in self.instances if not instance.is_expired()]

        for explosion in self.explosion_list:
            explosion.update()
    
    def firework_explosion(self, color, center):
        flash_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        flash_surface.fill(color)
        self.flash_list.append((flash_surface, pygame.time.get_ticks()))
        new_explosion = Explosion(self.explosion_lifetime, center, color)
        self.explosion_list.append(new_explosion)
        
    def draw(self, screen):
        for instance in self.instances:
            instance.draw(screen)
        ticks = pygame.time.get_ticks()
        self.flash_list = [flash for flash in self.flash_list if not ticks - flash[1] >= self.flash_lifetime]
        for flash in self.flash_list:
            flash_surface = flash[0]
            elapsed_time = ticks - flash[1]
            alpha = self.flash_start_alpha - self.flash_start_alpha * (elapsed_time / self.flash_lifetime)
            flash_surface.set_alpha(alpha)
            self.screen.blit(flash_surface, flash_surface.get_rect())

        self.explosion_list = [explosion for explosion in self.explosion_list if not explosion.is_expired()]
        for explosion in self.explosion_list:
            explosion.draw(screen)


class EffectInstance:
    def __init__(self, lifetime, position) -> None:
        self.lifetime = lifetime
        self.position = position
        self.color = None
        self.start_age = pygame.time.get_ticks()
        self.surface: pygame.Surface = None
        self.rect: pygame.Rect = None

    def update(self):
        pass

    def is_expired(self):
        ticks = pygame.time.get_ticks()
        return ticks - self.start_age >= self.lifetime
    
    def draw(self, screen):
        if self.surface and self.rect:
            screen.blit(self.surface, self.rect)


class Explosion(EffectInstance):
    def __init__(self, lifetime, position, color) -> None:
        super().__init__(lifetime, position)
        self.particle_list = []
        self.max_particles = 15
        self.min_particles = 10
        self.max_speed = 6
        self.min_speed = 4
        self.particle_amount = random.randrange(self.min_particles, self.max_particles + 1)
        angle_increment = 360 / self.particle_amount
        for i in range(self.particle_amount):
            random_angle_shift = random.randrange(0, angle_increment // 2)
            angle = (i * angle_increment + random_angle_shift) % 360
            angle_radians = math.radians(angle)
            direction = (math.cos(angle_radians), math.sin(angle_radians))
            new_particle = self.create_particle(position, color, direction)
            self.particle_list.append(new_particle)
        
    def create_particle(self, position, color, direction):
        surface_size = 3
        firework_size = 1
        firework_surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
        pygame.draw.circle(firework_surface, color, (firework_size, firework_size), firework_size)
        speed = random.randrange(self.min_speed * 10, self.max_speed * 10) / 10
        return {"surface": firework_surface, "velocity": {'x': direction[0] * speed, 'y': direction[1] * speed}, "position": {'x': position[0], 'y': position[1]}}

    def update(self):
        air_drag = 0.98
        gravity = 0.1
        ticks = pygame.time.get_ticks()
        for particle in self.particle_list:
            elapsed_time = (ticks - self.start_age) / 1000
            particle["velocity"]['y'] += gravity * elapsed_time**2
            particle["velocity"]['x'] *= air_drag
            particle["velocity"]['y'] *= air_drag
            particle["position"]['x'] += particle["velocity"]['x']
            particle["position"]['y'] += particle["velocity"]['y']

    def draw(self, screen: pygame.Surface):
        for particle in self.particle_list:
            screen.blit(particle['surface'], (int(particle["position"]['x']), int(particle["position"]['y'])))
            

class FireworkInstance(EffectInstance):
    def __init__(self, lifetime, position, color, speed) -> None:
        super().__init__(lifetime, position)
        self.speed = speed
        self.color = color
        self.x_variation = random.randrange(-1, 1) * 0.3
        surface_size = 9
        firework_size = surface_size // 2
        firework_surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
        pygame.draw.circle(firework_surface, color, (firework_size, firework_size), firework_size)
        firework_rect = firework_surface.get_rect()
        firework_rect.center = position
        self.surface = firework_surface
        self.rect = firework_rect

    def update(self):
        self.rect = self.rect[0] + self.x_variation, self.rect[1] - self.speed


if __name__ == "__main__":
    pygame.init()
    
    screen_size_x, screen_size_y = (1024, 768)

    screen = pygame.display.set_mode((screen_size_x, screen_size_y), pygame.RESIZABLE)

    TICK_SPEED = 60

    clock = pygame.time.Clock()

    running = True

    score_menu_effects = EffectController()
    score_menu_effects.add_effect(Fireworks(screen))

    while running:
        events = pygame.event.get()
        mousepos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    score_menu_effects.activate_effects()
                if event.button == 3: # Right click
                    score_menu_effects.deactivate_effects()

    
        screen.fill((100, 100, 100))

        score_menu_effects.update()
        score_menu_effects.draw(screen)

        pygame.display.flip()

        clock.tick(TICK_SPEED)
    