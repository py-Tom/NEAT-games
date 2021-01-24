"""
Neural Network learns to drive micro car.
"""
import math
import os
import random
import time

import neat
import pygame

WIN_WIDTH = 600
WIN_HEIGHT = 800
gen_score = 0
pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 50)

curr_folder = os.path.dirname(__file__)
car_img = pygame.image.load(os.path.join(curr_folder, "images", "car.png"))
road_img = pygame.image.load(os.path.join(curr_folder, "images", "road.png"))
cone_img = pygame.image.load(os.path.join(curr_folder, "images", "cone.png"))
block_img = pygame.image.load(os.path.join(curr_folder, "images", "roadblock2.png"))


class Car:
    # img = car_img
    max_rotation = 60
    rot_vel = 10

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.v_x = 0
        self.v_y = -10
        self.rot = 0
        self.img = car_img

    def rotation(self, turn):
        if turn == "left":
            self.rot += self.rot_vel
        if turn == "right":
            self.rot -= self.rot_vel

        if self.rot <= -self.max_rotation:
            self.rot = -self.max_rotation
        if self.rot >= self.max_rotation:
            self.rot = self.max_rotation

        if self.rot <= 0.5 and self.rot >= -0.5:
            self.v_x = 0
        else:
            self.v_x = self.v_y * math.tan(math.radians(self.rot))

    def move(self):

        if self.v_x >= 10:
            self.v_x = 10
        if self.v_x <= -10:
            self.v_x = -10

        self.x += self.v_x

    def draw(self, win):
        rotated_image = pygame.transform.rotate(self.img, self.rot)
        new_rect = rotated_image.get_rect(
            center=self.img.get_rect(topleft=(self.x, self.y)).center
        )
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Road:
    def __init__(self, x=0):
        self.v = 10
        self.img = road_img
        self.height = self.img.get_height()
        self.x = x
        self.y1 = 0
        self.y2 = self.height

    def move(self):
        self.y1 += self.v
        self.y2 += self.v

        if self.y1 - self.height > 0:
            self.y1 = self.y2 - self.height

        if self.y2 - self.height > 0:
            self.y2 = self.y1 - self.height

    def draw(self, win):
        win.blit(self.img, (self.x, self.y1))
        win.blit(self.img, (self.x, self.y2))


class Block:
    def __init__(self, y):
        self.gap = 200
        self.v = 10
        self.img = block_img
        self.y = y
        self.width = 0

        self.left = 0
        self.right = 0
        self.block_left = self.img
        self.block_right = self.img

        self.passed = False
        self.set_width()

    def set_width(self):
        self.width = random.randrange(50, 350)
        self.left = self.width - self.block_left.get_width()
        self.right = self.width + self.gap

    def move(self):
        self.y += self.v

    def draw(self, win):
        win.blit(self.block_left, (self.left, self.y))
        win.blit(self.block_right, (self.right, self.y))

    def collide(self, car):
        car_mask = car.get_mask()
        left_mask = pygame.mask.from_surface(self.block_left)
        right_mask = pygame.mask.from_surface(self.block_right)

        left_offset = (self.left - round(car.x), self.y - car.y)
        right_offset = (self.right - round(car.x), self.y - car.y)

        l_point = car_mask.overlap(left_mask, left_offset)
        r_point = car_mask.overlap(right_mask, right_offset)

        if l_point or r_point:
            return True

        return False


def draw_window(win, cars, road, blocks, score, gen_score, alive_score):
    road.draw(win)
    for car in cars:
        car.draw(win)
    for block in blocks:
        block.draw(win)

    text_score = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text_score, (WIN_WIDTH - 10 - text_score.get_width(), 10))

    text_gen = STAT_FONT.render("Gen: " + str(gen_score), 1, (255, 255, 255))
    win.blit(text_gen, (10, 10))

    text_alive = STAT_FONT.render("Alive: " + str(alive_score), 1, (255, 255, 255))
    win.blit(text_alive, (10, 50))

    pygame.display.update()


def main(genomes, config):
    global gen_score
    gen_score += 1
    run = True
    clock = pygame.time.Clock()

    road = Road()
    blocks = [Block(-500)]

    cars = []
    nets = []
    ge = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        cars.append(Car(300, 700))
        g.fitness = 0
        ge.append(g)

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    score = 0
    while run:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

            """if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                turn = "left"
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                turn = "right"
            else:
                continue"""

        block_ind = 0
        if len(cars) > 0:
            if (
                len(cars) > 1
                and cars[0].y > cars[0].y + blocks[0].block_left.get_height()
            ):
                block_ind = 1
        else:
            run = False
            break

        for n, car in enumerate(cars):

            ge[n].fitness += 0.1
            output = nets[n].activate(
                (
                    car.x,
                    abs(car.x - blocks[block_ind].left),
                    abs(car.x - blocks[block_ind].right),
                )
            )

            if output[0] > 0:
                turn = "left"
            elif output[0] <= 0:
                turn = "right"
            else:
                turn = None

            car.rotation(turn)
            car.move()

        add_block = False
        rem = []
        for block in blocks:
            for n, car in enumerate(cars):
                if block.collide(car):
                    ge[n].fitness -= 1
                    cars.pop(n)
                    nets.pop(n)
                    ge.pop(n)

                if not block.passed and block.y > car.y:
                    block.passed = True
                    add_block = True

            block.move()

            if block.y + block.block_left.get_height() > WIN_HEIGHT + 100:
                rem.append(block)

        if add_block:
            score += 1
            for g in ge:
                g.fitness += 5
            blocks.append(Block(-100))

        for r in rem:
            blocks.remove(r)

        for n, car in enumerate(cars):
            if car.x + car.img.get_width() >= 540 or car.x < 60:
                cars.pop(n)
                nets.pop(n)
                ge.pop(n)

        road.move()
        alive_score = len(cars)
        draw_window(win, cars, road, blocks, score, gen_score, alive_score)


def run(config_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-microcar.txt")
    run(config_path)
