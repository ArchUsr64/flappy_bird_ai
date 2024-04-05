import sys
import random
import math
from copy import deepcopy

random.seed(1)

# Disables logs leaking from pygame
sys.stdout = None
sys.stderr = None
import pygame
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

class Matrix:
    def __init__(self, data: [[int]]):
        self.row_count = len(data)
        self.col_count = len(data[0])
        self.data = data
    @classmethod
    def from_size(self, row_count: int, col_count: int, rand = False):
        if rand:
            data = [[random.uniform(-1, 1) for _ in range(col_count)] for _ in range(row_count)]
        else:
            data = [[0] * col_count for _ in range(row_count)]
        return Matrix(data)
    @classmethod
    def from_row(self, row: [int]):
            return Matrix([row])
    def __mul__(self, other):
        if self.col_count != other.row_count:
            raise Exception(f"Mismatched order of Matrices for multiplication {(self.row_count, self.col_count)} vs {(other.row_count, other.col_count)}")
        res = [[0 for _ in range(other.col_count)] for _ in range(self.row_count)]
        for i in range(self.row_count):
            for j in range(other.col_count):
                for k in range(self.col_count):
                    res[i][j] += self.data[i][k] * other.data[k][j]
        return Matrix(res)
    def __add__(self, other):
        if self.row_count != other.row_count or self.col_count != other.col_count:
            raise Exception(f"Mismatched order of Matrices for addition {(self.row_count, self.col_count)} vs {(other.row_count, other.col_count)}")
        res = [[0 for _ in range(self.col_count)] for _ in range(self.row_count)]
        for i in range(self.row_count):
            for j in range(self.col_count):
                res[i][j] = self.data[i][j] + other.data[i][j]
        return Matrix(res)
    def sigmoid(self):
        if self.row_count != 1:
            raise Exception("Can't apply activation function for non row matrix")
        for i in range(self.col_count):
            self.data[0][i] = 1 / (1 + math.e ** -self.data[0][i])
    def mutate(self, fuzz_factor: float):
        for row in self.data:
            for i in range(len(row)):
                row[i] += random.uniform(-fuzz_factor, fuzz_factor)
                row[i] *= 1 + random.uniform(-fuzz_factor, fuzz_factor)

class NN:
    def __init__(self, architecture: [int], rand = False):
        self.arch = architecture
        self.layers = []
        self.biases = []
        for i in range(len(architecture) - 1):
            self.layers.append(Matrix.from_size(architecture[i], architecture[i + 1], rand))
            self.biases.append(Matrix.from_size(1, architecture[i + 1], rand))
    def solve(self, input: Matrix) -> Matrix:
        temp = input
        for layer, bias in zip(self.layers, self.biases):
            temp = temp * layer
            temp = temp + bias
            temp.sigmoid()
        return temp
    def mutate(self, fuzz_factor: float):
        for layer in self.layers:
            layer.mutate(fuzz_factor)
        for bias in self.biases:
            bias.mutate(fuzz_factor)
    def __str__(self):
        res = f"Arch: {self.arch} | "
        for i, layer in enumerate(self.layers):
            res += f"L#{i}: {layer.data}, "
        res = res[:-1]
        res += "| "
        for i, bias in enumerate(self.biases):
            res += f"B#{i}: {bias.data}, "
        return res[:-2]

pygame.init()

DISPLAY = pygame.display.set_mode((640, 480), vsync = 1)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)

GRAVITY: float = -0.001
TERMINAL_VELOCITY: float = 0.05
JUMP_VELCOITY: float = 0.015
OBSTACLE_SPEED: float = 0.002
OBSTACLE_DENSITY: int = 5
BALL_RADIUS: float = 0.01
FPS: int = 60

def lerp(x, min_x, max_x, min_out, max_out):
    x -= min_x
    x /= (max_x - min_x)
    x *= (max_out - min_out)
    x += min_out
    return x

def restrict(value, range_min, range_max):
    value = max(value, range_min)
    value = min(value, range_max)
    return value

class Obstacle:
    def __init__(self, height, gap):
        self.top = height + gap
        self.bottom = height
        self.gap = gap
        self.mid = (self.top + self.bottom) / 2
    def render(self, pos_x):
        pos_x = lerp(pos_x, 0, 1, 0, DISPLAY.get_width())
        top = lerp(self.top, 0, 1, DISPLAY.get_height(), 0)
        bottom = lerp(self.bottom, 0, 1, DISPLAY.get_height(), 0)
        line_width = int(lerp(BALL_RADIUS, 0, 1, 0, DISPLAY.get_width()))
        pygame.draw.line(DISPLAY, COLOR_BLUE, (pos_x, 0), (pos_x, top), line_width)
        pygame.draw.line(DISPLAY, COLOR_BLUE, (pos_x, bottom), (pos_x, DISPLAY.get_height()), line_width)
    def random():
        return Obstacle(random.uniform(0.2, 0.5), random.uniform(0.15, 0.3))
    def collision(self, pos) -> bool:
        return pos >= self.top or pos <= self.bottom

