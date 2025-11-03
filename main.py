"""
Juego de lucha 2D mejorado con sistema de selección de personajes,
zoom dinámico basado en distancia y visualización de hitboxes.

Características principales:
- Sistema de clases padre-hijo para personajes
- Carga de sprites frame por frame
- Tercer ataque para cada personaje
- Zoom dinámico según distancia entre luchadores
- Pantalla de selección de personajes
- Visualización de hitboxes con tecla Z
- Escenario más amplio para mejor combate
"""

import pygame
from pygame import mixer
from fighters import WarriorFighter, SlimeDemonFighter, AssassinFighter, TankFighter, TrapperFighter
from character_select import CharacterSelectScreen
import math

# Inicialización de pygame y mixer para audio
mixer.init()
pygame.init()

# Configuración de la ventana del juego - escenario más amplio
SCREEN_WIDTH = 1400  # Aumentado de 1000 para dar más espacio
SCREEN_HEIGHT = 600
ORIGINAL_SCREEN_WIDTH = SCREEN_WIDTH  # Para cálculos de zoom

# Crear ventana del juego
game_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dungeon Fighters - Enhanced Edition")

# Configuración de framerate
game_clock = pygame.time.Clock()
FRAMES_PER_SECOND = 60

# Definición de colores usando snake_case
COLOR_RED = (255, 0, 0)
COLOR_YELLOW = (255, 255, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_ORANGE = (255, 165, 0)

# Variables de estado del juego
intro_countdown = 3
last_countdown_update = pygame.time.get_ticks()
player_scores = [0, 0]  # Puntuaciones de los jugadores [P1, P2]
is_round_over = False
ROUND_OVER_DURATION = 2000  # Duración en milisegundos antes de la nueva ronda

# Estados del juego
GAME_STATE_CHARACTER_SELECT = 0
GAME_STATE_COUNTDOWN = 1
GAME_STATE_FIGHTING = 2
GAME_STATE_ROUND_OVER = 3

current_game_state = GAME_STATE_CHARACTER_SELECT

# Sistema de cámara simple con desplazamiento horizontal
camera_offset_x = 0
CAMERA_FOLLOW_SPEED = 0.1  # Velocidad de seguimiento de la cámara
CAMERA_BORDER_MARGIN = 200  # Margen desde los bordes para mover la cámara

# Control de visualización de hitboxes
show_hitboxes = False

# Cargar y configurar música y efectos de sonido
try:
    pygame.mixer.music.load("assets/audio/music.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1, 0.0, 5000)  # Loop infinito con fade-in
except:
    print("No se pudo cargar la música de fondo")

# Cargar efectos de sonido
try:
    sword_sound_effect = pygame.mixer.Sound("assets/audio/sword.wav")
    sword_sound_effect.set_volume(0.5)
except:
    sword_sound_effect = None
    print("No se pudo cargar el efecto de sonido de espada")

try:
    magic_sound_effect = pygame.mixer.Sound("assets/audio/magic.wav")
    magic_sound_effect.set_volume(0.75)
except:
    magic_sound_effect = None
    print("No se pudo cargar el efecto de sonido de magia")

# Cargar imagen de fondo
try:
    background_image = pygame.image.load("assets/images/background/background.jpg").convert_alpha()
except:
    # Crear fondo por defecto si no se encuentra la imagen
    background_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background_image.fill((50, 50, 100))  # Azul oscuro como fondo por defecto
    print("No se pudo cargar la imagen de fondo, usando color por defecto")

# Cargar imagen de victoria
try:
    victory_image = pygame.image.load("assets/images/icons/victory.png").convert_alpha()
except:
    # Crear imagen de victoria por defecto
    victory_image = pygame.Surface((200, 100))
    victory_image.fill((255, 215, 0))  # Dorado
    print("No se pudo cargar la imagen de victoria, usando por defecto")

# Configurar fuentes para el texto
try:
    countdown_font = pygame.font.Font("assets/fonts/turok.ttf", 80)
    score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)
    debug_font = pygame.font.Font("assets/fonts/turok.ttf", 16)
except:
    # Fuentes por defecto si no se encuentran las personalizadas
    countdown_font = pygame.font.Font(None, 80)
    score_font = pygame.font.Font(None, 30)
    debug_font = pygame.font.Font(None, 16)
    print("Usando fuentes por defecto")

# Inicializar pantalla de selección de personajes
character_select_screen = CharacterSelectScreen(SCREEN_WIDTH, SCREEN_HEIGHT)

# Variables para los luchadores (se inicializarán después de la selección)
fighter_player_1 = None
fighter_player_2 = None
selected_characters = (None, None)
round_over_start_time = 0

def draw_text_on_screen(text, font, text_color, x_position, y_position):
    """
    Dibuja texto en la pantalla en la posición especificada.
    
    Args:
        text (str): Texto a dibujar
        font: Fuente de pygame a usar
        text_color: Color del texto (tupla RGB)
        x_position (int): Posición X donde dibujar
        y_position (int): Posición Y donde dibujar
    """
    text_surface = font.render(str(text), True, text_color)
    game_screen.blit(text_surface, (x_position, y_position))

def draw_game_background():
    """
    Dibuja el fondo del juego con desplazamiento horizontal correcto.
    Un solo fondo que se mueve suavemente sin mostrar franjas negras.
    """
    # Crear fondo extendido para permitir movimiento sin mostrar bordes
    extended_width = SCREEN_WIDTH + 800  # Fondo más amplio para el movimiento
    scaled_background = pygame.transform.scale(background_image, (extended_width, SCREEN_HEIGHT))
    
    # Aplicar offset de cámara con parallax sutil
    bg_x = int(camera_offset_x * 0.2) - 300  # Offset inicial para centrar el fondo
    bg_y = 0
    
    # Asegurar que el fondo siempre cubra toda la pantalla
    # Si el fondo se sale por la izquierda, ajustarlo
    if bg_x > 0:
        bg_x = 0
    # Si el fondo se sale por la derecha, ajustarlo
    elif bg_x < -(extended_width - SCREEN_WIDTH):
        bg_x = -(extended_width - SCREEN_WIDTH)
    
    # Dibujar el fondo una sola vez en la posición calculada
    game_screen.blit(scaled_background, (bg_x, bg_y))

def draw_health_bar(current_health, max_health, x_position, y_position):
    """
    Dibuja la barra de salud de un jugador.
    
    Args:
        current_health (int): Salud actual del jugador
        max_health (int): Salud máxima del jugador
        x_position (int): Posición X de la barra
        y_position (int): Posición Y de la barra
    """
    # Calcular proporción de salud restante
    health_ratio = max(current_health / max_health, 0)  # Asegurar que no sea negativo
    
    # Dimensiones de la barra de salud
    bar_width = 400
    bar_height = 30
    border_thickness = 2
    
    # Dibujar borde blanco
    border_rect = pygame.Rect(x_position - border_thickness, y_position - border_thickness, 
                             bar_width + 2 * border_thickness, bar_height + 2 * border_thickness)
    pygame.draw.rect(game_screen, COLOR_WHITE, border_rect)
    
    # Dibujar fondo rojo (salud perdida)
    background_rect = pygame.Rect(x_position, y_position, bar_width, bar_height)
    pygame.draw.rect(game_screen, COLOR_RED, background_rect)
    
    # Dibujar salud actual con progresión de color: Verde (>66%), Amarillo (33-66%), Naranja (<=33%)
    health_width = int(bar_width * health_ratio)
    if health_ratio > 0.66:
        health_color = COLOR_GREEN
    elif health_ratio > 0.33:
        health_color = COLOR_YELLOW
    else:
        health_color = COLOR_ORANGE
        
    health_rect = pygame.Rect(x_position, y_position, health_width, bar_height)
    pygame.draw.rect(game_screen, health_color, health_rect)

def calculate_camera_follow(fighter1, fighter2):
    """
    Calcula el seguimiento simple de cámara basado en la posición de los luchadores.
    La cámara se mueve horizontalmente para mantener a ambos luchadores en pantalla.
    
    Args:
        fighter1: Primer luchador
        fighter2: Segundo luchador
    """
    global camera_offset_x
    
    if not fighter1 or not fighter2:
        return
    
    # Calcular punto medio entre luchadores
    midpoint_x = (fighter1.collision_rect.centerx + fighter2.collision_rect.centerx) // 2
    
    # Calcular posición ideal de cámara para centrar el punto medio
    ideal_camera_x = (SCREEN_WIDTH // 2) - midpoint_x
    
    # Límites mejorados para evitar mostrar áreas vacías
    max_offset = 300  # Máximo desplazamiento permitido (aumentado)
    min_offset = -300
    ideal_camera_x = max(min_offset, min(max_offset, ideal_camera_x))
    
    # Suavizar movimiento de cámara con mejor responsividad
    camera_offset_x += (ideal_camera_x - camera_offset_x) * (CAMERA_FOLLOW_SPEED * 1.5)

def create_fighters_from_selection():
    """
    Crea las instancias de luchadores basadas en la selección de personajes.
    
    Returns:
        tuple: (fighter_1, fighter_2)
    """
    p1_character, p2_character = character_select_screen.get_selected_characters()
    
    # Posiciones iniciales más separadas para el escenario amplio
    initial_x_p1 = 300  # Más hacia la izquierda
    initial_x_p2 = 1100  # Más hacia la derecha
    initial_y = 370  # Posición que permite que el bottom del rect toque el suelo en 550
    
    # Crear luchador del jugador 1
    if p1_character == 'WarriorFighter':
        fighter_1 = WarriorFighter(1, initial_x_p1, initial_y, False, sword_sound_effect)
    elif p1_character == 'SlimeDemonFighter':
        fighter_1 = SlimeDemonFighter(1, initial_x_p1, initial_y, False, magic_sound_effect)
    elif p1_character == 'AssassinFighter':
        fighter_1 = AssassinFighter(1, initial_x_p1, initial_y, False, sword_sound_effect)
    elif p1_character == 'TankFighter':
        fighter_1 = TankFighter(1, initial_x_p1, initial_y, False, sword_sound_effect)
    elif p1_character == 'TrapperFighter':
        fighter_1 = TrapperFighter(1, initial_x_p1, initial_y, False, sword_sound_effect)
    else:
        # Por defecto, usar Warrior
        fighter_1 = WarriorFighter(1, initial_x_p1, initial_y, False, sword_sound_effect)
    
    # Crear luchador del jugador 2
    if p2_character == 'WarriorFighter':
        fighter_2 = WarriorFighter(2, initial_x_p2, initial_y, True, sword_sound_effect)
    elif p2_character == 'SlimeDemonFighter':
        fighter_2 = SlimeDemonFighter(2, initial_x_p2, initial_y, True, magic_sound_effect)
    elif p2_character == 'AssassinFighter':
        fighter_2 = AssassinFighter(2, initial_x_p2, initial_y, True, sword_sound_effect)
    elif p2_character == 'TankFighter':
        fighter_2 = TankFighter(2, initial_x_p2, initial_y, True, sword_sound_effect)
    elif p2_character == 'TrapperFighter':
        fighter_2 = TrapperFighter(2, initial_x_p2, initial_y, True, sword_sound_effect)
    else:
        # Por defecto, usar Slime Demon
        fighter_2 = SlimeDemonFighter(2, initial_x_p2, initial_y, True, magic_sound_effect)
    
    return fighter_1, fighter_2

def handle_game_input(event):
    """
    Maneja la entrada del usuario según el estado actual del juego.
    
    Args:
        event: Evento de pygame a procesar
    """
    global show_hitboxes, current_game_state, is_round_over, intro_countdown
    global last_countdown_update, fighter_player_1, fighter_player_2
    
    if event.type == pygame.KEYDOWN:
        # Tecla Z para alternar visualización de hitboxes
        if event.key == pygame.K_z:
            show_hitboxes = not show_hitboxes
        
        # Manejo específico según estado del juego
        if current_game_state == GAME_STATE_CHARACTER_SELECT:
            # Pantalla de selección de personajes
            if character_select_screen.handle_input(event):
                # Selección completa, crear luchadores y comenzar cuenta regresiva
                fighter_player_1, fighter_player_2 = create_fighters_from_selection()
                current_game_state = GAME_STATE_COUNTDOWN
                intro_countdown = 3
                last_countdown_update = pygame.time.get_ticks()
        
        elif current_game_state == GAME_STATE_ROUND_OVER:
            # Después de una ronda, permitir ir a selección con Enter
            if event.key == pygame.K_RETURN:
                character_select_screen.reset_selection()
                current_game_state = GAME_STATE_CHARACTER_SELECT

def update_game_state():
    """
    Actualiza el estado del juego y maneja transiciones entre estados.
    """
    global current_game_state, intro_countdown, last_countdown_update
    global is_round_over, round_over_start_time, player_scores
    
    if current_game_state == GAME_STATE_CHARACTER_SELECT:
        # Actualizar pantalla de selección
        character_select_screen.update()
    
    elif current_game_state == GAME_STATE_COUNTDOWN:
        # Manejar cuenta regresiva
        if intro_countdown > 0:
            current_time = pygame.time.get_ticks()
            if current_time - last_countdown_update >= 1000:
                intro_countdown -= 1
                last_countdown_update = current_time
        else:
            current_game_state = GAME_STATE_FIGHTING
    
    elif current_game_state == GAME_STATE_FIGHTING:
        # Actualizar luchadores
        if fighter_player_1 and fighter_player_2:
            # Calcular seguimiento de cámara
            calculate_camera_follow(fighter_player_1, fighter_player_2)
            
            # Mover luchadores
            fighter_player_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, game_screen, fighter_player_2, False)
            fighter_player_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, game_screen, fighter_player_1, False)
            
            # Actualizar animaciones
            fighter_player_1.update(fighter_player_2)
            fighter_player_2.update(fighter_player_1)
            
            # Victoria solo cuando la animación de muerte se completó
            if not fighter_player_1.is_alive and fighter_player_1.death_animation_done:
                player_scores[1] += 1
                current_game_state = GAME_STATE_ROUND_OVER
                round_over_start_time = pygame.time.get_ticks()
            elif not fighter_player_2.is_alive and fighter_player_2.death_animation_done:
                player_scores[0] += 1
                current_game_state = GAME_STATE_ROUND_OVER
                round_over_start_time = pygame.time.get_ticks()
    
    elif current_game_state == GAME_STATE_ROUND_OVER:
        # Esperar antes de permitir nueva ronda
        if pygame.time.get_ticks() - round_over_start_time > ROUND_OVER_DURATION:
            # Automáticamente volver a selección de personajes
            character_select_screen.reset_selection()
            current_game_state = GAME_STATE_CHARACTER_SELECT
            # Nada adicional que resetear

