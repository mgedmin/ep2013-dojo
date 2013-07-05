#!/usr/bin/python
import os
import math
import pygame
from pygame.locals import QUIT, KEYDOWN, K_LEFT, K_RIGHT, K_SPACE, K_UP, K_DOWN

GRAVITY = 1 # pixels per frame
TURN_SPEED = 3 # degrees per frame
MAG_SPEED = 1 # pixels per frame per frame
MIN_MAGNITUDE = 1
MAX_MAGNITUDE = 50
FRAMERATE = 30
COLLISION_RADIUS = 10 # pixels


RED = (255, 0, 0)
GREEN = (0, 255, 0)

DEAD_TANK_COLOR = (64, 64, 64)


class Tank(object):
    def __init__(self, x, y, direction=45, magnitude=10, color=RED):
        self.x = x
        self.y = y
        self.direction = direction
        self.magnitude = magnitude
        self.color = color
        self.active = False
        self.alive = True

    def explode(self):
        self.alive = False

    def vector(self, magnitude=1):
        angle = math.radians(self.direction)
        return (magnitude * math.cos(angle), -magnitude * math.sin(angle))

    def rel_pos(self, magnitude=1):
        dx, dy = self.vector(magnitude)
        return (self.x + dx, self.y + dy)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color if self.alive else DEAD_TANK_COLOR,
                           (self.x, self.y), 7)
        if self.active and self.alive:
            pygame.draw.line(surface, self.color,
                             map(int, self.rel_pos(10)),
                             map(int, self.rel_pos(10 + self.magnitude)))
        ##  pygame.draw.rect(surface, self.color,
        ##                   (self.x - 20, self.y - 20, 40, 40), 1)

    def shoot(self):
        return Bullet(*(self.rel_pos(10) + self.vector(self.magnitude)))


class Bullet(object):
    def __init__(self, x, y, dx=0, dy=0):
        self.x = self.old_x = x
        self.y = self.old_y = y
        self.dx = dx
        self.dy = dy

    def update(self):
        self.old_x = self.x
        self.old_y = self.y
        self.x += self.dx
        self.y += self.dy
        self.dy += GRAVITY

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), 3)

    def collides_with(self, tank):
        # use brute force damnit
        x = self.old_x
        y = self.old_y
        if math.hypot(x - tank.x, y - tank.y) < COLLISION_RADIUS:
            return True
        dx = self.x - self.old_x
        dy = self.y - self.old_y
        length = math.hypot(dx, dy)
        for n in range(int(length)):
            x += dx / length
            y += dy / length
            if math.hypot(x - tank.x, y - tank.y) < COLLISION_RADIUS:
                return True
        return False


def collides(bullet, tank):
    return math.hypot(tank.x - bullet.x, tank.y - bullet.y) < COLLISION_RADIUS


def main():
    pygame.init()
    pygame.display.set_caption('Py Scorched Earth')
    screen = pygame.display.set_mode((1024, 600))

    tank1 = Tank(30, 290)
    tank2 = Tank(900, 243, direction=45+90, color=GREEN)
    tanks = [tank1, tank2]
    bullets = []

    current_tank = tank1 # focus tracking ;)

    clock = pygame.time.Clock()

    while True:
        # draw
        screen.fill((0, 0, 0))
        pygame.draw.line(screen, (255, 255, 255), (20, 300), (1000, 250))
        for tank in tanks:
            tank.active = tank is current_tank
            tank.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)
        pygame.display.flip()
        # process events
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.unicode in ('q', 'Q'):
                    return
                if event.key == K_SPACE:
                    bullets.append(current_tank.shoot())
                    # hardcoded for two tanks
                    current_tank = tanks[1 - tanks.index(current_tank)]

        if pygame.key.get_pressed()[K_UP]:
            current_tank.magnitude += MAG_SPEED
            current_tank.magnitude = min(current_tank.magnitude, MAX_MAGNITUDE)
        if pygame.key.get_pressed()[K_DOWN]:
            current_tank.magnitude -= MAG_SPEED
            current_tank.magnitude = max(current_tank.magnitude, MIN_MAGNITUDE)
        if pygame.key.get_pressed()[K_LEFT]:
            current_tank.direction += TURN_SPEED
        if pygame.key.get_pressed()[K_RIGHT]:
            current_tank.direction -= TURN_SPEED
        # move
        live_bullets = []
        for bullet in bullets:
            if bullet.y > screen.get_height():
                continue
            bullet.update()
            for tank in tanks:
                if bullet.collides_with(tank):
                    tank.explode()
                    continue # bullet is gone gone gone
            live_bullets.append(bullet)
        bullets = live_bullets
        # wait
        clock.tick(FRAMERATE)


if __name__ == '__main__':
    main()
    # avoid irritating pause during pygame cleanup
    os._exit(0)
