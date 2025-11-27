"""
Módulo de selección de escenarios para el juego de lucha.
Permite a ambos jugadores elegir un escenario y luego elige uno aleatoriamente.
"""

import pygame
import os
import random
import math


class ScenarioSelectScreen:
    """
    Pantalla de selección de escenarios que permite a los jugadores
    elegir sus escenarios preferidos antes de la batalla.
    """
    
    def __init__(self, screen_width, screen_height):
        """
        Inicializa la pantalla de selección de escenarios.
        
        Args:
            screen_width (int): Ancho de la pantalla
            screen_height (int): Alto de la pantalla
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Configuración de colores
        self.background_color = (15, 15, 30)
        self.background_accent = (25, 25, 45)
        self.text_color = (255, 255, 255)
        self.title_color = (255, 215, 0)
        self.selection_color = (255, 215, 0)
        self.border_color = (70, 70, 90)
        self.player1_color = (100, 200, 255)
        self.player2_color = (255, 100, 150)
        self.confirmed_color = (100, 255, 100)
        
        # Cargar fuentes
        try:
            self.title_font = pygame.font.Font("assets/fonts/turok.ttf", 48)
            self.scenario_font = pygame.font.Font("assets/fonts/turok.ttf", 24)
            self.instruction_font = pygame.font.Font("assets/fonts/turok.ttf", 16)
        except:
            self.title_font = pygame.font.Font(None, 48)
            self.scenario_font = pygame.font.Font(None, 24)
            self.instruction_font = pygame.font.Font(None, 16)
        
        # Cargar escenarios disponibles
        self.available_scenarios = self.load_scenarios()
        
        # Selecciones actuales de los jugadores
        self.player_1_selection = 0
        self.player_2_selection = 0 if len(self.available_scenarios) > 0 else 0
        self.active_player = 1
        
        # Estados de selección
        self.selection_confirmed = [False, False]
        self.selection_complete = False
        self.selected_scenario = None  # Escenario elegido aleatoriamente
        
        # Animación
        self.animation_time = 0
        self.selection_complete_time = 0  # Tiempo cuando se completa la selección
        self.show_completion_message = False  # Mostrar mensaje de finalización
        self.completion_message_duration = 3000  # Mostrar mensaje por 3 segundos
    
    def load_scenarios(self):
        """
        Carga los escenarios disponibles desde la carpeta de backgrounds.
        
        Returns:
            list: Lista de diccionarios con información de escenarios
        """
        scenarios = []
        background_dir = "assets/images/background"
        
        if os.path.exists(background_dir):
            files = sorted([f for f in os.listdir(background_dir) 
                           if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            
            for i, filename in enumerate(files):
                filepath = os.path.join(background_dir, filename)
                try:
                    image = pygame.image.load(filepath).convert_alpha()
                    # Escalar a tamaño de pantalla
                    image = pygame.transform.scale(image, (self.screen_width, self.screen_height))
                    
                    scenario_name = os.path.splitext(filename)[0].replace('_', ' ').title()
                    scenarios.append({
                        'name': scenario_name,
                        'filename': filename,
                        'image': image,
                        'path': filepath
                    })
                except Exception as e:
                    print(f"Error cargando escenario {filename}: {e}")
        
        return scenarios
    
    def handle_input(self, event):
        """
        Maneja la entrada del usuario para la selección de escenarios.
        
        Args:
            event: Evento de pygame a procesar
            
        Returns:
            bool: True si la selección está completa, False en otro caso
        """
        if event.type != pygame.KEYDOWN:
            return False
        
        if self.selection_complete:
            return True
        
        if len(self.available_scenarios) == 0:
            return False
        
        if self.active_player == 1:
            if event.key == pygame.K_a:  # Anterior
                self.player_1_selection = (self.player_1_selection - 1) % len(self.available_scenarios)
            elif event.key == pygame.K_d:  # Siguiente
                self.player_1_selection = (self.player_1_selection + 1) % len(self.available_scenarios)
            elif event.key == pygame.K_r:  # Confirmar
                self.selection_confirmed[0] = True
                self.active_player = 2
                if self.selection_confirmed[1]:
                    self.finalize_selection()
            elif event.key == pygame.K_ESCAPE and self.selection_confirmed[0]:
                self.selection_confirmed[0] = False
                self.active_player = 1
        
        elif self.active_player == 2:
            if event.key == pygame.K_LEFT:  # Anterior
                self.player_2_selection = (self.player_2_selection - 1) % len(self.available_scenarios)
            elif event.key == pygame.K_RIGHT:  # Siguiente
                self.player_2_selection = (self.player_2_selection + 1) % len(self.available_scenarios)
            elif event.key == pygame.K_KP1:  # Confirmar
                self.selection_confirmed[1] = True
                if self.selection_confirmed[0]:
                    self.finalize_selection()
                else:
                    self.active_player = 1
            elif event.key == pygame.K_ESCAPE and self.selection_confirmed[1]:
                self.selection_confirmed[1] = False
                self.active_player = 2
        
        # Retornar True solo si la selección está completa Y ya se mostró el mensaje
        return self.selection_complete and not self.show_completion_message
    
    def finalize_selection(self):
        """
        Finaliza la selección y elige un escenario aleatoriamente.
        """
        choices = [self.player_1_selection, self.player_2_selection]
        self.selected_scenario = random.choice(choices)
        self.selection_complete = True
        self.selection_complete_time = pygame.time.get_ticks()  # Registrar momento de finalización
        self.show_completion_message = True
    
    def update(self):
        """Actualiza el estado de la pantalla."""
        self.animation_time += 1
        
        # Si la selección está completa, verificar si el mensaje ya se mostró lo suficiente
        if self.selection_complete and self.show_completion_message:
            elapsed_time = pygame.time.get_ticks() - self.selection_complete_time
            if elapsed_time >= self.completion_message_duration:
                self.show_completion_message = False
    
    def get_selected_background(self):
        """
        Obtiene el background seleccionado aleatoriamente.
        
        Returns:
            dict: Información del escenario seleccionado
        """
        if self.selected_scenario is not None and self.selected_scenario < len(self.available_scenarios):
            return self.available_scenarios[self.selected_scenario]
        return None
    
    def draw(self, surface):
        """
        Dibuja la pantalla de selección de escenarios con animaciones.
        
        Args:
            surface: Superficie de pygame donde dibujar
        """
        # Fondo base con gradiente animado (efecto de pulso)
        pulse_intensity = int(20 * abs(math.sin(self.animation_time * 0.01)))
        animated_bg_color = (
            self.background_color[0] + pulse_intensity // 2,
            self.background_color[1] + pulse_intensity // 2,
            self.background_color[2] + pulse_intensity
        )
        surface.fill(animated_bg_color)
        
        # Título con efecto de brillo
        glow_intensity = int(50 + 30 * abs(math.sin(self.animation_time * 0.008)))
        title_color_animated = (
            min(255, self.title_color[0] + glow_intensity // 2),
            min(255, self.title_color[1] + glow_intensity // 3),
            self.title_color[2]
        )
        title_text = self.title_font.render("SELECCIONA UN ESCENARIO", True, title_color_animated)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 40))
        
        # Sombra animada del título
        shadow_offset = int(2 + 1 * math.sin(self.animation_time * 0.01))
        title_shadow = self.title_font.render("SELECCIONA UN ESCENARIO", True, (0, 0, 0))
        surface.blit(title_shadow, (title_rect.x + shadow_offset, title_rect.y + shadow_offset))
        surface.blit(title_text, title_rect)
        
        if len(self.available_scenarios) == 0:
            no_scenarios_text = self.scenario_font.render("No hay escenarios disponibles", True, self.text_color)
            no_scenarios_rect = no_scenarios_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            surface.blit(no_scenarios_text, no_scenarios_rect)
            return
        
        # Mostrar previsualizaciones de escenarios
        preview_height = 250
        preview_y = 100
        
        # Preview del Jugador 1 con efecto de escala animada
        p1_preview = self.available_scenarios[self.player_1_selection]['image']
        p1_scale_factor = 1.0 if not self.selection_confirmed[0] else 1.02
        if self.active_player == 1 and not self.selection_confirmed[0]:
            p1_scale_factor = 1.0 + 0.02 * abs(math.sin(self.animation_time * 0.015))
        p1_preview_scaled = pygame.transform.scale(p1_preview, 
                                                   (int(300 * p1_scale_factor), int(preview_height * p1_scale_factor)))
        
        # Dibuja bordes animados alrededor del preview del P1
        p1_border_thickness = 3 if self.selection_confirmed[0] else (
            5 + int(2 * abs(math.sin(self.animation_time * 0.02))) if self.active_player == 1 else 3
        )
        p1_border_color = self.confirmed_color if self.selection_confirmed[0] else (
            self.player1_color if self.active_player == 1 else self.border_color
        )
        p1_border_rect = pygame.Rect(
            50 - int(3 * p1_scale_factor - 3) // 2,
            preview_y - int(3 * p1_scale_factor - 3) // 2,
            300 + int(6 * (p1_scale_factor - 1)),
            preview_height + int(6 * (p1_scale_factor - 1))
        )
        pygame.draw.rect(surface, p1_border_color, p1_border_rect, p1_border_thickness)
        
        # Centrar preview escalado
        p1_blit_x = 50 + (300 - p1_preview_scaled.get_width()) // 2
        p1_blit_y = preview_y + (preview_height - p1_preview_scaled.get_height()) // 2
        surface.blit(p1_preview_scaled, (p1_blit_x, p1_blit_y))
        
        # Información del Jugador 1
        p1_name = self.available_scenarios[self.player_1_selection]['name']
        p1_text = self.scenario_font.render(f"P1: {p1_name}", True, self.player1_color)
        surface.blit(p1_text, (50, preview_y + preview_height + 10))
        
        p1_status = "✓ CONFIRMADO" if self.selection_confirmed[0] else "Seleccionando..."
        p1_status_color = self.confirmed_color if self.selection_confirmed[0] else self.player1_color
        p1_status_text = self.instruction_font.render(p1_status, True, p1_status_color)
        surface.blit(p1_status_text, (50, preview_y + preview_height + 35))
        
        # Preview del Jugador 2 con efecto de escala animada
        p2_preview = self.available_scenarios[self.player_2_selection]['image']
        p2_scale_factor = 1.0 if not self.selection_confirmed[1] else 1.02
        if self.active_player == 2 and not self.selection_confirmed[1]:
            p2_scale_factor = 1.0 + 0.02 * abs(math.sin(self.animation_time * 0.015))
        p2_preview_scaled = pygame.transform.scale(p2_preview,
                                                   (int(300 * p2_scale_factor), int(preview_height * p2_scale_factor)))
        p2_x = self.screen_width - 350
        
        # Dibuja bordes animados alrededor del preview del P2
        p2_border_thickness = 3 if self.selection_confirmed[1] else (
            5 + int(2 * abs(math.sin(self.animation_time * 0.02))) if self.active_player == 2 else 3
        )
        p2_border_color = self.confirmed_color if self.selection_confirmed[1] else (
            self.player2_color if self.active_player == 2 else self.border_color
        )
        p2_border_rect = pygame.Rect(
            p2_x - int(3 * p2_scale_factor - 3) // 2,
            preview_y - int(3 * p2_scale_factor - 3) // 2,
            300 + int(6 * (p2_scale_factor - 1)),
            preview_height + int(6 * (p2_scale_factor - 1))
        )
        pygame.draw.rect(surface, p2_border_color, p2_border_rect, p2_border_thickness)
        
        # Centrar preview escalado
        p2_blit_x = p2_x + (300 - p2_preview_scaled.get_width()) // 2
        p2_blit_y = preview_y + (preview_height - p2_preview_scaled.get_height()) // 2
        surface.blit(p2_preview_scaled, (p2_blit_x, p2_blit_y))
        
        # Información del Jugador 2
        p2_name = self.available_scenarios[self.player_2_selection]['name']
        p2_text = self.scenario_font.render(f"P2: {p2_name}", True, self.player2_color)
        surface.blit(p2_text, (p2_x, preview_y + preview_height + 10))
        
        p2_status = "✓ CONFIRMADO" if self.selection_confirmed[1] else "Seleccionando..."
        p2_status_color = self.confirmed_color if self.selection_confirmed[1] else self.player2_color
        p2_status_text = self.instruction_font.render(p2_status, True, p2_status_color)
        surface.blit(p2_status_text, (p2_x, preview_y + preview_height + 35))
        
        # Controles en la parte inferior
        controls_y = self.screen_height - 100
        
        if not self.selection_confirmed[0]:
            controls_p1 = "P1: A/D - Navegar | R - Confirmar"
            controls_p1_color = self.player1_color if self.active_player == 1 else self.text_color
        else:
            controls_p1 = "P1: ✓ Esperando a P2 (ESC para cambiar)"
            controls_p1_color = self.confirmed_color
        
        controls1_text = self.instruction_font.render(controls_p1, True, controls_p1_color)
        surface.blit(controls1_text, (50, controls_y))
        
        if not self.selection_confirmed[1]:
            controls_p2 = "P2: ◄► - Navegar | 1(KP) - Confirmar"
            controls_p2_color = self.player2_color if self.active_player == 2 else self.text_color
        else:
            controls_p2 = "P2: ✓ Esperando a P1 (ESC para cambiar)"
            controls_p2_color = self.confirmed_color
        
        controls2_text = self.instruction_font.render(controls_p2, True, controls_p2_color)
        surface.blit(controls2_text, (self.screen_width - 500, controls_y))
        
        # Mensaje cuando ambos han confirmado con efecto de pulso
        if self.selection_complete and self.show_completion_message:
            selected_scenario = self.get_selected_background()
            if selected_scenario:
                message = f"Escenario elegido: {selected_scenario['name']}"
            else:
                message = "¡ESCENARIO ELEGIDO ALEATORIAMENTE!"
            
            # Efecto de pulso en el mensaje
            pulse = int(50 + 40 * abs(math.sin(self.animation_time * 0.01)))
            msg_color = (
                min(255, self.selection_color[0] + pulse // 2),
                min(255, self.selection_color[1]),
                self.selection_color[2]
            )
            
            msg_text = self.title_font.render(message, True, msg_color)
            msg_rect = msg_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            
            # Sombra animada
            shadow_offset = int(3 + 2 * math.sin(self.animation_time * 0.015))
            msg_shadow = self.title_font.render(message, True, (0, 0, 0))
            surface.blit(msg_shadow, (msg_rect.x + shadow_offset, msg_rect.y + shadow_offset))
            surface.blit(msg_text, msg_rect)
    
    def reset_selection(self):
        """Reinicia la selección para una nueva ronda."""
        self.selection_confirmed = [False, False]
        self.selection_complete = False
        self.selected_scenario = None
        self.active_player = 1
        self.animation_time = 0
        self.selection_complete_time = 0
        self.show_completion_message = False
