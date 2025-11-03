import pygame
import os
from .base_fighter import Fighter


class WarriorFighter(Fighter):
    """
    Clase específica para el personaje Warrior (Guerrero).
    Hereda de Fighter e implementa carga de sprites y características específicas.
    """
    def __init__(self, player_number, initial_x, initial_y, flip_sprite, attack_sound):
        # Datos específicos del Warrior
        warrior_data = [162, 4, [72, 30]]  # [size, scale, offset]
        
        # Propiedades específicas de ataques del Warrior
        self.attack2_hit_frames = [0, 2, 4, 6]
        self.attack2_final_frame = None

        # Inicializar la clase padre
        super().__init__(player_number, initial_x, initial_y, flip_sprite, warrior_data, attack_sound)
        
        # Características específicas del Warrior
        self.character_name = "Warrior"
        self.max_health = 120  # Más salud que otros personajes
        self.current_health = self.max_health
        
        # Flag para indicar orientación de sprites
        self.sprites_inverted = False
        
    def load_individual_sprites(self):
        """Carga los sprites individuales del Warrior desde sus directorios."""
        base_path = "assets/images/warrior/Sprites"
        animation_directories = [
            "idle",      # 0: idle
            "run",       # 1: run  
            "jump_up",   # 2: jump
            "1_atk",     # 3: attack1
            "2_atk",     # 4: attack2
            "3_atk",     # 5: attack3
            "take_hit",  # 6: hit
            "death"      # 7: death
        ]
        
        animation_list = []
        
        for directory in animation_directories:
            directory_path = os.path.join(base_path, directory)
            frame_list = []
            
            if os.path.exists(directory_path):
                # Obtener todos los archivos PNG en el directorio
                files = [f for f in os.listdir(directory_path) if f.endswith('.png')]
                
                # Ordenar numéricamente
                def extract_number(filename):
                    import re
                    numbers = re.findall(r'\d+', filename)
                    return int(numbers[0]) if numbers else 0
                files.sort(key=extract_number)
                
                for file_name in files:
                    file_path = os.path.join(directory_path, file_name)
                    # Cargar y escalar la imagen
                    sprite_image = pygame.image.load(file_path).convert_alpha()
                    scaled_sprite = pygame.transform.scale(
                        sprite_image, 
                        (self.character_size * self.image_scale, self.character_size * self.image_scale)
                    )
                    frame_list.append(scaled_sprite)
            
            # Si no hay frames, agregar un frame dummy
            if not frame_list:
                dummy_surface = pygame.Surface((self.character_size * self.image_scale, self.character_size * self.image_scale))
                dummy_surface.fill((255, 0, 255))
                frame_list.append(dummy_surface)
                
            animation_list.append(frame_list)
        
        # Calcular el frame final del segundo ataque
        if len(animation_list) > 4:
            self.attack2_final_frame = len(animation_list[4]) - 1
            if self.attack2_final_frame is not None:
                early = 0
                mid = max(1, self.attack2_final_frame // 2)
                late = max(mid+1, (3 * self.attack2_final_frame) // 4)
                self.attack2_hit_frames = sorted(set([early, mid, late]))
        
        return animation_list
    
    def calculate_attack_damage(self):
        """Sobrescribe el cálculo de daño para ataques específicos del Warrior."""
        if self.current_attack_type == 1:
            return 8
        elif self.current_attack_type == 2:
            if self.frame_index in self.attack2_hit_frames:
                return 6
            elif self.frame_index == self.attack2_final_frame:
                return 13
            return 0
        elif self.current_attack_type == 3:
            return 11
        return 8
    
    def check_collision_with_target(self, target):
        """Método personalizado de colisión para el Warrior con múltiples hits y burn effect."""
        if not self.is_attacking or not self.is_alive or not target.is_alive:
            return

        attack_area = self.get_attack_area()
        if attack_area is None:
            return

        if not attack_area.colliderect(target.collision_rect):
            return

        # Control de ventanas de impacto para cada tipo de ataque
        if self.current_attack_type == 1:
            # Un solo impacto por animación
            if self.attack_has_hit:
                return
            damage = self.calculate_attack_damage()
            if damage > 0:
                target.apply_damage(damage)
                target.is_hit = True
                self.attack_has_hit = True

        elif self.current_attack_type == 2:
            # Ataque multi-frame: permitir impactos solo en frames definidos
            if not hasattr(self, 'attack2_frames_hit_record'):
                self.attack2_frames_hit_record = set()
            
            is_damage_frame = (self.frame_index in self.attack2_hit_frames) or (self.frame_index == self.attack2_final_frame)
            if not is_damage_frame:
                return
            
            if self.frame_index in self.attack2_frames_hit_record:
                return
            
            damage = self.calculate_attack_damage()
            if damage > 0:
                target.apply_damage(damage)
                target.is_hit = True
                self.attack2_frames_hit_record.add(self.frame_index)

        # Limpiar registros cuando no está atacando
        if not self.is_attacking:
            if hasattr(self, 'attack2_frames_hit_record'):
                self.attack2_frames_hit_record.clear()

        elif self.current_attack_type == 3:
            # Retrasar impacto hasta segunda mitad de animación + burn effect
            if self.attack_has_hit:
                return
            
            total_frames_attack3 = len(self.animation_list[5]) if len(self.animation_list) > 5 else 0
            half_threshold = total_frames_attack3 // 2
            if self.frame_index < half_threshold:
                return
            
            damage = self.calculate_attack_damage()
            if damage > 0:
                target.apply_damage(damage)
                target.is_hit = True
                # Aplicar efecto de quemadura (5 de daño durante 3 segundos)
                target.apply_burn_effect(5, 180)  # 180 frames = 3 segundos a 60 FPS
                self.attack_has_hit = True

    def get_attack_area(self):
        """Obtiene el área de ataque actual del Warrior."""
        if not self.is_attacking:
            return None
            
        # Área de ataque del Warrior
        attack_width = 4 * self.collision_rect.width
        attack_y = self.collision_rect.y - 20
        attack_height = 550 - attack_y + 20
        
        if self.flip_sprite:
            attack_x = self.collision_rect.centerx - attack_width
        else:
            attack_x = self.collision_rect.centerx
            
        return pygame.Rect(attack_x, attack_y, attack_width, attack_height)
    
    def get_attack_area_for_display(self, attack_type):
        """Obtiene el área de ataque para visualización."""
        # Para el Warrior, todos los ataques usan la misma área
        return self.get_attack_area()