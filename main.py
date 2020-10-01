#!/usr/bin/env python3
import asyncio
import curses
import time
from random import choice, randrange

from animation import (
    animate_spaceship,
    blink,
    explode,
    fire,
    fly_garbage,
    load_frames,
    obstacles_list,
    sleep,
)
from curses_tools import draw_frame, get_frame_size, read_controls
from physics import update_speed
from settings import (
    DELAYS,
    OBJECTS_RATIO,
    PHRASES,
    STARS_COUNT,
    STARS_SYMBOLS,
    TIC_TIMEOUT,
)

coroutines = []
year = 1957


def get_garbage_delay_tics(year):
    delay = [delay for period, delay in DELAYS.items() if year in period]
    return delay[0] if delay else 2


async def fill_orbit_with_garbage(canvas, columns):
    trash = load_frames("trash")
    objects = load_frames("object")
    garbage = objects + trash * OBJECTS_RATIO
    global coroutines, year
    while True:
        if delay := get_garbage_delay_tics(year):
            await sleep(delay)
            frame = choice(garbage)
            _, width = get_frame_size(frame)
            coroutines.append(fly_garbage(canvas, randrange(columns - width), frame))
        await asyncio.sleep(0)


async def run_spaceship(canvas):
    game_over = load_frames("game")[0]
    spaceship_frames = animate_spaceship()
    height, width = get_frame_size(next(spaceship_frames))

    row_max, column_max = canvas.getmaxyx()
    row = row_max // 2 - height // 2
    column = column_max // 2 - width // 2
    field_height = row_max - height
    field_width = column_max - width

    row_speed = column_speed = 0

    for frame in spaceship_frames:
        row_dir, column_dir, space_pressed = read_controls(canvas)
        row_speed, column_speed = update_speed(
            row_speed, column_speed, row_dir, column_dir
        )
        row += row_speed
        column += column_speed

        row = min(row, field_height) if row >= 0 else 0
        column = min(column, field_width) if column >= 0 else 0

        global coroutines, obstacles_list, year
        if space_pressed and year >= 2020:
            coroutines.append(fire(canvas, row, column + width // 2, rows_speed=-1))

        draw_frame(canvas, row, column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, negative=True)

        for obstacle in obstacles_list:
            if obstacle.has_collision(row, column):
                await explode(canvas, row, column)
                break
        else:
            continue
        break

    sign_height, sign_width = get_frame_size(game_over)
    row = row_max // 2 - sign_height // 2
    column = column_max // 2 - sign_width // 2
    while True:
        draw_frame(canvas, row, column, game_over)
        await asyncio.sleep(0)


def draw(canvas):
    curses.curs_set(0)
    canvas.nodelay(True)

    time_elapsed = 0
    rows, columns = canvas.getmaxyx()
    stars = [
        blink(
            canvas,
            randrange(rows),
            randrange(columns),
            choice(STARS_SYMBOLS),
        )
        for _ in range(STARS_COUNT)
    ]
    global coroutines, year
    coroutines.extend(stars)
    coroutines.append(run_spaceship(canvas))
    coroutines.append(fill_orbit_with_garbage(canvas, columns))

    exhausted = set()
    while True:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                exhausted.add(coroutine)

        coroutines = [coro for coro in coroutines if coro not in exhausted]
        exhausted.clear()

        legend = canvas.derwin(rows - 2, 2)
        inscription = f"{year} {PHRASES.get(year, '')}"
        legend.addstr(0, 0, inscription)

        canvas.border()
        canvas.refresh()

        time.sleep(TIC_TIMEOUT)

        time_elapsed += TIC_TIMEOUT
        if round(time_elapsed % 1.5, 1) == 0:
            year += 1
            time_elapsed = 0
            legend.erase()


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.wrapper(draw)
