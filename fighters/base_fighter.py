import pygame
import os
import random


class BaseProjectile:
    """
    Clase base para proyectiles que pueden ser usados por cualquier fighter.
    Proporciona funcionalidad común como movimiento, animación y colisión.
    """
    def __init__(self, x, y, velocity_x, velocity_y, damage, frames=None, target=None):
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.damage = damage
        self.target = target
        self.width = 20
        self.height = 20
        
        # Sistema de animación
        self.frames = frames or []
        self.current_frame_index = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.animation_speed = 100  # ms entre frames
        
        # Estados
        self.is_alive = True
        self.has_hit = False
        
    def rect(self):
        """Retorna el rectángulo de colisión del proyectil."""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        
    def update(self, ground_level=550):
        """Actualiza la posición y estado del proyectil."""
        if not self.is_alive:
            return
            
        # Actualizar posición
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Aplicar gravedad si es necesario (subclases pueden sobrescribir)
        self.apply_physics()
        
        # Verificar colisiones
        self.check_collisions(ground_level)
        
        # Actualizar animación
        self.update_animation()
        
    def apply_physics(self):
        """Aplica física básica (gravedad). Subclases pueden sobrescribir."""
        # Por defecto, no hay gravedad
        pass
        
    def check_collisions(self, ground_level):
        """Verifica colisiones con suelo y objetivo."""
        # Colisión con suelo
        if self.y + self.height >= ground_level:
            self.on_ground_hit()
            
        # Colisión con objetivo
        if self.target and self.rect().colliderect(self.target.collision_rect):
            self.on_target_hit()
            
    def on_ground_hit(self):
        """Llamado cuando el proyectil toca el suelo."""
        self.is_alive = False
        
    def on_target_hit(self):
        """Llamado cuando el proyectil toca el objetivo."""
        if not self.has_hit:
            self.target.apply_damage(self.damage)
            self.target.is_hit = True
            self.has_hit = True
            self.is_alive = False
            
    def update_animation(self):
        """Actualiza la animación del proyectil."""
        if not self.frames or len(self.frames) <= 1:
            return
            
        now = pygame.time.get_ticks()
        if now - self.last_frame_time >= self.animation_speed:
            self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
            self.last_frame_time = now
            
    def get_current_frame(self):
        """Retorna el frame actual para dibujar."""
        if not self.frames:
            return None
        return pygame.transform.scale(self.frames[self.current_frame_index], (self.width, self.height))
        