class Agent:
    def __init__(self, color: tuple[int, int, int]):
        self.color = color
        self.pos: float = 0.5
        self.velocity: float = 0
        self.tick_count: int = 0
        self.dead: bool = False
    def tick(self):
        if not self.dead:
            self.pos += self.velocity
            if self.pos <= 0:
                self.pos = 0
                self.dead = True
            self.velocity += GRAVITY
            self.velocity = restrict(self.velocity, -TERMINAL_VELOCITY, TERMINAL_VELOCITY)
            self.tick_count += 1
    def jump(self):
        self.velocity = JUMP_VELCOITY
    def render(self):
        radius = BALL_RADIUS
        pos_x = DISPLAY.get_width() / 2
        if self.dead:
            radius /= 2
            pos_x = 0
        pygame.draw.circle(DISPLAY, self.color, (pos_x, lerp(self.pos, 0, 1, DISPLAY.get_height(), 0)), lerp(radius, 0, 1, 0, DISPLAY.get_width()))
    def kill(self):
        self.dead = True

class Game:
    def __init__(self):
        # Scales form 0 to 1
        self.agents: [Agent] = []
        self.tick_count: int = 0
        self.obstacles: [Obstacle] = [Obstacle.random() for _ in range(OBSTACLE_DENSITY)]
        self.obstacle_positions = [0.5 + (i + 1) / OBSTACLE_DENSITY for i in range(0, OBSTACLE_DENSITY + 1)]
    def add_player(self, player: Agent):
        self.agents.append(player)
    def tick(self):
        # Obstacle generation
        for i in range(len(self.obstacle_positions)):
            self.obstacle_positions[i] -= OBSTACLE_SPEED
        for i in range(len(self.obstacle_positions)):
            if self.obstacle_positions[i] <= 0:
                self.obstacle_positions.pop(i)
                self.obstacles.pop(i)
                self.obstacles.append(Obstacle.random())
                self.obstacle_positions.append(1 + 1 / OBSTACLE_DENSITY)
        # Physics
        for agent in self.agents:
            agent.tick()
        # Collision
        for i, obstacle in enumerate(self.obstacles):
            obstacle_pos = self.obstacle_positions[i]
            if obstacle_pos >= 0.5 - BALL_RADIUS and obstacle_pos <= 0.5 + BALL_RADIUS :
                for agent in self.agents:
                    if obstacle.collision(agent.pos):
                        agent.kill()
        self.tick_count += 1
    def next_obstacle_index(self) -> int:
        index = 0
        while self.obstacle_positions[index] <= 0.5:
            index += 1
        return index
    def over(self) -> bool:
        for agent in self.agents:
            if not agent.dead:
                return False
        return True
    def render(self):
        for i, obstacle in enumerate(self.obstacles):
            obstacle.render(self.obstacle_positions[i])
        for agent in self.agents:
            agent.render()

def multiplayer_game():
    game = Game()
    player1 = Agent(COLOR_RED)
    player2 = Agent(COLOR_GREEN)
    game.add_player(player1)
    game.add_player(player2)
    running = True
    while running:
        start_time = pygame.time.get_ticks()
        DISPLAY.fill(COLOR_WHITE)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                player1.jump()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_j:
                player2.jump()
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
        game.render()
        if not game.over():
            game.tick()
        else:
            pygame.draw.line(DISPLAY, COLOR_RED, (0, 0), (DISPLAY.get_width(), DISPLAY.get_height()), DISPLAY.get_width() // 100)
            pygame.draw.line(DISPLAY, COLOR_RED, (DISPLAY.get_width(), 0), (0, DISPLAY.get_height()), DISPLAY.get_width() // 100)
        pygame.display.update()
        pygame.time.delay(1000 // FPS - (pygame.time.get_ticks() - start_time))
    pygame.quit()

# Returns the best performing network after running each in parallel
def ai_gym(networks: [NN]) -> (NN, int):
    global FPS
    game = Game()
    agents = [Agent((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))) for _ in range(len(networks))]
    for agent in agents:
        game.add_player(agent)
    while not game.over():
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_EQUALS:
                FPS *= 2
                print(f"FPS: {FPS}")
            if event.type == pygame.KEYDOWN and event.key == pygame.K_MINUS:
                FPS //= 2
                FPS = max(FPS, 1)
                print(f"FPS: {FPS}")
        start_time = pygame.time.get_ticks()
        DISPLAY.fill(COLOR_WHITE)
        next_obstacle_idx = game.next_obstacle_index()
        next_obstacle = game.obstacles[next_obstacle_idx]
        next_obstacle_dist = game.obstacle_positions[next_obstacle_idx] - 0.5
        for agent, network in zip(agents, networks):
            if agent.dead:
                continue
            input = [next_obstacle.mid, next_obstacle.mid, next_obstacle_dist, agent.velocity, agent.pos]
            result_matrix = network.solve(Matrix.from_row(input))
            if result_matrix.data[0][0] > 0.5:
                agent.jump()
        game.tick()
        game.render()
        pygame.display.update()
        pygame.time.delay(1000 // FPS - (pygame.time.get_ticks() - start_time))
    scores = [agent.tick_count for agent in agents]
    best_score = max(scores)
    return (networks[scores.index(best_score)], best_score)

GENERATION_SIZE = 1000
parent = [NN([5, 6, 4, 1], rand=True) for _ in range(GENERATION_SIZE)]
gen_count = 1
while True:
    best_network, score = ai_gym(parent)
    print(f"Best score at gen#{gen_count}: {score}")
    next_generation = [deepcopy(best_network) for _ in range(GENERATION_SIZE - 1)]
    # Dynamic mutations
    for i, child in enumerate(next_generation):
        child.mutate(lerp(i, 0, GENERATION_SIZE, 0, 0.05))
    next_generation.append(best_network)
    parent = next_generation
    gen_count += 1
