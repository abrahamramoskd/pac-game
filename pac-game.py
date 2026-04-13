"""
╔══════════════════════════════════════════════════════════════╗
║                    PAC-MAN EN PYTHON                        ║
║                 Desarrollado con pygame                     ║
╚══════════════════════════════════════════════════════════════╝

CÓMO EJECUTAR:
    1. Instala pygame:  pip install pygame
    2. Ejecuta:         python pacman.py

CONTROLES:
    ← ↑ → ↓   Mover a Pac-Man
    P          Pausar / reanudar
    R          Reiniciar partida
    ESC        Salir

REGLAS:
    - Come todos los puntos del laberinto para pasar de nivel.
    - Los puntos grandes (energizadores) permiten comer fantasmas.
    - Fantasma azul = vulnerable (puedes comerlo, vale 200 pts).
    - Si un fantasma normal te toca, pierdes una vida.
    - Tienes 3 vidas. Cada nivel el juego se vuelve más rápido.
"""

import pygame
import sys
import math
import random

# ─────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────

CELL     = 24          # Tamaño de cada celda del laberinto en px
COLS     = 21          # Columnas del laberinto
ROWS     = 23          # Filas del laberinto
HUD_H    = 48          # Altura del HUD (puntuación y vidas)

SCREEN_W = COLS * CELL
SCREEN_H = ROWS * CELL + HUD_H
FPS      = 60

# ── Colores ───────────────────────────────────────────────────
C_BG       = (0,   0,   0)
C_WALL     = (30,  80, 220)   # Azul clásico de Pac-Man
C_WALL2    = (60, 120, 255)   # Borde interior de pared
C_DOT      = (255, 200, 150)  # Puntos pequeños
C_POWER    = (255, 220,  80)  # Energizadores
C_PACMAN   = (255, 230,   0)  # Amarillo
C_TEXT     = (255, 255, 255)
C_TITLE    = (255, 200,   0)
C_HUD      = (200, 200, 255)
C_SCARED   = (30,  60, 220)   # Fantasma vulnerable (azul)
C_SCARED2  = (255, 255, 255)  # Fantasma a punto de recuperarse (blanco)
C_EYES     = (255, 255, 255)
C_PUPIL    = (0,   0,  180)
C_FRUIT    = (255,  80,  80)

# Colores de cada fantasma: Blinky, Pinky, Inky, Clyde
GHOST_COLORS = [
    (255,  0,   0),   # Blinky – rojo
    (255, 180, 220),  # Pinky  – rosa
    (0,   220, 255),  # Inky   – cian
    (255, 165,   0),  # Clyde  – naranja
]

# ── Tipos de celda del laberinto ─────────────────────────────
EMPTY  = 0   # Pasillo vacío (ya comido o inicio de fantasmas)
WALL   = 1   # Pared
DOT    = 2   # Punto pequeño
POWER  = 3   # Energizador (punto grande)
GATE   = 4   # Puerta de la casa de fantasmas (traspasable solo por fantasmas)

# ── Puntuación ────────────────────────────────────────────────
PTS_DOT    = 10
PTS_POWER  = 50
PTS_GHOST  = 200   # Por fantasma comido (se multiplica en cadena)
PTS_FRUIT  = 300

# ── Duración del modo asustado (frames a 60 FPS) ─────────────
SCARED_DURATION  = 360   # 6 segundos
SCARED_FLASH_AT  = 120   # Últimos 2 seg parpadean

