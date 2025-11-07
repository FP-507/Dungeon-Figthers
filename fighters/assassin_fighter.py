import pygame
import os
from .base_fighter import Fighter


class AssassinFighter(Fighter):
    """
    Clase específica para el personaje Assassin.
    Personaje rápido con ataques veloces pero menor daño y salud.
    Se enfoca en velocidad y ataques consecutivos.
    """
    def __init__(self, player_number, initial_x, initial_y, flip_sprite, attack_sound):
        # Datos específicos del Assassin - sprite más grande para compensar hitbox reducida
        assassin_data = [170, 4.2, [65, 30]]  # [size, scale, offset] - sprite aumentado significativamente
        
        # Inicializar la clase padre
        super().__init__(player_number, initial_x, initial_y, flip_sprite, assassin_data, attack_sound)
        
        # Características específicas del Assassin
        self.character_name = "Assassin"
        self.max_health = 80  # Menos salud que otros personajes (frágil pero rápido)
        self.current_health = self.max_health
        
        # Velocidad aumentada significativamente
        self.base_movement_speed = 14  # Mucho más rápido que Warrior (10) y SlimeDemon (6)
        
        # Ajustar hitbox igual al Warrior (80x180)
        old_bottom = self.collision_rect.bottom
        self.collision_rect.width = 80   # Igual que Warrior
        self.collision_rect.height = 180  # Igual que Warrior
        self.collision_rect.bottom = old_bottom
        
        # Propiedades específicas de ataques del Assassin
        self.attack_combo_counter = 0  # Contador para combos
        self.last_attack_time = 0      # Tiempo del último ataque para combos
        self.combo_window = 1000       # Ventana de tiempo para combos (ms)
        
        # Cooldowns reducidos para ataques rápidos
        self.fast_attack_cooldown = 10  # Cooldown reducido (vs 20 normal)
        
        # Sistema de daño distribuido para ataque 3
        self.attack3_hit_frames = []   # Frames en los que se hace daño
        self.attack3_damage_dealt = [] # Frames donde ya se hizo daño
        
        # Flag para indicar orientación de sprites
        self.sprites_inverted = False
        
    def load_individual_sprites(self):
        """Carga los sprites individuales del Assassin desde sus directorios."""
        base_path = "assets/images/assasin/Sprites"  # Nota: mantener el nombre original "assasin"
        animation_directories = [
            "idle",      # 0: idle
            "run",       # 1: run  
            "j_up",      # 2: jump (usar j_up para salto)
            "1_atk",     # 3: attack1
            "2_atk",     # 4: attack2
            "3_atk",     # 5: attack3 (era sp_atk)
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
                
                # Función de ordenamiento para manejar diferentes formatos de nombres
                def extract_number(filename):
                    import re
                    numbers = re.findall(r'\d+', filename)
                    return int(numbers[-1]) if numbers else 0  # Usar el último número encontrado
                
                files.sort(key=extract_number)
                
                for file_name in files:
                    file_path = os.path.join(directory_path, file_name)
                    try:
                        # Cargar y escalar la imagen
                        sprite_image = pygame.image.load(file_path).convert_alpha()
                        scaled_sprite = pygame.transform.scale(
                            sprite_image, 
                            (self.character_size * self.image_scale, self.character_size * self.image_scale)
                        )
                        frame_list.append(scaled_sprite)
                    except Exception as e:
                        print(f"Error cargando {file_path}: {e}")
            
            # Si no hay frames, agregar un frame dummy
            if not frame_list:
                dummy_surface = pygame.Surface((self.character_size * self.image_scale, self.character_size * self.image_scale))
                dummy_surface.fill((128, 0, 128))  # Púrpura para identificar frames faltantes del Assassin
                frame_list.append(dummy_surface)
                print(f"Directorio vacío o no encontrado: {directory_path}")
                
            animation_list.append(frame_list)
        
        return animation_list
    
    def calculate_attack_damage(self):
        """Calcula el daño de los ataques del Assassin - rápidos pero menos daño."""
        if self.current_attack_type == 1:
            return 6  # Ataque rápido básico
        elif self.current_attack_type == 2:
            return 10  # Tornado - hit único con daño moderado
        elif self.current_attack_type == 3:
            return 12  # Ataque especial con más daño pero sigue siendo menor que otros personajes
        return 5  # Daño por defecto
    
    def execute_attack(self, target):
        """Ejecuta ataques rápidos con cooldown reducido."""
        current_time = pygame.time.get_ticks()
        
        # Sistema de combos - si atacas dentro de la ventana de tiempo, cooldown reducido
        if current_time - self.last_attack_time < self.combo_window:
            required_cooldown = self.fast_attack_cooldown
            self.attack_combo_counter += 1
        else:
            required_cooldown = 20  # Cooldown normal si rompiste el combo
            self.attack_combo_counter = 0
        
        if self.attack_cooldown_timer == 0:
            self.is_attacking = True
            self.attack_sound_effect.play()
            self.attack_has_hit = False
            self.attack_frame_counter = 0
            self.attack_cooldown_timer = required_cooldown
            self.last_attack_time = current_time
            
            # Resetear sistema de daño distribuido del ataque 3
            self.attack3_hit_frames = []
            self.attack3_damage_dealt = []
            
            # Limpiar registros de frames golpeados para ataques multi-hit
            if hasattr(self, 'attack_frames_hit_record'):
                self.attack_frames_hit_record.clear()
    
    def check_collision_with_target(self, target):
        """Colisión optimizada para ataques rápidos del Assassin."""
        if not self.is_attacking or not self.is_alive or not target.is_alive:
            return

        attack_area = self.get_attack_area()
        if attack_area is None:
            return

        if not attack_area.colliderect(target.collision_rect):
            return

        # Ataques rápidos con diferentes ventanas de impacto
        if self.current_attack_type == 1:
            # Ataque 1: Impacto rápido en la primera mitad
            total_frames = len(self.animation_list[3]) if len(self.animation_list) > 3 else 4
            if self.frame_index >= total_frames // 3 and not self.attack_has_hit:
                damage = self.calculate_attack_damage()
                target.apply_damage(damage)
                target.is_hit = True
                self.attack_has_hit = True

        elif self.current_attack_type == 2:
            # Ataque 2: Lanzamiento de tornado - hit único con empuje
            total_frames = len(self.animation_list[4]) if len(self.animation_list) > 4 else 15
            # El tornado se lanza aproximadamente en el 60% de la animación
            tornado_launch_frame = (3 * total_frames) // 5
            
            if self.frame_index == tornado_launch_frame and not self.attack_has_hit:
                damage = self.calculate_attack_damage()
                target.apply_damage(damage)
                target.is_hit = True
                self.attack_has_hit = True
                
                # Empujar al enemigo con fuerza masiva del tornado
                push_force = 80  # Fuerza del empuje aumentada significativamente (era 25)
                if self.flip_sprite:
                    # Empujar hacia la izquierda
                    target.collision_rect.x -= push_force
                else:
                    # Empujar hacia la derecha
                    target.collision_rect.x += push_force
                
                # Asegurar que el enemigo no salga de los límites de pantalla
                if target.collision_rect.left < 0:
                    target.collision_rect.left = 0
                elif target.collision_rect.right > 1400:  # SCREEN_WIDTH
                    target.collision_rect.right = 1400

        elif self.current_attack_type == 3:
            # Ataque 3: Ultimate con daño distribuido en múltiples frames
            total_frames = len(self.animation_list[5]) if len(self.animation_list) > 5 else 10
            
            # Definir frames de daño distribuido (40%, 60%, 80% de la animación)
            if not self.attack3_hit_frames:
                self.attack3_hit_frames = [
                    (2 * total_frames) // 5,  # 40% - primer golpe
                    (3 * total_frames) // 5,  # 60% - segundo golpe  
                    (4 * total_frames) // 5   # 80% - golpe final
                ]
                self.attack3_damage_dealt = []
            
            # Verificar si estamos en un frame de daño
            for i, damage_frame in enumerate(self.attack3_hit_frames):
                if self.frame_index == damage_frame and i not in self.attack3_damage_dealt:
                    # Daño aumentado y distribuido: 8 por golpe (total 24, era 12)
                    damage = 8
                    target.apply_damage(damage)
                    target.is_hit = True
                    self.attack3_damage_dealt.append(i)
                    
                    # Aplicar sangrado solo en el último golpe
                    if i == len(self.attack3_hit_frames) - 1:
                        target.apply_burn_effect(4, 150)  # 4 de daño durante 2.5 segundos
                    
                    break

    def get_attack_area(self):
        """Área de ataque del Assassin - más pequeña pero precisa."""
        if not self.is_attacking:
            return None
            
        # Áreas de ataque ajustadas
        if self.current_attack_type == 1:
            # Ataque 1: Área que llega hasta el suelo
            attack_width = 160  # Mantener ancho
            attack_height = 370  # Altura desde personaje hasta suelo (550 - 180 = 370)
        elif self.current_attack_type == 2:
            # Ataque 2: Tornado con alcance masivo
            attack_width = 280  # +60 píxeles
            attack_height = 240  # +60 píxeles
        elif self.current_attack_type == 3:
            # Ataque 3: Área gigantesca que domina la pantalla
            attack_width = 450  # +100 píxeles
            attack_height = 380  # +80 píxeles
        else:
            return None
        
        if self.current_attack_type == 1:
            # Ataque 1: Posicionar desde el personaje hasta el suelo
            attack_y = self.collision_rect.y  # Desde la parte superior del personaje
            if self.flip_sprite:
                attack_x = self.collision_rect.centerx - attack_width
            else:
                attack_x = self.collision_rect.centerx
        elif self.current_attack_type == 3:
            # Ataque 3: Centrar el área gigantesca en el personaje
            attack_y = self.collision_rect.y - 80  # Más arriba para cobertura total
            attack_x = self.collision_rect.centerx - (attack_width // 2)  # Centrado
        else:
            # Ataque 2: Posicionamiento frontal mejorado
            attack_y = self.collision_rect.y - 30  # Más arriba que antes
            if self.flip_sprite:
                attack_x = self.collision_rect.centerx - attack_width
            else:
                attack_x = self.collision_rect.centerx
            
        return pygame.Rect(attack_x, attack_y, attack_width, attack_height)
    
    def get_attack_area_for_display(self, attack_type):
        """Área de ataque para visualización de hitboxes."""
        # Simular el área de ataque para el tipo especificado
        if attack_type == 1:
            attack_width, attack_height = 160, 370  # Área que llega hasta el suelo
        elif attack_type == 2:
            attack_width, attack_height = 280, 240  # Tornado masivo
        elif attack_type == 3:
            attack_width, attack_height = 450, 380  # Área gigantesca
        else:
            return None
        
        if attack_type == 1:
            # Ataque 1: Posicionar desde el personaje hasta el suelo
            attack_y = self.collision_rect.y  # Desde la parte superior del personaje
            if self.flip_sprite:
                attack_x = self.collision_rect.centerx - attack_width
            else:
                attack_x = self.collision_rect.centerx
        elif attack_type == 3:
            # Ataque 3: Centrar el área gigantesca en el personaje
            attack_y = self.collision_rect.y - 80  # Más arriba para cobertura total
            attack_x = self.collision_rect.centerx - (attack_width // 2)  # Centrado
        else:
            # Ataque 2: Posicionamiento frontal mejorado
            attack_y = self.collision_rect.y - 30  # Más arriba que antes
            if self.flip_sprite:
                attack_x = self.collision_rect.centerx - attack_width
            else:
                attack_x = self.collision_rect.centerx
            
        return pygame.Rect(attack_x, attack_y, attack_width, attack_height)
    
    def update(self, target=None):
        """Update personalizado para manejar la velocidad aumentada del Assassin."""
        # Usar el update base pero con animaciones más rápidas
        super().update(target)
        
        # Decrementar combo counter si pasa mucho tiempo sin atacar
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.combo_window:
            self.attack_combo_counter = 0
    
    def draw(self, surface, camera_offset_x=0, show_hitboxes=False):
        """Dibujar el Assassin con posibles efectos visuales de velocidad."""
        # Dibujar normalmente
        super().draw(surface, camera_offset_x, show_hitboxes)
        
        # Opcional: Efecto visual cuando está en combo
        if self.attack_combo_counter > 2:
            # Efecto de resplandor sutil durante combos largos
            glow_surface = pygame.Surface((self.collision_rect.width + 20, self.collision_rect.height + 20), pygame.SRCALPHA)
            glow_color = (150, 0, 150, 30)  # Púrpura semi-transparente
            pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect())
            glow_rect = glow_surface.get_rect(center=(self.collision_rect.centerx + camera_offset_x, self.collision_rect.centery))
            surface.blit(glow_surface, glow_rect, special_flags=pygame.BLEND_ADD)