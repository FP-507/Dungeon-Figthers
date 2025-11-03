"""
Módulo de selección de personajes para el juego de lucha.
Maneja la interfaz de selección de personajes antes y después de cada ronda.
"""

import pygame
import os

class CharacterSelectScreen:
    """
    Pantalla de selección de personajes que permite a los jugadores
    elegir sus luchadores antes de cada ronda.
    """
    
    def __init__(self, screen_width, screen_height):
        """
        Inicializa la pantalla de selección de personajes.
        
        Args:
            screen_width (int): Ancho de la pantalla
            screen_height (int): Alto de la pantalla
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Configuración de colores mejorada
        self.background_color = (15, 15, 30)           # Azul muy oscuro
        self.background_accent = (25, 25, 45)          # Azul oscuro para acentos
        self.text_color = (255, 255, 255)              # Blanco para texto
        self.title_color = (255, 215, 0)               # Dorado para título
        self.selection_color = (255, 215, 0)           # Dorado para selecciones
        self.border_color = (70, 70, 90)               # Gris azulado para bordes
        self.active_border_color = (255, 100, 100)     # Rojo suave para jugador activo
        self.player1_color = (100, 200, 255)           # Azul claro para P1
        self.player2_color = (255, 100, 150)           # Rosa para P2
        self.confirmed_color = (100, 255, 100)         # Verde para confirmado
        
        # Efectos visuales
        self.particles = []                            # Partículas de fondo
        self.glow_intensity = 0                        # Intensidad del resplandor
        self.glow_direction = 1                        # Dirección del resplandor
        
        # Cargar fuentes para diferentes elementos de texto
        try:
            self.title_font = pygame.font.Font("assets/fonts/turok.ttf", 48)
            self.character_font = pygame.font.Font("assets/fonts/turok.ttf", 24)
            self.instruction_font = pygame.font.Font("assets/fonts/turok.ttf", 16)
        except:
            # Fuentes por defecto si no se encuentran las personalizadas
            self.title_font = pygame.font.Font(None, 48)
            self.character_font = pygame.font.Font(None, 24)
            self.instruction_font = pygame.font.Font(None, 16)
        
        # Lista de personajes disponibles
        self.available_characters = [
            {
                'name': 'Warrior',
                'class_name': 'WarriorFighter',
                'description': 'Guerrero resistente con ataques poderosos',
                'preview_image': None  # Se cargará dinámicamente
            },
            {
                'name': 'Slime Demon',
                'class_name': 'SlimeDemonFighter', 
                'description': 'Demonio ágil con ataques especiales',
                'preview_image': None  # Se cargará dinámicamente
            },
            {
                'name': 'Assassin',
                'class_name': 'AssassinFighter',
                'description': 'Asesino rápido con ataques consecutivos',
                'preview_image': None  # Se cargará dinámicamente
            },
            {
                'name': 'Tank',
                'class_name': 'TankFighter',
                'description': 'Tanque resistente con ataques de gran empuje',
                'preview_image': None  # Se cargará dinámicamente
            },
            {
                'name': 'Trapper',
                'class_name': 'TrapperFighter',
                'description': 'Cazador ágil con trampas y ataques a distancia',
                'preview_image': None  # Se cargará dinámicamente
            }
        ]
        
        # Cargar imágenes de preview de personajes
        self.load_character_previews()
        
        # Selecciones actuales de los jugadores
        self.player_1_selection = 0  # Índice del personaje seleccionado
        self.player_2_selection = 1  # Índice del personaje seleccionado (SlimeDemon por defecto)
        self.active_player = 1       # Qué jugador está seleccionando actualmente
        
        # Estados de selección
        self.selection_confirmed = [False, False]  # [P1_confirmed, P2_confirmed]
        self.selection_complete = False
        
        # Animaciones y efectos
        self.last_blink_time = 0
        self.blink_state = True
        self.animation_time = 0
        self.character_hover_scale = [1.0, 1.0, 1.0, 1.0, 1.0]  # Escala de hover para cada personaje
        self.last_particle_spawn = 0
        
        # Inicializar partículas de fondo
        self.init_particles()
        
    def load_character_previews(self):
        """
        Carga las imágenes de preview de cada personaje.
        Utiliza el primer frame de la animación idle como preview.
        """
        for character_data in self.available_characters:
            character_name = character_data['name'].lower().replace(' ', '_')
            
            if character_name == 'warrior':
                preview_path = "assets/images/warrior/Sprites/idle/idle_1.png"
            elif character_name == 'slime_demon':
                preview_path = "assets/images/slime_demon/Sprites/idle/1.png"
            elif character_name == 'assassin':
                preview_path = "assets/images/assasin/Sprites/idle/idle_1.png"  # Ruta corregida
            elif character_name == 'tank':
                preview_path = "assets/images/tank/Sprites/idle/idle_1.png"  # Ruta corregida
            elif character_name == 'trapper':
                preview_path = "assets/images/trapper/Sprites/01_idle/01_idle_1.png"  # Ruta del Trapper
            else:
                continue
                
            try:
                if os.path.exists(preview_path):
                    # Cargar y escalar la imagen de preview
                    preview_image = pygame.image.load(preview_path).convert_alpha()
                    # Escalar a un tamaño más grande para mejor visibilidad
                    scaled_preview = pygame.transform.scale(preview_image, (140, 140))  # Aumentado de 120
                    character_data['preview_image'] = scaled_preview
                else:
                    # Crear imagen placeholder si no se encuentra la imagen
                    placeholder = pygame.Surface((140, 140))  # Aumentado para coincidir
                    placeholder.fill((128, 128, 128))  # Gris como placeholder
                    character_data['preview_image'] = placeholder
            except:
                # Crear imagen placeholder en caso de error
                placeholder = pygame.Surface((140, 140))  # Aumentado para coincidir
                placeholder.fill((128, 128, 128))
                character_data['preview_image'] = placeholder
    
    def init_particles(self):
        """Inicializa las partículas de fondo para efectos visuales."""
        import random
        for _ in range(50):
            particle = {
                'x': random.randint(0, self.screen_width),
                'y': random.randint(0, self.screen_height),
                'speed': random.uniform(0.5, 2.0),
                'size': random.randint(1, 3),
                'opacity': random.randint(50, 150)
            }
            self.particles.append(particle)
    
    def update_particles(self):
        """Actualiza las partículas de fondo."""
        import random
        for particle in self.particles:
            particle['y'] += particle['speed']
            if particle['y'] > self.screen_height:
                particle['y'] = -10
                particle['x'] = random.randint(0, self.screen_width)
    
    def draw_particles(self, surface):
        """Dibuja las partículas de fondo."""
        for particle in self.particles:
            color = (particle['opacity'], particle['opacity'], particle['opacity'] + 50)
            pygame.draw.circle(surface, color, 
                             (int(particle['x']), int(particle['y'])), 
                             particle['size'])
    
    def draw_gradient_background(self, surface):
        """Dibuja un fondo con gradiente mejorado."""
        # Crear gradiente vertical
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            r = int(self.background_color[0] + (self.background_accent[0] - self.background_color[0]) * ratio)
            g = int(self.background_color[1] + (self.background_accent[1] - self.background_color[1]) * ratio)
            b = int(self.background_color[2] + (self.background_accent[2] - self.background_color[2]) * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.screen_width, y))
    
    def draw_character_card(self, surface, character_data, x, y, scale, selected_by_p1, selected_by_p2, active_selection):
        """Dibuja una carta de personaje mejorada con efectos visuales."""
        # Dimensiones de la carta
        card_width = int(160 * scale)
        card_height = int(240 * scale)
        
        # Crear superficie de la carta con transparencia
        card_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        
        # Fondo de la carta con gradiente
        for i in range(card_height):
            ratio = i / card_height
            color_intensity = int(40 + 20 * ratio)
            color = (color_intensity, color_intensity, color_intensity + 10)
            pygame.draw.line(card_surface, color, (0, i), (card_width, i))
        
        # Borde de la carta según el estado
        border_color = self.border_color
        border_width = 2
        
        if active_selection and self.blink_state:
            border_color = self.active_border_color
            border_width = 4
        elif selected_by_p1 and self.selection_confirmed[0]:
            border_color = self.player1_color
            border_width = 3
        elif selected_by_p2 and self.selection_confirmed[1]:
            border_color = self.player2_color
            border_width = 3
        elif selected_by_p1:
            border_color = self.player1_color
            border_width = 2
        elif selected_by_p2:
            border_color = self.player2_color
            border_width = 2
        
        pygame.draw.rect(card_surface, border_color, card_surface.get_rect(), border_width)
        
        # Imagen del personaje - ENORME ocupando casi toda la carta
        if character_data['preview_image']:
            img_size = int(180 * scale)  # ENORME - 80% más grande que el original
            scaled_img = pygame.transform.scale(character_data['preview_image'], (img_size, img_size))
            img_x = (card_width - img_size) // 2
            img_y = 5  # Muy arriba para maximizar espacio
            card_surface.blit(scaled_img, (img_x, img_y))
        
        # Nombre del personaje con sombra
        name_font_size = int(20 * scale)
        try:
            name_font = pygame.font.Font("assets/fonts/turok.ttf", name_font_size)
        except:
            name_font = pygame.font.Font(None, name_font_size)
        
        # Sombra del texto - en la parte inferior para imagen enorme
        shadow_text = name_font.render(character_data['name'], True, (0, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(card_width // 2 + 2, int(210 * scale) + 2))
        card_surface.blit(shadow_text, shadow_rect)
        
        # Texto principal
        name_text = name_font.render(character_data['name'], True, self.text_color)
        name_rect = name_text.get_rect(center=(card_width // 2, int(210 * scale)))
        card_surface.blit(name_text, name_rect)
        
        # Descripción eliminada para dar más espacio a la imagen
        
        # Dibujar la carta en la superficie principal
        card_rect = card_surface.get_rect(center=(x, y))
        surface.blit(card_surface, card_rect)
    
    def handle_input(self, event):
        """
        Maneja la entrada del usuario en la pantalla de selección.
        
        Args:
            event: Evento de pygame a procesar
            
        Returns:
            bool: True si la selección está completa, False en caso contrario
        """
        if event.type == pygame.KEYDOWN:
            # Controles para el jugador activo
            if self.active_player == 1 and not self.selection_confirmed[0]:
                # Controles del Jugador 1 (A/D para navegar, R para confirmar)
                if event.key == pygame.K_a:  # Mover selección a la izquierda
                    self.player_1_selection = (self.player_1_selection - 1) % len(self.available_characters)
                elif event.key == pygame.K_d:  # Mover selección a la derecha
                    self.player_1_selection = (self.player_1_selection + 1) % len(self.available_characters)
                elif event.key == pygame.K_r:  # Confirmar selección
                    self.selection_confirmed[0] = True
                    self.active_player = 2  # Cambiar al jugador 2
                    
            elif self.active_player == 2 and not self.selection_confirmed[1]:
                # Controles del Jugador 2 (Flechas para navegar, 1 para confirmar)
                if event.key == pygame.K_LEFT:  # Mover selección a la izquierda
                    self.player_2_selection = (self.player_2_selection - 1) % len(self.available_characters)
                elif event.key == pygame.K_RIGHT:  # Mover selección a la derecha
                    self.player_2_selection = (self.player_2_selection + 1) % len(self.available_characters)
                elif event.key == pygame.K_KP1:  # Confirmar selección
                    self.selection_confirmed[1] = True
                    self.selection_complete = True  # Ambos jugadores han seleccionado
            
            # Permitir cancelar selección con ESC
            if event.key == pygame.K_ESCAPE:
                if self.selection_confirmed[1]:
                    self.selection_confirmed[1] = False
                    self.active_player = 2
                    self.selection_complete = False
                elif self.selection_confirmed[0]:
                    self.selection_confirmed[0] = False
                    self.active_player = 1
        
        return self.selection_complete
    
    def update(self):
        """
        Actualiza el estado de la pantalla de selección.
        Maneja animaciones y efectos visuales.
        """
        current_time = pygame.time.get_ticks()
        
        # Actualizar parpadeo para indicar jugador activo
        if current_time - self.last_blink_time > 500:  # Parpadear cada 500ms
            self.blink_state = not self.blink_state
            self.last_blink_time = current_time
        
        # Actualizar tiempo de animación
        self.animation_time = current_time
        
        # Actualizar efecto de resplandor
        self.glow_intensity += self.glow_direction * 2
        if self.glow_intensity >= 100:
            self.glow_direction = -1
        elif self.glow_intensity <= 0:
            self.glow_direction = 1
        
        # Actualizar escalas de hover para personajes
        for i in range(len(self.available_characters)):
            target_scale = 1.1 if (i == self.player_1_selection and self.active_player == 1) or \
                                 (i == self.player_2_selection and self.active_player == 2) else 1.0
            
            # Suavizar transición de escala
            self.character_hover_scale[i] += (target_scale - self.character_hover_scale[i]) * 0.1
        
        # Actualizar partículas
        self.update_particles()
    
    def draw(self, surface):
        """
        Dibuja la pantalla de selección de personajes con efectos visuales mejorados.
        
        Args:
            surface: Superficie de pygame donde dibujar
        """
        # Dibujar fondo con gradiente
        self.draw_gradient_background(surface)
        
        # Dibujar partículas de fondo
        self.draw_particles(surface)
        
        # Dibujar título con efectos
        title_text = self.title_font.render("SELECCIÓN DE PERSONAJES", True, self.title_color)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 60))
        
        # Sombra del título
        title_shadow = self.title_font.render("SELECCIÓN DE PERSONAJES", True, (0, 0, 0))
        shadow_rect = title_shadow.get_rect(center=(self.screen_width // 2 + 3, 63))
        surface.blit(title_shadow, shadow_rect)
        surface.blit(title_text, title_rect)
        
        # Línea decorativa bajo el título
        line_y = 100
        pygame.draw.line(surface, self.title_color, 
                        (self.screen_width // 2 - 200, line_y), 
                        (self.screen_width // 2 + 200, line_y), 3)
        
        # Calcular posiciones para las cartas de personajes
        character_spacing = 240  # Reducido para acomodar 5 personajes
        start_x = (self.screen_width - (len(self.available_characters) * character_spacing)) // 2 + character_spacing // 2
        character_y = 280
        
        # Dibujar cada personaje disponible con cartas mejoradas
        for i, character_data in enumerate(self.available_characters):
            character_x = start_x + (i * character_spacing)
            
            # Determinar estados de selección
            selected_by_player_1 = (i == self.player_1_selection)
            selected_by_player_2 = (i == self.player_2_selection)
            active_selection = ((selected_by_player_1 and self.active_player == 1 and not self.selection_confirmed[0]) or
                              (selected_by_player_2 and self.active_player == 2 and not self.selection_confirmed[1]))
            
            # Dibujar carta del personaje con efectos
            scale = self.character_hover_scale[i]
            self.draw_character_card(surface, character_data, character_x, character_y, scale,
                                   selected_by_player_1, selected_by_player_2, active_selection)
            
            # Efectos de resplandor para personajes seleccionados
            if (selected_by_player_1 and self.selection_confirmed[0]) or \
               (selected_by_player_2 and self.selection_confirmed[1]):
                glow_surface = pygame.Surface((200, 280), pygame.SRCALPHA)
                glow_color = (*self.confirmed_color, int(30 + self.glow_intensity * 0.3))
                pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect(), 0)
                glow_rect = glow_surface.get_rect(center=(character_x, character_y))
                surface.blit(glow_surface, glow_rect, special_flags=pygame.BLEND_ADD)
        
        # Panel de información de jugadores mejorado
        panel_height = 150
        panel_y = self.screen_height - panel_height
        
        # Fondo del panel con transparencia
        panel_surface = pygame.Surface((self.screen_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (*self.background_accent, 180), panel_surface.get_rect())
        surface.blit(panel_surface, (0, panel_y))
        
        # Información del Jugador 1
        p1_status = "✓ LISTO" if self.selection_confirmed[0] else "Seleccionando..."
        p1_char = self.available_characters[self.player_1_selection]['name']
        p1_color = self.confirmed_color if self.selection_confirmed[0] else self.player1_color
        
        p1_title = self.character_font.render("JUGADOR 1", True, self.player1_color)
        p1_character = self.character_font.render(f"Personaje: {p1_char}", True, self.text_color)
        p1_status_text = self.character_font.render(p1_status, True, p1_color)
        
        surface.blit(p1_title, (50, panel_y + 20))
        surface.blit(p1_character, (50, panel_y + 45))
        surface.blit(p1_status_text, (50, panel_y + 70))
        
        # Información del Jugador 2
        p2_status = "✓ LISTO" if self.selection_confirmed[1] else "Seleccionando..."
        p2_char = self.available_characters[self.player_2_selection]['name']
        p2_color = self.confirmed_color if self.selection_confirmed[1] else self.player2_color
        
        p2_title = self.character_font.render("JUGADOR 2", True, self.player2_color)
        p2_character = self.character_font.render(f"Personaje: {p2_char}", True, self.text_color)
        p2_status_text = self.character_font.render(p2_status, True, p2_color)
        
        p2_x = self.screen_width // 2 + 50
        surface.blit(p2_title, (p2_x, panel_y + 20))
        surface.blit(p2_character, (p2_x, panel_y + 45))
        surface.blit(p2_status_text, (p2_x, panel_y + 70))
        
        # Controles en la parte inferior
        if not self.selection_confirmed[0]:
            controls_p1 = "P1: A/D - Navegar | R - Confirmar"
        else:
            controls_p1 = "P1: ESC - Cambiar selección"
            
        if not self.selection_confirmed[1]:
            controls_p2 = "P2: ←/→ - Navegar | 1 - Confirmar"
        else:
            controls_p2 = "P2: ESC - Cambiar selección"
        
        controls1_text = self.instruction_font.render(controls_p1, True, self.text_color)
        controls2_text = self.instruction_font.render(controls_p2, True, self.text_color)
        
        surface.blit(controls1_text, (50, panel_y + 100))
        surface.blit(controls2_text, (50, panel_y + 120))
        
        # Mensaje final animado cuando ambos han seleccionado
        if self.selection_complete:
            # Efecto de resplandor en el mensaje final
            glow_intensity = int(50 + 30 * abs(pygame.math.cos(self.animation_time * 0.005)))
            final_color = (*self.title_color, glow_intensity)
            
            final_text = self.title_font.render("¡PREPARADOS PARA LA BATALLA!", True, self.title_color)
            final_rect = final_text.get_rect(center=(self.screen_width // 2, 150))
            
            # Sombra animada
            shadow_offset = int(3 + 2 * pygame.math.sin(self.animation_time * 0.01))
            final_shadow = self.title_font.render("¡PREPARADOS PARA LA BATALLA!", True, (0, 0, 0))
            shadow_rect = final_shadow.get_rect(center=(self.screen_width // 2 + shadow_offset, 150 + shadow_offset))
            
            surface.blit(final_shadow, shadow_rect)
            surface.blit(final_text, final_rect)
    
    def get_selected_characters(self):
        """
        Obtiene los personajes seleccionados por ambos jugadores.
        
        Returns:
            tuple: (character_class_p1, character_class_p2)
        """
        p1_character = self.available_characters[self.player_1_selection]['class_name']
        p2_character = self.available_characters[self.player_2_selection]['class_name']
        return p1_character, p2_character
    
    def reset_selection(self):
        """
        Reinicia la pantalla de selección para una nueva ronda.
        """
        self.selection_confirmed = [False, False]
        self.selection_complete = False
        self.active_player = 1
        # Mantener las selecciones anteriores para conveniencia del jugador