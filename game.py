# game.py - Lógica principal, pantallas y renderizado del juego

import pygame
import sys
import math
import random
import array
from avl_tree import AVLTree
from game_data import COLORS, LEVELS, assign_suspects, get_evidence_for_level

# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1200, 800
FPS = 60

# Estados del juego
STATE_TITLE          = "title"
STATE_CHAR_SELECT    = "char_select"
STATE_LEVEL_INTRO    = "level_intro"
STATE_INVESTIGATION  = "investigation"
STATE_VERDICT        = "verdict"
STATE_LEVEL_COMPLETE = "level_complete"
STATE_VICTORY        = "victory"

# Sub-estados de investigación
INV_INTRO       = "inv_intro"
INV_COLLECT     = "inv_collect"
INV_ANALYZE     = "inv_analyze"
INV_ACCUSE      = "inv_accuse"
INV_WRONG       = "inv_wrong"
INV_CORRECT     = "inv_correct"
INV_TREE_REVIEW = "inv_tree_review"   # Nivel 5: revisión del árbol antes de acusar

# Colores por tipo de caso para los nodos del árbol AVL
CASE_COLORS = {
    "INJURIA":            (30, 100, 200),
    "CALUMNIA":           (180, 100, 20),
    "SUPLANTACIÓN":       (130, 40, 200),
    "ACOSO COORDINADO":   (200, 40, 40),
    "CASO FINAL":         (180, 160, 0),
}


# ─────────────────────────────────────────────
# UTILIDADES DE DIBUJO
# ─────────────────────────────────────────────
def draw_rounded_rect(surface, color, rect, radius=12, border=0, border_color=None):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)


def draw_text(surface, text, font, color, x, y, center=False, max_width=None):
    """Dibuja texto con opción de centrado y ajuste de ancho"""
    if max_width:
        words = text.split()
        lines = []
        current = ""
        for w in words:
            test = (current + " " + w).strip()
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = w
        if current:
            lines.append(current)
    else:
        lines = [text]

    offset_y = 0
    for line in lines:
        surf = font.render(line, True, color)
        rx = x - surf.get_width() // 2 if center else x
        surface.blit(surf, (rx, y + offset_y))
        offset_y += surf.get_height() + 2
    return offset_y


def wrap_text(text, font, max_width):
    """Divide texto en líneas que caben en max_width"""
    words = text.split()
    lines = []
    current = ""
    for w in words:
        test = (current + " " + w).strip()
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def pulse_value(t, speed=2.0, low=0.7, high=1.0):
    """Valor oscilante para animaciones"""
    return low + (high - low) * (0.5 + 0.5 * math.sin(t * speed))


