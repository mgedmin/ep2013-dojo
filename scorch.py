#!/usr/bin/python
import os
import math
import pygame
from pygame.locals import QUIT, KEYDOWN, K_LEFT, K_RIGHT, K_SPACE

GRAVITY = 1 # pixels per frame
TURN_SPEED = 3 # degrees per keystroke
FRAMERATE = 30


class Tank(object):
    def __init__(self, x, y, direction=45):
        self.x = x
        self.y = y
        self.direction = direction

    def vector(self, magnitude=1):
        angle = math.radians(self.direction)
        return (magnitude * math.cos(angle), -magnitude * math.sin(angle))

    def rel_pos(self, magnitude=1):
        dx, dy = self.vector(magnitude)
        return (self.x + dx, self.y + dy)

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 0, 0), (self.x, self.y), 7)
        pygame.draw.line(surface, (255, 0, 0),
                         map(int, self.rel_pos(10)),
                         map(int, self.rel_pos(20)))

    def shoot(self):
        return Bullet(*(self.rel_pos(20) + self.vector(10)))


class Bullet(object):
    def __init__(self, x, y, dx=0, dy=0):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += GRAVITY

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), 5)


def main():
    pygame.init()
    pygame.display.set_caption('Py Scorched Earth')
    screen = pygame.display.set_mode((1024, 600))

    tank = Tank(30, 300)
    bullets = []

    clock = pygame.time.Clock()

    while True:
        # draw
        screen.fill((0, 0, 0))
        pygame.draw.line(screen, (255, 255, 255), (20, 300), (1000, 250))
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
                    bullets.append(tank.shoot())

        if pygame.key.get_pressed()[K_LEFT]:
            tank.direction += TURN_SPEED
        if pygame.key.get_pressed()[K_RIGHT]:
            tank.direction -= TURN_SPEED
        # move
        live_bullets = []
        for bullet in bullets:
            if bullet.y < screen.get_height():
                bullet.update()
                live_bullets.append(bullet)
        bullets = live_bullets
        # wait
        clock.tick(FRAMERATE)


if __name__ == '__main__':
    main()
    # avoid irritating pause during pygame cleanup
    os._exit(0)
