import asyncio
import curses
import itertools
import os
import random
import uuid

from curses_tools import draw_frame, get_frame_size, get_max_coords
from obstacles import Obstacle
from settings import FRAMES_DIR, STARS_COUNT, TIC_TIMEOUT

obstacles_list = []
obstacles_in_last_collisions = []


def load_frames(item):
    files = [entry for entry in os.scandir(FRAMES_DIR) if entry.name.startswith(item)]
    frames = []
    for entry in files:
        with open(entry) as fh:
            frames.append(fh.read())
    return frames


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol="*"):
    styles = ("A_DIM", "A_NORMAL", "A_BOLD", "A_NORMAL")
    delays = (2, 0.3, 0.5, 0.3)
    await sleep(round(random.random() * STARS_COUNT // 4))
    while True:
        for style, delay in zip(styles, delays):
            canvas.addch(row, column, symbol, getattr(curses, style))
            await sleep(round(delay / TIC_TIMEOUT))


def animate_spaceship():
    rocket = load_frames("rocket")
    frames = sorted(rocket * 2)
    return itertools.cycle(frames)


async def explode(canvas, center_row, center_column):
    frames = load_frames("explosion")
    rows, columns = get_frame_size(frames[0])
    corner_row = center_row - rows / 2
    corner_column = center_column - columns / 2

    curses.beep()
    for frame in frames:
        draw_frame(canvas, corner_row, corner_column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, corner_row, corner_column, frame, negative=True)
        await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), "*")
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), "O")
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), " ")

    row += rows_speed
    column += columns_speed

    symbol = "-" if columns_speed else "|"

    max_row, max_column = get_max_coords(canvas)

    curses.beep()
    global obstacles_list, obstacles_in_last_collisions
    while 0 < row < max_row and 0 < column < max_column:
        for obstacle in obstacles_list:
            if obstacle.has_collision(round(row), round(column)):
                obstacles_in_last_collisions.append(obstacle)
                return
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), " ")
        row += rows_speed
        column += columns_speed


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    row_max, column_max = get_max_coords(canvas)
    column = min(max(column, 0), column_max)
    row = 0
    height, width = get_frame_size(garbage_frame)

    global obstacles_list, obstacles_in_last_collisions

    uid = uuid.uuid4()
    obstacle = Obstacle(row, column, height, width, uid)
    obstacles_list.append(obstacle)

    while obstacle.row < row_max:
        draw_frame(canvas, obstacle.row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, obstacle.row, column, garbage_frame, negative=True)

        if obstacle in obstacles_in_last_collisions:
            obstacles_in_last_collisions.remove(obstacle)
            obstacles_list.remove(obstacle)
            row = obstacle.row + obstacle.rows_size / 2
            column = obstacle.column + obstacle.columns_size / 2
            await explode(canvas, round(row), round(column))
            return

        obstacle.row += speed

    obstacles_list.remove(obstacle)