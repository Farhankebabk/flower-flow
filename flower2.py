import math
import random
import time
import turtle

random.seed(42)

# =========================================================
#  KONSTANTA ANIMASI  ← atur kecepatan dari sini
# =========================================================
HEART_STEP   = 2       # makin kecil → update makin sering (makin halus)
HEART_DELAY  = 0.006   # detik jeda tiap update garis hati
FLOWER_DELAY = 0.08    # detik jeda antar-bunga
# =========================================================

WIN_W, WIN_H = 700, 700

screen = turtle.Screen()
screen.setup(width=WIN_W, height=WIN_H)
screen.bgcolor("black")
screen.title("Love & Flowers  —  [F] fullscreen   [ESC] keluar")
screen.tracer(0)

root = screen.getcanvas().winfo_toplevel()
is_fullscreen = {"on": False}


def toggle_fullscreen(_event=None):
    is_fullscreen["on"] = not is_fullscreen["on"]
    root.attributes("-fullscreen", is_fullscreen["on"])
    root.after(80, redraw_everything)


def quit_app(_event=None):
    try:
        screen.bye()
    except turtle.Terminator:
        pass


screen.onkey(toggle_fullscreen, "f")
screen.onkey(toggle_fullscreen, "F")
screen.onkey(quit_app, "Escape")
screen.listen()

t = turtle.Turtle(visible=False)
t.speed(0)
t.penup()

flower_pen = turtle.Turtle(visible=False)
flower_pen.speed(0)
flower_pen.penup()


# ---------------- Rumus hati ----------------
def hearta(k):
    return 15 * math.sin(k) ** 3


def heartb(k):
    return (12 * math.cos(k) - 5 * math.cos(2 * k)
            - 2 * math.cos(3 * k) - math.cos(4 * k))


N_POINTS = 400
HEART_HALF_W = 15.0
HEART_HALF_H = 17.0
SCALE = 18.0


def fit_scale():
    """Skala dinamis supaya hati + bunga selalu masuk jendela."""
    global SCALE
    w = root.winfo_width() or WIN_W
    h = root.winfo_height() or WIN_H
    SCALE = min(w * 0.55 / HEART_HALF_W, h * 0.55 / HEART_HALF_H)


def heart_point(k):
    return hearta(k) * SCALE, heartb(k) * SCALE


# ---------------- Gambar hati (dengan animasi) ----------------
GLOW_LAYERS = [
    (28, "#3a0208"),
    (20, "#5c0410"),
    (13, "#8b0718"),
    (8,  "#c30a24"),
]
HEART_EDGE = "#ff1a3c"
HEART_FILL = "#c30a24"


def trace_heart_slow(pensize, color, delay=HEART_DELAY, step=HEART_STEP):
    """
    Gambar outline hati SEKARANG satu titik demi satu titik.
    Arah k = 0 → 2π menghasilkan gambar yang berjalan searah jarum jam.
    """
    t.penup()
    t.goto(*heart_point(0))
    t.pendown()
    t.pensize(pensize)
    t.pencolor(color)

    for i in range(1, N_POINTS + 1):
        k = 2 * math.pi * i / N_POINTS
        t.goto(*heart_point(k))
        if i % step == 0:
            screen.update()
            time.sleep(delay)
    t.penup()
    screen.update()


def fill_heart():
    """Isi dalam hati (tidak dianimasikan, langsung)."""
    t.penup()
    t.goto(*heart_point(0))
    t.color(HEART_FILL, HEART_FILL)
    t.begin_fill()
    for i in range(1, N_POINTS + 1):
        k = 2 * math.pi * i / N_POINTS
        t.goto(*heart_point(k))
    t.end_fill()
    t.penup()


def draw_heart_animated():
    # 1) Glow dari luar ke dalam — tiap lapis "tumbuh" searah jarum jam
    for width, color in GLOW_LAYERS:
        trace_heart_slow(width, color)

    # 2) Isi hati
    fill_heart()
    screen.update()

    # 3) Garis tepi terang — di-trace pelan searah jarum jam
    trace_heart_slow(3, HEART_EDGE)