def render_game():
    """
    Renderiza todos los elementos visuales del juego según el estado actual.
    """
    # Limpiar pantalla
    game_screen.fill((0, 0, 0))
    
    if current_game_state == GAME_STATE_CHARACTER_SELECT:
        # Mostrar pantalla de selección de personajes
        character_select_screen.draw(game_screen)
    
    else:
        # Dibujar fondo del juego
        draw_game_background()
        
        # Mostrar estadísticas de jugadores
        if fighter_player_1 and fighter_player_2:
            # Barras de salud
            draw_health_bar(fighter_player_1.current_health, fighter_player_1.max_health, 20, 20)
            draw_health_bar(fighter_player_2.current_health, fighter_player_2.max_health, 
                          SCREEN_WIDTH - 420, 20)
            
            # Puntuaciones
            draw_text_on_screen(f"P1: {player_scores[0]}", score_font, COLOR_RED, 20, 60)
            draw_text_on_screen(f"P2: {player_scores[1]}", score_font, COLOR_RED, SCREEN_WIDTH - 420, 60)
        
        if current_game_state == GAME_STATE_COUNTDOWN:
            # Mostrar cuenta regresiva
            if intro_countdown > 0:
                draw_text_on_screen(str(intro_countdown), countdown_font, COLOR_RED, 
                                  SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 3)
        
        elif current_game_state == GAME_STATE_FIGHTING:
            # Dibujar luchadores
            if fighter_player_1 and fighter_player_2:
                fighter_player_1.draw(game_screen, camera_offset_x)
                fighter_player_2.draw(game_screen, camera_offset_x)
                
                # Mostrar hitboxes si está activado
                if show_hitboxes:
                    fighter_player_1.draw_hitbox(game_screen, True, camera_offset_x)
                    fighter_player_2.draw_hitbox(game_screen, True, camera_offset_x)
                    # Overlay de daño debug sobre cada luchador
                    now_ms = pygame.time.get_ticks()
                    for f in [fighter_player_1, fighter_player_2]:
                        if hasattr(f, 'last_damage_timestamp') and now_ms - f.last_damage_timestamp < 1500:
                            dmg_text = f"Daño: {f.last_damage_applied}" if f.last_damage_applied > 0 else "Daño: 0"
                            draw_text_on_screen(dmg_text, debug_font, COLOR_WHITE, f.collision_rect.centerx - 40 + camera_offset_x, f.collision_rect.y - 25)
                            frame_text = f"Frame atk: {f.frame_index}" if f.is_attacking else ""
                            if frame_text:
                                draw_text_on_screen(frame_text, debug_font, COLOR_YELLOW, f.collision_rect.centerx - 50 + camera_offset_x, f.collision_rect.y - 40)
        
        elif current_game_state == GAME_STATE_ROUND_OVER:
            # Dibujar luchadores en su estado final
            if fighter_player_1 and fighter_player_2:
                fighter_player_1.draw(game_screen, camera_offset_x)
                fighter_player_2.draw(game_screen, camera_offset_x)
            
            # Mostrar imagen de victoria
            victory_rect = victory_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            game_screen.blit(victory_image, victory_rect)
            
            # Instrucción para continuar
            draw_text_on_screen("Presiona ENTER para nueva ronda", score_font, COLOR_WHITE, 
                              SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 100)
        
        # Información de debug
        if show_hitboxes:
            debug_text = f"Hitboxes: ON | Camera Offset: {camera_offset_x:.1f}"
            draw_text_on_screen(debug_text, debug_font, COLOR_WHITE, 10, SCREEN_HEIGHT - 30)

# Bucle principal del juego
game_running = True
while game_running:
    # Mantener framerate constante
    game_clock.tick(FRAMES_PER_SECOND)
    
    # Manejar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False
        else:
            handle_game_input(event)
    
    # Actualizar estado del juego
    update_game_state()
    
    # Renderizar todo
    render_game()
    
    # Actualizar pantalla
    pygame.display.update()

# Salir de pygame limpiamente
pygame.quit()