def make_tone(frequency, duration_ms, volume=0.35, sample_rate=22050):
    """Genera un tono sin archivos de audio externos"""
    n = int(sample_rate * duration_ms / 1000)
    buf = array.array('h')
    fade = max(1, n // 8)
    for i in range(n):
        val = math.sin(2 * math.pi * frequency * i / sample_rate)
        if i < fade:
            val *= i / fade
        elif i > n - fade:
            val *= (n - i) / fade
        buf.append(int(32767 * volume * val))
    return pygame.mixer.Sound(buffer=buf)


# ─────────────────────────────────────────────
# BOTÓN INTERACTIVO
# ─────────────────────────────────────────────
class Button:
    def __init__(self, x, y, w, h, text, color=None, text_color=None,
                 font=None, radius=10, enabled=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color or COLORS["btn_primary"]
        self.text_color = text_color or COLORS["white"]
        self.font = font
        self.radius = radius
        self.enabled = enabled
        self.hovered = False
        self._ev_data: dict = {}
        self._suspect: dict = {}

    def draw(self, surface):
        if not self.enabled:
            c = COLORS["btn_disabled"]
            tc = COLORS["text_dim"]
        elif self.hovered:
            c = COLORS["btn_hover"]
            tc = COLORS["white"]
        else:
            c = self.color
            tc = self.text_color

        draw_rounded_rect(surface, c, self.rect, self.radius)
        pygame.draw.rect(surface, COLORS["gold"] if self.hovered and self.enabled
                         else (80, 100, 130), self.rect, 2, border_radius=self.radius)

        if self.font:
            ts = self.font.render(self.text, True, tc)
            surface.blit(ts, (self.rect.centerx - ts.get_width() // 2,
                               self.rect.centery - ts.get_height() // 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.enabled:
                return True
        return False


# ─────────────────────────────────────────────
# PARTÍCULA (efectos visuales)
# ─────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.life = random.uniform(0.5, 1.2)
        self.max_life = self.life
        self.color = color
        self.r = random.randint(3, 7)

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # gravedad
        self.life -= dt
        return self.life > 0

    def draw(self, surface):
        alpha = max(0, self.life / self.max_life)
        r = int(self.r * alpha)
        if r > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), r)


# ─────────────────────────────────────────────
# CLASE PRINCIPAL DEL JUEGO
# ─────────────────────────────────────────────
class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.t = 0.0  # tiempo acumulado para animaciones

        # Fuentes
        self.font_large   = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_med     = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_small   = pygame.font.SysFont("Arial", 18)
        self.font_tiny    = pygame.font.SysFont("Arial", 14)
        self.font_title   = pygame.font.SysFont("Arial", 52, bold=True)
        self.font_mono    = pygame.font.SysFont("Courier New", 16)

        # Estado del juego
        self.state = STATE_TITLE
        self.inv_state = INV_INTRO

        # Personaje elegido
        self.detective_gender = None  # "male" | "female"
        self.detective_name = ""

        # Progreso
        self.current_level_idx = 0
        self.avl = AVLTree()
        self.solved_levels = []
        self.particles = []
        self.score = 0

        # Datos del nivel actual
        self.level_data: dict = {}
        self.suspects: list[dict] = []
        self.guilty: dict | None = None
        self.evidence_pool: list[dict] = []
        self.collected_evidence: list[dict] = []
        self.narrator_lines: list[str] = []
        self.narrator_idx = 0

        # UI dinámica
        self.buttons = []
        self.evidence_buttons = []
        self.suspect_buttons = []
        self.wrong_attempts = 0
        self.show_hint = False
        self.show_evidence_review = False   # toggle panel de evidencias en INV_ACCUSE
        self.verdict_message = ""
        self.verdict_correct = False
        self.flash_timer = 0.0

        # Animación del árbol
        self.tree_anim_timer = 0.0
        self.new_node_highlight = None

        # Scroll del narrador
        self.narrator_scroll = 0

        # Advertencia de evidencia clave
        self.key_warn_timer = 0.0
        self.key_warn_msg = ""

        # Sonidos
        self.snd_correct = make_tone(880, 200)
        self.snd_wrong   = make_tone(220, 300, volume=0.5)
        self.snd_click   = make_tone(660, 80,  volume=0.2)
        self.snd_level   = make_tone(1046, 400, volume=0.4)

        self._init_title_screen()

    # ─────────────────────────────────────────
    # INIT SCREENS
    # ─────────────────────────────────────────
    def _init_title_screen(self):
        self.state = STATE_TITLE
        f = self.font_med
        self.buttons = [
            Button(SCREEN_W // 2 - 150, 520, 300, 55, "INICIAR JUEGO",
                   COLORS["btn_primary"], font=f, radius=12),
            Button(SCREEN_W // 2 - 150, 590, 300, 55, "SALIR",
                   (80, 30, 30), font=f, radius=12),
        ]

    def _init_char_select(self):
        self.state = STATE_CHAR_SELECT
        f = self.font_med
        self.buttons = [
            Button(SCREEN_W // 2 - 320, 420, 280, 80, "Detective Masculino",
                   (30, 80, 160), font=f, radius=12),
            Button(SCREEN_W // 2 + 40, 420, 280, 80, "Detective Femenino",
                   (140, 30, 120), font=f, radius=12),
        ]

    def _init_level_intro(self):
        self.state = STATE_LEVEL_INTRO
        self.level_data = LEVELS[self.current_level_idx]
        self.suspects, self.guilty = assign_suspects(self.level_data)
        self.evidence_pool = get_evidence_for_level(self.level_data)
        self.collected_evidence = []
        self.wrong_attempts = 0
        self.show_hint = False
        self.show_evidence_review = False
        self.narrator_lines = self.level_data["intro_lines"]
        self.narrator_idx = 0
        f = self.font_med
        self.buttons = [
            Button(SCREEN_W // 2 - 130, 680, 260, 52, "Comenzar Investigación",
                   COLORS["btn_primary"], font=f, radius=12),
        ]

    def _init_investigation(self):
        self.state = STATE_INVESTIGATION
        self.inv_state = INV_INTRO
        scenario_lines = wrap_text(self.level_data["scenario"], self.font_tiny, 350)
        self.narrator_lines = (
            [f"Caso: {self.level_data['subtitle']}",
             f"Víctima: {self.level_data['victim']}"]
            + scenario_lines
            + ["Presiona 'Recoger Evidencia' para comenzar."]
        )
        self._rebuild_inv_buttons()

    def _rebuild_inv_buttons(self):
        self.buttons = []
        self.evidence_buttons = []
        self.suspect_buttons = []
        f = self.font_small

        needed = self.level_data["evidence_needed"]
        collected = len(self.collected_evidence)

        if self.inv_state == INV_INTRO:
            self.buttons = [
                Button(8, 722, 374, 44, "▶ Recoger Evidencia",
                       COLORS["btn_primary"], font=f, radius=10),
            ]
        elif self.inv_state == INV_COLLECT:
            # Botones de evidencia disponible
            available = [e for e in self.evidence_pool
                         if e["id"] not in [c["id"] for c in self.collected_evidence]]
            by = 320
            for ev in available[:5]:
                label = f"★ {ev['name'][:32]}" if ev["is_key"] else f"  {ev['name'][:35]}"
                btn = Button(8, by, 374, 38, label,
                             (20, 90, 40) if ev["is_key"] else (20, 50, 100),
                             font=self.font_tiny, radius=8)
                btn._ev_data = ev
                self.evidence_buttons.append(btn)
                by += 44

            key_ids = set(self.level_data["key_evidence_ids"])
            collected_ids = {e["id"] for e in self.collected_evidence}
            has_all_keys = key_ids.issubset(collected_ids)
            can_analyze = collected >= needed and has_all_keys
            if can_analyze:
                btn_label = "▶ Analizar Sospechosos"
                btn_color = COLORS["success"]
                btn_text_color = (10, 20, 30)
            elif collected >= needed:
                btn_label = "⚠ Recolecta evidencias ★ clave"
                btn_color = COLORS["btn_disabled"]
                btn_text_color = COLORS["white"]
            else:
                btn_label = f"Evidencias: {collected}/{needed} — sigue buscando"
                btn_color = COLORS["btn_disabled"]
                btn_text_color = COLORS["white"]
            self.buttons = [
                Button(8, 722, 374, 44, btn_label,
                       btn_color, btn_text_color,
                       font=f, radius=10, enabled=can_analyze),
            ]

        elif self.inv_state == INV_ANALYZE:
            # Botones de sospechosos
            sy = 320
            for s in self.suspects:
                btn = Button(8, sy, 374, 48,
                             f"Buscar {s['name']} ({s['age']} anos)",
                             (20, 50, 95), font=f, radius=8)
                btn._suspect = s
                self.suspect_buttons.append(btn)
                sy += 54
            self.buttons = [
                Button(8, 722, 374, 44, "▶ Hacer Acusación",
                       COLORS["btn_primary"], font=f, radius=10),
            ]

        elif self.inv_state == INV_ACCUSE:
            # Botones de acusación — solo cuando NO estamos viendo el panel de evidencias
            if not self.show_evidence_review:
                sy = 320
                for s in self.suspects:
                    btn = Button(8, sy, 374, 46, f"⚖ Acusar a {s['name']}",
                                 (110, 25, 25), font=f, radius=8)
                    btn._suspect = s
                    self.suspect_buttons.append(btn)
                    sy += 72
            # Dos botones lado a lado: pista | evidencias
            hint_text = "Ocultar Pista" if self.show_hint else "💡 Ver Pista"
            ev_text   = "Ocultar Evidencias" if self.show_evidence_review else "📋 Ver Evidencias"
            btn_hint = Button(8,   722, 183, 44, hint_text, (80, 60, 10), font=f, radius=10)
            btn_hint._action = "hint"
            btn_ev   = Button(199, 722, 183, 44, ev_text, (20, 60, 110), font=f, radius=10)
            btn_ev._action = "evidence"
            self.buttons = [btn_hint, btn_ev]

        elif self.inv_state == INV_TREE_REVIEW:
            self.buttons = [
                Button(8, 722, 374, 44, "▶ Hacer Acusación Final",
                       COLORS["gold"], (0, 0, 0), font=f, radius=10),
            ]

        elif self.inv_state in (INV_WRONG, INV_CORRECT):
            self.buttons = [
                Button(8, 722, 374, 44,
                       "▶ Continuar" if self.inv_state == INV_CORRECT else "▶ Reintentar",
                       COLORS["success"] if self.inv_state == INV_CORRECT else COLORS["error"],
                       font=f, radius=10),
            ]

    # ─────────────────────────────────────────
    # LOOP PRINCIPAL
    # ─────────────────────────────────────────
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            self.t += dt
            self.flash_timer = max(0, self.flash_timer - dt)
            self.tree_anim_timer = max(0, self.tree_anim_timer - dt)
            self.key_warn_timer = max(0, self.key_warn_timer - dt)

            # Actualizar partículas
            self.particles = [p for p in self.particles if p.update(dt)]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self._handle_event(event)

            self._draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    # ─────────────────────────────────────────
    # MANEJO DE EVENTOS
    # ─────────────────────────────────────────
    def _handle_event(self, event):
        if self.state == STATE_TITLE:
            self._handle_title(event)
        elif self.state == STATE_CHAR_SELECT:
            self._handle_char_select(event)
        elif self.state == STATE_LEVEL_INTRO:
            self._handle_level_intro(event)
        elif self.state == STATE_INVESTIGATION:
            self._handle_investigation(event)
        elif self.state == STATE_LEVEL_COMPLETE:
            self._handle_level_complete(event)
        elif self.state == STATE_VICTORY:
            self._handle_victory(event)

    def _handle_title(self, event):
        for i, btn in enumerate(self.buttons):
            if btn.handle_event(event):
                if i == 0:
                    self._init_char_select()
                elif i == 1:
                    pygame.quit()
                    sys.exit()

    def _handle_char_select(self, event):
        for i, btn in enumerate(self.buttons):
            if btn.handle_event(event):
                if i == 0:
                    self.detective_gender = "male"
                    self.detective_name = "Det. Rodrigo Vargas"
                else:
                    self.detective_gender = "female"
                    self.detective_name = "Det. Carolina Reyes"
                self.current_level_idx = 0
                self._init_level_intro()

    def _handle_level_intro(self, event):
        for btn in self.buttons:
            if btn.handle_event(event):
                self._init_investigation()
                return  # evita avanzar narrator_idx tras iniciar investigación
        # Click avanza línea narradora
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.narrator_idx < len(self.narrator_lines) - 1:
                self.narrator_idx += 1

    def _handle_investigation(self, event):
        # Botones de evidencia
        for btn in self.evidence_buttons:
            if btn.handle_event(event):
                ev = btn._ev_data
                if ev["id"] not in [c["id"] for c in self.collected_evidence]:
                    self.collected_evidence.append(ev)
                    key_marker = " [EVIDENCIA CLAVE ★]" if ev["is_key"] else ""
                    self._show_narrator(
                        f"Recolectada{key_marker}: {ev['name']}. {ev['detail']}"
                    )
                    color = COLORS["gold"] if ev["is_key"] else COLORS["cyan"]
                    self._spawn_particles(SCREEN_W // 2, SCREEN_H // 2, color)
                    self.snd_click.play()
                    self._rebuild_inv_buttons()

        # Botones de sospechosos
        for btn in self.suspect_buttons:
            if btn.handle_event(event):
                s = btn._suspect
                if self.inv_state == INV_ANALYZE:
                    self._show_narrator(
                        f"Sospechoso: {s['name']}, {s['age']} años. {s['profile']}"
                    )
                elif self.inv_state == INV_ACCUSE:
                    self._process_accusation(s)

        # Botones principales
        for btn in self.buttons:
            if btn.handle_event(event):
                self._process_main_btn(getattr(btn, "_action", None))
                return

    def _process_main_btn(self, action=None):
        self.snd_click.play()

        if self.inv_state == INV_INTRO:
            pronoun = "Detective" if not self.detective_gender else (
                "Det. Vargas" if self.detective_gender == "male" else "Det. Reyes"
            )
            self.inv_state = INV_COLLECT
            self._show_narrator(
                f"{pronoun}, revisa las evidencias del panel izquierdo. "
                "Las marcadas con ★ son evidencias CLAVE — sin ellas no podrás acusar."
            )
            self._rebuild_inv_buttons()

        elif self.inv_state == INV_COLLECT:
            needed = self.level_data["evidence_needed"]
            if len(self.collected_evidence) >= needed:
                key_ids = set(self.level_data["key_evidence_ids"])
                collected_ids = {e["id"] for e in self.collected_evidence}
                missing = key_ids - collected_ids
                if missing:
                    missing_names = [e["name"] for e in self.evidence_pool if e["id"] in missing]
                    msg = "Faltan claves ★: " + ", ".join(missing_names[:2])
                    self._show_narrator(
                        f"¡Faltan evidencias clave (★)! Sin estas no puedes acusar: "
                        + ", ".join(missing_names[:2])
                    )
                    self.key_warn_msg = msg
                    self.key_warn_timer = 3.5
                else:
                    self.inv_state = INV_ANALYZE
                    self._show_narrator("Evidencias clave aseguradas. Ahora revisa los perfiles "
                                        "de los sospechosos antes de acusar.")
                    self._rebuild_inv_buttons()

        elif self.inv_state == INV_ANALYZE:
            # Nivel 5 → revisión del árbol completo antes de acusar
            if self.level_data["id"] == 5:
                self.inv_state = INV_TREE_REVIEW
                self._show_narrator(
                    "Antes de tu acusación final: analiza el Árbol AVL. "
                    "Los 4 casos anteriores están conectados por el mismo servidor. "
                    "Recorre el árbol en inorden y verás la cadena completa."
                )
                self._rebuild_inv_buttons()
            else:
                self.inv_state = INV_ACCUSE
                self._show_narrator(self.level_data["question"])
                self._rebuild_inv_buttons()

        elif self.inv_state == INV_TREE_REVIEW:
            self.inv_state = INV_ACCUSE
            self._show_narrator(self.level_data["question"])
            self._rebuild_inv_buttons()

        elif self.inv_state == INV_ACCUSE:
            if action == "evidence":
                self.show_evidence_review = not self.show_evidence_review
                if self.show_evidence_review:
                    self.show_hint = False
            else:  # action == "hint" o default
                self.show_hint = not self.show_hint
                if self.show_hint:
                    self.show_evidence_review = False
                    self._show_narrator(f"PISTA: {self.level_data['hint']}")
            self._rebuild_inv_buttons()

        elif self.inv_state == INV_CORRECT:
            self._complete_level()

        elif self.inv_state == INV_WRONG:
            self.inv_state = INV_ACCUSE
            self._show_narrator("Inténtalo de nuevo. Revisa la evidencia clave marcada con ★.")
            self._rebuild_inv_buttons()

    def _process_accusation(self, suspect):
        if suspect["guilty"]:
            # CORRECTO
            self.snd_correct.play()
            self.inv_state = INV_CORRECT
            self.verdict_correct = True
            self.flash_timer = 0.8
            bonus = max(100 - self.wrong_attempts * 20, 20)
            self.score += bonus
            reveal = self.level_data["guilty_reveal"].format(culprit=suspect["name"])
            pronoun = "Detective" if not self.detective_gender else (
                "Det. Vargas" if self.detective_gender == "male" else "Det. Reyes"
            )
            self._show_narrator(
                f"¡CORRECTO, {pronoun}! {reveal} (+{bonus} pts)"
            )
            self._spawn_particles(SCREEN_W // 2, 400, COLORS["success"], n=40)

            # Insertar en el árbol AVL — aquí es donde el árbol cobra significado
            ld = self.level_data
            ev_names = [e["name"] for e in self.collected_evidence]
            new_node = self.avl.insert(
                ld["case_id"], ld["case_type"], ev_names,
                ld["law"], ld["penalty"],
                f"Culpable: {suspect['name']}"
            )
            self.new_node_highlight = new_node
            self.tree_anim_timer = 2.5
            self._rebuild_inv_buttons()
        else:
            # INCORRECTO
            self.snd_wrong.play()
            self.wrong_attempts += 1
            self.inv_state = INV_WRONG
            self.verdict_correct = False
            self.flash_timer = 0.5
            self._show_narrator(
                f"{suspect['name']} no es el culpable. "
                f"Revisa las evidencias clave (★). (Intento {self.wrong_attempts})"
            )
            self._rebuild_inv_buttons()

    def _complete_level(self):
        self.snd_level.play()
        self.solved_levels.append(self.level_data)
        self.state = STATE_LEVEL_COMPLETE
        self.flash_timer = 0.0
        f = self.font_med
        if self.current_level_idx < len(LEVELS) - 1:
            self.buttons = [
                Button(SCREEN_W // 2 - 160, 700, 320, 55, "▶ Siguiente Nivel",
                       COLORS["btn_primary"], font=f, radius=12),
            ]
        else:
            self.buttons = [
                Button(SCREEN_W // 2 - 160, 700, 320, 55, "▶ Ver Victoria",
                       COLORS["gold"], (0, 0, 0), font=f, radius=12),
            ]
        self._spawn_particles(SCREEN_W // 2, SCREEN_H // 2, COLORS["gold"], n=60)

    def _handle_level_complete(self, event):
        for btn in self.buttons:
            if btn.handle_event(event):
                self.current_level_idx += 1
                if self.current_level_idx < len(LEVELS):
                    self._init_level_intro()
                else:
                    self._init_victory()

    def _init_victory(self):
        self.state = STATE_VICTORY
        f = self.font_med
        self.buttons = [
            Button(SCREEN_W // 2 - 160, 720, 320, 55, "Jugar de Nuevo",
                   COLORS["btn_primary"], font=f, radius=12),
        ]
        self._spawn_particles(SCREEN_W // 2, SCREEN_H // 2, COLORS["gold"], n=100)

    def _handle_victory(self, event):
        for btn in self.buttons:
            if btn.handle_event(event):
                self.avl = AVLTree()
                self.solved_levels = []
                self.score = 0
                self.current_level_idx = 0
                self._init_char_select()

    # ─────────────────────────────────────────
    # EFECTOS
    # ─────────────────────────────────────────
    def _show_narrator(self, text):
        self.narrator_lines = wrap_text(text, self.font_tiny, 355)
        self.narrator_idx = 0

    def _spawn_particles(self, x, y, color, n=20):
        for _ in range(n):
            self.particles.append(Particle(x, y, color))

    # ─────────────────────────────────────────
    # DIBUJO PRINCIPAL
    # ─────────────────────────────────────────
    def _draw(self):
        self.screen.fill(COLORS["bg"])
        self._draw_bg_grid()

        if self.state == STATE_TITLE:
            self._draw_title()
        elif self.state == STATE_CHAR_SELECT:
            self._draw_char_select()
        elif self.state == STATE_LEVEL_INTRO:
            self._draw_level_intro()
        elif self.state == STATE_INVESTIGATION:
            self._draw_investigation()
        elif self.state == STATE_LEVEL_COMPLETE:
            self._draw_level_complete()
        elif self.state == STATE_VICTORY:
            self._draw_victory()

        # Partículas encima de todo
        for p in self.particles:
            p.draw(self.screen)

        # Flash de feedback
        if self.flash_timer > 0:
            alpha = int(255 * (self.flash_timer / 0.8) * 0.3)
            color = COLORS["success"] if self.verdict_correct else COLORS["error"]
            flash_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            flash_surf.fill((*color, alpha))
            self.screen.blit(flash_surf, (0, 0))

    def _draw_bg_grid(self):
        """Cuadrícula de fondo sutil"""
        gc = (20, 35, 52)
        for x in range(0, SCREEN_W, 60):
            pygame.draw.line(self.screen, gc, (x, 0), (x, SCREEN_H))
        for y in range(0, SCREEN_H, 60):
            pygame.draw.line(self.screen, gc, (0, y), (SCREEN_W, y))

    # ─────────────────────────────────────────
    # PANTALLA: TÍTULO
    # ─────────────────────────────────────────
    def _draw_title(self):
        # Logo
        pulse = pulse_value(self.t, 1.5)
        title_color = (
            int(255 * pulse),
            int(215 * pulse),
            int(0 * pulse),
        )
        t1 = self.font_title.render("CyberDetective", True, COLORS["gold"])
        t2 = self.font_large.render("El Árbol de la Verdad", True, COLORS["cyan"])
        self.screen.blit(t1, (SCREEN_W // 2 - t1.get_width() // 2, 160))
        self.screen.blit(t2, (SCREEN_W // 2 - t2.get_width() // 2, 225))

        # Subtítulo
        sub = self.font_small.render(
            "Un juego educativo sobre ciberacoso y sus consecuencias legales",
            True, COLORS["text_dim"]
        )
        self.screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 285))

        # Detective animado (ícono)
        icon_y = 340 + int(8 * math.sin(self.t * 2))
        icon = self.font_title.render("🔍", True, COLORS["white"])
        self.screen.blit(icon, (SCREEN_W // 2 - icon.get_width() // 2, icon_y))

        # Info de leyes
        laws_y = 420
        laws = [
            "Art. 220 C.P. – Injuria",
            "Art. 221 C.P. – Calumnia",
            "Ley 1273/2009 – Delitos Informáticos",
        ]
        for law in laws:
            lt = self.font_tiny.render(law, True, COLORS["text_dim"])
            self.screen.blit(lt, (SCREEN_W // 2 - lt.get_width() // 2, laws_y))
            laws_y += 20

        # Botones
        for btn in self.buttons:
            btn.font = btn.font or self.font_med
            btn.draw(self.screen)

        # Crédito
        cr = self.font_tiny.render("Proyecto Universitario – Estructuras de Datos", True, (70, 90, 110))
        self.screen.blit(cr, (SCREEN_W // 2 - cr.get_width() // 2, SCREEN_H - 30))

    # ─────────────────────────────────────────
    # PANTALLA: SELECCIÓN DE PERSONAJE
    # ─────────────────────────────────────────
    def _draw_char_select(self):
        title = self.font_large.render("Elige tu Detective", True, COLORS["gold"])
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 120))

        sub = self.font_small.render(
            "El personaje que elijas narrará la investigación", True, COLORS["text_dim"]
        )
        self.screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 175))

        # Tarjeta masculina
        card_m = pygame.Rect(SCREEN_W // 2 - 340, 220, 280, 200)
        draw_rounded_rect(self.screen, COLORS["panel"], card_m, 15, 2, (80, 130, 200))
        icon_m = self.font_title.render("🕵", True, (100, 170, 255))
        self.screen.blit(icon_m, (card_m.centerx - icon_m.get_width() // 2, 245))
        nm = self.font_med.render("Det. Rodrigo Vargas", True, COLORS["text"])
        self.screen.blit(nm, (card_m.centerx - nm.get_width() // 2, 345))
        desc_m = self.font_tiny.render("Especialista en Delitos Digitales", True, COLORS["text_dim"])
        self.screen.blit(desc_m, (card_m.centerx - desc_m.get_width() // 2, 372))

        # Tarjeta femenina
        card_f = pygame.Rect(SCREEN_W // 2 + 60, 220, 280, 200)
        draw_rounded_rect(self.screen, COLORS["panel"], card_f, 15, 2, (200, 80, 180))
        icon_f = self.font_title.render("🕵", True, (220, 120, 255))
        self.screen.blit(icon_f, (card_f.centerx - icon_f.get_width() // 2, 245))
        nf = self.font_med.render("Det. Carolina Reyes", True, COLORS["text"])
        self.screen.blit(nf, (card_f.centerx - nf.get_width() // 2, 345))
        desc_f = self.font_tiny.render("Experta en Cibercriminología", True, COLORS["text_dim"])
        self.screen.blit(desc_f, (card_f.centerx - desc_f.get_width() // 2, 372))

        for btn in self.buttons:
            btn.draw(self.screen)

        # Caja de reglas con fondo coloreado
        rules_y = 530
        rules_rect = pygame.Rect(SCREEN_W // 2 - 310, rules_y - 10, 620, 130)
        draw_rounded_rect(self.screen, (12, 28, 48), rules_rect, 12, 2, (50, 90, 140))

        rules_title = self.font_small.render("CÓMO JUGAR:", True, COLORS["gold"])
        self.screen.blit(rules_title, (SCREEN_W // 2 - rules_title.get_width() // 2, rules_y))

        rules = [
            "1. Recolecta evidencias haciendo clic en los paneles",
            "2. Analiza los perfiles de los sospechosos",
            "3. Haz tu acusación — ¡piensa antes de actuar!",
            "4. Las evidencias se guardan en el Árbol AVL automáticamente",
        ]
        ry = rules_y + 26
        for line in rules:
            rt = self.font_tiny.render(line, True, COLORS["text_dim"])
            self.screen.blit(rt, (SCREEN_W // 2 - rt.get_width() // 2, ry))
            ry += 20

    # ─────────────────────────────────────────
    # PANTALLA: INTRO DE NIVEL
    # ─────────────────────────────────────────
    def _draw_level_intro(self):
        ld = self.level_data
        accent = ld["color_accent"]

        # Encabezado
        header_rect = pygame.Rect(0, 0, SCREEN_W, 90)
        pygame.draw.rect(self.screen, COLORS["panel"], header_rect)
        pygame.draw.line(self.screen, accent, (0, 90), (SCREEN_W, 90), 3)

        lt = self.font_large.render(ld["title"], True, accent)
        self.screen.blit(lt, (60, 20))
        ls = self.font_small.render(ld["subtitle"], True, COLORS["text_dim"])
        self.screen.blit(ls, (60, 60))

        # Número de nivel
        ln = self.font_title.render(str(ld["id"]), True, (*accent, 60))
        self.screen.blit(ln, (SCREEN_W - 100, 15))

        # Panel del narrador
        narr_rect = pygame.Rect(80, 120, SCREEN_W - 160, 300)
        draw_rounded_rect(self.screen, COLORS["panel"], narr_rect, 15, 2, accent)

        detective_icon = "🕵" if self.detective_gender else "🔍"
        icon_surf = self.font_large.render(detective_icon, True, COLORS["white"])
        self.screen.blit(icon_surf, (110, 140))

        name_surf = self.font_small.render(self.detective_name, True, accent)
        self.screen.blit(name_surf, (160, 140))

        # Texto narrador (líneas de intro) — mostrar hasta narrator_idx
        ny = 185
        for line in self.narrator_lines[:self.narrator_idx + 1]:
            lt = self.font_small.render(line, True, COLORS["text"])
            self.screen.blit(lt, (110, ny))
            ny += 28

        # Click to continue hint
        if self.t % 1.0 < 0.7:
            hint = self.font_tiny.render("(Haz clic para avanzar el texto)", True, COLORS["text_dim"])
            self.screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, 445))

        # Info del caso
        info_rect = pygame.Rect(80, 480, SCREEN_W - 160, 170)
        draw_rounded_rect(self.screen, COLORS["panel_light"], info_rect, 12, 1, (60, 80, 100))

        info_y = 498
        infos = [
            ("Víctima:", ld["victim"]),
            ("Tipo de Delito:", ld["case_type"]),
            ("Ley Aplicable:", ld["law"]),
            ("Pena:", ld["penalty"]),
        ]
        for label, value in infos:
            lt = self.font_small.render(label, True, COLORS["gold"])
            lv = self.font_small.render(value, True, COLORS["text"])
            self.screen.blit(lt, (110, info_y))
            self.screen.blit(lv, (280, info_y))
            info_y += 32

        for btn in self.buttons:
            btn.draw(self.screen)

    # ─────────────────────────────────────────
    # PANTALLA: INVESTIGACIÓN
    # ─────────────────────────────────────────
    def _draw_investigation(self):
        # Layout: izquierda=panel, centro=árbol, derecha=info
        self._draw_inv_left_panel()
        if self.inv_state == INV_TREE_REVIEW:
            self._draw_tree_review_panel()
        else:
            self._draw_avl_panel()
        self._draw_inv_right_panel()
        self._draw_inv_header()

    def _draw_inv_header(self):
        ld = self.level_data
        hbar = pygame.Rect(0, 0, SCREEN_W, 55)
        pygame.draw.rect(self.screen, COLORS["panel"], hbar)
        pygame.draw.line(self.screen, ld["color_accent"], (0, 55), (SCREEN_W, 55), 2)

        title_s = self.font_med.render(ld["title"], True, ld["color_accent"])
        self.screen.blit(title_s, (20, 15))

        # Detective
        det = self.font_small.render(f"  {self.detective_name}", True, COLORS["text_dim"])
        self.screen.blit(det, (SCREEN_W // 2 - det.get_width() // 2, 18))

        # Score + progreso
        score_s = self.font_small.render(f"Puntos: {self.score}", True, COLORS["gold"])
        self.screen.blit(score_s, (SCREEN_W - 160, 18))

        # Barra de progreso evidencia
        needed = ld["evidence_needed"]
        collected = len(self.collected_evidence)
        prog_rect = pygame.Rect(SCREEN_W - 280, 40, 100, 8)
        pygame.draw.rect(self.screen, (40, 60, 80), prog_rect, border_radius=4)
        fill_w = int(100 * min(collected / needed, 1.0))
        if fill_w > 0:
            pygame.draw.rect(self.screen, COLORS["success"],
                             (prog_rect.x, prog_rect.y, fill_w, 8), border_radius=4)
        prog_label = self.font_tiny.render(f"Evidencia {collected}/{needed}", True, COLORS["text_dim"])
        self.screen.blit(prog_label, (SCREEN_W - 400, 37))

    def _draw_inv_left_panel(self):
        """Panel izquierdo con layout claro sin solapamientos de texto.

        Layout (y relativo al panel, desde y=56 de pantalla):
          y=56-84:   Header oscuro + título "PANEL DE INVESTIGACIÓN"
          y=84:      Separador dorado
          y=86-120:  Step pills (① Recoger  ② Analizar  ③ Acusar)
          y=120:     Separador
          y=123-287: Narrator box (164px, borde cian)
          y=287:     Separador
          y=290-692: CLIPPED ZONE — sección dinámica según inv_state
          y=692:     Separador
          y=694-720: Barra de progreso + texto de estado
          y=722-766: Botón principal (44px alto)
          y=768-792: Barra de intentos fallidos (si aplica)
        """
        # Fondo del panel
        panel = pygame.Rect(0, 56, 390, SCREEN_H - 56)
        draw_rounded_rect(self.screen, COLORS["panel"], panel, 0)
        pygame.draw.line(self.screen, (40, 70, 100), (390, 56), (390, SCREEN_H), 2)

        # ── Header oscuro ──────────────────────────────────────────────
        header_bar = pygame.Rect(0, 56, 390, 28)
        pygame.draw.rect(self.screen, (8, 20, 36), header_bar)
        pt = self.font_tiny.render("PANEL DE INVESTIGACIÓN", True, COLORS["gold"])
        self.screen.blit(pt, (190 - pt.get_width() // 2, 63))

        # Separador dorado
        pygame.draw.line(self.screen, COLORS["gold"], (0, 84), (390, 84), 1)

        # ── Step indicator pills ───────────────────────────────────────
        step_labels = ["① Recoger", "② Analizar", "③ Acusar"]
        step_map = {
            INV_INTRO: 0, INV_COLLECT: 0,
            INV_ANALYZE: 1, INV_TREE_REVIEW: 1,
            INV_ACCUSE: 2, INV_WRONG: 2, INV_CORRECT: 2,
        }
        current_step = step_map.get(self.inv_state, 0)
        step_xs = [65, 195, 320]
        pill_y = 88

        for i, (sx, slabel) in enumerate(zip(step_xs, step_labels)):
            done   = i < current_step
            active = i == current_step
            if done:
                bg_c  = (15, 65, 30)
                bdr_c = COLORS["success"]
                txt_c = COLORS["success"]
            elif active:
                bg_c  = (30, 55, 90)
                bdr_c = COLORS["gold"]
                txt_c = COLORS["gold"]
            else:
                bg_c  = (18, 30, 45)
                bdr_c = (50, 70, 90)
                txt_c = (60, 80, 100)

            pill_w = 100
            pill_rect = pygame.Rect(sx - pill_w // 2, pill_y, pill_w, 26)
            draw_rounded_rect(self.screen, bg_c, pill_rect, 10, 1, bdr_c)
            label_text = ("✓ " + slabel) if done else slabel
            ls = self.font_tiny.render(label_text, True, txt_c)
            self.screen.blit(ls, (pill_rect.centerx - ls.get_width() // 2,
                                   pill_rect.centery - ls.get_height() // 2))

        # Separador
        pygame.draw.line(self.screen, (40, 60, 85), (0, 120), (390, 120), 1)

        # ── Narrator box ────────────────────────────────────────────────
        narr_bg = pygame.Rect(6, 123, 378, 162)
        draw_rounded_rect(self.screen, (14, 30, 50), narr_bg, 10, 1, COLORS["cyan"])

        # Detective name header
        nt = self.font_tiny.render(f"{self.detective_name}:", True, COLORS["cyan"])
        self.screen.blit(nt, (14, 126))
        pygame.draw.line(self.screen, (40, 80, 110), (10, 142), (380, 142), 1)

        # Narrator text — 7 lines max at 18px each (fits 164px box)
        ny = 146
        for line in self.narrator_lines[:7]:
            lt = self.font_tiny.render(line, True, COLORS["text"])
            self.screen.blit(lt, (14, ny))
            ny += 18

        # Separador
        pygame.draw.line(self.screen, (40, 60, 85), (0, 287), (390, 287), 1)

        # ── CLIPPED CONTENT ZONE (y=290 to y=692) ──────────────────────
        clip_rect = pygame.Rect(0, 290, 390, 402)
        self.screen.set_clip(clip_rect)

        # Section header pill (colored by state)
        section_cfg = {
            INV_INTRO:   ((12, 40, 75),  COLORS["cyan"],    "Presiona el botón para iniciar"),
            INV_COLLECT: ((15, 58, 32),  COLORS["success"], "EVIDENCIAS DISPONIBLES — clic para recoger"),
            INV_ANALYZE: ((14, 42, 85),  COLORS["cyan"],    "SOSPECHOSOS — clic para ver perfil"),
            INV_ACCUSE:  ((72, 16, 16),  COLORS["error"],   "VER EVIDENCIAS" if self.show_evidence_review else "QUIÉN ES EL CULPABLE? — clic para acusar"),
            INV_TREE_REVIEW: ((14, 42, 85), COLORS["cyan"], "SOSPECHOSOS — revisa el árbol primero"),
            INV_CORRECT: ((10, 65, 32),  COLORS["success"], "ACUSACIÓN CORRECTA!"),
            INV_WRONG:   ((65, 12, 12),  COLORS["error"],   "ACUSACIÓN INCORRECTA"),
        }
        s_bg, s_bdr, s_txt = section_cfg.get(self.inv_state,
                                               ((20, 40, 65), COLORS["cyan"], ""))
        section_pill = pygame.Rect(4, 292, 382, 24)
        draw_rounded_rect(self.screen, s_bg, section_pill, 8, 1, s_bdr)
        sec_surf = self.font_tiny.render(s_txt, True, s_bdr)
        self.screen.blit(sec_surf, (section_pill.centerx - sec_surf.get_width() // 2,
                                    section_pill.centery - sec_surf.get_height() // 2))

        # ── Interactive items starting at y=320 ──────────────────────
        if self.inv_state == INV_COLLECT:
            # Evidence buttons (already positioned at y=320 by _rebuild_inv_buttons)
            for btn in self.evidence_buttons:
                btn.draw(self.screen)

            # Collected evidence summary BELOW buttons
            last_ev_btn_bottom = 320 + len(self.evidence_buttons) * 44
            summary_y = max(last_ev_btn_bottom + 8, 548)

            needed = self.level_data["evidence_needed"]
            collected_n = len(self.collected_evidence)
            key_ids = set(self.level_data["key_evidence_ids"])
            collected_ids = {e["id"] for e in self.collected_evidence}
            keys_found = len(key_ids & collected_ids)
            keys_total = len(key_ids)

            if self.collected_evidence:
                col_label = f"Recolectadas: {collected_n}/{needed}  Claves: {keys_found}/{keys_total}"
                ev_title_color = (COLORS["success"] if keys_found == keys_total and collected_n >= needed
                                  else COLORS["gold"])
                ev_header = self.font_tiny.render(col_label, True, ev_title_color)
                self.screen.blit(ev_header, (10, summary_y))
                summary_y += 16

                for ev in self.collected_evidence[:6]:
                    key_marker = "★" if ev["is_key"] else "◆"
                    marker_color = COLORS["gold"] if ev["is_key"] else COLORS["cyan"]
                    mk = self.font_tiny.render(key_marker, True, marker_color)
                    self.screen.blit(mk, (12, summary_y))
                    name_short = ev["name"][:42]
                    et = self.font_tiny.render(name_short, True, COLORS["text"])
                    self.screen.blit(et, (26, summary_y))
                    summary_y += 16

            # Key warning
            if self.key_warn_timer > 0:
                warn_rect = pygame.Rect(6, 648, 378, 36)
                draw_rounded_rect(self.screen, (60, 20, 5), warn_rect, 6, 1, COLORS["warning"])
                wt = self.font_tiny.render("⚠ " + self.key_warn_msg[:52], True, COLORS["warning"])
                self.screen.blit(wt, (12, 656))

        elif self.inv_state in (INV_ANALYZE, INV_TREE_REVIEW):
            # Suspect buttons for ANALYZE (y=320+)
            for btn in self.suspect_buttons:
                btn.draw(self.screen)

        elif self.inv_state == INV_ACCUSE:
            if self.show_evidence_review:
                # Panel de evidencias recolectadas
                ev_y = 322
                hdr = self.font_tiny.render("EVIDENCIAS RECOLECTADAS:", True, COLORS["gold"])
                self.screen.blit(hdr, (10, ev_y))
                ev_y += 20
                for ev in self.collected_evidence:
                    if ev_y > 660:
                        break
                    bg  = (18, 58, 22) if ev["is_key"] else (14, 32, 62)
                    bdr = COLORS["gold"] if ev["is_key"] else COLORS["cyan"]
                    ev_box = pygame.Rect(6, ev_y, 378, 48)
                    draw_rounded_rect(self.screen, bg, ev_box, 6, 1, bdr)
                    mk_c = COLORS["gold"] if ev["is_key"] else COLORS["cyan"]
                    mk = self.font_tiny.render("★" if ev["is_key"] else "◆", True, mk_c)
                    self.screen.blit(mk, (12, ev_y + 5))
                    name_s = self.font_small.render(ev["name"][:36], True, COLORS["text"])
                    self.screen.blit(name_s, (26, ev_y + 3))
                    det_lines = wrap_text(ev["detail"], self.font_tiny, 350)
                    if det_lines:
                        det_s = self.font_tiny.render(det_lines[0][:50], True, (150, 175, 205))
                        self.screen.blit(det_s, (26, ev_y + 25))
                    ev_y += 54
            else:
                # Botones de sospechosos + perfil debajo de cada uno
                for btn in self.suspect_buttons:
                    btn.draw(self.screen)
                    s = btn._suspect
                    plines = wrap_text(s["profile"], self.font_tiny, 350)
                    py = btn.rect.bottom + 2
                    for pl in plines[:2]:
                        ps = self.font_tiny.render(pl, True, (118, 145, 175))
                        self.screen.blit(ps, (14, py))
                        py += 14

        elif self.inv_state == INV_CORRECT:
            ok_surf = self.font_small.render("¡Caso resuelto correctamente!", True, COLORS["success"])
            self.screen.blit(ok_surf, (195 - ok_surf.get_width() // 2, 340))
            score_surf = self.font_tiny.render(f"Puntos totales: {self.score}", True, COLORS["gold"])
            self.screen.blit(score_surf, (195 - score_surf.get_width() // 2, 366))

        elif self.inv_state == INV_WRONG:
            err_surf = self.font_small.render("Acusación incorrecta — ¡Inténtalo de nuevo!", True, COLORS["error"])
            self.screen.blit(err_surf, (195 - err_surf.get_width() // 2, 340))
            att_surf = self.font_tiny.render(f"Intentos fallidos: {self.wrong_attempts}", True, COLORS["error"])
            self.screen.blit(att_surf, (195 - att_surf.get_width() // 2, 364))

        # End clip
        self.screen.set_clip(None)

        # ── Separador inferior de la zona clipeada ───────────────────
        pygame.draw.line(self.screen, (40, 60, 85), (0, 692), (390, 692), 1)

        # ── Progress bar + status text ───────────────────────────────
        needed = self.level_data["evidence_needed"]
        collected_n = len(self.collected_evidence)
        key_ids = set(self.level_data["key_evidence_ids"])
        collected_ids = {e["id"] for e in self.collected_evidence}
        keys_found = len(key_ids & collected_ids)
        keys_total = len(key_ids)

        prog_bg = pygame.Rect(8, 694, 200, 10)
        pygame.draw.rect(self.screen, (30, 50, 70), prog_bg, border_radius=5)
        fill_w = int(200 * min(collected_n / max(needed, 1), 1.0))
        if fill_w > 0:
            fill_color = COLORS["success"] if collected_n >= needed else COLORS["cyan"]
            pygame.draw.rect(self.screen, fill_color,
                             (8, 694, fill_w, 10), border_radius=5)

        status_txt = f"Evidencias: {collected_n}/{needed}  ★ Claves: {keys_found}/{keys_total}"
        status_surf = self.font_tiny.render(status_txt, True, COLORS["text_dim"])
        self.screen.blit(status_surf, (8, 708))

        # ── Main button (drawn outside clip so it's always visible) ─
        if self.inv_state != INV_TREE_REVIEW:
            for btn in self.buttons:
                btn.draw(self.screen)

        # ── Wrong attempts bar ────────────────────────────────────────
        if self.wrong_attempts > 0:
            wa_rect = pygame.Rect(8, 768, 374, 22)
            draw_rounded_rect(self.screen, (55, 10, 10), wa_rect, 6, 1, COLORS["error"])
            wa = self.font_tiny.render(
                f"Intentos fallidos: {self.wrong_attempts}", True, COLORS["error"]
            )
            self.screen.blit(wa, (wa_rect.centerx - wa.get_width() // 2,
                                   wa_rect.centery - wa.get_height() // 2))

    def _draw_tree_review_panel(self):
        """Panel central exclusivo del Nivel 5: análisis del árbol completo"""
        panel = pygame.Rect(390, 56, 450, SCREEN_H - 56)
        draw_rounded_rect(self.screen, (8, 18, 32), panel, 0)
        pygame.draw.line(self.screen, (40, 70, 100), (840, 56), (840, SCREEN_H), 2)

        # Título
        title = self.font_small.render("ANÁLISIS FINAL DEL ÁRBOL AVL", True, COLORS["gold"])
        self.screen.blit(title, (410, 70))
        pygame.draw.line(self.screen, COLORS["gold"], (400, 92), (835, 92), 1)

        # Introducción educativa
        intro_lines = [
            "Recorrido INORDEN del árbol (orden por ID):",
            "Este recorrido revela la cadena cronológica de ataques.",
        ]
        iy = 102
        for line in intro_lines:
            s = self.font_tiny.render(line, True, COLORS["cyan"])
            self.screen.blit(s, (408, iy))
            iy += 18

        # Recorrido inorden con detalles de cada nodo
        nodes = self.avl.inorder()
        ny = iy + 10
        for i, node in enumerate(nodes):
            # Caja del nodo
            box = pygame.Rect(405, ny, 425, 90)
            draw_rounded_rect(self.screen, (15, 35, 60), box, 10, 2, COLORS["node_border"])

            # Número de orden
            order_s = self.font_med.render(str(i + 1), True, COLORS["gold"])
            self.screen.blit(order_s, (415, ny + 30))

            # ID y tipo
            id_s = self.font_small.render(f"Caso #{node.case_id} — {node.case_type}", True, COLORS["text"])
            self.screen.blit(id_s, (440, ny + 8))

            # Ley
            law_s = self.font_tiny.render(node.law, True, COLORS["cyan"])
            self.screen.blit(law_s, (440, ny + 32))

            # Descripción (culpable)
            desc_s = self.font_tiny.render(node.description, True, COLORS["success"])
            self.screen.blit(desc_s, (440, ny + 50))

            # Altura y factor de balance
            bf = self.avl._balance_factor(node)
            bf_color = COLORS["success"] if abs(bf) <= 1 else COLORS["error"]
            bf_s = self.font_tiny.render(f"h={node.height}  bf={bf}", True, bf_color)
            self.screen.blit(bf_s, (750, ny + 35))

            ny += 100

            # Flecha de conexión entre nodos
            if i < len(nodes) - 1:
                mid_x = 615
                pygame.draw.line(self.screen, COLORS["line"], (mid_x, ny - 10), (mid_x, ny), 2)
                pygame.draw.polygon(self.screen, COLORS["line"],
                                    [(mid_x - 5, ny), (mid_x + 5, ny), (mid_x, ny + 8)])

        # Conclusión
        concl_y = ny + 15
        concl_box = pygame.Rect(405, concl_y, 425, 55)
        draw_rounded_rect(self.screen, (40, 20, 5), concl_box, 8, 2, COLORS["warning"])
        concl1 = self.font_tiny.render("Conexión entre todos los casos:", True, COLORS["warning"])
        concl2 = self.font_tiny.render("Mismo servidor — mismo responsable.", True, COLORS["text"])
        self.screen.blit(concl1, (415, concl_y + 8))
        self.screen.blit(concl2, (415, concl_y + 28))

        # Estadísticas del árbol
        stats_y = SCREEN_H - 100
        pygame.draw.line(self.screen, (40, 70, 100), (400, stats_y), (835, stats_y), 1)
        stats = [
            f"Altura del árbol: {self.avl.get_depth()}",
            f"Rotaciones AVL realizadas: {len(self.avl.rotation_log)}",
            f"Búsqueda garantizada: O(log {len(nodes)}) = O({self.avl.get_depth()})",
        ]
        sx = 408
        for stat in stats:
            ss = self.font_tiny.render(stat, True, COLORS["text_dim"])
            self.screen.blit(ss, (sx, stats_y + 8))
            sx += ss.get_width() + 20

        for btn in self.buttons:
            btn.draw(self.screen)

    def _draw_avl_panel(self):
        """Panel central: visualización del árbol AVL con nodos coloreados por tipo de caso"""
        panel = pygame.Rect(390, 56, 450, SCREEN_H - 56)
        draw_rounded_rect(self.screen, (10, 20, 35), panel, 0)
        pygame.draw.line(self.screen, (40, 70, 100), (840, 56), (840, SCREEN_H), 2)

        # Header con subtítulo educativo
        depth = self.avl.get_depth()
        node_count = len(self.avl.inorder())
        pt = self.font_small.render("ÁRBOL AVL DE CASOS", True, COLORS["gold"])
        self.screen.blit(pt, (410, 65))
        sub_txt = f"Altura: {depth} | Casos: {node_count} | Búsqueda O(log n)"
        sub_s = self.font_tiny.render(sub_txt, True, COLORS["text_dim"])
        self.screen.blit(sub_s, (410, 88))
        pygame.draw.line(self.screen, COLORS["gold"], (400, 108), (835, 108), 1)

        # Dibujar árbol
        if self.avl.root:
            center_x = 615
            start_y = 150
            self.avl.calculate_positions(self.avl.root, center_x, start_y, 100)
            self._draw_tree_edges(self.avl.root)
            self._draw_tree_nodes(self.avl.root)
        else:
            # Caja educativa cuando el árbol está vacío
            empty_box = pygame.Rect(420, 150, 380, 200)
            draw_rounded_rect(self.screen, (12, 28, 52), empty_box, 14, 2, COLORS["cyan"])

            empty_title = self.font_small.render("¿Qué es un Árbol AVL?", True, COLORS["cyan"])
            self.screen.blit(empty_title, (615 - empty_title.get_width() // 2, 162))
            pygame.draw.line(self.screen, (40, 80, 120), (430, 185), (790, 185), 1)

            avl_tips = [
                "Es un árbol binario de búsqueda autobalanceado.",
                "Cada nodo tiene un factor de balance: |bf| ≤ 1.",
                "Las rotaciones mantienen el árbol equilibrado.",
                "Búsquedas siempre en tiempo O(log n).",
                "",
                "Resuelve un caso para agregar tu primer nodo.",
            ]
            tip_y = 192
            for tip in avl_tips:
                c = COLORS["text"] if tip else COLORS["text_dim"]
                ts = self.font_tiny.render(tip, True, c)
                self.screen.blit(ts, (615 - ts.get_width() // 2, tip_y))
                tip_y += 18

        # Leyenda con pills coloreadas por tipo de caso
        ley_y = SCREEN_H - 135
        pygame.draw.line(self.screen, (40, 70, 100), (400, ley_y - 5), (835, ley_y - 5), 1)
        self.screen.blit(self.font_tiny.render("Tipos de caso:", True, COLORS["gold"]), (405, ley_y))
        ley_y += 18

        legend_items = list(CASE_COLORS.items())
        lx = 405
        for case_name, case_col in legend_items:
            pill = pygame.Rect(lx, ley_y, 82, 16)
            draw_rounded_rect(self.screen, case_col, pill, 5, 1, (200, 200, 200))
            case_short = case_name[:10]
            lt_surf = self.font_tiny.render(case_short, True, COLORS["white"])
            self.screen.blit(lt_surf, (pill.centerx - lt_surf.get_width() // 2,
                                        pill.centery - lt_surf.get_height() // 2))
            lx += 86
            if lx > 800:
                lx = 405
                ley_y += 20

        # Rotaciones realizadas
        if self.avl.rotation_log:
            rot_y = SCREEN_H - 42
            rl_title = self.font_tiny.render("Última rotación AVL:", True, COLORS["cyan"])
            self.screen.blit(rl_title, (405, rot_y))
            last_rot = self.avl.rotation_log[-1] if self.avl.rotation_log else ""
            lr_surf = self.font_tiny.render(last_rot[:55], True, COLORS["text_dim"])
            self.screen.blit(lr_surf, (405, rot_y + 16))

    def _draw_tree_edges(self, node):
        """Dibuja las aristas del árbol recursivamente"""
        if not node:
            return
        if node.left:
            pygame.draw.line(self.screen, COLORS["line"],
                             (int(node.x), int(node.y)),
                             (int(node.left.x), int(node.left.y)), 2)
            self._draw_tree_edges(node.left)
        if node.right:
            pygame.draw.line(self.screen, COLORS["line"],
                             (int(node.x), int(node.y)),
                             (int(node.right.x), int(node.right.y)), 2)
            self._draw_tree_edges(node.right)

    def _draw_tree_nodes(self, node):
        """Dibuja los nodos del árbol con color por tipo de caso"""
        if not node:
            return

        x, y = int(node.x), int(node.y)
        r = 32  # radio más grande para mejor legibilidad

        # Color según tipo de caso
        is_root = (node == self.avl.root)
        is_new = (node == self.new_node_highlight and self.tree_anim_timer > 0)

        if is_new:
            pulse = pulse_value(self.t, 5.0, 0.6, 1.0)
            color = (int(0 * pulse), int(220 * pulse), int(130 * pulse))
            border = COLORS["success"]
            br = 3
        elif is_root:
            # Color por tipo de caso, con borde especial de raíz
            color = CASE_COLORS.get(node.case_type, COLORS["node_root"])
            border = (220, 200, 255)
            br = 3
        else:
            color = CASE_COLORS.get(node.case_type, COLORS["node_fill"])
            border = COLORS["node_border"]
            br = 2

        # Sombra
        pygame.draw.circle(self.screen, (5, 10, 20), (x + 3, y + 3), r)
        pygame.draw.circle(self.screen, color, (x, y), r)
        pygame.draw.circle(self.screen, border, (x, y), r, br)

        # ID del caso
        id_text = self.font_tiny.render(str(node.case_id), True, COLORS["white"])
        self.screen.blit(id_text, (x - id_text.get_width() // 2, y - id_text.get_height() // 2 - 5))

        # Tipo (abreviado)
        type_short = node.case_type[:8]
        tp_text = self.font_tiny.render(type_short, True, COLORS["gold"])
        self.screen.blit(tp_text, (x - tp_text.get_width() // 2, y + 6))

        # Factor de balance
        bf = self.avl._balance_factor(node)
        bf_color = COLORS["success"] if abs(bf) <= 1 else COLORS["error"]
        bf_text = self.font_tiny.render(f"bf:{bf}", True, bf_color)
        self.screen.blit(bf_text, (x - bf_text.get_width() // 2, y + r + 2))

        self._draw_tree_nodes(node.left)
        self._draw_tree_nodes(node.right)

    def _draw_inv_right_panel(self):
        """Panel derecho: info del caso + evidencias recolectadas + árbol + consejo AVL"""
        panel = pygame.Rect(840, 56, 360, SCREEN_H - 56)
        draw_rounded_rect(self.screen, COLORS["panel"], panel, 0)

        pt = self.font_small.render("INFORMACIÓN DEL CASO", True, COLORS["gold"])
        self.screen.blit(pt, (860, 70))
        pygame.draw.line(self.screen, COLORS["gold"], (850, 92), (1190, 92), 1)

        ld = self.level_data
        info_y = 105

        # Caso
        ct = self.font_tiny.render("TIPO DE DELITO:", True, COLORS["text_dim"])
        self.screen.blit(ct, (855, info_y))
        cv = self.font_small.render(ld["case_type"], True, ld["color_accent"])
        self.screen.blit(cv, (855, info_y + 18))
        info_y += 52

        # Víctima
        self.screen.blit(self.font_tiny.render("VÍCTIMA:", True, COLORS["text_dim"]), (855, info_y))
        self.screen.blit(self.font_small.render(ld["victim"], True, COLORS["text"]), (855, info_y + 18))
        info_y += 50

        pygame.draw.line(self.screen, (40, 70, 100), (850, info_y), (1190, info_y), 1)
        info_y += 8

        # Ley colombiana
        law_header = self.font_small.render("LEY COLOMBIANA APLICABLE:", True, COLORS["gold"])
        self.screen.blit(law_header, (855, info_y))
        info_y += 22

        law_lines = wrap_text(ld["law_detail"], self.font_tiny, 318)
        law_h = max(72, 24 + len(law_lines) * 15 + 6)
        law_rect = pygame.Rect(850, info_y, 340, law_h)
        draw_rounded_rect(self.screen, (15, 35, 60), law_rect, 8, 1, (60, 100, 150))
        law_name = self.font_tiny.render(ld["law"], True, COLORS["cyan"])
        self.screen.blit(law_name, (860, info_y + 6))
        ly = info_y + 22
        for line in law_lines:
            lt = self.font_tiny.render(line, True, COLORS["text"])
            self.screen.blit(lt, (860, ly))
            ly += 15
        info_y += law_h + 8

        # Pena
        pen_header = self.font_tiny.render("PENA POSIBLE:", True, COLORS["text_dim"])
        self.screen.blit(pen_header, (855, info_y))
        info_y += 18
        pen_lines = wrap_text(ld["penalty"], self.font_tiny, 318)
        pen_h = max(32, len(pen_lines) * 15 + 10)
        pen_rect = pygame.Rect(850, info_y, 340, pen_h)
        draw_rounded_rect(self.screen, (60, 20, 20), pen_rect, 8, 1, COLORS["error"])
        py = info_y + 6
        for pl in pen_lines:
            pts = self.font_tiny.render(pl, True, COLORS["error"])
            self.screen.blit(pts, (860, py))
            py += 15
        info_y += pen_h + 10

        pygame.draw.line(self.screen, (40, 70, 100), (850, info_y), (1190, info_y), 1)
        info_y += 8

        # ── EVIDENCIAS RECOLECTADAS (nueva sección) ─────────────────────
        if self.collected_evidence:
            ev_hdr = self.font_tiny.render("EVIDENCIAS RECOLECTADAS:", True, COLORS["gold"])
            self.screen.blit(ev_hdr, (855, info_y))
            info_y += 18

            for ev in self.collected_evidence:
                if info_y > SCREEN_H - 130:
                    break
                if ev["is_key"]:
                    ev_bg = (20, 60, 25)
                    ev_bdr = COLORS["gold"]
                else:
                    ev_bg = (15, 35, 65)
                    ev_bdr = (60, 100, 150)
                ev_box = pygame.Rect(850, info_y, 340, 28)
                draw_rounded_rect(self.screen, ev_bg, ev_box, 5, 1, ev_bdr)
                marker = "★ " if ev["is_key"] else "◆ "
                mk_c = COLORS["gold"] if ev["is_key"] else COLORS["cyan"]
                mk_s = self.font_tiny.render(marker, True, mk_c)
                self.screen.blit(mk_s, (856, info_y + 7))
                ev_name = ev["name"][:38]
                ev_s = self.font_tiny.render(ev_name, True, COLORS["text"])
                self.screen.blit(ev_s, (872, info_y + 7))
                info_y += 32

            pygame.draw.line(self.screen, (40, 70, 100), (850, info_y), (1190, info_y), 1)
            info_y += 8

        # ── CASOS EN EL ÁRBOL ─────────────────────────────────────────
        if info_y < SCREEN_H - 120:
            solved_header = self.font_tiny.render("CASOS EN EL ÁRBOL:", True, COLORS["gold"])
            self.screen.blit(solved_header, (855, info_y))
            info_y += 18

            for node in self.avl.inorder():
                if info_y > SCREEN_H - 120:
                    break
                node_color = CASE_COLORS.get(node.case_type, COLORS["success"])
                ns = self.font_tiny.render(f"#{node.case_id} – {node.case_type}", True, node_color)
                self.screen.blit(ns, (862, info_y))
                info_y += 17

        # ── CONSEJO DEL ÁRBOL AVL (parte inferior) ───────────────────
        tip_y = SCREEN_H - 110
        pygame.draw.line(self.screen, (40, 70, 100), (850, tip_y), (1190, tip_y), 1)

        tip_box = pygame.Rect(850, tip_y + 5, 340, 100)
        draw_rounded_rect(self.screen, (10, 25, 45), tip_box, 8, 1, COLORS["cyan"])

        tip_header = self.font_tiny.render("CONSEJO DEL ÁRBOL AVL:", True, COLORS["cyan"])
        self.screen.blit(tip_header, (858, tip_y + 10))

        tips = [
            "Árbol AVL: siempre balanceado (|bf| ≤ 1).",
            "Las rotaciones preservan O(log n) en inserciones.",
            "Inorden produce los casos en orden de ID.",
        ]
        for i, tip in enumerate(tips):
            tt = self.font_tiny.render(tip, True, COLORS["text_dim"])
            self.screen.blit(tt, (858, tip_y + 28 + i * 16))

    # ─────────────────────────────────────────
    # PANTALLA: NIVEL COMPLETADO
    # ─────────────────────────────────────────
    def _draw_level_complete(self):
        ld = self.level_data
        accent = ld["color_accent"]

        # Panel central
        panel = pygame.Rect(150, 80, 900, 580)
        draw_rounded_rect(self.screen, COLORS["panel"], panel, 20, 3, accent)

        # Título
        title = self.font_large.render("¡CASO RESUELTO!", True, COLORS["success"])
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 110))

        lv_t = self.font_med.render(ld["title"], True, accent)
        self.screen.blit(lv_t, (SCREEN_W // 2 - lv_t.get_width() // 2, 155))

        # Separador
        pygame.draw.line(self.screen, accent, (200, 195), (1000, 195), 2)

        # Culpable
        guilty_name = self.guilty["name"]
        g_label = self.font_small.render("CULPABLE IDENTIFICADO:", True, COLORS["text_dim"])
        self.screen.blit(g_label, (SCREEN_W // 2 - g_label.get_width() // 2, 210))
        g_name = self.font_large.render(guilty_name, True, COLORS["error"])
        self.screen.blit(g_name, (SCREEN_W // 2 - g_name.get_width() // 2, 240))

        # Ley y pena
        pygame.draw.line(self.screen, (40, 70, 100), (200, 290), (1000, 290), 1)

        law_y = 305
        law_title = self.font_med.render(ld["law_title"], True, COLORS["gold"])
        self.screen.blit(law_title, (SCREEN_W // 2 - law_title.get_width() // 2, law_y))

        law_detail_lines = wrap_text(ld["law_detail"], self.font_small, 780)
        ly = law_y + 35
        for line in law_detail_lines:
            lt = self.font_small.render(line, True, COLORS["text"])
            self.screen.blit(lt, (SCREEN_W // 2 - lt.get_width() // 2, ly))
            ly += 26

        # Pena
        pen_full = f"Pena: {ld['penalty']}"
        pen_full_lines = wrap_text(pen_full, self.font_small, 760)
        pen_full_h = max(45, len(pen_full_lines) * 26 + 14)
        pen_rect = pygame.Rect(200, ly + 10, 800, pen_full_h)
        draw_rounded_rect(self.screen, (60, 15, 15), pen_rect, 10, 2, COLORS["error"])
        pfy = ly + 18
        for pfl in pen_full_lines:
            pft = self.font_small.render(pfl, True, COLORS["error"])
            self.screen.blit(pft, (SCREEN_W // 2 - pft.get_width() // 2, pfy))
            pfy += 26

        # Mensaje educativo (siempre debajo de la caja de pena)
        edu_y = ly + 10 + pen_full_h + 15
        pygame.draw.line(self.screen, (40, 70, 100), (200, edu_y), (1000, edu_y), 1)
        edu_msg = self.font_small.render(
            "Recuerda: El ciberacoso tiene consecuencias legales reales en Colombia.",
            True, COLORS["cyan"]
        )
        self.screen.blit(edu_msg, (SCREEN_W // 2 - edu_msg.get_width() // 2, edu_y + 10))

        # Puntos
        score_t = self.font_med.render(f"Puntos acumulados: {self.score}", True, COLORS["gold"])
        self.screen.blit(score_t, (SCREEN_W // 2 - score_t.get_width() // 2, edu_y + 40))

        for btn in self.buttons:
            btn.draw(self.screen)

    # ─────────────────────────────────────────
    # PANTALLA: VICTORIA
    # ─────────────────────────────────────────
    def _draw_victory(self):
        # Partículas continuas
        if random.random() < 0.3:
            self._spawn_particles(
                random.randint(100, SCREEN_W - 100),
                random.randint(100, SCREEN_H - 100),
                random.choice([COLORS["gold"], COLORS["success"], COLORS["cyan"]]),
                n=3
            )

        # Panel principal
        panel = pygame.Rect(80, 40, SCREEN_W - 160, SCREEN_H - 120)
        draw_rounded_rect(self.screen, COLORS["panel"], panel, 20, 3, COLORS["gold"])

        # Título
        t1 = self.font_title.render("¡FELICITACIONES!", True, COLORS["gold"])
        self.screen.blit(t1, (SCREEN_W // 2 - t1.get_width() // 2, 70))

        t2 = self.font_med.render("Has completado CyberDetective: El Árbol de la Verdad", True, COLORS["text"])
        self.screen.blit(t2, (SCREEN_W // 2 - t2.get_width() // 2, 143))

        pygame.draw.line(self.screen, COLORS["gold"], (120, 180), (SCREEN_W - 120, 180), 2)

        # Estadísticas
        stats_y = 195
        stats_title = self.font_med.render("RESUMEN DE LA INVESTIGACIÓN", True, COLORS["gold"])
        self.screen.blit(stats_title, (SCREEN_W // 2 - stats_title.get_width() // 2, stats_y))

        stats = [
            ("Casos resueltos:", str(len(self.solved_levels))),
            ("Nodos en el árbol AVL:", str(len(self.avl.inorder()))),
            ("Altura del árbol:", str(self.avl.get_depth())),
            ("Rotaciones realizadas:", str(len(self.avl.rotation_log))),
            ("Puntuación final:", str(self.score)),
        ]
        sy: int = stats_y + 40
        for label, value in stats:
            lt = self.font_small.render(label, True, COLORS["text_dim"])
            lv = self.font_med.render(value, True, COLORS["cyan"])
            self.screen.blit(lt, (200, sy))
            self.screen.blit(lv, (550, sy))
            sy += 35

        pygame.draw.line(self.screen, (40, 70, 100), (120, sy + 5), (SCREEN_W - 120, sy + 5), 1)

        # Mensaje educativo final
        msg_y: int = int(sy) + 20
        messages = [
            "Lo que aprendiste en este juego:",
            "• El ciberacoso es un delito en Colombia con penas de hasta 12 años de prisión.",
            "• Injuria (Art. 220 C.P.): insultos en redes sociales tienen consecuencias legales.",
            "• Calumnia (Art. 221 C.P.): acusaciones falsas son punibles por la ley.",
            "• Ley 1273/2009: protege a los ciudadanos de delitos informáticos.",
            "• Denuncia el ciberacoso: Fiscalía General de la Nación o CAI Virtual.",
        ]
        for i, msg in enumerate(messages):
            c = COLORS["gold"] if i == 0 else COLORS["text"]
            f = self.font_small if i == 0 else self.font_tiny
            mt = f.render(msg, True, c)
            self.screen.blit(mt, (150, msg_y + i * 24))

        # Árbol final — recorrido inorden educativo
        tree_y: int = msg_y + len(messages) * 24 + 15
        tree_box = pygame.Rect(120, tree_y, SCREEN_W - 240, 80)
        draw_rounded_rect(self.screen, (10, 25, 45), tree_box, 10, 2, COLORS["node_border"])

        tree_title = self.font_tiny.render(
            f"Recorrido INORDEN del árbol AVL (altura={self.avl.get_depth()}, "
            f"rotaciones={len(self.avl.rotation_log)}, complejidad O(log n)):",
            True, COLORS["cyan"]
        )
        self.screen.blit(tree_title, (135, tree_y + 8))

        nodes = self.avl.inorder()
        nx = 135
        arrow_s = self.font_tiny.render(" → ", True, COLORS["text_dim"])
        for i, node in enumerate(nodes):
            bf = self.avl._balance_factor(node)
            bf_color = COLORS["success"] if abs(bf) <= 1 else COLORS["error"]
            node_txt = f"#{node.case_id}({node.case_type[:6]})"
            nt = self.font_tiny.render(node_txt, True, bf_color)
            self.screen.blit(nt, (nx, tree_y + 48))
            nx += nt.get_width()
            if i < len(nodes) - 1:
                self.screen.blit(arrow_s, (nx, tree_y + 48))
                nx += arrow_s.get_width()
            if nx > SCREEN_W - 250:
                break

        for btn in self.buttons:
            btn.draw(self.screen)