# ---------------- Bunga ----------------
def draw_petal(cx, cy, size, angle_deg, color):
    flower_pen.penup()
    flower_pen.goto(cx, cy)
    flower_pen.color(color, color)
    flower_pen.pendown()
    flower_pen.begin_fill()
    rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    for i in range(21):
        a = 2 * math.pi * i / 20
        px = math.cos(a) * size
        py = math.sin(a) * size * 0.6
        rx = px * cos_a - py * sin_a
        ry = px * sin_a + py * cos_a
        flower_pen.goto(cx + rx, cy + ry)
    flower_pen.end_fill()
    flower_pen.penup()


def draw_flower(cx, cy, size, petal_color, center_color,
                n_petals=6, rotation=0.0):
    dist = size * 0.9
    for i in range(n_petals):
        a = rotation + i * (360.0 / n_petals)
        px = cx + math.cos(math.radians(a)) * dist
        py = cy + math.sin(math.radians(a)) * dist
        draw_petal(px, py, size, a, petal_color)

    flower_pen.penup()
    flower_pen.goto(cx, cy - size * 0.35)
    flower_pen.setheading(0)
    flower_pen.color(center_color, center_color)
    flower_pen.pendown()
    flower_pen.begin_fill()
    flower_pen.circle(size * 0.35)
    flower_pen.end_fill()
    flower_pen.penup()


# ---------------- Point-in-polygon ----------------
def build_heart_poly():
    return [heart_point(2 * math.pi * i / N_POINTS) for i in range(N_POINTS)]


def point_in_poly(px, py, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and \
           (px < (xj - xi) * (py - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside


PALETTE = [
    ("#9b59b6", "#fff3b0"),
    ("#b07cd6", "#fff3b0"),
    ("#ffb6c1", "#fff3b0"),
    ("#ff8fab", "#fff8dc"),
    ("#e6c6f2", "#fff3b0"),
]


def generate_flower_positions(poly, n_target):
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)

    margin = SCALE * 3.5
    xmin -= margin; xmax += margin
    ymin -= margin; ymax += margin

    positions = []
    attempts = 0
    while len(positions) < n_target and attempts < 30000:
        attempts += 1
        x = random.uniform(xmin, xmax)
        y = random.uniform(ymin, ymax)

        if point_in_poly(x, y, poly):
            continue

        size = random.uniform(0.30, 0.55) * SCALE

        ok = True
        for (ox, oy, osz) in positions:
            if math.hypot(x - ox, y - oy) < (size + osz) * 1.6:
                ok = False
                break
        if not ok:
            continue

        positions.append((x, y, size))
    return positions


# ---------------- Alur gambar ----------------
def redraw_everything():
    fit_scale()
    t.clear()
    flower_pen.clear()

    poly = build_heart_poly()
    draw_heart_animated()   # <- hati muncul perlahan searah jarum jam

    positions = generate_flower_positions(poly, n_target=65)

    # URUTKAN dari yang paling DEKAT PUSAT → paling jauh
    # supaya bunga "mekar" dari tengah melebar ke samping
    positions.sort(key=lambda p: math.hypot(p[0], p[1]))

    for (x, y, size) in positions:
        petal_color, center_color = random.choice(PALETTE)
        rot = random.uniform(0, 360)
        n_petals = random.choice([5, 5, 6, 6, 7])
        draw_flower(x, y, size, petal_color, center_color,
                    n_petals=n_petals, rotation=rot)
        screen.update()
        time.sleep(FLOWER_DELAY)

    t.hideturtle()
    flower_pen.hideturtle()
    screen.update()


def main():
    root.after(100, redraw_everything)
    print("Tekan [F] untuk fullscreen, [ESC] untuk keluar.")
    screen.mainloop()


if __name__ == "__main__":
    try:
        main()
    except turtle.Terminator:
        pass