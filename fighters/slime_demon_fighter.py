import pygame
import os
import random
from .base_fighter import Fighter


class SlimeDemonFighter(Fighter):
    """
    Clase específica para el personaje Slime Demon.
    Hereda de Fighter e implementa carga de sprites y características específicas.
    NOTA: Los sprites del Slime Demon pueden estar orientados en dirección opuesta,
    por lo que sobrescribimos la lógica de flip.
    """
    
    class LavaDropProjectile:
        """Pequeña gota de lava que usa frames de attack2 para animación.
        - Mientras cae: usa los primeros 2 frames de attack2 alternando
        - Cuando explota: usa los frames restantes de attack2 rápidamente
        """
        def __init__(self, x, y, fall_speed, damage, target_rect, fall_frames=None, explosion_frames=None):
            self.x = x
            self.y = y
            self.fall_speed = fall_speed
            self.damage = damage
            self.target_rect = target_rect
            self.width = 20
            self.height = 20
            self.phase = 'fall'
            # Frames de animación para el PROYECTIL (no el personaje)
            self.fall_frames = fall_frames or []
            self.explosion_frames = explosion_frames or []
            self.current_frame_index = 0
            self.last_frame_time = pygame.time.get_ticks()
            self.fall_anim_speed = 150  # ms entre frames mientras cae
            self.explosion_anim_speed = 50  # ms entre frames durante explosión
            # Estados de explosión
            self.explosion_rect = None
            self.explosion_finished = False
            self.damage_applied = False

        def rect(self):
            return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

        def update(self, ground_level, target):
            if self.phase == 'fall':
                self.y += self.fall_speed
                self._update_fall_animation()
                r = self.rect()
                # Impacto con enemigo
                if r.colliderect(target.collision_rect):
                    self._enter_explosion()
                    self._apply_damage_if_inside(target)
                # Impacto con suelo
                elif self.y + self.height >= ground_level:
                    self._enter_explosion()
                    self._apply_damage_if_inside(target)
            elif self.phase == 'explosion':
                self._update_explosion_animation()

        def _update_fall_animation(self):
            """Anima el proyectil alternando entre los primeros 2 frames de attack2."""
            if not self.fall_frames or len(self.fall_frames) < 2:
                return
            now = pygame.time.get_ticks()
            if now - self.last_frame_time >= self.fall_anim_speed:
                self.current_frame_index = (self.current_frame_index + 1) % len(self.fall_frames)
                self.last_frame_time = now

        def _update_explosion_animation(self):
            """Reproduce rápidamente los frames de explosión."""
            if not self.explosion_frames:
                self.explosion_finished = True
                return
            now = pygame.time.get_ticks()
            if now - self.last_frame_time >= self.explosion_anim_speed:
                self.current_frame_index += 1
                if self.current_frame_index >= len(self.explosion_frames):
                    self.explosion_finished = True
                else:
                    self.last_frame_time = now

        def _enter_explosion(self):
            if self.phase == 'explosion':
                return
            self.phase = 'explosion'
            self.current_frame_index = 0  # Começar desde el primer frame de explosión
            self.last_frame_time = pygame.time.get_ticks()
            # Área de explosión
            size = 60
            ex = int(self.x + self.width/2 - size/2)
            ey = int(self.y + self.height/2 - size/2)
            self.explosion_rect = pygame.Rect(ex, ey, size, size)

        def _apply_damage_if_inside(self, target):
            if not self.damage_applied and self.explosion_rect and self.explosion_rect.colliderect(target.collision_rect):
                target.apply_damage(self.damage)
                target.is_hit = True
                self.damage_applied = True

        def get_current_frame(self):
            """Retorna el frame actual del proyectil según su fase."""
            if self.phase == 'fall' and self.fall_frames:
                frame = self.fall_frames[self.current_frame_index % len(self.fall_frames)]
                # Escalar a tamaño pequeño para proyectil
                return pygame.transform.scale(frame, (self.width, self.height))
            elif self.phase == 'explosion' and self.explosion_frames and self.current_frame_index < len(self.explosion_frames):
                frame = self.explosion_frames[self.current_frame_index]
                # Escalar a tamaño de explosión más grande y centrar en la posición del proyectil
                explosion_size = 60  # Mismo tamaño que el área de daño
                return pygame.transform.scale(frame, (explosion_size, explosion_size))
            return None

        def is_alive(self):
            return not (self.phase == 'explosion' and self.explosion_finished)

    def __init__(self, player_number, initial_x, initial_y, flip_sprite, attack_sound):
        # Slime Demon con tamaño más moderado
        slime_demon_data = [150, 3.2, [65, 40]]  # [size, scale, offset] - reducido considerablemente

        # Inicializar la clase padre
        super().__init__(player_number, initial_x, initial_y, flip_sprite, slime_demon_data, attack_sound)

        # Características específicas del Slime Demon
        self.character_name = "Slime Demon"
        self.max_health = 100  # Salud estándar
        self.current_health = self.max_health
        
        # Flag para indicar que este personaje tiene sprites invertidos
        self.sprites_inverted = True

        # Ajustar velocidad reducida
        self.base_movement_speed = 6  # Notoriamente menor que 10 del Warrior

        # Ajustar hitbox para tamaño más moderado
        old_bottom = self.collision_rect.bottom
        self.collision_rect.width = 90   # Reducido de 110
        self.collision_rect.height = 190  # Reducido de 220
        self.collision_rect.bottom = old_bottom

        # Sistema de proyectiles para ataque 2 (lluvia)
        self.active_projectiles = []
        self.attack2_projectiles_spawned = False

        # Flags para explosión de ataque 3 (auto-sacrificio)
        self.attack3_explosion_triggered = False

    def spawn_attack2_projectiles(self, target):
        """Genera de 1 a 3 pequeñas gotas de lava que usan frames de attack2."""
        if self.attack2_projectiles_spawned:
            return
        count = random.randint(1, 3)
        # Obtener frames de attack2 para los PROYECTILES
        attack2_frames = self.animation_list[4] if len(self.animation_list) > 4 else []
        fall_frames = attack2_frames[:2] if len(attack2_frames) >= 2 else []
        explosion_frames = attack2_frames[2:] if len(attack2_frames) > 2 else []
        
        for i in range(count):
            # Reducir el rango de offset para asegurar que los proyectiles sean visibles
            offset = random.randint(-100, 100)
            spawn_x = max(50, min(1350, target.collision_rect.centerx + offset))
            spawn_y = 50
            fall_speed = random.uniform(7, 11)
            proj = self.LavaDropProjectile(
                spawn_x, spawn_y, 
                fall_speed=fall_speed, 
                damage=4, 
                target_rect=target.collision_rect,
                fall_frames=fall_frames, 
                explosion_frames=explosion_frames
            )
            self.active_projectiles.append(proj)
        
        self.attack2_projectiles_spawned = True

    def process_projectiles(self, target):
        """Actualiza todos los proyectiles activos."""
        ground_level = 550
        remaining = []
        for proj in self.active_projectiles:
            proj.update(ground_level, target)
            if proj.is_alive():
                remaining.append(proj)
        self.active_projectiles = remaining

    def trigger_attack3_explosion(self, target):
        """Explosión sacrificando mitad de vida actual para infligir igual daño al enemigo."""
        if self.attack3_explosion_triggered:
            return
        current_effective_health = self.current_health
        if current_effective_health <= 0:
            return
        sacrifice = current_effective_health // 2
        if sacrifice <= 0:
            return
        
        # Aplicar daño a sí mismo (sacrificio)
        self.apply_damage(sacrifice)
        
        # Definir área de explosión grande alrededor del Slime Demon
        explosion_width = 520
        explosion_height = 360
        explosion_x = self.collision_rect.centerx - explosion_width // 2
        explosion_y = self.collision_rect.bottom - explosion_height
        explosion_rect = pygame.Rect(explosion_x, explosion_y, explosion_width, explosion_height)
        
        if explosion_rect.colliderect(target.collision_rect) and target.is_alive:
            target.apply_damage(sacrifice)
            target.is_hit = True
        
        self.attack3_explosion_triggered = True
        self.attack3_explosion_rect = explosion_rect

    def update(self, target=None):
        """Actualización personalizada para SlimeDemon que mantiene idle durante attack2."""
        # Recalcular salud derivada en cada update
        self.current_health = max(self.max_health - self.damage_taken, 0)

        if self.current_health <= 0:
            self.current_health = 0
            self.is_alive = False
            self.update_current_action(7)  # 7: animación de muerte
        elif self.is_hit:
            self.update_current_action(6)  # 6: animación de ser golpeado
        elif self.is_attacking:
            # PERSONALIZACIÓN: Durante attack2, mantener idle para evitar frames de attack2
            if self.current_attack_type == 1:
                self.update_current_action(3)  # 3: primer ataque
            elif self.current_attack_type == 2:
                self.update_current_action(0)  # 0: idle (NO attack2)
                # Para attack2, terminar después de cierta cantidad de frames
                attack2_duration = len(self.animation_list[4]) if len(self.animation_list) > 4 else 5
                if self.attack_frame_counter >= attack2_duration:
                    self.is_attacking = False
                    self.attack_cooldown_timer = 20
                    self.attack_has_hit = False
                    self.attack2_projectiles_spawned = False
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
        
        # Actualizar la imagen actual del personaje
        self.current_image = self.animation_list[self.current_action][self.frame_index]
        
        # Verificar si es tiempo de avanzar al siguiente frame de animación
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time > animation_frame_duration:
            self.frame_index += 1
            self.last_update_time = current_time
            
            # Si está atacando y tenemos un target, verificar colisión en cada frame
            if self.is_attacking and target:
                self.check_collision_with_target(target)
            
        # Verificar si la animación ha completado todos sus frames
        if self.frame_index >= len(self.animation_list[self.current_action]):
            if not self.is_alive:
                # Si está muerto, mantener en el último frame de muerte
                self.frame_index = len(self.animation_list[self.current_action]) - 1
                self.death_animation_done = True
            else:
                # Reiniciar animación para acciones repetitivas
                self.frame_index = 0
                
                # Manejar fin de animaciones específicas
                if self.current_action in [3, 5]:  # Solo ataques 1 y 3 (no 2)
                    self.is_attacking = False
                    self.attack_cooldown_timer = 20
                    self.attack_has_hit = False
                    
                if self.current_action == 6:  # Animación de recibir daño
                    self.is_hit = False
                    self.is_attacking = False
                    self.attack_cooldown_timer = 20
        
        # Decrementar el cooldown de ataque
        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= 1
            
        # Procesar efectos de quemadura
        self.process_burn_effect()
            
        # Llamar hook personalizado
        self.post_update_hook(target)

    def post_update_hook(self, target):
        """Hook llamado tras update base para manejar comportamientos especiales."""
        if not self.is_alive:
            return
        
        # Siempre procesar proyectiles activos sin importar estado de ataque
        if self.active_projectiles:
            self.process_projectiles(target)
        
        # Spawn proyectiles al inicio del segundo ataque
        if self.is_attacking and self.current_attack_type == 2 and self.frame_index == 0:
            self.spawn_attack2_projectiles(target)
        
        # Ataque 3: explosión al alcanzar último tercio de la animación
        if self.is_attacking and self.current_attack_type == 3:
            total_frames_atk3 = len(self.animation_list[5]) if len(self.animation_list) > 5 else 0
            trigger_threshold = (2 * total_frames_atk3) // 3
            if self.frame_index >= trigger_threshold:
                self.trigger_attack3_explosion(target)
        else:
            if not self.is_attacking:
                self.attack3_explosion_triggered = False
                self.attack3_explosion_rect = None

    def calculate_attack_damage(self):
        """Daños específicos del Slime Demon rework."""
        if self.current_attack_type == 1:
            # Aplicar daño sólo segunda mitad para simular carga lenta
            total_frames_atk1 = len(self.animation_list[3]) if len(self.animation_list) > 3 else 0
            if total_frames_atk1 and self.frame_index >= total_frames_atk1 // 2 and not self.attack_has_hit:
                return 14  # Un poco más que el ataque 3 del Warrior
            return 0
        # Ataque 2 y 3 gestionan su daño externamente
        return 0

    def check_collision_with_target(self, target):
        """Sobrescribe colisión para ataque 1 (pesado). Ataques 2 y 3 gestionan daño externamente."""
        if not self.is_attacking or not self.is_alive or not target.is_alive:
            return
        if self.current_attack_type != 1:
            return  # Otros ataques no aplican daño por contacto directo
        
        attack_area = self.get_attack_area()
        if attack_area is None or not attack_area.colliderect(target.collision_rect):
            return
        if self.attack_has_hit:
            return
        
        dmg = self.calculate_attack_damage()
        if dmg > 0:
            target.apply_damage(dmg)
            target.is_hit = True
            self.attack_has_hit = True

    def get_attack_area(self):
        """Área de ataque personalizada."""
        if not self.is_attacking:
            return None
        if self.current_attack_type == 1:
            width = 300
            attack_y = self.collision_rect.y - 60
            attack_height = 550 - attack_y + 20
            if self.flip_sprite:
                attack_x = self.collision_rect.centerx - width
            else:
                attack_x = self.collision_rect.centerx
            return pygame.Rect(attack_x, attack_y, width, attack_height)
        return None

    def get_attack_area_for_display(self, attack_type):
        """Para visualización, mostrar área del ataque 1 únicamente."""
        if attack_type == 1:
            return self.get_attack_area()
        return None

    def draw(self, surface, camera_offset_x=0):
        """Dibuja el Slime Demon y sus proyectiles independientes."""
        # Durante attack2, mostrar idle en lugar de la animación de attack2
        if self.is_attacking and self.current_attack_type == 2:
            # Crear imagen temporal de idle para dibujar sin modificar current_image
            temp_image = None
            
            # Calcular frame de idle basado en el tiempo para mantener animación fluida
            if len(self.animation_list) > 0 and len(self.animation_list[0]) > 0:
                idle_frames = len(self.animation_list[0])
                # Usar el tiempo para determinar el frame actual de idle
                current_time = pygame.time.get_ticks()
                animation_frame_duration = 200  # Animación más lenta para idle
                idle_frame_index = (current_time // animation_frame_duration) % idle_frames
                temp_image = self.animation_list[0][idle_frame_index]
            
            # Dibujar manualmente el frame de idle
            if temp_image:
                # Manejar sprites invertidos
                actual_flip = self.flip_sprite
                if hasattr(self, 'sprites_inverted') and self.sprites_inverted:
                    actual_flip = not self.flip_sprite
                
                # Voltear la imagen horizontalmente si es necesario
                final_image = pygame.transform.flip(temp_image, actual_flip, False)
                
                # Centrar el sprite en la hitbox automáticamente
                sprite_width = temp_image.get_width()
                sprite_height = temp_image.get_height()
                
                # Centrar horizontalmente el sprite en la hitbox
                draw_x = self.collision_rect.centerx - (sprite_width // 2) + camera_offset_x
                
                # Alinear verticalmente
                draw_y = self.collision_rect.bottom - sprite_height + 20
                
                surface.blit(final_image, (draw_x, draw_y))
        else:
            # Dibujar normalmente para todos los otros ataques
            super().draw(surface, camera_offset_x)
        
        # Dibujar proyectiles usando sus propios frames de animación
        for proj in self.active_projectiles:
            frame = proj.get_current_frame()
            if frame:
                if proj.phase == 'explosion':
                    # Para explosión, centrar el frame en la posición del proyectil
                    draw_x = int(proj.x) - frame.get_width()//2 + camera_offset_x
                    draw_y = int(proj.y) - frame.get_height()//2
                else:
                    # Para caída, dibujar el frame normalmente
                    draw_x = int(proj.x) + camera_offset_x
                    draw_y = int(proj.y)
                surface.blit(frame, (draw_x, draw_y))
            # Eliminado el fallback de círculo naranja
        
        # Opcional: dibujar contorno de explosión del ataque 3
        if self.attack3_explosion_triggered and self.is_attacking and self.current_attack_type == 3:
            if hasattr(self, 'attack3_explosion_rect') and self.attack3_explosion_rect:
                r = self.attack3_explosion_rect
                pygame.draw.rect(surface, (255, 140, 0), pygame.Rect(r.x + camera_offset_x, r.y, r.width, r.height), 3)
        
    def load_individual_sprites(self):
        """Carga los sprites individuales del Slime Demon desde sus directorios."""
        base_path = "assets/images/slime_demon/Sprites"
        animation_directories = [
            "idle",      # 0: idle
            "run",       # 1: run  
            "idle",      # 2: jump (reutilizamos idle ya que no hay jump específico)
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
            print(f"Cargando sprites de: {directory_path}")
            
            if os.path.exists(directory_path):
                # Obtener todos los archivos PNG en el directorio
                files = [f for f in os.listdir(directory_path) if f.endswith('.png')]
                
                # Límite de seguridad para evitar cargar demasiados archivos
                if len(files) > 50:
                    print(f"Advertencia: Demasiados archivos en {directory}: {len(files)}, limitando a 50")
                    files = files[:50]
                
                # Ordenar numéricamente
                def extract_number(filename):
                    import re
                    numbers = re.findall(r'\d+', filename)
                    return int(numbers[0]) if numbers else 0
                files.sort(key=extract_number)
                
                for file_name in files:
                    file_path = os.path.join(directory_path, file_name)
                    try:
                        # Cargar imagen original
                        sprite_image = pygame.image.load(file_path).convert_alpha()
                        
                        # Validar dimensiones de escalado
                        final_size = int(self.character_size * self.image_scale)
                        if final_size > 1000:  # Límite de seguridad
                            print(f"Advertencia: Tamaño muy grande para {file_name}: {final_size}px")
                            final_size = 500  # Reducir a tamaño seguro
                        
                        # Escalar la imagen
                        scaled_sprite = pygame.transform.scale(sprite_image, (final_size, final_size))
                        frame_list.append(scaled_sprite)
                        
                    except Exception as e:
                        print(f"Error cargando {file_path}: {e}")
                        continue
            
            # Si no hay frames, agregar un frame dummy
            if not frame_list:
                dummy_surface = pygame.Surface((self.character_size * self.image_scale, self.character_size * self.image_scale))
                dummy_surface.fill((255, 0, 255))  # Magenta para identificar frames faltantes
                frame_list.append(dummy_surface)
                
            animation_list.append(frame_list)
        
        return animation_list