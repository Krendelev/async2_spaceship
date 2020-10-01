TIC_TIMEOUT = 0.1
STARS_SYMBOLS = "+*.:"
STARS_COUNT = 100
FRAMES_DIR = "frames"
OBJECTS_RATIO = 4
PHRASES = {
    1957: "First Sputnik",
    1961: "Gagarin flew!",
    1969: "Armstrong got on the moon!",
    1971: "First orbital space station Salute-1",
    1981: "Flight of the Shuttle Columbia",
    1998: "ISS start building",
    2011: "Messenger launch to Mercury",
    2020: "Take the plasma gun! Shoot the garbage!",
}
DELAYS = {
    range(1957, 1961): None,
    range(1961, 1969): 20,
    range(1969, 1981): 14,
    range(1981, 1995): 10,
    range(1995, 2010): 8,
    range(2010, 2020): 6,
}