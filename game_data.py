# game_data.py - Datos del juego: niveles, sospechosos, evidencias y leyes colombianas

import random

# ─────────────────────────────────────────────
# PALETA DE COLORES
# ─────────────────────────────────────────────
COLORS = {
    "bg":           (13, 27, 42),       # Fondo oscuro naval
    "panel":        (22, 40, 60),       # Panel secundario
    "panel_light":  (30, 55, 80),       # Panel claro
    "gold":         (255, 215, 0),      # Dorado (acento principal)
    "gold_dark":    (200, 165, 0),      # Dorado oscuro
    "text":         (232, 232, 232),    # Texto principal
    "text_dim":     (160, 175, 190),    # Texto secundario
    "success":      (0, 220, 130),      # Verde éxito
    "error":        (255, 80, 80),      # Rojo error
    "warning":      (255, 165, 0),      # Naranja advertencia
    "node_fill":    (30, 100, 180),     # Nodo del árbol
    "node_border":  (80, 180, 255),     # Borde del nodo
    "node_root":    (180, 60, 200),     # Nodo raíz (morado)
    "node_solved":  (0, 160, 100),      # Nodo resuelto
    "btn_primary":  (30, 100, 200),     # Botón primario
    "btn_hover":    (50, 140, 255),     # Botón hover
    "btn_disabled": (60, 70, 85),       # Botón deshabilitado
    "white":        (255, 255, 255),
    "black":        (0, 0, 0),
    "cyan":         (0, 200, 230),
    "line":         (60, 120, 180),     # Líneas del árbol
}

# ─────────────────────────────────────────────
# SOSPECHOSOS (pool compartido)
# ─────────────────────────────────────────────
SUSPECTS_POOL = [
    {
        "name": "Andrés Ruiz",
        "age": 17,
        "profile": "Compañero de clase. Historial de conflictos verbales con varias personas.",
        "icon": "♟",
    },
    {
        "name": "Sofía Mendoza",
        "age": 18,
        "profile": "Ex-amiga de la víctima. Tuvieron una pelea pública hace 3 semanas.",
        "icon": "♟",
    },
    {
        "name": "Carlos Vega",
        "age": 19,
        "profile": "Estudiante de otro curso. Conocido por hacer comentarios hirientes en línea.",
        "icon": "♟",
    },
    {
        "name": "Valentina Torres",
        "age": 17,
        "profile": "Conocida de la víctima. Muestra envidia hacia sus logros académicos.",
        "icon": "♟",
    },
    {
        "name": "Diego Morales",
        "age": 20,
        "profile": "Vecino de la víctima. Tiene acceso a información personal de ella.",
        "icon": "♟",
    },
    {
        "name": "Isabella Castro",
        "age": 18,
        "profile": "Amiga de un amigo. Conoce detalles íntimos de la víctima.",
        "icon": "♟",
    },
    {
        "name": "Santiago López",
        "age": 21,
        "profile": "Usuario activo en foros. Historial previo de acoso anónimo en línea.",
        "icon": "♟",
    },
]

