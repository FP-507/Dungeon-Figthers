import pygame
import os
from .base_fighter import Fighter


class TankFighter(Fighter):
    """
    Clase específica para el personaje Tank.
    Tanque resistente con ataques de daño medio pero con gran empuje.
    Movimientos lentos y poca altura de salto, pero muy resistente.
    """
    def __init__(self, player_number, initial_x, initial_y, flip_sprite, attack_sound):
        # Datos específicos del Tank - más pequeño pero robusto
        tank_data = [140, 3.0, [55, 25]]  # [size, scale, offset] - más pequeño que otros
        
        # Inicializar la clase padre
        super().__init__(player_number, initial_x, initial_y, flip_sprite, tank_data, attack_sound)
        
        # Características específicas del Tank
        self.character_name = "Tank"
        self.max_health = 150  # Mucha más salud que otros personajes (tanque resistente)
        self.current_health = self.max_health
        
        # Velocidad muy reducida (tanque lento)
        self.base_movement_speed = 4  # Muy lento comparado con otros (Warrior: 10, Assassin: 14)
        
        # Ajustar hitbox para un personaje más pequeño y compacto
        old_bottom = self.collision_rect.bottom
        self.collision_rect.width = 85   # Ligeramente más ancho para estabilidad
        self.collision_rect.height = 120  # Más bajo - tanque compacto
        self.collision_rect.bottom = old_bottom
        
        # Propiedades específicas de ataques del Tank
        self.heavy_attack_cooldown = 35  # Cooldown más largo para ataques pesados
        self.massive_knockback_force = 160  # Empuje masivo aumentado significativamente
        
        # Propiedades de salto limitado
        self.max_jump_strength = -20  # Salto más bajo que otros (-30 normal)
        
        # Flag para indicar orientación de sprites
        self.sprites_inverted = False
        
    def load_individual_sprites(self):
        """Carga los sprites individuales del Tank desde sus directorios."""
        base_path = "assets/images/tank/Sprites"
        animation_directories = [
            "idle",      # 0: idle
            "run",       # 1: run  
            "j_up",      # 2: jump up
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
                dummy_surface.fill((139, 69, 19))  # Marrón para identificar frames faltantes del Tank
                frame_list.append(dummy_surface)
                print(f"Directorio vacío o no encontrado: {directory_path}")
                
            animation_list.append(frame_list)
        
        return animation_list
    
    def get_movement_speed(self):
        """Retorna la velocidad de movimiento reducida del Tank."""
        return self.base_movement_speed  # Muy lento: 4
    
    def move(self, screen_width, screen_height, surface, target, round_over):
        """Sobrescribe el movimiento para limitar el salto del Tank."""
        # Constantes de movimiento específicas del Tank
        MOVEMENT_SPEED = self.get_movement_speed()  # 4 (muy lento)
        GRAVITY_FORCE = 2
        JUMP_STRENGTH = self.max_jump_strength  # -20 (salto bajo)
        
        # Variables de movimiento para este frame
        horizontal_delta = 0
        vertical_delta = 0
        
        # Resetear estado de correr cada frame
        self.is_running = False
        if not self.is_attacking:
            self.current_attack_type = 0
        
        # Obtener teclas presionadas actualmente
        pressed_keys = pygame.key.get_pressed()
        
        # Solo permitir acciones si no está atacando, está vivo y la ronda no ha terminado
        if not self.is_attacking and self.is_alive and not round_over:
            # Procesamiento de movimiento horizontal (lento)
            if pressed_keys[self.movement_controls['left']]:
                horizontal_delta = -MOVEMENT_SPEED
                self.is_running = True
            if pressed_keys[self.movement_controls['right']]:
                horizontal_delta = MOVEMENT_SPEED
                self.is_running = True
                
            # Procesamiento de salto limitado
            if pressed_keys[self.movement_controls['jump']] and not self.is_jumping:
                self.vertical_velocity = JUMP_STRENGTH  # Salto más bajo
                self.is_jumping = True
                
            # Procesamiento de ataques
            for attack_name, attack_key in self.attack_controls.items():
                if pressed_keys[attack_key]:
                    self.execute_attack(target)
                    if attack_name == 'attack1':
                        self.current_attack_type = 1
                    elif attack_name == 'attack2':
                        self.current_attack_type = 2
                    elif attack_name == 'attack3':
                        self.current_attack_type = 3
                    break
        
        # Aplicar gravedad a la velocidad vertical
        self.vertical_velocity += GRAVITY_FORCE
        vertical_delta += self.vertical_velocity
        
        # Mantener personaje dentro de los límites de pantalla horizontalmente
        if self.collision_rect.left + horizontal_delta < 0:
            horizontal_delta = -self.collision_rect.left
        if self.collision_rect.right + horizontal_delta > screen_width:
            horizontal_delta = screen_width - self.collision_rect.right
            
        # Mantener personaje en el suelo
        ground_level = screen_height - 50
        if self.collision_rect.bottom + vertical_delta > ground_level:
            self.vertical_velocity = 0
            self.is_jumping = False
            vertical_delta = ground_level - self.collision_rect.bottom
        
        # Hacer que los personajes se miren entre sí
        if target.collision_rect.centerx > self.collision_rect.centerx:
            self.flip_sprite = False
        else:
            self.flip_sprite = True
        
        # Procesar efectos de quemadura
        self.process_burn_effect()
        
        # Actualizar posición final del personaje
        self.collision_rect.x += horizontal_delta
        self.collision_rect.y += vertical_delta
    
    def execute_attack(self, target):
        """Ejecuta ataques pesados con cooldown más largo."""
        if self.attack_cooldown_timer == 0:
            self.is_attacking = True
            self.attack_sound_effect.play()
            self.attack_has_hit = False
            self.attack_frame_counter = 0
            self.attack_cooldown_timer = self.heavy_attack_cooldown  # Cooldown más largo
            
            # Limpiar registros de frames golpeados para ataques multi-hit
            if hasattr(self, 'attack_frames_hit_record'):
                self.attack_frames_hit_record.clear()
    
    def calculate_attack_damage(self):
        """Calcula el daño de los ataques del Tank - daño medio pero con empuje."""
        if self.current_attack_type == 1:
            return 9  # Daño medio-alto (sin cambios)
        elif self.current_attack_type == 2:
            return 12  # Daño alto con empuje (reducido de 14)
        elif self.current_attack_type == 3:
            return 15  # Daño muy alto con empuje masivo (reducido de 18)
        return 8  # Daño por defecto
    
    def check_collision_with_target(self, target):
        """Colisión del Tank con gran empuje en todos los ataques."""
        if not self.is_attacking or not self.is_alive or not target.is_alive:
            return

        attack_area = self.get_attack_area()
        if attack_area is None:
            return

        if not attack_area.colliderect(target.collision_rect):
            return

        # Todos los ataques del Tank tienen ventanas de impacto específicas
        if self.current_attack_type == 1:
            # Ataque 1: Impacto en la segunda mitad de la animación
            total_frames = len(self.animation_list[3]) if len(self.animation_list) > 3 else 8
            if self.frame_index >= total_frames // 2 and not self.attack_has_hit:
                damage = self.calculate_attack_damage()
                target.apply_damage(damage)
                target.is_hit = True
                self.attack_has_hit = True
                
                # Empuje medio en ataque 1
                self.apply_knockback(target, 60)

        elif self.current_attack_type == 2:
            # Ataque 2: Impacto al 85% de la animación - más lento que ataque 1
            total_frames = len(self.animation_list[4]) if len(self.animation_list) > 4 else 10
            trigger_frame = (85 * total_frames) // 100  # Más tardío que antes (era 70%)
            
            if self.frame_index >= trigger_frame and not self.attack_has_hit:
                damage = self.calculate_attack_damage()
                target.apply_damage(damage)
                target.is_hit = True
                self.attack_has_hit = True
                
                # Empuje fuerte en ataque 2
                self.apply_knockback(target, 90)

        elif self.current_attack_type == 3:
            # Ataque 3: Impacto al 90% de la animación - el más lento pero más devastador
            total_frames = len(self.animation_list[5]) if len(self.animation_list) > 5 else 12
            trigger_frame = (9 * total_frames) // 10  # Muy tardío para máximo impacto
            
            if self.frame_index >= trigger_frame and not self.attack_has_hit:
                damage = self.calculate_attack_damage()
                target.apply_damage(damage)
                target.is_hit = True
                self.attack_has_hit = True
                
                # Empuje masivo en ataque 3
                self.apply_knockback(target, self.massive_knockback_force)
    
    def apply_knockback(self, target, knockback_force):
        """Aplica empuje masivo al objetivo."""
        if self.flip_sprite:
            # Empujar hacia la izquierda
            target.collision_rect.x -= knockback_force
        else:
            # Empujar hacia la derecha
            target.collision_rect.x += knockback_force
        
        # Asegurar que el enemigo no salga de los límites de pantalla
        if target.collision_rect.left < 0:
            target.collision_rect.left = 0
        elif target.collision_rect.right > 1400:  # SCREEN_WIDTH
            target.collision_rect.right = 1400

    def get_attack_area(self):
        """Área de ataque del Tank - compacta pero efectiva."""
        if not self.is_attacking:
            return None
            
        # Áreas de ataque del Tank reducidas - combate cuerpo a cuerpo
        if self.current_attack_type == 1:
            # Ataque 1: Área frontal compacta
            attack_width = 100  # Reducido significativamente
            attack_height = 130  # Más bajo
        elif self.current_attack_type == 2:
            # Ataque 2: Área aumentada para mejor alcance
            attack_width = 170  # Aumentado de 130
            attack_height = 180  # Aumentado de 150
        elif self.current_attack_type == 3:
            # Ataque 3: Área expandida para ataque final con mayor altura
            attack_width = 200  # Mantener ancho
            attack_height = 240  # Aumentar altura significativamente
        else:
            return None
        
        # Posicionamiento frontal estándar
        attack_y = self.collision_rect.y - 20
        if self.flip_sprite:
            attack_x = self.collision_rect.centerx - attack_width
        else:
            attack_x = self.collision_rect.centerx
            
        return pygame.Rect(attack_x, attack_y, attack_width, attack_height)
    
    def get_attack_area_for_display(self, attack_type):
        """Área de ataque para visualización de hitboxes."""
        # Simular el área de ataque para el tipo especificado
        if attack_type == 1:
            attack_width, attack_height = 100, 130  # Compacto
        elif attack_type == 2:
            attack_width, attack_height = 170, 180  # Aumentado
        elif attack_type == 3:
            attack_width, attack_height = 200, 240  # Expandido con mayor altura
        else:
            return None
        
        # Posicionamiento frontal estándar
        attack_y = self.collision_rect.y - 20
        if self.flip_sprite:
            attack_x = self.collision_rect.centerx - attack_width
        else:
            attack_x = self.collision_rect.centerx
            
        return pygame.Rect(attack_x, attack_y, attack_width, attack_height)
    
    def draw(self, surface, camera_offset_x=0, show_hitboxes=False):
        """Dibujar el Tank con posibles efectos visuales de resistencia."""
        # Dibujar normalmente
        super().draw(surface, camera_offset_x, show_hitboxes)
        
        # Efecto berserker eliminado - sin elementos visuales adicionales