#!/usr/bin/python
import os
import math
import random
import pygame
from pygame.locals import QUIT, KEYDOWN, K_LEFT, K_RIGHT, K_SPACE, K_UP, K_DOWN
from collections import defaultdict

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
                           map(int, (self.x, self.y)), 7)
        if self.active:
            pygame.draw.line(surface, self.color,
                             map(int, self.rel_pos(10)),
                             map(int, self.rel_pos(10 + self.magnitude)))
        ##  pygame.draw.rect(surface, self.color,
        ##                   (self.x - 20, self.y - 20, 40, 40), 1)

    def shoot(self):
        return Bullet(*(self.rel_pos(COLLISION_RADIUS + 1) + self.vector(self.magnitude)),
                      color=self.color)


class Bullet(object):
    def __init__(self, x, y, dx=0, dy=0, color=None):
        self.x = self.old_x = x
        self.y = self.old_y = y
        self.dx = dx
        self.dy = dy
        self.color = color

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


class Game(object):
    def __init__(self):
        y1 = random.randrange(300-30, 300+30)
        y2 = random.randrange(300-30, 300+30)

        x1 = random.randrange(20, 300)
        x2 = 1024 - random.randrange(20, 300)

        colors = [RED, GREEN]
        random.shuffle(colors)
        self.tank1 = Tank(x1, y1 + (y2 - y1) * x1 / 1024.0,
                          color=colors[0])
        self.tank2 = Tank(x2, y1 + (y2 - y1) * x2 / 1024.0,
                          color=colors[1], direction=45+90)
        self.ground = [(0, y1), (1024, y2)]
        self.tanks = [self.tank1, self.tank2]
        self.bullets = []
        self.current_tank = self.tank1
        self.font = pygame.font.Font(None, 48)
        self.message = self.font.render("Go go go!", True, (255, 255, 255))
        self.message_ttl = FRAMERATE * 5
        self.over = False

    def draw(self, screen):
        if self.message:
            screen.blit(self.message, ((screen.get_width() - self.message.get_width())//2, 20))
            self.message_ttl -= 1
            if self.message_ttl < 0:
                self.message = None
                self.message_ttl = FRAMERATE * 5
        pygame.draw.line(screen, (255, 255, 255), *self.ground)
        for tank in self.tanks:
            tank.active = tank is self.current_tank
            tank.draw(screen)
        for bullet in self.bullets:
            bullet.draw(screen)

    def update(self, scores):
        live_bullets = []
        for bullet in self.bullets:
            if bullet.y > max(y for x, y in self.ground):
                continue
            bullet.update()
            for tank in self.tanks:
                if bullet.collides_with(tank):
                    tank.explode()
                    if bullet.color == tank.color: # aka suicide
                        self.message = self.font.render("YOU LOSE!", True, bullet.color)
                        scores[tank.color] -= 1
                    else:
                        self.message = self.font.render("YOU WIN!", True, bullet.color)
                        scores[bullet.color] += 1
                    self.over = True
                    break # bullet is gone gone gone
            else:
                live_bullets.append(bullet)
        self.bullets = live_bullets

    def shoot(self):
        self.bullets.append(self.current_tank.shoot())
        # hardcoded for two tanks
        self.current_tank = self.tanks[1 - self.tanks.index(self.current_tank)]


def main():
    pygame.init()
    pygame.display.set_caption('Py Scorched Earth')

    screen = pygame.display.set_mode((1024, 600))
    clock = pygame.time.Clock()

    game = Game()

    scores = defaultdict(int)
    font = pygame.font.Font(None, 24)

    while True:
        # draw
        screen.fill((0, 0, 0))
        screen.blit(font.render("Red: %d" % scores[RED], True, RED), (10, 10))
        text = font.render("Green: %d" % scores[GREEN], True, GREEN)
        screen.blit(text, (screen.get_width()-10-text.get_width(), 10))
        game.draw(screen)
        pygame.display.flip()
        # process events
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.unicode in ('q', 'Q'):
                    return
                if event.unicode in ('n', 'N'):
                    game = Game()
                if event.key == K_SPACE and not game.over:
                    game.shoot()

        if not game.over:
            current_tank = game.current_tank
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
        game.update(scores)
        if game.over and game.message is None:
            game = Game()
        # wait
        clock.tick(FRAMERATE)


if __name__ == '__main__':
    main()
    # avoid irritating pause during pygame cleanup
    os._exit(0)
