# Fichier de :bob: pour :bob: par :bob:

import random as rd

MOVES = {
    "H": (0, -1),
    "B": (0, 1),
    "D": (1, 0),
    "G": (-1, 0)
}

def main(maze: list[list[str]], pos_self: tuple[int, int], pos_enemy: tuple[int, int]) -> str:

    moves = list(MOVES.items())
    rd.shuffle(moves)

    for move, delta in moves:
        if maze[pos_self[1] + delta[1]][pos_self[0] + delta[0]] != "#":
            return move