# ─────────────────────────────────────────────
# DEFINICIÓN DE NIVELES
# ─────────────────────────────────────────────
LEVELS = [
    {
        "id": 1,
        "case_id": 101,
        "title": "Nivel 1 – Las Primeras Señales",
        "subtitle": "Injurias en Redes Sociales",
        "case_type": "INJURIA",
        "color_accent": (100, 180, 255),
        "victim": "Laura García (17 años)",
        "intro_lines": [
            "Detective, hemos recibido una denuncia urgente.",
            "Laura García, estudiante de 17 años, recibió mensajes",
            "ofensivos publicados en su muro de Facebook.",
            "Alguien la llamó 'mentirosa' y 'ladrona' sin ninguna prueba.",
            "La publicación fue compartida 47 veces en pocas horas.",
            "Tu misión: recolectar evidencias e identificar al culpable.",
        ],
        "scenario": (
            "Laura García encontró insultos graves publicados en su perfil de Facebook. "
            "Los mensajes la acusaban de cosas falsas ante sus amigos y familia. "
            "El daño a su reputación fue inmediato y severo."
        ),
        "evidence_pool": [
            {
                "id": "E1-1",
                "name": "Captura del mensaje ofensivo",
                "is_key": False,
                "detail": "Publicación del 15/03/2024 a las 10:23 PM. Contenido insultante.",
            },
            {
                "id": "E1-2",
                "name": "Registro de IP del publicante",
                "is_key": True,
                "detail": "IP 192.168.1.45 rastreada hasta proveedor de internet en Barrio El Poblado.",
            },
            {
                "id": "E1-3",
                "name": "Testimonio de testigos digitales",
                "is_key": False,
                "detail": "Tres amigos confirman haber visto la publicación antes de ser eliminada.",
            },
            {
                "id": "E1-4",
                "name": "Historial de interacciones previas",
                "is_key": True,
                "detail": "El agresor comentó en fotos de Laura 12 veces la semana anterior al incidente.",
            },
            {
                "id": "E1-5",
                "name": "Análisis del perfil del agresor",
                "is_key": False,
                "detail": "Cuenta activa hace 2 años, miembro de los mismos grupos escolares que la víctima.",
            },
        ],
        "evidence_needed": 3,
        "key_evidence_ids": ["E1-2", "E1-4"],
        "guilty_reveal": (
            "La IP registrada en el momento de la publicación pertenece al proveedor "
            "de internet de {culprit}. Además, el historial de interacciones obsesivas "
            "confirma que {culprit} es el responsable."
        ),
        "question": "¿Quién publicó los mensajes ofensivos contra Laura García?",
        "hint": "La dirección IP y el historial de interacciones son las claves.",
        "law": "Art. 220 Código Penal Colombiano",
        "law_title": "Delito de Injuria",
        "law_detail": (
            "Art. 220 C.P.: 'El que haga a otra persona imputaciones deshonrosas, "
            "incurrirá en prisión de 16 a 54 meses y multa de 13.33 a 1.500 SMLMV.'"
        ),
        "penalty": "16 a 54 meses de prisión + multa económica",
        "num_suspects": 3,
        "num_choices": 3,
    },
    {
        "id": 2,
        "case_id": 205,
        "title": "Nivel 2 – El Rumor Viral",
        "subtitle": "Calumnias y Publicaciones Falsas",
        "case_type": "CALUMNIA",
        "color_accent": (255, 180, 80),
        "victim": "Marcos Peña (16 años)",
        "intro_lines": [
            "Buen trabajo, Detective. Ahora un caso más grave.",
            "Marcos Peña fue acusado falsamente de robar $500.000",
            "de la tesorería del colegio.",
            "Esta calumnia se propagó por 5 grupos de WhatsApp",
            "y llegó hasta los padres de familia.",
            "La información era completamente falsa. Necesitamos pruebas.",
        ],
        "scenario": (
            "Marcos Peña fue víctima de calumnias masivas en WhatsApp y Facebook. "
            "La acusación falsa afectó su relación con compañeros, profesores y padres. "
            "Los registros bancarios confirman que nunca hubo ningún robo."
        ),
        "evidence_pool": [
            {
                "id": "E2-1",
                "name": "Capturas de chats de WhatsApp",
                "is_key": False,
                "detail": "Mensaje inicial enviado el 20/03/2024 a las 3:15 PM.",
            },
            {
                "id": "E2-2",
                "name": "Metadatos del mensaje original",
                "is_key": True,
                "detail": "Creado desde un iPhone 13 con IMEI 352987654321098.",
            },
            {
                "id": "E2-3",
                "name": "Registros del banco estudiantil",
                "is_key": False,
                "detail": "No existe ningún faltante de dinero. La acusación es falsa.",
            },
            {
                "id": "E2-4",
                "name": "Análisis de propagación del rumor",
                "is_key": True,
                "detail": "El primer reenvío partió de un contacto directo del agresor.",
            },
            {
                "id": "E2-5",
                "name": "Testimonio del tesorero",
                "is_key": False,
                "detail": "Confirma que no hubo robo y que fue sorprendido por la noticia.",
            },
            {
                "id": "E2-6",
                "name": "Registro de dispositivos conectados",
                "is_key": True,
                "detail": "El IMEI del dispositivo emisor coincide con el del sospechoso.",
            },
        ],
        "evidence_needed": 4,
        "key_evidence_ids": ["E2-2", "E2-4", "E2-6"],
        "guilty_reveal": (
            "Los metadatos del mensaje y el registro de dispositivos confirman "
            "que {culprit} fue quien inició la calumnia desde su iPhone personal."
        ),
        "question": "¿Quién inició la propagación de las calumnias contra Marcos Peña?",
        "hint": "Los metadatos del mensaje revelan el dispositivo del agresor.",
        "law": "Art. 221 Código Penal Colombiano",
        "law_title": "Delito de Calumnia",
        "law_detail": (
            "Art. 221 C.P.: 'El que impute falsamente a otro una conducta típica, "
            "incurrirá en prisión de 16 a 72 meses y multa de 13.33 a 1.500 SMLMV.'"
        ),
        "penalty": "16 a 72 meses de prisión + multa económica",
        "num_suspects": 3,
        "num_choices": 3,
    },
    {
        "id": 3,
        "case_id": 312,
        "title": "Nivel 3 – La Cuenta Fantasma",
        "subtitle": "Suplantación de Identidad Digital",
        "case_type": "SUPLANTACIÓN",
        "color_accent": (180, 100, 255),
        "victim": "Ana Rodríguez (19 años)",
        "intro_lines": [
            "Detective, este caso es especialmente grave.",
            "Alguien creó un perfil falso haciéndose pasar por",
            "Ana Rodríguez en Instagram.",
            "Con ese perfil, el impostor contactó a 23 personas,",
            "pidió dinero a 5 de ellas y publicó contenido inapropiado",
            "arruinando la imagen profesional de Ana.",
        ],
        "scenario": (
            "Ana Rodríguez descubrió que existía un perfil falso con sus fotos en Instagram. "
            "El impostor solicitó dinero prestado y publicó contenido que dañó su imagen. "
            "Cinco personas cayeron en el engaño y perdieron dinero."
        ),
        "evidence_pool": [
            {
                "id": "E3-1",
                "name": "Perfil falso en Instagram",
                "is_key": False,
                "detail": "Cuenta creada el 01/03/2024. Usa fotos robadas del perfil original.",
            },
            {
                "id": "E3-2",
                "name": "IP de registro de la cuenta falsa",
                "is_key": True,
                "detail": "La cuenta fue creada desde la red WiFi del centro comercial Unicentro.",
            },
            {
                "id": "E3-3",
                "name": "Análisis forense del dispositivo",
                "is_key": True,
                "detail": "Huellas de un Android Samsung específico con ID único rastreable.",
            },
            {
                "id": "E3-4",
                "name": "Grabación de cámaras del mall",
                "is_key": False,
                "detail": "Se ve a una persona usando el WiFi en la fecha y hora registradas.",
            },
            {
                "id": "E3-5",
                "name": "Mensajes del perfil falso",
                "is_key": False,
                "detail": "El impostor reveló detalles que solo alguien cercano a Ana conocería.",
            },
            {
                "id": "E3-6",
                "name": "Análisis de escritura digital",
                "is_key": True,
                "detail": "Frases y errores ortográficos únicos coinciden con mensajes previos del sospechoso.",
            },
            {
                "id": "E3-7",
                "name": "Registros de transferencias bancarias",
                "is_key": False,
                "detail": "El dinero solicitado fue a una cuenta vinculada al agresor.",
            },
        ],
        "evidence_needed": 4,
        "key_evidence_ids": ["E3-2", "E3-3", "E3-6"],
        "guilty_reveal": (
            "El análisis forense del dispositivo Android y los patrones de escritura "
            "confirman que {culprit} creó el perfil falso para suplantar a Ana."
        ),
        "question": "¿Quién creó el perfil falso suplantando la identidad de Ana Rodríguez?",
        "hint": "El análisis forense del dispositivo y el estilo de escritura son determinantes.",
        "law": "Ley 1273 de 2009 – Art. 269F",
        "law_title": "Violación de Datos Personales / Suplantación",
        "law_detail": (
            "Ley 1273/2009 Art. 269F: 'Violación de datos personales. "
            "Pena de prisión de 48 a 96 meses y multa de 100 a 1.000 SMLMV.'"
        ),
        "penalty": "48 a 96 meses de prisión + multa hasta 1.000 SMLMV",
        "num_suspects": 4,
        "num_choices": 4,
    },
    {
        "id": 4,
        "case_id": 418,
        "title": "Nivel 4 – El Ataque Coordinado",
        "subtitle": "Acoso y Hostigamiento Digital Masivo",
        "case_type": "ACOSO COORDINADO",
        "color_accent": (255, 80, 80),
        "victim": "Camila Herrera (20 años)",
        "intro_lines": [
            "Detective, estamos ante un caso sin precedentes.",
            "Camila Herrera fue atacada simultáneamente desde",
            "8 cuentas falsas durante 3 semanas continuas.",
            "Los mensajes tenían patrones similares y se enviaban",
            "a horas específicas, sugiriendo una coordinación deliberada.",
            "Necesitamos identificar al líder de este ataque organizado.",
        ],
        "scenario": (
            "Camila Herrera fue objetivo de un ataque coordinado con 8 cuentas falsas. "
            "Los mensajes seguían patrones de vocabulario idéntico y horarios fijos. "
            "Se descubrió un grupo secreto donde se coordinaban los ataques."
        ),
        "evidence_pool": [
            {
                "id": "E4-1",
                "name": "Patrón temporal de los ataques",
                "is_key": True,
                "detail": "Todos los mensajes enviados entre 10PM-12AM. Horario del sospechoso principal.",
            },
            {
                "id": "E4-2",
                "name": "Análisis de vocabulario cruzado",
                "is_key": True,
                "detail": "Frases y expresiones únicas del agresor identificadas en múltiples cuentas.",
            },
            {
                "id": "E4-3",
                "name": "Registros de IPs de las 8 cuentas",
                "is_key": False,
                "detail": "8 IPs diferentes, pero todas desde la misma subred de proveedor.",
            },
            {
                "id": "E4-4",
                "name": "Grupo secreto de coordinación",
                "is_key": True,
                "detail": "Grupo privado descubierto donde el líder coordinaba a sus cómplices.",
            },
            {
                "id": "E4-5",
                "name": "Testimonios de cómplices",
                "is_key": False,
                "detail": "Dos participantes confesaron recibir instrucciones de un líder por voz.",
            },
            {
                "id": "E4-6",
                "name": "Historial del dispositivo principal",
                "is_key": True,
                "detail": "Un único dispositivo accedió a todas las cuentas falsas en secuencia.",
            },
            {
                "id": "E4-7",
                "name": "Perfil psicológico del agresor",
                "is_key": False,
                "detail": "El perfil coincide con el historial conductual del sospechoso.",
            },
            {
                "id": "E4-8",
                "name": "Registros de llamadas previas al ataque",
                "is_key": False,
                "detail": "Llamadas entre el sospechoso y cómplices justo antes de cada oleada.",
            },
        ],
        "evidence_needed": 5,
        "key_evidence_ids": ["E4-1", "E4-2", "E4-4", "E4-6"],
        "guilty_reveal": (
            "El patrón temporal, el vocabulario compartido, el grupo secreto y el historial "
            "del dispositivo prueban que {culprit} organizó y coordinó todo el ataque."
        ),
        "question": "¿Quién organizó el ataque digital coordinado contra Camila Herrera?",
        "hint": "Busca patrones: vocabulario, horarios y el grupo secreto te darán la respuesta.",
        "law": "Ley 1273 de 2009 + Art. 220 C.P. + Agravantes",
        "law_title": "Acoso Digital Coordinado",
        "law_detail": (
            "Ley 1273/2009 + Art. 220 C.P.: Acoso sistemático con medios informáticos. "
            "Pena de 48 a 100 meses con agravantes por organización y múltiples víctimas. "
            "La coordinación aumenta la pena hasta en una tercera parte adicional."
        ),
        "penalty": "48 a 100 meses + agravantes por coordinación criminal",
        "num_suspects": 4,
        "num_choices": 4,
    },
    {
        "id": 5,
        "case_id": 500,
        "title": "Nivel 5 – La Verdad Detrás del Acoso",
        "subtitle": "Reconstrucción Total: El Caso Final",
        "case_type": "CASO FINAL",
        "color_accent": (255, 215, 0),
        "victim": "Múltiples víctimas",
        "intro_lines": [
            "Detective, has llegado al caso más importante.",
            "Toda la cadena de eventos que investigaste estaba conectada.",
            "Un mismo individuo está detrás de todas las víctimas,",
            "operando desde un foro clandestino de acosadores.",
            "Es momento de reconstruir toda la línea de hechos",
            "y presentar el caso completo ante las autoridades.",
        ],
        "scenario": (
            "Al cruzar todos los casos, descubres que un foro clandestino conecta todos los ataques. "
            "El mismo líder orquestó cada uno de los incidentes investigados. "
            "Los logs del servidor y las comunicaciones cifradas revelan su identidad real."
        ),
        "evidence_pool": [
            {
                "id": "E5-1",
                "name": "Servidor común entre todos los casos",
                "is_key": True,
                "detail": "Una misma dirección de servidor conecta los 4 casos anteriores.",
            },
            {
                "id": "E5-2",
                "name": "Foro clandestino descubierto",
                "is_key": True,
                "detail": "Foro privado donde se planificaron todos los ataques de forma sistemática.",
            },
            {
                "id": "E5-3",
                "name": "Identidad del administrador del foro",
                "is_key": True,
                "detail": "Los logs del servidor revelan la IP real del administrador.",
            },
            {
                "id": "E5-4",
                "name": "Víctimas adicionales identificadas",
                "is_key": False,
                "detail": "7 víctimas más que no habían denunciado encontradas en el foro.",
            },
            {
                "id": "E5-5",
                "name": "Comunicaciones cifradas descifradas",
                "is_key": True,
                "detail": "Mensajes internos revelan nombre real y foto del líder de la red.",
            },
            {
                "id": "E5-6",
                "name": "Evidencia de pagos a cómplices",
                "is_key": False,
                "detail": "Pagos rastreados del líder a colaboradores para ejecutar los ataques.",
            },
            {
                "id": "E5-7",
                "name": "Declaración de las 4 víctimas anteriores",
                "is_key": False,
                "detail": "Las víctimas de los casos anteriores identifican al mismo agresor.",
            },
            {
                "id": "E5-8",
                "name": "Reporte forense digital final",
                "is_key": True,
                "detail": "Vincula todos los dispositivos analizados al mismo individuo.",
            },
        ],
        "evidence_needed": 5,
        "key_evidence_ids": ["E5-1", "E5-2", "E5-3", "E5-5", "E5-8"],
        "guilty_reveal": (
            "La suma de todas las evidencias —el servidor compartido, el foro clandestino, "
            "las comunicaciones cifradas y el reporte forense— confirman irrefutablemente "
            "que {culprit} es el líder de la red de ciberacosadores."
        ),
        "question": "¿Quién es el líder de la red de ciberacosadores detrás de todos los ataques?",
        "hint": "Conecta todos los puntos: el servidor, el foro y las comunicaciones cifradas.",
        "law": "Ley 1273/2009 + Arts. 220-221 C.P. + Agravantes Máximos",
        "law_title": "Red Criminal de Ciberacoso",
        "law_detail": (
            "Ley 1273/2009 + Arts. 220 y 221 C.P. aplicados conjuntamente. "
            "Por la sistematicidad y múltiples víctimas: pena de hasta 144 meses (12 años). "
            "Inhabilitación de derechos, multa máxima y decomiso de equipos utilizados."
        ),
        "penalty": "Hasta 144 meses (12 años) + multa máxima + inhabilitación de derechos",
        "num_suspects": 4,
        "num_choices": 4,
    },
]


def assign_suspects(level_data):
    """
    Retorna lista de sospechosos para el nivel (uno es culpable, elegido aleatoriamente).
    Retorna: (lista_sospechosos, sospechoso_culpable)
    """
    num = level_data["num_suspects"]
    selected = random.sample(SUSPECTS_POOL, num)
    selected = [dict(s) for s in selected]  # copias independientes
    guilty_idx = random.randint(0, num - 1)
    for i, s in enumerate(selected):
        s["guilty"] = (i == guilty_idx)
    return selected, selected[guilty_idx]


def get_evidence_for_level(level_data):
    """Retorna evidencias mezcladas del nivel"""
    pool = [dict(e) for e in level_data["evidence_pool"]]
    random.shuffle(pool)
    return pool
