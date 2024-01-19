from __future__ import annotations
import pygame
import pygame.gfxdraw
import random
from typing import List, Dict
import math
from itertools import cycle
import time

random.seed()

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
        self.flash_list: List[tuple[pygame.Surface, int, int]] = [] # flash surface and flash start tick
        self.flash_update_interval = 1000 / 60
        self.explosion_lifetime = 1500
        self.explosion_object: Explosion = Explosion(self.screen, self.explosion_lifetime)
        self.explosion_object.init_particles()
        self.last_update = 0

    def new_instance(self):
        x_padding = 100
        screen_x, screen_y = self.screen.get_size()
        random_x = random.randrange(x_padding, screen_x - x_padding)
        lifetime = random.randrange(self.min_lifetime, self.max_lifetime)
        speed = random.randrange(self.min_speed * 10, self.max_speed * 10) / 10
        new_firework = FireworkInstance(self.screen, lifetime, (random_x, screen_y + 5), (random.choice(self.firework_colors)), speed)
        self.instances.append(new_firework)

    def update(self):
        current_time = time.time()
        delta_time = current_time - self.last_update
        self.last_update = current_time
        ticks = pygame.time.get_ticks()
        if len(self.instances) < self.max_effects and ticks - self.last_launch >= self.next_launch:
            self.new_instance()
            self.next_launch = ticks + random.randrange(self.min_launch_delay, self.max_launch_delay)
        for instance in self.instances:
            instance.update()

        for instance in self.instances:
            if instance.is_expired():
                self.firework_explosion(self.randomized_dark_color(), instance.rect)
        
        self.instances = [instance for instance in self.instances if not instance.is_expired()]

        self.explosion_object.update()


    def randomized_dark_color(self):
        high_range = (150, 255)
        full_range = (0, 255)
        low_range = (0, 100)
        red_range, green_range, blue_range = random.sample([high_range, full_range, low_range], 3)
        return (random.randint(*red_range), random.randint(*green_range), random.randint(*blue_range))

    
    def firework_explosion(self, color, center):
        flash_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        flash_surface.fill(color)
        self.flash_list.append({'surface': flash_surface, 'start_tick': pygame.time.get_ticks(), 'last_update': 0})
        self.explosion_object.new_explosion(center, color)
        
    def draw(self, screen):
        for instance in self.instances:
            instance.draw(screen)
        ticks = pygame.time.get_ticks()
        self.flash_list = [flash for flash in self.flash_list if not ticks - flash['start_tick'] >= self.flash_lifetime]
        for flash in self.flash_list:
            flash_surface = flash['surface']
            elapsed_time = ticks - flash['start_tick']
            if ticks - flash['last_update'] >= self.flash_update_interval:
                alpha = self.flash_start_alpha - self.flash_start_alpha * (elapsed_time / self.flash_lifetime)
                flash_surface.set_alpha(alpha)
                self.screen.blit(flash_surface, flash_surface.get_rect())
                flash['last_update'] = ticks

        self.explosion_object.draw(screen)


class EffectInstance:
    def __init__(self, screen: pygame.Surface, lifetime, position) -> None:
        self.screen = screen
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


class Explosion:
    particle_list: List[Dict] = []
    particle_cycle = cycle(particle_list)

    def __init__(self, screen, lifetime) -> None:
        self.screen = screen
        self.lifetime = lifetime
        self.color = None
        self.start_age = pygame.time.get_ticks()
        self.surface: pygame.Surface = None
        self.rect: pygame.Rect = None

        self.particle_amount = 30
        self.max_speed = 15
        self.min_speed = 1
        self.particle_size = 6
        self.particle_update_list = []

    def set_particle_color(self, surface: pygame.Surface, color):
        width, height = surface.get_size()
        red, green, blue = color
        for x in range(width):
            for y in range(height):
                alpha = surface.get_at((x, y ))[3]
                surface.set_at((x, y), pygame.Color(red, green, blue, alpha))

    def new_explosion(self, position, color):
        for _ in range(self.particle_amount):
            new_particle = next(self.particle_cycle)
            new_particle['surface'].set_alpha(255)
            self.set_particle_color(new_particle['surface'], color)
            speed = random.randrange(self.min_speed * 10, self.max_speed * 10) / 10
            new_particle['position']['x'], new_particle['position']['y'] = position
            new_particle['velocity']['x'] = speed * new_particle['direction']['x']
            new_particle['velocity']['y'] = speed * new_particle['direction']['y']
            new_particle['lifetime'] = self.lifetime
            new_particle['start_tick'] = pygame.time.get_ticks()
            new_particle['color'] = color
            self.particle_update_list.append(new_particle)
        
    def init_particles(self):
        if not self.particle_list:
            particles_to_prerender = self.particle_amount * 5
            angle_increment = 360 / self.particle_amount
            for i in range(particles_to_prerender):
                random_angle_shift = random.randrange(0, angle_increment // 2)
                angle = (i * angle_increment + random_angle_shift) % 360
                angle_radians = math.radians(angle)
                direction = (math.cos(angle_radians), math.sin(angle_radians))
                new_particle = self.create_particle(direction)
                self.particle_list.append(new_particle)

            self.particle_cycle = cycle(self.particle_list)
        
    def create_particle(self, direction):
        color = (0, 0, 0)
        position = (-50, -50)
        surface_size = self.particle_size * 2
        firework_surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
        pygame.draw.circle(firework_surface, color, (self.particle_size, self.particle_size), self.particle_size)
        return {"surface": firework_surface, "direction": {'x': direction[0], 'y': direction[1]}, "velocity": {'x': 0, 'y': 0}, "position": {'x': position[0], 'y': position[1], "lifetime": 0, "color": (0, 0, 0)}}

    def update(self):
        air_drag = 0.98
        gravity = 0.1
        ticks = pygame.time.get_ticks()
        for particle in self.particle_update_list:
            elapsed_time = (ticks - particle["start_tick"])
            particle["velocity"]['y'] += gravity * (elapsed_time / 1000)**2
            particle["velocity"]['x'] *= air_drag
            particle["velocity"]['y'] *= air_drag
            particle["position"]['x'] += particle["velocity"]['x']
            particle["position"]['y'] += particle["velocity"]['y']
            if elapsed_time >= particle["lifetime"]:
                self.particle_update_list.remove(particle)

    def draw(self, screen: pygame.Surface):
        for particle in self.particle_update_list:
            screen.blit(particle['surface'], (int(particle["position"]['x']), int(particle["position"]['y'])))
            

class FireworkInstance(EffectInstance):
    def __init__(self, screen, lifetime, position, color, speed) -> None:
        super().__init__(screen, lifetime, position)
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
    