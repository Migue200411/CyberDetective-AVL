#!/usr/bin/env python3
"""
CyberDetective: El Árbol de la Verdad
======================================
Juego educativo interactivo sobre ciberacoso y consecuencias legales en Colombia.
Utiliza un Árbol AVL para organizar los casos de investigación.

Requisitos:
    pip install pygame

Ejecución:
    python main.py
"""

import pygame
import sys

def check_dependencies():
    """Verifica que pygame esté instalado"""
    try:
        import pygame
        return True
    except ImportError:
        print("ERROR: pygame no está instalado.")
        print("Instálalo con: pip install pygame")
        sys.exit(1)

def main():
    check_dependencies()

    pygame.mixer.pre_init(22050, -16, 1, 512)
    pygame.init()
    pygame.mixer.init()

    # Configuración de pantalla
    SCREEN_W, SCREEN_H = 1200, 800
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("CyberDetective: El Árbol de la Verdad")

    # Intentar poner ícono (si hay archivo)
    try:
        icon = pygame.Surface((32, 32))
        icon.fill((30, 80, 160))
        pygame.display.set_icon(icon)
    except Exception:
        pass

    # Importar e iniciar el juego
    from game import Game
    game = Game(screen)
    game.run()

if __name__ == "__main__":
    main()