# ─────────────────────────────────────────────────────────────
# LABERINTO
#
# Diseñado manualmente con los tipos de celda definidos arriba.
# 0=vacío, 1=pared, 2=punto, 3=energizador, 4=puerta
#
# El laberinto tiene 21 columnas × 23 filas.
# La casa de los fantasmas está en el centro (filas 9-12, cols 7-13).
# ─────────────────────────────────────────────────────────────
LEVEL_MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,2,1],
    [1,3,1,1,2,1,1,1,2,1,1,1,2,1,1,1,2,1,1,3,1],
    [1,2,1,1,2,1,1,1,2,1,1,1,2,1,1,1,2,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,2,1,2,1,1,1,1,1,1,1,2,1,2,1,1,2,1],
    [1,2,2,2,2,1,2,2,2,2,1,2,2,2,2,1,2,2,2,2,1],
    [1,1,1,1,2,1,1,1,0,1,1,1,0,1,1,1,2,1,1,1,1],
    [1,1,1,1,2,1,0,0,0,0,0,0,0,0,0,1,2,1,1,1,1],
    [1,1,1,1,2,1,0,1,1,4,1,4,1,1,0,1,2,1,1,1,1],
    [0,0,0,0,2,0,0,1,0,0,0,0,0,1,0,0,2,0,0,0,0],  # fila 10: túneles laterales
    [1,1,1,1,2,1,0,1,1,1,1,1,1,1,0,1,2,1,1,1,1],
    [1,1,1,1,2,1,0,0,0,0,0,0,0,0,0,1,2,1,1,1,1],
    [1,1,1,1,2,1,0,1,1,1,1,1,1,1,0,1,2,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,2,1,1,1,2,1,1,1,2,1,1,1,2,1,1,2,1],
    [1,3,2,1,2,2,2,2,2,2,0,2,2,2,2,2,2,1,2,3,1],
    [1,1,2,1,2,1,2,1,1,1,1,1,1,1,2,1,2,1,2,1,1],
    [1,2,2,2,2,1,2,2,2,2,1,2,2,2,2,1,2,2,2,2,1],
    [1,2,1,1,1,1,1,1,2,1,1,1,2,1,1,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,2,1,1,2,1,1,1,1,1,2,1,1,2,1,1,2,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

# Posición inicial de Pac-Man (fila, col)
PACMAN_START = (16, 10)

# Posiciones iniciales de los 4 fantasmas dentro de la casa
GHOST_STARTS = [
    (10, 10),  # Blinky  – sale primero, ronda afuera
    (10,  9),  # Pinky
    (10, 10),  # Inky
    (10, 11),  # Clyde
]

# Posición de la fruta que aparece a mitad del nivel
FRUIT_POS = (16, 10)


# ─────────────────────────────────────────────────────────────
# FUNCIONES DE DIBUJO DE SPRITES
#
# Todos los sprites se dibujan con primitivas pygame (círculos,
# polígonos, arcos) para no depender de imágenes externas.
# ─────────────────────────────────────────────────────────────

def draw_pacman(surface, cx, cy, radius, mouth_angle, direction):
    """
    Dibuja a Pac-Man como un círculo amarillo con una boca
    que abre y cierra (efecto de masticación).

    cx, cy        : centro en píxeles
    radius        : radio del sprite
    mouth_angle   : ángulo de apertura de la boca (0–40 grados)
    direction     : (dx, dy) para orientar la boca
    """
    # Calculamos el ángulo de orientación según la dirección
    dx, dy = direction
    if   dx ==  1: base_angle =   0
    elif dx == -1: base_angle = 180
    elif dy == -1: base_angle =  90
    else:          base_angle = 270   # dy == 1

    # Dibujamos el arco de Pac-Man como un polígono "tarta"
    start_deg = base_angle + mouth_angle
    end_deg   = base_angle - mouth_angle + 360

    # Convertir a radianes y construir puntos del polígono
    points = [(cx, cy)]
    steps  = 36
    for i in range(steps + 1):
        angle_deg = start_deg + (end_deg - start_deg) * i / steps
        angle_rad = math.radians(angle_deg)
        px = cx + math.cos(angle_rad) * radius
        py = cy - math.sin(angle_rad) * radius
        points.append((px, py))

    if len(points) > 2:
        pygame.draw.polygon(surface, C_PACMAN, points)

    # Ojo
    eye_x = int(cx + math.cos(math.radians(base_angle + 70)) * radius * 0.55)
    eye_y = int(cy - math.sin(math.radians(base_angle + 70)) * radius * 0.55)
    pygame.draw.circle(surface, C_BG, (eye_x, eye_y), 3)


def draw_ghost(surface, cx, cy, radius, color, direction, scared, flash):
    """
    Dibuja un fantasma con:
      - Cuerpo redondeado arriba y ondulado abajo
      - Ojos con pupilas orientadas según la dirección
      - Color azul si está asustado, blanco si está a punto de recuperarse

    scared : True si está en modo vulnerable
    flash  : True si debe dibujarse en color alterno (parpadeo)
    """
    body_color = (C_SCARED2 if flash else C_SCARED) if scared else color
    r = radius

    # ── Cuerpo superior (semicírculo) ──
    pygame.draw.circle(surface, body_color, (cx, cy - r//4), r)

    # ── Cuerpo inferior (rectángulo + ondas) ──
    body_rect = pygame.Rect(cx - r, cy - r//4, r*2, r + r//2)
    pygame.draw.rect(surface, body_color, body_rect)

    # Ondas en la parte inferior (3 triángulos invertidos)
    wave_y  = cy + r + r//4
    wave_w  = (r * 2) // 3
    for i in range(3):
        wx = cx - r + i * wave_w
        pts = [(wx, wave_y), (wx + wave_w//2, wave_y - r//3),
               (wx + wave_w, wave_y)]
        pygame.draw.polygon(surface, C_BG, pts)

    # ── Ojos ──
    if not scared:
        for side in [-1, 1]:
            ex = cx + side * r // 3
            ey = cy - r // 3
            pygame.draw.circle(surface, C_EYES, (ex, ey), r // 4)
            # Pupila orientada según dirección
            dx, dy = direction
            px = ex + dx * (r // 8)
            py = ey + dy * (r // 8)
            pygame.draw.circle(surface, C_PUPIL, (int(px), int(py)), r // 7)
    else:
        # Ojos de X cuando está asustado
        ec = C_SCARED2 if not flash else C_SCARED
        for side in [-1, 1]:
            ex = cx + side * r // 3
            ey = cy - r // 3
            s  = r // 5
            pygame.draw.line(surface, ec, (ex-s, ey-s), (ex+s, ey+s), 2)
            pygame.draw.line(surface, ec, (ex+s, ey-s), (ex-s, ey+s), 2)


def draw_wall_cell(surface, row, col):
    """
    Dibuja una celda de pared con borde redondeado interior,
    imitando el estilo visual del Pac-Man original.
    """
    x = col * CELL
    y = row * CELL + HUD_H
    rect = pygame.Rect(x, y, CELL, CELL)
    pygame.draw.rect(surface, C_WALL, rect)
    # Borde interior más claro
    inner = rect.inflate(-6, -6)
    pygame.draw.rect(surface, C_WALL2, inner, 2)


def draw_dot(surface, row, col):
    cx = col * CELL + CELL // 2
    cy = row * CELL + CELL // 2 + HUD_H
    pygame.draw.circle(surface, C_DOT, (cx, cy), 3)


def draw_power(surface, row, col, frame):
    """Energizador que pulsa (crece y achica) con el tiempo."""
    cx  = col * CELL + CELL // 2
    cy  = row * CELL + CELL // 2 + HUD_H
    r   = 7 + int(math.sin(frame * 0.15) * 2)
    pygame.draw.circle(surface, C_POWER, (cx, cy), r)


def draw_fruit(surface, row, col):
    """Fruta (cereza simple) dibujada con círculos."""
    cx = col * CELL + CELL // 2
    cy = row * CELL + CELL // 2 + HUD_H
    pygame.draw.circle(surface, C_FRUIT, (cx - 4, cy + 2), 5)
    pygame.draw.circle(surface, C_FRUIT, (cx + 4, cy + 2), 5)
    pygame.draw.line(surface, (0, 200, 0), (cx, cy + 2), (cx, cy - 6), 2)


# ─────────────────────────────────────────────────────────────
# CLASE: Ghost
#
# Cada fantasma tiene su propia IA de movimiento.
# En modo normal persiguen a Pac-Man con distintas estrategias.
# En modo asustado se mueven aleatoriamente.
# ─────────────────────────────────────────────────────────────
class Ghost:
    def __init__(self, idx, start_row, start_col, color):
        self.idx       = idx           # 0=Blinky, 1=Pinky, 2=Inky, 3=Clyde
        self.color     = color
        self.home_row  = start_row
        self.home_col  = start_col
        self.reset()

    def reset(self):
        """Vuelve a la posición inicial (al perder una vida)."""
        self.row      = float(self.home_row)
        self.col      = float(self.home_col)
        self.dir      = (0, -1)        # Dirección actual (dr, dc)
        self.scared   = False
        self.scared_timer = 0
        self.dead     = False          # Ojos volando de regreso a casa
        self.speed    = 0.08
        # Los fantasmas salen de casa con un retardo escalonado
        self.exit_delay = self.idx * 90   # frames

    def activate_scared(self):
        """El jugador comió un energizador: activa modo asustado."""
        if not self.dead:
            self.scared       = True
            self.scared_timer = SCARED_DURATION

    def update(self, grid, pacman_row, pacman_col, frame):
        """
        Actualiza la posición del fantasma.
        La lógica se divide en:
          1. Salida de la casa (retardo inicial).
          2. Modo asustado: movimiento aleatorio.
          3. Modo normal: persecución de Pac-Man.
          4. Modo muerto: regresar a la casa.
        """
        # ── Retardo de salida ──
        if self.exit_delay > 0:
            self.exit_delay -= 1
            return

        # ── Temporizador de modo asustado ──
        if self.scared:
            self.scared_timer -= 1
            if self.scared_timer <= 0:
                self.scared = False

        # ── Movimiento por cuadrícula ──
        # Cada fantasma avanza en su dirección actual.
        # Al llegar al centro de una celda, decide la próxima dirección.
        speed = 0.06 if self.scared else (0.12 if self.dead else self.speed)

        self.row += self.dir[0] * speed
        self.col += self.dir[1] * speed

        # Túnel lateral: wrap-around
        if self.col < -0.5:
            self.col = COLS - 0.5
        elif self.col > COLS - 0.5:
            self.col = -0.5

        # ── En el centro de la celda: elegir nueva dirección ──
        r_int = int(round(self.row))
        c_int = int(round(self.col))
        dr    = abs(self.row - r_int)
        dc    = abs(self.col - c_int)

        if dr < speed * 1.5 and dc < speed * 1.5:
            self.row = float(r_int)
            self.col = float(c_int)
            self._choose_direction(grid, r_int, c_int,
                                   pacman_row, pacman_col)

    def _choose_direction(self, grid, r, c, pr, pc):
        """
        Elige la próxima dirección según el modo:
          - Muerto    → hacia la casa (9, 10)
          - Asustado  → dirección aleatoria válida
          - Normal    → hacia el objetivo según estrategia de cada fantasma
        """
        if self.dead:
            target_r, target_c = 10, 10   # Centro de la casa
            if r == target_r and c == target_c:
                self.dead   = False
                self.scared = False
        elif self.scared:
            target_r, target_c = None, None   # Aleatorio
        else:
            target_r, target_c = self._get_target(r, c, pr, pc)

        # Generar movimientos posibles (no puede dar marcha atrás)
        opposite = (-self.dir[0], -self.dir[1])
        dirs = [(0,1),(0,-1),(1,0),(-1,0)]
        valid = []
        for d in dirs:
            if d == opposite:
                continue
            nr, nc = r + d[0], c + d[1]
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                cell = grid[nr][nc]
                # Los fantasmas no pueden pasar por la puerta
                # (excepto cuando están muertos regresando a casa)
                if cell == WALL:
                    continue
                if cell == GATE and not self.dead:
                    continue
                valid.append(d)

        if not valid:
            return

        if target_r is None:
            # Modo asustado: dirección aleatoria
            self.dir = random.choice(valid)
        else:
            # Elegir la dirección que minimice la distancia al objetivo
            def dist(d):
                nr, nc = r + d[0], c + d[1]
                return (nr - target_r)**2 + (nc - target_c)**2
            self.dir = min(valid, key=dist)

    def _get_target(self, r, c, pr, pc):
        """
        Estrategia de persecución según el índice del fantasma:
          0 Blinky → apunta directamente a Pac-Man
          1 Pinky  → apunta 4 celdas delante de Pac-Man
          2 Inky   → estrategia mixta con Blinky (simplificada)
          3 Clyde  → persigue si está lejos, huye si está cerca
        """
        if self.idx == 0:
            return pr, pc
        elif self.idx == 1:
            return pr - 2, pc - 2   # Aprox. "adelante" de Pac-Man
        elif self.idx == 2:
            return pr + 1, pc + 1
        else:   # Clyde
            dist = math.hypot(r - pr, c - pc)
            if dist > 8:
                return pr, pc        # Persigue
            else:
                return ROWS - 2, 0  # Huye a esquina

    @property
    def pixel_pos(self):
        """Posición central en píxeles para dibujar el sprite."""
        cx = int(self.col * CELL + CELL // 2)
        cy = int(self.row * CELL + CELL // 2 + HUD_H)
        return cx, cy

    def draw(self, surface, frame):
        cx, cy = self.pixel_pos
        r      = CELL // 2 - 2

        if self.dead:
            # Solo dibujamos ojos (el cuerpo "voló")
            for side in [-1, 1]:
                ex = cx + side * r // 3
                ey = cy - r // 3
                pygame.draw.circle(surface, C_EYES,  (ex, ey), r // 4)
                pygame.draw.circle(surface, C_PUPIL, (ex, ey), r // 7)
        else:
            flash = self.scared and self.scared_timer < SCARED_FLASH_AT \
                    and (frame // 8) % 2 == 0
            draw_ghost(surface, cx, cy, r, self.color,
                       self.dir, self.scared, flash)


# ─────────────────────────────────────────────────────────────
# CLASE: PacMan
# ─────────────────────────────────────────────────────────────
class PacMan:
    def __init__(self):
        self.reset()

    def reset(self):
        self.row       = float(PACMAN_START[0])
        self.col       = float(PACMAN_START[1])
        self.dir       = (0, 0)        # Dirección actual
        self.next_dir  = (0, -1)       # Próxima dirección solicitada
        self.speed     = 0.10
        self.mouth     = 0             # Ángulo de la boca (0–40°)
        self.mouth_dir = 1             # 1 = abriendo, -1 = cerrando
        self.alive     = True

    def set_direction(self, d):
        """
        El jugador presiona una tecla: guardamos la dirección deseada.
        Se aplicará en cuanto sea posible (celda libre en esa dirección).
        """
        self.next_dir = d

    def update(self, grid):
        """
        Mueve a Pac-Man:
          1. Intenta aplicar la dirección deseada (next_dir).
          2. Si no puede, continúa con la dirección actual.
          3. Anima la boca.
        """
        r_int = int(round(self.row))
        c_int = int(round(self.col))

        # Al estar centrado en una celda: intentar cambiar de dirección
        if abs(self.row - r_int) < self.speed * 1.5 and \
           abs(self.col - c_int) < self.speed * 1.5:

            # Probar next_dir
            nr = r_int + self.next_dir[0]
            nc = c_int + self.next_dir[1]
            if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] != WALL:
                self.dir = self.next_dir
                self.row = float(r_int)
                self.col = float(c_int)

            # Si la dirección actual está bloqueada, detener
            nr2 = r_int + self.dir[0]
            nc2 = c_int + self.dir[1]
            if self.dir != (0, 0):
                if not (0 <= nr2 < ROWS and 0 <= nc2 < COLS) or \
                   grid[nr2][nc2] == WALL:
                    self.dir = (0, 0)

        # Mover
        self.row += self.dir[0] * self.speed
        self.col += self.dir[1] * self.speed

        # Túnel lateral
        if self.col < -0.5:
            self.col = COLS - 0.5
        elif self.col > COLS - 0.5:
            self.col = -0.5

        # Animar boca
        self.mouth += 3 * self.mouth_dir
        if self.mouth >= 38:
            self.mouth_dir = -1
        elif self.mouth <= 2:
            self.mouth_dir = 1

    @property
    def pixel_pos(self):
        cx = int(self.col * CELL + CELL // 2)
        cy = int(self.row * CELL + CELL // 2 + HUD_H)
        return cx, cy

    def draw(self, surface):
        cx, cy = self.pixel_pos
        r = CELL // 2 - 1
        dir_draw = self.dir if self.dir != (0, 0) else (1, 0)
        draw_pacman(surface, cx, cy, r, self.mouth,
                    (dir_draw[1], dir_draw[0]))  # (dx, dy) para draw_pacman


# ─────────────────────────────────────────────────────────────
# CLASE: Game
# ─────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        self.font_lg = pygame.font.SysFont("monospace", 24, bold=True)
        self.font_md = pygame.font.SysFont("monospace", 16, bold=True)
        self.font_sm = pygame.font.SysFont("monospace", 12)
        self.hi_score = 0
        self.reset()

    def reset(self, full=True):
        """
        full=True  → nueva partida completa (score=0, lives=3)
        full=False → siguiente nivel (score acumulado, mismas vidas)
        """
        if full:
            self.score = 0
            self.lives = 3
            self.level = 1

        # Copiar el laberinto para poder modificarlo al comer puntos
        self.grid = [row[:] for row in LEVEL_MAP]

        # Contar puntos totales para saber cuándo se gana el nivel
        self.total_dots = sum(
            1 for r in range(ROWS) for c in range(COLS)
            if self.grid[r][c] in (DOT, POWER)
        )
        self.eaten_dots = 0

        # Pac-Man
        self.pacman = PacMan()
        # Ajustar velocidad de Pac-Man según nivel
        self.pacman.speed = min(0.10 + self.level * 0.005, 0.16)

        # Fantasmas
        self.ghosts = [
            Ghost(i, *GHOST_STARTS[i], GHOST_COLORS[i])
            for i in range(4)
        ]
        # Ajustar velocidad de fantasmas según nivel
        for g in self.ghosts:
            g.speed = min(0.08 + self.level * 0.005, 0.13)

        # Estado del juego
        self.paused     = False
        self.game_over  = False
        self.won        = False
        self.frame      = 0
        self.death_timer = 0   # Frames de animación de muerte

        # Fruta
        self.fruit_active = False
        self.fruit_timer  = 0
        self.fruit_eaten  = False
        self.FRUIT_SPAWN  = self.total_dots // 2   # Aparece a mitad del nivel

        # Popups de puntos
        self.popups = []

        # Ghost combo (cuántos fantasmas se comen en cadena con 1 energizador)
        self.ghost_combo = 0

    # ── Lógica de juego ───────────────────────────────────────

    def _eat(self):
        """
        Comprueba si Pac-Man está sobre una celda comestible
        y aplica el efecto correspondiente.
        """
        r = int(round(self.pacman.row))
        c = int(round(self.pacman.col))
        if not (0 <= r < ROWS and 0 <= c < COLS):
            return

        cell = self.grid[r][c]

        if cell == DOT:
            self.grid[r][c] = EMPTY
            self.score      += PTS_DOT
            self.eaten_dots += 1

        elif cell == POWER:
            self.grid[r][c] = EMPTY
            self.score      += PTS_POWER
            self.eaten_dots += 1
            self.ghost_combo = 0
            # Activar modo asustado en todos los fantasmas
            for g in self.ghosts:
                g.activate_scared()

        # Aparición de la fruta
        if self.eaten_dots >= self.FRUIT_SPAWN and \
           not self.fruit_active and not self.fruit_eaten:
            self.fruit_active = True
            self.fruit_timer  = 300   # Disponible por 5 segundos

        # Fruta
        fr, fc = FRUIT_POS
        if self.fruit_active and r == fr and c == fc:
            self.fruit_active = False
            self.fruit_eaten  = True
            self.score       += PTS_FRUIT
            self._add_popup(PTS_FRUIT, fc, fr)

    def _check_ghost_collision(self):
        """
        Verifica si Pac-Man colisiona con algún fantasma:
          - Fantasma asustado → Pac-Man lo come (puntos + fantasma muerto).
          - Fantasma normal   → Pac-Man muere.
        """
        pr, pc = self.pacman.row, self.pacman.col

        for g in self.ghosts:
            if g.dead:
                continue
            dist = math.hypot(g.row - pr, g.col - pc)
            if dist < 0.8:
                if g.scared:
                    # Comer fantasma
                    g.scared = False
                    g.dead   = True
                    self.ghost_combo += 1
                    pts = PTS_GHOST * (2 ** (self.ghost_combo - 1))
                    self.score += pts
                    self._add_popup(pts, int(g.col), int(g.row))
                else:
                    # Pac-Man muere
                    self.death_timer = 90
                    self.pacman.alive = False

    def _add_popup(self, pts, col, row):
        self.popups.append({
            "text": str(pts),
            "x": col * CELL,
            "y": float(row * CELL + HUD_H),
            "life": 60,
        })

    def _check_win(self):
        """Si se comieron todos los puntos, se gana el nivel."""
        if self.eaten_dots >= self.total_dots:
            self.won = True

    def update(self, keys):
        if self.paused or self.game_over:
            return

        self.frame += 1

        # ── Animación de muerte ──
        if not self.pacman.alive:
            self.death_timer -= 1
            if self.death_timer <= 0:
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
                    self.hi_score  = max(self.hi_score, self.score)
                else:
                    # Reiniciar posiciones sin perder el tablero
                    self.pacman = PacMan()
                    for g in self.ghosts:
                        g.reset()
            return

        # ── Dirección del jugador ──
        if keys[pygame.K_LEFT]:
            self.pacman.set_direction((0, -1))
        elif keys[pygame.K_RIGHT]:
            self.pacman.set_direction((0,  1))
        elif keys[pygame.K_UP]:
            self.pacman.set_direction((-1, 0))
        elif keys[pygame.K_DOWN]:
            self.pacman.set_direction(( 1, 0))

        # ── Mover Pac-Man ──
        self.pacman.update(self.grid)

        # ── Comer puntos ──
        self._eat()

        # ── Mover fantasmas ──
        pr, pc = int(round(self.pacman.row)), int(round(self.pacman.col))
        for g in self.ghosts:
            g.update(self.grid, pr, pc, self.frame)

        # ── Colisiones con fantasmas ──
        self._check_ghost_collision()

        # ── Fruta ──
        if self.fruit_active:
            self.fruit_timer -= 1
            if self.fruit_timer <= 0:
                self.fruit_active = False

        # ── Popups ──
        for p in self.popups:
            p["y"]   -= 0.6
            p["life"] -= 1
        self.popups = [p for p in self.popups if p["life"] > 0]

        # ── Victoria ──
        self._check_win()
        if self.won:
            self.hi_score = max(self.hi_score, self.score)

    # ── Renderizado ───────────────────────────────────────────

    def draw(self, surface):
        surface.fill(C_BG)

        # ── HUD ──
        self._draw_hud(surface)

        # ── Laberinto ──
        for r in range(ROWS):
            for c in range(COLS):
                cell = self.grid[r][c]
                if cell == WALL:
                    draw_wall_cell(surface, r, c)
                elif cell == GATE:
                    # Puerta de la casa: línea magenta
                    x = c * CELL
                    y = r * CELL + HUD_H + CELL // 2
                    pygame.draw.line(surface, (200, 100, 255),
                                     (x, y), (x + CELL, y), 3)
                elif cell == DOT:
                    draw_dot(surface, r, c)
                elif cell == POWER:
                    draw_power(surface, r, c, self.frame)

        # ── Fruta ──
        if self.fruit_active:
            draw_fruit(surface, *FRUIT_POS)

        # ── Fantasmas ──
        for g in self.ghosts:
            g.draw(surface, self.frame)

        # ── Pac-Man ──
        if self.pacman.alive or (self.death_timer // 8) % 2 == 0:
            self.pacman.draw(surface)

        # ── Popups ──
        for p in self.popups:
            t = self.font_sm.render(p["text"], True, (255, 255, 100))
            surface.blit(t, (p["x"], int(p["y"])))

        # ── Overlays ──
        if self.paused:
            self._draw_overlay(surface, "PAUSA", "(P) continuar")
        elif self.game_over:
            self._draw_overlay(surface, "GAME OVER",
                               f"Puntaje: {self.score}   (R) reiniciar")
        elif self.won:
            self._draw_overlay(surface, f"¡NIVEL {self.level}!",
                               "Preparate para el siguiente...")

    def _draw_hud(self, surface):
        """HUD superior: hi-score, score y vidas."""
        pygame.draw.rect(surface, (10, 10, 30), (0, 0, SCREEN_W, HUD_H))

        hi = self.font_sm.render(f"MEJOR  {self.hi_score:06d}", True, C_HUD)
        surface.blit(hi, (8, 4))

        sc = self.font_md.render(f"SCORE  {self.score:06d}", True, C_TITLE)
        surface.blit(sc, (8, 22))

        lv = self.font_sm.render(f"NIV {self.level}", True, C_HUD)
        surface.blit(lv, (SCREEN_W // 2 - lv.get_width() // 2, 4))

        # Vidas como mini Pac-Mans
        lives_lbl = self.font_sm.render("VIDAS:", True, C_HUD)
        surface.blit(lives_lbl, (SCREEN_W - 130, 4))
        for i in range(self.lives):
            draw_pacman(surface,
                        SCREEN_W - 85 + i * 28, 22,
                        10, 30, (1, 0))

    def _draw_overlay(self, surface, title, subtitle):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        surface.blit(ov, (0, 0))

        t1 = self.font_lg.render(title, True, C_TITLE)
        surface.blit(t1, (SCREEN_W//2 - t1.get_width()//2,
                          SCREEN_H//2 - 36))
        t2 = self.font_sm.render(subtitle, True, C_TEXT)
        surface.blit(t2, (SCREEN_W//2 - t2.get_width()//2,
                          SCREEN_H//2 + 10))


# ─────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────
def main():
    pygame.init()
    pygame.display.set_caption("Pac-Man – Python")
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock  = pygame.time.Clock()

    game       = Game()
    won_timer  = 0   # Espera antes de pasar al siguiente nivel

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    game.reset(full=True)
                    won_timer = 0
                if event.key == pygame.K_p and not game.game_over and not game.won:
                    game.paused = not game.paused

        # Pasar al siguiente nivel automáticamente tras ganar
        if game.won:
            won_timer += 1
            if won_timer > 120:
                game.level += 1
                game.won   = False
                game.reset(full=False)
                won_timer  = 0

        keys = pygame.key.get_pressed()
        game.update(keys)
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