class Fighter:
    """
    Clase padre Fighter que define la funcionalidad base para todos los personajes luchadores.
    Esta clase maneja movimiento, animaciones, ataques básicos y física del juego.
    Las clases hijas implementarán personajes específicos con sus propias características.
    """
    def __init__(self, player_number, initial_x, initial_y, flip_sprite, character_data, attack_sound):
        # Propiedades básicas del jugador
        self.player_number = player_number  # Número del jugador (1 o 2)
        self.character_size = character_data[0]  # Tamaño base del sprite
        self.image_scale = character_data[1]  # Factor de escalado de la imagen
        self.sprite_offset = character_data[2]  # Offset para posicionamiento correcto del sprite
        self.flip_sprite = flip_sprite  # Si el sprite debe estar volteado horizontalmente
        
        # Sistema de animaciones - ahora carga sprites individuales frame por frame
        self.animation_list = self.load_individual_sprites()
        self.current_action = 0  # 0:idle, 1:run, 2:jump, 3:attack1, 4:attack2, 5:attack3, 6:hit, 7:death
        self.frame_index = 0  # Índice del frame actual en la animación
        self.current_image = self.animation_list[self.current_action][self.frame_index]
        self.last_update_time = pygame.time.get_ticks()  # Tiempo de la última actualización de animación
        
        # Propiedades físicas y de colisión
        self.collision_rect = pygame.Rect((initial_x, initial_y, 80, 180))  # Rectángulo de colisión
        self.vertical_velocity = 0  # Velocidad vertical para saltos y gravedad
        
        # Ajustar posición inicial para que esté exactamente en el suelo
        ground_level = 550  # Nivel del suelo estándar
        self.collision_rect.bottom = ground_level  # Forzar que el bottom toque el suelo
        
        # Estados del personaje
        self.is_running = False  # Si el personaje está corriendo
        self.is_jumping = False  # Si el personaje está saltando
        self.is_attacking = False  # Si el personaje está atacando
        self.current_attack_type = 0  # Tipo de ataque actual (1, 2, o 3)
        self.attack_cooldown_timer = 0  # Temporizador de cooldown entre ataques
        self.attack_sound_effect = attack_sound  # Efecto de sonido para ataques
        self.is_hit = False  # Si el personaje fue golpeado
        
        # Sistema de salud (centralizado)
        self.max_health = 100  # Salud máxima base para todos los personajes
        self.damage_taken = 0   # Daño acumulado total recibido
        self.current_health = self.max_health  # Salud derivada
        self.is_alive = True  # Si el personaje está vivo
        self.death_animation_done = False  # Flag para saber si terminó animación de muerte
        
        # Sistema de efectos de estado
        self.burn_damage_remaining = 0  # Daño de quemadura pendiente
        self.burn_timer = 0  # Tiempo de quemadura restante (en frames)
        self.burn_interval = 60  # Frames entre aplicaciones de daño de quemadura
        self.burn_counter = 0  # Contador interno para el intervalo de quemadura
        
        # Sistema de sangrado (bleeding)
        self.bleeding_damage_remaining = 0  # Daño de sangrado pendiente
        self.bleeding_timer = 0  # Tiempo de sangrado restante (en frames)
        self.bleeding_interval = 45  # Frames entre aplicaciones de daño de sangrado (más rápido que burn)
        self.bleeding_counter = 0  # Contador interno para el intervalo de sangrado
        
        # Sistema avanzado de ataques
        self.attack_frame_counter = 0  # Contador de frames para ataques complejos
        self.attack_has_hit = False  # Para evitar múltiples golpes en un ataque
        
        # Sistema de proyectiles
        self.active_projectiles = []  # Lista de proyectiles activos
        
        # Velocidad base
        self.base_movement_speed = 10
        
        # Controles específicos del personaje
        self.movement_controls = {}
        self.attack_controls = {}
        self.setup_controls()

    def create_projectile(self, projectile_class, x, y, velocity_x, velocity_y, damage, **kwargs):
        """
        Crea un proyectil y lo añade a la lista de proyectiles activos.
        
        Args:
            projectile_class: Clase del proyectil a crear
            x, y: Posición inicial
            velocity_x, velocity_y: Velocidad del proyectil
            damage: Daño que causa el proyectil
            **kwargs: Argumentos adicionales específicos del proyectil
        """
        projectile = projectile_class(x, y, velocity_x, velocity_y, damage, **kwargs)
        self.active_projectiles.append(projectile)
        return projectile
        
    def update_projectiles(self, ground_level=550):
        """Actualiza todos los proyectiles activos."""
        remaining_projectiles = []
        for projectile in self.active_projectiles:
            projectile.update(ground_level)
            if projectile.is_alive:
                remaining_projectiles.append(projectile)
        self.active_projectiles = remaining_projectiles
        
    def draw_projectiles(self, surface, camera_offset_x=0):
        """Dibuja todos los proyectiles activos."""
        for projectile in self.active_projectiles:
            frame = projectile.get_current_frame()
            if frame:
                draw_x = int(projectile.x) + camera_offset_x
                draw_y = int(projectile.y)
                surface.blit(frame, (draw_x, draw_y))
            # Eliminado el fallback de círculo blanco

    def load_individual_sprites(self):
        """
        Carga sprites individuales frame por frame desde directorios separados.
        Debe ser implementado por las clases hijas según su estructura de assets.
        """
        pass
    
    def setup_controls(self):
        """Configura los controles específicos para cada jugador."""
        if self.player_number == 1:
            # Controles para el jugador 1 (WASD + R, T, Y)
            self.movement_controls = {
                'left': pygame.K_a,
                'right': pygame.K_d,
                'jump': pygame.K_w
            }
            self.attack_controls = {
                'attack1': pygame.K_r,
                'attack2': pygame.K_t,
                'attack3': pygame.K_y
            }
        elif self.player_number == 2:
            # Controles para el jugador 2 (Flechas + 1, 2, 3 del teclado numérico)
            self.movement_controls = {
                'left': pygame.K_LEFT,
                'right': pygame.K_RIGHT,
                'jump': pygame.K_UP
            }
            self.attack_controls = {
                'attack1': pygame.K_KP1,
                'attack2': pygame.K_KP2,
                'attack3': pygame.K_KP3
            }

    def apply_damage(self, damage):
        """Aplica daño al personaje de manera centralizada."""
        if damage <= 0 or not self.is_alive:
            return
        self.damage_taken += damage
        self.current_health = max(self.max_health - self.damage_taken, 0)
        if self.current_health <= 0:
            self.is_alive = False

    def apply_burn_effect(self, burn_damage, burn_duration_frames):
        """Aplica un efecto de quemadura gradual."""
        self.burn_damage_remaining = burn_damage
        self.burn_timer = burn_duration_frames
        self.burn_counter = 0
    
    def apply_bleeding_effect(self, bleeding_damage, bleeding_duration_frames):
        """Aplica un efecto de sangrado gradual."""
        self.bleeding_damage_remaining = bleeding_damage
        self.bleeding_timer = bleeding_duration_frames
        self.bleeding_counter = 0

    def get_movement_speed(self):
        """Retorna la velocidad de movimiento actual."""
        return self.base_movement_speed

    def move(self, screen_width, screen_height, surface, target, round_over):
        """Maneja el movimiento del personaje, incluyendo controles, física y colisiones."""
        # Constantes de movimiento y física
        MOVEMENT_SPEED = self.get_movement_speed()
        GRAVITY_FORCE = 2
        JUMP_STRENGTH = -30
        
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
            # Procesamiento de movimiento horizontal
            if pressed_keys[self.movement_controls['left']]:
                horizontal_delta = -MOVEMENT_SPEED
                self.is_running = True
            if pressed_keys[self.movement_controls['right']]:
                horizontal_delta = MOVEMENT_SPEED
                self.is_running = True
                
            # Procesamiento de salto
            if pressed_keys[self.movement_controls['jump']] and not self.is_jumping:
                self.vertical_velocity = JUMP_STRENGTH
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
        
        # Procesar efectos de quemadura y sangrado
        self.process_burn_effect()
        self.process_bleeding_effect()
        
        # Actualizar posición final del personaje
        self.collision_rect.x += horizontal_delta
        self.collision_rect.y += vertical_delta

    def update(self, target=None):
        """Actualiza las animaciones y estados del personaje cada frame."""
        # Determinar qué acción debe estar realizando el personaje
        self.current_health = max(self.max_health - self.damage_taken, 0)

        if self.current_health <= 0:
            self.current_health = 0
            self.is_alive = False
            self.update_current_action(7)  # 7: animación de muerte
        elif self.is_hit:
            self.update_current_action(6)  # 6: animación de ser golpeado
        elif self.is_attacking:
            if self.current_attack_type == 1:
                self.update_current_action(3)  # 3: primer ataque
            elif self.current_attack_type == 2:
                self.update_current_action(4)  # 4: segundo ataque
            elif self.current_attack_type == 3:
                self.update_current_action(5)  # 5: tercer ataque
            self.attack_frame_counter += 1
        elif self.is_jumping:
            self.update_current_action(2)  # 2: animación de salto
        elif self.is_running:
            self.update_current_action(1)  # 1: animación de correr
        else:
            self.update_current_action(0)  # 0: animación idle
        
        # Lógica de actualización de animación
        animation_frame_duration = 50
        self.current_image = self.animation_list[self.current_action][self.frame_index]
        
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time > animation_frame_duration:
            self.frame_index += 1
            self.last_update_time = current_time
            
            if self.is_attacking and target:
                self.check_collision_with_target(target)
            
        # Verificar si la animación ha completado todos sus frames
        if self.frame_index >= len(self.animation_list[self.current_action]):
            if not self.is_alive:
                self.frame_index = len(self.animation_list[self.current_action]) - 1
                self.death_animation_done = True
            else:
                self.frame_index = 0
                
                if self.current_action in [3, 4, 5]:  # Cualquiera de los 3 ataques
                    self.is_attacking = False
                    self.attack_cooldown_timer = 20
                    self.attack_has_hit = False
                    self.attack_frame_counter = 0
                    
                if self.current_action == 6:
                    self.is_hit = False
                    self.is_attacking = False
                    self.attack_cooldown_timer = 20

        # Decrementar el cooldown de ataque
        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= 1

        # Actualizar proyectiles
        self.update_projectiles()
        
        # Hook para clases hijas
        if hasattr(self, 'post_update_hook'):
            self.post_update_hook(target)

    def execute_attack(self, target):
        """Ejecuta un ataque contra el objetivo si no hay cooldown activo."""
        if self.attack_cooldown_timer == 0:
            self.is_attacking = True
            self.attack_sound_effect.play()
            self.attack_has_hit = False
            self.attack_frame_counter = 0
            if hasattr(self, 'attack2_frames_hit_record'):
                self.attack2_frames_hit_record.clear()

    def process_burn_effect(self):
        """Procesa los efectos de quemadura aplicados al personaje."""
        if self.burn_timer > 0:
            self.burn_counter += 1
            
            if self.burn_counter >= self.burn_interval:
                damage_per_interval = max(1, self.burn_damage_remaining // (self.burn_timer // self.burn_interval)) if self.burn_timer >= self.burn_interval else self.burn_damage_remaining
                
                if damage_per_interval > 0:
                    self.apply_damage(damage_per_interval)
                    self.burn_damage_remaining -= damage_per_interval
                
                self.burn_counter = 0
                
            self.burn_timer -= 1
            
            if self.burn_timer <= 0 or self.burn_damage_remaining <= 0:
                self.burn_timer = 0
                self.burn_damage_remaining = 0
    
    def process_bleeding_effect(self):
        """Procesa los efectos de sangrado aplicados al personaje."""
        if self.bleeding_timer > 0:
            self.bleeding_counter += 1
            
            if self.bleeding_counter >= self.bleeding_interval:
                damage_per_interval = max(1, self.bleeding_damage_remaining // (self.bleeding_timer // self.bleeding_interval)) if self.bleeding_timer >= self.bleeding_interval else self.bleeding_damage_remaining
                
                if damage_per_interval > 0:
                    self.apply_damage(damage_per_interval)
                    self.bleeding_damage_remaining -= damage_per_interval
                
                self.bleeding_counter = 0
                
            self.bleeding_timer -= 1
            
            if self.bleeding_timer <= 0 or self.bleeding_damage_remaining <= 0:
                self.bleeding_timer = 0
                self.bleeding_damage_remaining = 0
                self.burn_counter = 0

    def update_current_action(self, new_action):
        """Actualiza la acción actual del personaje si es diferente a la anterior."""
        if new_action != self.current_action:
            self.current_action = new_action
            self.frame_index = 0
            self.last_update_time = pygame.time.get_ticks()

    def draw(self, surface, camera_offset_x=0):
        """Dibuja el personaje en la superficie especificada."""
        actual_flip = self.flip_sprite
        if hasattr(self, 'sprites_inverted') and self.sprites_inverted:
            actual_flip = not self.flip_sprite
        
        final_image = pygame.transform.flip(self.current_image, actual_flip, False)
        
        sprite_width = self.current_image.get_width()
        sprite_height = self.current_image.get_height()
        
        draw_x = self.collision_rect.centerx - (sprite_width // 2) + camera_offset_x
        draw_y = self.collision_rect.bottom - sprite_height + 20
        
        surface.blit(final_image, (draw_x, draw_y))
        
        # Dibujar proyectiles
        self.draw_projectiles(surface, camera_offset_x)

    def draw_hitbox(self, surface, show_attack_area=False, camera_offset_x=0):
        """Dibuja la hitbox del personaje y opcionalmente el área de ataque."""
        # Dibujar hitbox del personaje
        adjusted_rect = pygame.Rect(
            self.collision_rect.x + camera_offset_x,
            self.collision_rect.y,
            self.collision_rect.width,
            self.collision_rect.height
        )
        pygame.draw.rect(surface, (0, 255, 0), adjusted_rect, 2)
        
        # Dibujar área de ataque si está atacando
        if show_attack_area and self.is_attacking:
            attack_area = self.get_attack_area_for_display(self.current_attack_type)
            if attack_area:
                adjusted_attack_area = pygame.Rect(
                    attack_area.x + camera_offset_x,
                    attack_area.y,
                    attack_area.width,
                    attack_area.height
                )
                pygame.draw.rect(surface, (255, 0, 0), adjusted_attack_area, 2)

    # Métodos que deben ser implementados por las clases hijas
    def get_attack_area(self):
        """Retorna el área de ataque actual. Debe ser implementado por clases hijas."""
        return None
        
    def get_attack_area_for_display(self, attack_type):
        """Retorna el área de ataque para visualización. Debe ser implementado por clases hijas."""
        return None
        
    def calculate_attack_damage(self):
        """Calcula el daño del ataque actual. Debe ser implementado por clases hijas."""
        return 10
        
    def check_collision_with_target(self, target):
        """Verifica colisión con el objetivo. Puede ser sobrescrito por clases hijas."""
        attack_area = self.get_attack_area()
        if attack_area is None:
            return
            
        if not attack_area.colliderect(target.collision_rect):
            return
            
        if self.attack_has_hit:
            return
            
        damage = self.calculate_attack_damage()
        if damage > 0:
            target.apply_damage(damage)
            target.is_hit = True
            self.attack_has_hit = True