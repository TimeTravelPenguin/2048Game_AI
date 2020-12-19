from __future__ import annotations

import random
from abc import ABCMeta, abstractmethod
from enum import Enum
from os import system, name

import numpy as np
import pygame
from pygame.locals import *

pygame.init()
SCREEN_SIZE = 500
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("2048 Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

CELLS = 3
GRID_COORD_MARGIN_SIZE = 20
CELL_SIZE = (SCREEN_SIZE - 2 * GRID_COORD_MARGIN_SIZE) // CELLS


def cls():
    system('cls' if name == 'nt' else 'clear')


class ControllerInput(Enum):
    Up = 0
    Left = 1
    Down = 2
    Right = 3


class ControllerBase(metaclass=ABCMeta):

    @classmethod
    def version(cls): return "1.0"

    def __init__(self, game: Game = None):
        self._game_reference = game

    @abstractmethod
    def await_input(self, controller_input: ControllerInput):
        raise NotImplementedError()

    def update_game_ref(self, game: Game):
        self._game_reference = game


class PlayerController(ControllerBase):
    def await_input(self, controller_input: ControllerInput):
        raise NotImplementedError()  # TODO


class Game:
    four_spawn_mod: float = 0.33

    def __init__(self, size: int, controller: ControllerBase) -> None:
        self.size = size
        self.state = np.zeros((size, size))
        self.controller = controller

    def add_tile(self) -> bool:
        # check there is an empty
        zeros = np.argwhere(self.state == 0)
        if len(zeros) == 0:
            return False

        idx = random.choice(zeros)
        self.state[idx[0], idx[1]] = 2 if random.random() > self.four_spawn_mod else 4

        return True

    def shift_left(self):
        for idx, row in enumerate(self.state):
            non_zeros = [r for r in row if r != 0]
            for i in range(len(non_zeros) - 1):
                if non_zeros[i] == non_zeros[i + 1]:
                    non_zeros[i] *= 2
                    non_zeros[i + 1] = 0
            shifted = [r for r in non_zeros if r != 0]
            padded = np.pad(shifted, pad_width=(0, self.size - len(shifted)), constant_values=0)
            self.state[idx] = padded

    def shift_right(self):
        self.state = np.flip(self.state)
        self.shift_left()
        self.state = np.flip(self.state)

    def shift_up(self):
        self.state = self.state.T
        self.shift_left()
        self.state = self.state.T

    def shift_down(self):
        self.state = np.flip(self.state.T)
        self.shift_left()
        self.state = np.flip(self.state).T

    def shift_direction(self, direction: ControllerInput) -> bool:
        prev_state = self.state.copy()

        if direction == ControllerInput.Up:
            self.shift_up()

        elif direction == ControllerInput.Down:
            self.shift_down()

        elif direction == ControllerInput.Left:
            self.shift_left()

        elif direction == ControllerInput.Right:
            self.shift_right()

        shift_occurred = not np.array_equal(self.state, prev_state)
        return shift_occurred


class Grid:
    def __init__(self, surface, cellSize, axisLabels):
        self.surface = surface
        self.colNb = surface.get_width() // cellSize
        self.lineNb = surface.get_height() // cellSize
        self.cellSize = cellSize
        self.axisLabels = axisLabels
        self.grid = [[0 for i in range(self.colNb)] for j in range(self.lineNb)]
        self.font = pygame.font.SysFont('arial', 12, False)

    def draw(self):
        for li in range(self.lineNb + 1):
            liCoord = GRID_COORD_MARGIN_SIZE + li * CELL_SIZE
            if self.axisLabels and li < self.lineNb:
                text = self.font.render(str(li), True, (0, 0, 0))
                self.surface.blit(text, (GRID_COORD_MARGIN_SIZE // 2 - len(str(li)), liCoord))
            pygame.draw.line(self.surface, BLACK, (GRID_COORD_MARGIN_SIZE, liCoord),
                             (self.surface.get_width() - GRID_COORD_MARGIN_SIZE - 1, liCoord))
        for co in range(self.colNb + 1):
            colCoord = GRID_COORD_MARGIN_SIZE + co * CELL_SIZE
            if self.axisLabels and co < self.colNb:
                text = self.font.render(str(co), True, (0, 0, 0))
                self.surface.blit(text, (colCoord, 1))
            pygame.draw.line(self.surface, BLACK, (colCoord, GRID_COORD_MARGIN_SIZE),
                             (colCoord, self.surface.get_height() - GRID_COORD_MARGIN_SIZE - 1))


if __name__ == "__main__":
    controller = PlayerController()
    game = Game(3, controller)

    gameFinished = False

    print("Go!")
    loopIdx = 0


    def print_game_state(game: Game):
        global loopIdx
        print("move:", loopIdx)
        loopIdx += 1

        for i in game.state:
            row = ", ".join([str(j) for j in i])
            print(row)


    grid = Grid(surface=screen, cellSize=CELL_SIZE, axisLabels=True)

    game.add_tile()
    print_game_state(game)

    screen.fill(WHITE)
    grid.draw()
    pygame.display.flip()

    while not gameFinished:
        screen.fill(WHITE)
        grid.draw()

        event = pygame.event.wait()

        if event.type == QUIT:
            gameFinished = True

        if event.type == KEYDOWN:
            print("\n" + "=" * 20 + "\n")

            key: ControllerInput = None
            if event.key == pygame.K_UP:
                key = ControllerInput.Up
            elif event.key == pygame.K_DOWN:
                key = ControllerInput.Down
            elif event.key == pygame.K_LEFT:
                key = ControllerInput.Left
            elif event.key == pygame.K_RIGHT:
                key = ControllerInput.Right

            move_made = False
            if key is not None:
                move_made = game.shift_direction(key)

            if move_made and not game.add_tile():
                gameFinished = True

            print_game_state(game)

            pygame.display.flip()
    pygame.quit()
    print("\nGame Over!")
