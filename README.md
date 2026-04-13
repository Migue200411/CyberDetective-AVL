# CyberDetective: El Árbol de la Verdad

Juego educativo interactivo sobre **ciberacoso y sus consecuencias legales en Colombia**, desarrollado con Pygame. Utiliza un **Árbol AVL** para organizar los casos de investigación resueltos.

## Instalación

```bash
pip install pygame
python main.py
```

## Cómo jugar

1. **Elige tu detective** (Rodrigo Vargas o Carolina Reyes)
2. **Recolecta evidencias** — las marcadas con ★ son clave
3. **Analiza los sospechosos** — lee sus perfiles
4. **Haz tu acusación** — usa "Ver Evidencias" y "Ver Pista" si necesitas ayuda
5. El caso resuelto se inserta en el **Árbol AVL** automáticamente

## Leyes colombianas incluidas

| Ley | Delito | Pena |
|-----|--------|------|
| Art. 220 C.P. | Injuria | 16–54 meses |
| Art. 221 C.P. | Calumnia | 16–72 meses |
| Ley 1273/2009 Art. 269F | Suplantación / Datos personales | 48–96 meses |
| Ley 1273/2009 + agravantes | Acoso coordinado | 48–100 meses |
| Conjunto leyes + máx. agravantes | Red criminal de ciberacoso | hasta 144 meses |

## Estructura del proyecto

```
CyberDetective-AVL/
├── main.py        # Punto de entrada
├── game.py        # Lógica principal, estados y renderizado
├── game_data.py   # Niveles, sospechosos, evidencias y leyes
└── avl_tree.py    # Implementación del Árbol AVL
```

## Árbol AVL

Cada caso resuelto se inserta como nodo. El árbol se autobalancea mediante rotaciones para garantizar búsquedas en **O(log n)**. El factor de balance `bf` de cada nodo siempre satisface `|bf| ≤ 1`.

---
Proyecto universitario — Estructuras de Datos
