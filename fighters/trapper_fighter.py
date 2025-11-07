import pygame
import os
import random
from .base_fighter import Fighter, BaseProjectile


class TrapperFighter(Fighter):
    """
    Clase específica para el personaje Trapper.
    Personaje ágil que coloca trampas en el suelo, ataca a distancia
    y tiene alta movilidad tanto en tierra como en aire.
    Diseñado para ser molesto y elusivo.
    """
    
    class TrapProjectile(BaseProjectile):
        """Entidad única que representa una trampa - se lanza, se coloca y espera a ser pisada."""
        def __init__(self, x, y, damage, target, trap_sprite, land_sprites, detonate_sprites):
            super().__init__(x, y, 0, 0, damage, None, target)  # Velocidad 0 - las trampas no se mueven
            self.trap_active_time = 10000  # 10 segundos activa
            self.creation_time = pygame.time.get_ticks()
            self.trap_triggered = False
            self.detection_radius = 50  # Radio de detección ajustado para sprites más grandes
            self.width = 60
            self.height = 30
            
            # Sprites de la trampa
            self.trap_sprite = trap_sprite  # Sprite cuando está colocada
            self.land_sprites = land_sprites  # Animación de aterrizaje
            self.detonate_sprites = detonate_sprites  # Animación de detonación
            
            # Estados: landing -> landed -> detonating -> dead
            self.trap_state = "landing"
            self.animation_frame = 0
            self.animation_speed = 6
            self.frame_counter = 0
            self.detonation_started = False
            
        def update(self, ground_level=550):
            """Actualizar la trampa según su estado."""
            current_time = pygame.time.get_ticks()
            
            # Controlar animación
            self.frame_counter += 1
            if self.frame_counter >= self.animation_speed:
                self.frame_counter = 0
                self.animation_frame += 1
            
            if self.trap_state == "landing":
                # Animación de aterrizaje
                if self.animation_frame >= len(self.land_sprites):
                    self.trap_state = "landed"
                    self.animation_frame = 0
                    
            elif self.trap_state == "landed":
                # Expirar después del tiempo límite
                if current_time - self.creation_time > self.trap_active_time:
                    self.is_alive = False
                    return
                
                # Detectar si el enemigo pisa la trampa
                if self.target and not self.trap_triggered:
                    # Verificar si el enemigo está directamente sobre la trampa
                    enemy_bottom = self.target.collision_rect.bottom
                    enemy_center_x = self.target.collision_rect.centerx
                    
                    trap_center_x = self.x + self.width // 2
                    trap_top = self.y
                    
                    # Distancia horizontal y verificar que esté en el suelo
                    horizontal_distance = abs(enemy_center_x - trap_center_x)
                    on_ground = abs(enemy_bottom - ground_level) < 10
                    
                    if horizontal_distance <= self.detection_radius and on_ground:
                        self.trigger_trap()
                        
            elif self.trap_state == "detonating":
                # Animación de detonación
                if self.animation_frame >= len(self.detonate_sprites):
                    self.is_alive = False
        
        def trigger_trap(self):
            """Activa la trampa cuando es pisada."""
            if not self.trap_triggered and self.target:
                self.trap_triggered = True
                self.trap_state = "detonating"
                self.animation_frame = 0
                
                # Aplicar daño medio y stunear al enemigo
                self.target.apply_damage(self.damage)
                self.target.is_hit = True
                
                # Stun: hacer que el enemigo se quede en animación de hit más tiempo
                if hasattr(self.target, 'hit_cooldown_timer'):
                    self.target.hit_cooldown_timer = 45  # Stun por 45 frames (0.75 segundos)
        
        def get_current_sprite(self):
            """Obtiene el sprite actual de la trampa."""
            if self.trap_state == "landing":
                frame_index = min(self.animation_frame, len(self.land_sprites) - 1)
                return self.land_sprites[frame_index]
            elif self.trap_state == "landed":
                return self.trap_sprite
            elif self.trap_state == "detonating":
                frame_index = min(self.animation_frame, len(self.detonate_sprites) - 1)
                return self.detonate_sprites[frame_index]
            return self.trap_sprite
        
        def get_attack_area(self):
            """Área de ataque cuando la trampa detona - igual al tamaño del sprite."""
            if self.trap_state == "detonating":
                sprite = self.get_current_sprite()
                if sprite:
                    sprite_rect = sprite.get_rect()
                    # Posicionar la detonación a nivel del suelo (ground_level = 550)
                    ground_level = 550
                    return pygame.Rect(self.x - sprite_rect.width // 2, 
                                     ground_level - sprite_rect.height,  # Alineado al suelo
                                     sprite_rect.width, 
                                     sprite_rect.height)
            return None
    
    class RangedProjectile(BaseProjectile):
        """Entidad única que representa un proyectil - va en línea recta hasta golpear al enemigo o salir de pantalla."""
        def __init__(self, x, y, velocity_x, velocity_y, damage, target, projectile_sprite, land_sprites):
            super().__init__(x, y, velocity_x, velocity_y, damage, None, target)
            self.width = 30
            self.height = 30
            self.projectile_sprite = projectile_sprite
            self.land_sprites = land_sprites
            self.has_hit_target = False
            self.projectile_state = "flying"  # flying -> landing -> dead
            self.animation_frame = 0
            self.animation_speed = 8
            self.frame_counter = 0
            
            # Calcular ángulo de rotación basado en la dirección
            import math
            self.rotation_angle = math.degrees(math.atan2(velocity_y, velocity_x))
            
            # Crear sprite rotado una vez al inicializar
            if self.projectile_sprite:
                self.rotated_sprite = pygame.transform.rotate(self.projectile_sprite, -self.rotation_angle)
            else:
                self.rotated_sprite = None
            
            # Crear sprites de aterrizaje rotados
            self.rotated_land_sprites = []
            if self.land_sprites:
                for land_sprite in self.land_sprites:
                    rotated_land = pygame.transform.rotate(land_sprite, -self.rotation_angle)
                    self.rotated_land_sprites.append(rotated_land)
            
        def update(self, ground_level=550):
            """Actualizar proyectil - vuela en línea recta hasta golpear o salir de pantalla."""
            # Mover el proyectil
            self.x += self.velocity_x
            self.y += self.velocity_y
            
            # Verificar colisión con el objetivo
            if self.target and not self.has_hit_target:
                projectile_rect = pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)
                if projectile_rect.colliderect(self.target.collision_rect):
                    self.hit_target()
                    return
            
            # Verificar si sale de pantalla (aproximadamente)
            if (self.x < -100 or self.x > 1500 or self.y < -100 or self.y > ground_level + 100):
                self.is_alive = False
                return
            
            # Si ha tocado el suelo sin golpear al enemigo
            if self.y >= ground_level - 10 and self.projectile_state == "flying":
                self.projectile_state = "landing"
                self.animation_frame = 0
                self.velocity_x = 0
                self.velocity_y = 0
            
            # Animar aterrizaje en el suelo
            if self.projectile_state == "landing":
                self.frame_counter += 1
                if self.frame_counter >= self.animation_speed:
                    self.frame_counter = 0
                    self.animation_frame += 1
                    
                if self.animation_frame >= len(self.land_sprites):
                    self.is_alive = False
        
        def hit_target(self):
            """El proyectil golpea al objetivo."""
            if not self.has_hit_target:
                self.has_hit_target = True
                self.target.apply_damage(self.damage)
                self.target.is_hit = True
                
                # Iniciar animación de impacto
                self.projectile_state = "landing"
                self.animation_frame = 0
                self.velocity_x = 0
                self.velocity_y = 0
                
                # El proyectil desaparecerá después de la animación de impacto
        
        def get_current_sprite(self):
            """Obtiene el sprite actual del proyectil."""
            if self.projectile_state == "flying":
                # Retornar el sprite rotado hacia el enemigo
                return self.rotated_sprite if self.rotated_sprite else self.projectile_sprite
            elif self.projectile_state == "landing":
                # Usar sprites de aterrizaje rotados según la dirección
                if self.rotated_land_sprites:
                    frame_index = min(self.animation_frame, len(self.rotated_land_sprites) - 1)
                    return self.rotated_land_sprites[frame_index]
                else:
                    # Fallback a sprites normales si no hay rotados
                    frame_index = min(self.animation_frame, len(self.land_sprites) - 1)
                    return self.land_sprites[frame_index]
            return self.rotated_sprite if self.rotated_sprite else self.projectile_sprite

    def __init__(self, player_number, initial_x, initial_y, flip_sprite, attack_sound):
        # Datos específicos del Trapper - ágil y elusivo
        trapper_data = [130, 3.5, [55, 25]]  # [size, scale, offset] - compacto y ágil
        
        # Inicializar la clase padre
        super().__init__(player_number, initial_x, initial_y, flip_sprite, trapper_data, attack_sound)
        
        # Características específicas del Trapper
        self.character_name = "Trapper"
        self.max_health = 70  # Muy frágil - menor que Assassin
        self.current_health = self.max_health
        
        # Velocidad muy alta - el más rápido del juego
        self.base_movement_speed = 16  # Más rápido que Assassin (14)
        
        # Ajustar hitbox para un personaje muy ágil y pequeño
        old_bottom = self.collision_rect.bottom
        self.collision_rect.width = 65   # Pequeño y difícil de golpear
        self.collision_rect.height = 160  # Altura moderada
        self.collision_rect.bottom = old_bottom
        
        # Propiedades de salto mejorado para alta movilidad aérea
        self.enhanced_jump_strength = -35  # Salto más alto que normal (-30)
        self.air_mobility_bonus = True     # Mejor control en el aire
        
        # Propiedades específicas de ataques del Trapper
        self.trap_cooldown = 120           # Cooldown para colocar trampas (2 segundos)
        self.last_trap_time = 0           # Tiempo de la última trampa colocada
        self.active_traps = []            # Lista de trampas activas
        self.max_traps = 3                # Máximo 3 trampas simultáneas
        
        # Propiedades de ataques a distancia
        self.ranged_attack_cooldown = 25   # Cooldown para ataques a distancia
        self.projectile_speed = 12         # Velocidad de proyectiles
        
        # Flag para indicar orientación de sprites
        self.sprites_inverted = False
    
    def load_individual_sprites(self):
        """Carga los sprites individuales del Trapper desde sus directorios."""
        base_path = "assets/images/trapper/Sprites"
        animation_directories = [
            "01_idle",      # 0: idle
            "02_run",       # 1: run  
            "03_jump_up",   # 2: jump
            "1_atk",        # 3: attack1 - ataque rápido
            "2_atk",        # 4: attack2 - colocar trampa
            "3_atk",        # 5: attack3 - proyectil a distancia
            "12_take_hit",  # 6: hit
            "13_death"      # 7: death
        ]
        
        animation_list = []
        
        for directory in animation_directories:
            directory_path = os.path.join(base_path, directory)
            frame_list = []
            
            if os.path.exists(directory_path):
                # Obtener todos los archivos PNG en el directorio (solo los principales)
                files = [f for f in os.listdir(directory_path) if f.endswith('.png') and not os.path.isdir(os.path.join(directory_path, f))]
                
                # Función de ordenamiento para manejar diferentes formatos de nombres
                def extract_number(filename):
                    import re
                    numbers = re.findall(r'\d+', filename)
                    return int(numbers[-1]) if numbers else 0
                
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
                dummy_surface.fill((0, 128, 0))  # Verde para identificar frames faltantes del Trapper
                frame_list.append(dummy_surface)
                print(f"Directorio vacío o no encontrado: {directory_path}")
                
            animation_list.append(frame_list)
        
        # Cargar sprites especiales de trampas y proyectiles
        self.load_trap_and_projectile_sprites()
        
        return animation_list
    
    def load_trap_and_projectile_sprites(self):
        """Carga los sprites especiales para trampas y proyectiles."""
        base_path = "assets/images/trapper/Sprites"
        
        # Cargar sprites de trampas (ataque 2)
        trap_path = os.path.join(base_path, "2_atk")
        
        # Sprite de trampa colocada
        self.trap_sprite = None
        trap_throw_path = os.path.join(trap_path, "trap_throw", "trap_throw.png")
        if os.path.exists(trap_throw_path):
            self.trap_sprite = pygame.image.load(trap_throw_path).convert_alpha()
        
        # Sprites de aterrizaje de trampa
        self.trap_land_sprites = []
        trap_land_path = os.path.join(trap_path, "trap_land")
        if os.path.exists(trap_land_path):
            files = [f for f in os.listdir(trap_land_path) if f.endswith('.png')]
            files.sort(key=lambda x: int(''.join(filter(str.isdigit, x))) if any(c.isdigit() for c in x) else 0)
            for file_name in files:
                self.trap_land_sprites.append(pygame.image.load(os.path.join(trap_land_path, file_name)).convert_alpha())
        
        # Sprites de detonación de trampa
        self.trap_detonate_sprites = []
        trap_detonate_path = os.path.join(trap_path, "trap_detonate")
        if os.path.exists(trap_detonate_path):
            files = [f for f in os.listdir(trap_detonate_path) if f.endswith('.png')]
            files.sort(key=lambda x: int(''.join(filter(str.isdigit, x))) if any(c.isdigit() for c in x) else 0)
            for file_name in files:
                self.trap_detonate_sprites.append(pygame.image.load(os.path.join(trap_detonate_path, file_name)).convert_alpha())
        
        # Cargar sprites de proyectiles (ataque 3)
        projectile_path = os.path.join(base_path, "3_atk")
        
        # Sprite de proyectil volando
        self.projectile_sprite = None
        projectile_throw_path = os.path.join(projectile_path, "projectile_throw", "projectile_throw.png")
        if os.path.exists(projectile_throw_path):
            self.projectile_sprite = pygame.image.load(projectile_throw_path).convert_alpha()
        
        # Sprites de aterrizaje de proyectil
        self.projectile_land_sprites = []
        projectile_land_path = os.path.join(projectile_path, "projectile_land")
        if os.path.exists(projectile_land_path):
            files = [f for f in os.listdir(projectile_land_path) if f.endswith('.png')]
            files.sort(key=lambda x: int(''.join(filter(str.isdigit, x))) if any(c.isdigit() for c in x) else 0)
            for file_name in files:
                self.projectile_land_sprites.append(pygame.image.load(os.path.join(projectile_land_path, file_name)).convert_alpha())
    
    def get_movement_speed(self):
        """Retorna la velocidad de movimiento muy alta del Trapper."""
        return self.base_movement_speed  # Muy rápido: 16
    
    def move(self, screen_width, screen_height, surface, target, round_over):
        """Sobrescribe el movimiento para mejor movilidad aérea del Trapper."""
        # Constantes de movimiento específicas del Trapper
        MOVEMENT_SPEED = self.get_movement_speed()  # 16 (muy rápido)
        GRAVITY_FORCE = 2
        JUMP_STRENGTH = self.enhanced_jump_strength  # -35 (salto alto)
        
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
            # Procesamiento de movimiento horizontal (muy rápido)
            if pressed_keys[self.movement_controls['left']]:
                horizontal_delta = -MOVEMENT_SPEED
                self.is_running = True
            if pressed_keys[self.movement_controls['right']]:
                horizontal_delta = MOVEMENT_SPEED
                self.is_running = True
                
            # Procesamiento de salto mejorado
            if pressed_keys[self.movement_controls['jump']] and not self.is_jumping:
                self.vertical_velocity = JUMP_STRENGTH  # Salto más alto
                self.is_jumping = True
                
            # Procesamiento de ataques
            for attack_name, attack_key in self.attack_controls.items():
                if pressed_keys[attack_key]:
                    self.execute_attack(target)
                    if attack_name == 'attack1':
                        self.current_attack_type = 1  # Ataque cuerpo a cuerpo
                    elif attack_name == 'attack2':
                        self.current_attack_type = 2  # Colocar trampa
                    elif attack_name == 'attack3':
                        self.current_attack_type = 3  # Proyectil a distancia
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
        """Ejecuta ataques especializados del Trapper."""
        if self.attack_cooldown_timer == 0:
            self.is_attacking = True
            self.attack_sound_effect.play()
            self.attack_has_hit = False
            self.attack_frame_counter = 0
            
            # Cooldown variable según el tipo de ataque
            if self.current_attack_type == 1:
                self.attack_cooldown_timer = self.trap_cooldown  # Trampa tiene cooldown largo
            else:
                self.attack_cooldown_timer = self.ranged_attack_cooldown  # Ataques a distancia más rápidos
            
            # Limpiar registros de frames golpeados
            if hasattr(self, 'attack_frames_hit_record'):
                self.attack_frames_hit_record.clear()
    
    def calculate_attack_damage(self):
        """Calcula el daño de los ataques del Trapper."""
        if self.current_attack_type == 1:
            return 5   # Ataque cuerpo a cuerpo - daño moderado + sangrado
        elif self.current_attack_type == 2:
            return 8   # Trampa - daño medio + stun
        elif self.current_attack_type == 3:
            return 4   # Proyectil - daño bajo
        return 4  # Daño por defecto
    
    def check_collision_with_target(self, target):
        """Colisión especializada del Trapper con mecánicas únicas."""
        if not self.is_attacking or not self.is_alive or not target.is_alive:
            return

        if self.current_attack_type == 1:
            # Ataque 1: Ataque cuerpo a cuerpo rápido con sangrado
            total_frames = len(self.animation_list[3]) if len(self.animation_list) > 3 else 6
            trigger_frame = total_frames // 2
            
            if self.frame_index == trigger_frame and not self.attack_has_hit:
                # Ataque tradicional de contacto
                attack_area = self.get_attack_area()
                if attack_area and attack_area.colliderect(target.collision_rect):
                    target.apply_damage(self.calculate_attack_damage())
                    target.is_hit = True
                    # Aplicar efecto de sangrado
                    target.apply_bleeding_effect(6, 240)  # 6 de daño total durante 4 segundos
                    self.attack_has_hit = True

        elif self.current_attack_type == 2:
            # Ataque 2: Colocar trampa en el suelo
            total_frames = len(self.animation_list[4]) if len(self.animation_list) > 4 else 10
            trigger_frame = (3 * total_frames) // 5
            
            if self.frame_index == trigger_frame and not self.attack_has_hit:
                self.place_trap()
                self.attack_has_hit = True

        elif self.current_attack_type == 3:
            # Ataque 3: Proyectil a distancia
            total_frames = len(self.animation_list[5]) if len(self.animation_list) > 5 else 7
            trigger_frame = (2 * total_frames) // 3
            
            if self.frame_index == trigger_frame and not self.attack_has_hit:
                self.fire_ranged_projectile(target)
                self.attack_has_hit = True
    
    def place_trap(self):
        """Coloca una trampa en el suelo."""
        current_time = pygame.time.get_ticks()
        
        # Verificar cooldown de trampas
        if current_time - self.last_trap_time < self.trap_cooldown:
            return
        
        # Remover trampas viejas si se excede el máximo
        if len(self.active_traps) >= self.max_traps:
            oldest_trap = self.active_traps.pop(0)
            if oldest_trap in self.active_projectiles:
                self.active_projectiles.remove(oldest_trap)
        
        # Posición de la trampa (en frente del personaje)
        trap_x = self.collision_rect.centerx + (50 if not self.flip_sprite else -50)
        trap_y = 535  # En el suelo
        
        # Crear trampa con sprites individuales
        trap = self.TrapProjectile(trap_x, trap_y, self.calculate_attack_damage(), self.last_target, 
                                 self.trap_sprite, self.trap_land_sprites, self.trap_detonate_sprites)
        self.active_traps.append(trap)
        self.active_projectiles.append(trap)
        self.last_trap_time = current_time
    
    def fire_ranged_projectile(self, target, spread_angle=0):
        """Dispara un proyectil a distancia hacia el objetivo."""
        # Calcular dirección hacia el objetivo
        target_x = target.collision_rect.centerx
        target_y = target.collision_rect.centery
        start_x = self.collision_rect.centerx
        start_y = self.collision_rect.centery - 20  # Disparar desde un poco más arriba
        
        # Calcular vector direccional - línea recta hacia el enemigo
        dx = target_x - start_x
        dy = target_y - start_y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        if distance > 0:
            # Normalizar y aplicar velocidad (línea recta, sin gravedad)
            vel_x = (dx / distance) * self.projectile_speed
            vel_y = (dy / distance) * self.projectile_speed
            
            # Crear proyectil con sprites individuales
            projectile = self.RangedProjectile(start_x, start_y, vel_x, vel_y, 
                                             self.calculate_attack_damage(), target, 
                                             self.projectile_sprite, self.projectile_land_sprites)
            self.active_projectiles.append(projectile)
    
    def update(self, target=None):
        """Update personalizado para manejar las mecánicas especiales del Trapper."""
        # Guardar referencia del objetivo para las trampas
        if target:
            self.last_target = target
        
        # Usar el update base
        super().update(target)
        
        # Actualizar trampas activas
        self.active_traps = [trap for trap in self.active_traps if trap.is_alive]
    
    def get_attack_area(self):
        """Retorna el área de ataque según el tipo de ataque actual."""
        if self.current_attack_type == 1:
            # Ataque 1: Ataque cuerpo a cuerpo rápido
            attack_width = 80
            attack_height = 60
            
            if self.flip_sprite:
                # Mirando hacia la izquierda
                attack_x = self.collision_rect.centerx - attack_width - 10
            else:
                # Mirando hacia la derecha
                attack_x = self.collision_rect.centerx + 10
            
            attack_y = self.collision_rect.centery - attack_height // 2
            return pygame.Rect(attack_x, attack_y, attack_width, attack_height)
        
        # Los demás ataques usan proyectiles, no áreas de colisión tradicionales
        return None
    
    def get_attack_area_for_display(self, attack_type):
        """Para visualización, mostrar áreas de ataques."""
        if attack_type == 1:  # Ataque cuerpo a cuerpo
            return self.get_attack_area()
        elif attack_type == 2:  # Área de colocación de trampas
            trap_x = self.collision_rect.centerx + (50 if not self.flip_sprite else -100)
            trap_y = self.collision_rect.bottom - 40
            return pygame.Rect(trap_x, trap_y, 50, 40)
        return None  # Ataque 3 (proyectil) no tiene área fija
    
    def draw(self, surface, camera_offset_x=0, show_hitboxes=False):
        """Dibujar el Trapper sin efectos visuales adicionales."""
        # Dibujar normalmente
        super().draw(surface, camera_offset_x, show_hitboxes)
        
        # Dibujar trampas activas usando sus sprites individuales - MÁS GRANDES
        for trap in self.active_traps:
            if trap.is_alive:
                trap_sprite = trap.get_current_sprite()
                if trap_sprite:
                    # Hacer las trampas bastante más grandes
                    sprite_rect = trap_sprite.get_rect()
                    scale_factor = 2.5  # Mucho más grande para mejor visibilidad
                    scaled_width = int(sprite_rect.width * scale_factor)
                    scaled_height = int(sprite_rect.height * scale_factor)
                    scaled_trap = pygame.transform.scale(trap_sprite, (scaled_width, scaled_height))
                    
                    # Ajustar posición según el estado de la trampa
                    if trap.trap_state == "detonating":
                        # La detonación debe estar a nivel del suelo (ground_level = 550)
                        ground_level = 550
                        trap_rect = scaled_trap.get_rect()
                        trap_rect.centerx = trap.x + trap.width // 2 + camera_offset_x
                        trap_rect.bottom = ground_level  # Alineado al suelo
                    else:
                        # Trampas normales centradas en su posición
                        trap_rect = scaled_trap.get_rect(center=(trap.x + trap.width // 2 + camera_offset_x, trap.y + trap.height // 2))
                    
                    surface.blit(scaled_trap, trap_rect)
        
        # Dibujar proyectiles activos usando sus sprites individuales - MÁS GRANDES
        for projectile in self.active_projectiles:
            if (projectile.is_alive and hasattr(projectile, 'get_current_sprite') and 
                not hasattr(projectile, 'trap_state')):  # Solo proyectiles, no trampas
                projectile_sprite = projectile.get_current_sprite()
                if projectile_sprite:
                    # Hacer los proyectiles bastante más grandes
                    sprite_rect = projectile_sprite.get_rect()
                    scale_factor = 2.0  # Más grande para mejor visibilidad
                    scaled_width = int(sprite_rect.width * scale_factor)
                    scaled_height = int(sprite_rect.height * scale_factor)
                    scaled_projectile = pygame.transform.scale(projectile_sprite, (scaled_width, scaled_height))
                    
                    # Centrar en la posición del proyectil
                    proj_rect = scaled_projectile.get_rect(center=(projectile.x + camera_offset_x, projectile.y))
                    surface.blit(scaled_projectile, proj_rect)