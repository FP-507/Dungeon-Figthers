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
        
        # Configuración de colores usando snake_case
        self.background_color = (30, 30, 50)      # Azul oscuro para el fondo
        self.text_color = (255, 255, 255)         # Blanco para texto
        self.selection_color = (255, 215, 0)      # Dorado para selecciones
        self.border_color = (100, 100, 100)       # Gris para bordes
        self.active_border_color = (255, 0, 0)    # Rojo para jugador activo
        
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
            }
        ]
        
        # Cargar imágenes de preview de personajes
        self.load_character_previews()
        
        # Selecciones actuales de los jugadores
        self.player_1_selection = 0  # Índice del personaje seleccionado
        self.player_2_selection = 1  # Índice del personaje seleccionado
        self.active_player = 1       # Qué jugador está seleccionando actualmente
        
        # Estados de selección
        self.selection_confirmed = [False, False]  # [P1_confirmed, P2_confirmed]
        self.selection_complete = False
        
        # Tiempo para animaciones
        self.last_blink_time = 0
        self.blink_state = True
        
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
            else:
                continue
                
            try:
                if os.path.exists(preview_path):
                    # Cargar y escalar la imagen de preview
                    preview_image = pygame.image.load(preview_path).convert_alpha()
                    # Escalar a un tamaño apropiado para la selección
                    scaled_preview = pygame.transform.scale(preview_image, (120, 120))
                    character_data['preview_image'] = scaled_preview
                else:
                    # Crear imagen placeholder si no se encuentra la imagen
                    placeholder = pygame.Surface((120, 120))
                    placeholder.fill((128, 128, 128))  # Gris como placeholder
                    character_data['preview_image'] = placeholder
            except:
                # Crear imagen placeholder en caso de error
                placeholder = pygame.Surface((120, 120))
                placeholder.fill((128, 128, 128))
                character_data['preview_image'] = placeholder
    
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
        # Actualizar parpadeo para indicar jugador activo
        current_time = pygame.time.get_ticks()
        if current_time - self.last_blink_time > 500:  # Parpadear cada 500ms
            self.blink_state = not self.blink_state
            self.last_blink_time = current_time
    
    def draw(self, surface):
        """
        Dibuja la pantalla de selección de personajes.
        
        Args:
            surface: Superficie de pygame donde dibujar
        """
        # Limpiar pantalla con color de fondo
        surface.fill(self.background_color)
        
        # Dibujar título
        title_text = self.title_font.render("SELECCIÓN DE PERSONAJES", True, self.text_color)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 50))
        surface.blit(title_text, title_rect)
        
        # Calcular posiciones para los personajes
        character_spacing = 200
        start_x = (self.screen_width - (len(self.available_characters) * character_spacing)) // 2
        character_y = 150
        
        # Dibujar cada personaje disponible
        for i, character_data in enumerate(self.available_characters):
            character_x = start_x + (i * character_spacing)
            
            # Determinar si este personaje está seleccionado por algún jugador
            selected_by_player_1 = (i == self.player_1_selection)
            selected_by_player_2 = (i == self.player_2_selection)
            
            # Dibujar borde de selección
            border_rect = pygame.Rect(character_x - 10, character_y - 10, 140, 200)
            
            if selected_by_player_1 and self.active_player == 1 and not self.selection_confirmed[0]:
                # Jugador 1 seleccionando - borde rojo parpadeante
                if self.blink_state:
                    pygame.draw.rect(surface, self.active_border_color, border_rect, 3)
            elif selected_by_player_2 and self.active_player == 2 and not self.selection_confirmed[1]:
                # Jugador 2 seleccionando - borde rojo parpadeante
                if self.blink_state:
                    pygame.draw.rect(surface, self.active_border_color, border_rect, 3)
            elif selected_by_player_1 and self.selection_confirmed[0]:
                # Jugador 1 confirmado - borde dorado sólido
                pygame.draw.rect(surface, self.selection_color, border_rect, 3)
            elif selected_by_player_2 and self.selection_confirmed[1]:
                # Jugador 2 confirmado - borde dorado sólido
                pygame.draw.rect(surface, self.selection_color, border_rect, 3)
            else:
                # No seleccionado - borde gris
                pygame.draw.rect(surface, self.border_color, border_rect, 2)
            
            # Dibujar imagen de preview del personaje
            if character_data['preview_image']:
                image_rect = character_data['preview_image'].get_rect(center=(character_x + 60, character_y + 60))
                surface.blit(character_data['preview_image'], image_rect)
            
            # Dibujar nombre del personaje
            name_text = self.character_font.render(character_data['name'], True, self.text_color)
            name_rect = name_text.get_rect(center=(character_x + 60, character_y + 140))
            surface.blit(name_text, name_rect)
            
            # Dibujar descripción del personaje
            description_words = character_data['description'].split()
            line_height = 16
            max_width = 120
            y_offset = character_y + 160
            
            current_line = ""
            for word in description_words:
                test_line = current_line + word + " "
                if self.instruction_font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        desc_text = self.instruction_font.render(current_line.strip(), True, self.text_color)
                        desc_rect = desc_text.get_rect(center=(character_x + 60, y_offset))
                        surface.blit(desc_text, desc_rect)
                        y_offset += line_height
                    current_line = word + " "
            
            # Dibujar última línea
            if current_line:
                desc_text = self.instruction_font.render(current_line.strip(), True, self.text_color)
                desc_rect = desc_text.get_rect(center=(character_x + 60, y_offset))
                surface.blit(desc_text, desc_rect)
        
        # Dibujar indicadores de jugador
        player_1_indicator = f"JUGADOR 1: {'✓' if self.selection_confirmed[0] else 'Seleccionando...'}"
        player_2_indicator = f"JUGADOR 2: {'✓' if self.selection_confirmed[1] else 'Seleccionando...'}"
        
        p1_text = self.character_font.render(player_1_indicator, True, 
                                           self.selection_color if self.selection_confirmed[0] else self.text_color)
        p2_text = self.character_font.render(player_2_indicator, True, 
                                           self.selection_color if self.selection_confirmed[1] else self.text_color)
        
        surface.blit(p1_text, (50, self.screen_height - 120))
        surface.blit(p2_text, (50, self.screen_height - 90))
        
        # Dibujar instrucciones
        if not self.selection_confirmed[0]:
            instructions_p1 = "P1: A/D para navegar, R para confirmar"
        else:
            instructions_p1 = "P1: Selección confirmada"
            
        if not self.selection_confirmed[1]:
            instructions_p2 = "P2: ←/→ para navegar, 1 para confirmar"
        else:
            instructions_p2 = "P2: Selección confirmada"
        
        inst1_text = self.instruction_font.render(instructions_p1, True, self.text_color)
        inst2_text = self.instruction_font.render(instructions_p2, True, self.text_color)
        
        surface.blit(inst1_text, (50, self.screen_height - 60))
        surface.blit(inst2_text, (50, self.screen_height - 40))
        
        # Mensaje final cuando ambos han seleccionado
        if self.selection_complete:
            final_text = self.title_font.render("¡PREPARADOS PARA LA BATALLA!", True, self.selection_color)
            final_rect = final_text.get_rect(center=(self.screen_width // 2, self.screen_height - 100))
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