import pygame
import os

class Fighter():
    """
    Clase padre Fighter que define la funcionalidad base para todos los personajes luchadores.
    Esta clase maneja movimiento, animaciones, ataques básicos y física del juego.
    Las clases hijas implementarán personajes específicos con sus propias características.
    """
    def __init__(self, player_number, initial_x, initial_y, flip_sprite, character_data, attack_sound):
        # Propiedades básicas del jugador
        self.player_number = player_number  # Número del jugador (1 o 2) usando snake_case
        self.character_size = character_data[0]  # Tamaño base del sprite usando snake_case
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
        # El suelo está en 550 (600-50), así que ajustar automáticamente
        ground_level = 550  # Nivel del suelo estándar más abajo
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
        self.max_health = 100  # Salud máxima base para todos los personajes (hijas pueden sobrescribir)
        self.damage_taken = 0   # Daño acumulado total recibido
        self.current_health = self.max_health  # Salud derivada (siempre max_health - damage_taken)
        self.is_alive = True  # Si el personaje está vivo
        self.death_animation_done = False  # Flag para saber si terminó animación de muerte
        
        # Sistema de efectos de estado (para efectos como quemadura)
        self.burn_damage_remaining = 0  # Daño de quemadura pendiente
        self.burn_timer = 0  # Tiempo de quemadura restante (en frames)
        self.burn_interval = 60  # Frames entre aplicaciones de daño de quemadura (1 segundo a 60 FPS)
        self.burn_counter = 0  # Contador interno para el intervalo de quemadura
        
        # Sistema avanzado de ataques
        self.attack_frame_counter = 0  # Contador de frames para ataques complejos
        self.attack_has_hit = False  # Para evitar múltiples golpes en un ataque
        # Instrumentación de daño (debug)
        self.last_damage_applied = 0
        self.last_damage_timestamp = 0
        
        # Controles específicos del personaje (serán definidos por las clases hijas)
        self.movement_controls = {}
        self.attack_controls = {}
        self.setup_controls()


    def load_individual_sprites(self):
        """
        Carga sprites individuales frame por frame desde directorios separados.
        Cada animación tiene su propio directorio con archivos PNG numerados.
        Debe ser implementado por las clases hijas según su estructura de assets.
        """
        # Esta función será sobrescrita por las clases hijas
        # que implementarán la carga específica de sus sprites
        pass
    
    def setup_controls(self):
        """
        Configura los controles específicos para cada jugador.
        Las clases hijas pueden sobrescribir este método para controles personalizados.
        """
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
                'attack3': pygame.K_y  # Tercer ataque con tecla Y
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
                'attack3': pygame.K_KP3  # Tercer ataque con tecla 3 del teclado numérico
            }


    def move(self, screen_width, screen_height, surface, target, round_over):
        """
        Maneja el movimiento del personaje, incluyendo controles, física y colisiones.
        
        Args:
            screen_width (int): Ancho de la pantalla para límites
            screen_height (int): Alto de la pantalla para límites
            surface: Superficie de pygame para dibujar
            target: El oponente (para determinar orientación)
            round_over (bool): Si la ronda ha terminado
        """
        # Constantes de movimiento y física
        MOVEMENT_SPEED = 10  # Velocidad de movimiento horizontal
        GRAVITY_FORCE = 2    # Fuerza de gravedad aplicada cada frame
        JUMP_STRENGTH = -30  # Fuerza inicial del salto (negativa = hacia arriba)
        
        # Variables de movimiento para este frame
        horizontal_delta = 0  # Cambio en posición horizontal
        vertical_delta = 0    # Cambio en posición vertical
        
        # Resetear estado de correr cada frame, pero NO borrar el tipo de ataque si está ejecutándose
        self.is_running = False
        if not self.is_attacking:  # Mantener el tipo de ataque durante toda la animación
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
                
            # Procesamiento de salto - solo si no está ya saltando
            if pressed_keys[self.movement_controls['jump']] and not self.is_jumping:
                self.vertical_velocity = JUMP_STRENGTH
                self.is_jumping = True
                
            # Procesamiento de ataques - incluyendo el nuevo tercer ataque
            for attack_name, attack_key in self.attack_controls.items():
                if pressed_keys[attack_key]:
                    self.execute_attack(target)
                    # Determinar tipo de ataque basado en la tecla presionada
                    if attack_name == 'attack1':
                        self.current_attack_type = 1
                    elif attack_name == 'attack2':
                        self.current_attack_type = 2
                    elif attack_name == 'attack3':
                        self.current_attack_type = 3  # Nuevo tercer ataque
                    break  # Solo un ataque por frame
        
        # Aplicar gravedad a la velocidad vertical
        self.vertical_velocity += GRAVITY_FORCE
        vertical_delta += self.vertical_velocity
        
        # Mantener personaje dentro de los límites de pantalla horizontalmente
        if self.collision_rect.left + horizontal_delta < 0:
            horizontal_delta = -self.collision_rect.left
        if self.collision_rect.right + horizontal_delta > screen_width:
            horizontal_delta = screen_width - self.collision_rect.right
            
        # Mantener personaje en el suelo (límite vertical inferior)
        ground_level = screen_height - 50  # Nivel del suelo más abajo (550 para pantalla de 600)
        if self.collision_rect.bottom + vertical_delta > ground_level:
            self.vertical_velocity = 0  # Detener velocidad vertical
            self.is_jumping = False     # Ya no está saltando
            # Forzar que el bottom del personaje esté exactamente en el nivel del suelo
            vertical_delta = ground_level - self.collision_rect.bottom
        
        # Hacer que los personajes se miren entre sí
        if target.collision_rect.centerx > self.collision_rect.centerx:
            self.flip_sprite = False  # Mirando hacia la derecha
        else:
            self.flip_sprite = True   # Mirando hacia la izquierda
        
        # Aplicar cooldown de ataque
        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= 1
        
        # Procesar efectos de quemadura
        self.process_burn_effect()
        
        # Actualizar posición final del personaje
        self.collision_rect.x += horizontal_delta
        self.collision_rect.y += vertical_delta


    def update(self, target=None):
        """
        Actualiza las animaciones y estados del personaje cada frame.
        Maneja la lógica de transición entre diferentes estados de animación
        y actualiza los sprites correspondientes.
        
        Args:
            target: El oponente para detección de colisiones de ataque
        """
        # Determinar qué acción debe estar realizando el personaje
        # Recalcular salud derivada en cada update (por si se modificó damage_taken externamente)
        self.current_health = max(self.max_health - self.damage_taken, 0)

        if self.current_health <= 0:
            # Si la salud es 0 o menor, el personaje está muerto
            self.current_health = 0
            self.is_alive = False
            self.update_current_action(7)  # 7: animación de muerte
            # No marcar done hasta que termine frames de muerte
        elif self.is_hit:
            # Si fue golpeado, mostrar animación de recibir daño
            self.update_current_action(6)  # 6: animación de ser golpeado
        elif self.is_attacking:
            # Si está atacando, mostrar la animación de ataque correspondiente
            if self.current_attack_type == 1:
                self.update_current_action(3)  # 3: primer ataque
            elif self.current_attack_type == 2:
                self.update_current_action(4)  # 4: segundo ataque
            elif self.current_attack_type == 3:
                self.update_current_action(5)  # 5: tercer ataque (nuevo)
            
            # Incrementar contador de frames del ataque
            self.attack_frame_counter += 1
        elif self.is_jumping:
            # Si está saltando, mostrar animación de salto
            self.update_current_action(2)  # 2: animación de salto
        elif self.is_running:
            # Si está corriendo, mostrar animación de correr
            self.update_current_action(1)  # 1: animación de correr
        else:
            # Estado por defecto: inactivo/idle
            self.update_current_action(0)  # 0: animación idle
        
        # Velocidad de animación (milisegundos entre frames)
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
                self.death_animation_done = True  # Marcar finalizada
            else:
                # Reiniciar animación para acciones repetitivas
                self.frame_index = 0
                
                # Manejar fin de animaciones específicas
                if self.current_action in [3, 4, 5]:  # Cualquiera de los 3 ataques
                    self.is_attacking = False
                    self.attack_cooldown_timer = 20  # Cooldown después del ataque
                    self.attack_has_hit = False  # Resetear para el próximo ataque
                    self.attack_frame_counter = 0  # Resetear contador de frames
                    
                # Manejar fin de animación de ser golpeado
                if self.current_action == 6:
                    self.is_hit = False
                    # Si estaba atacando cuando fue golpeado, cancelar el ataque
                    self.is_attacking = False
                    self.attack_cooldown_timer = 20


    def execute_attack(self, target):
        """
        Ejecuta un ataque contra el objetivo si no hay cooldown activo.
        Crea un área de ataque y verifica colisiones con el oponente.
        
        Args:
            target: El personaje objetivo del ataque
        """
        if self.attack_cooldown_timer == 0:
            # Iniciar el ataque
            self.is_attacking = True
            self.attack_sound_effect.play()
            self.attack_has_hit = False  # Resetear para permitir golpear
            self.attack_frame_counter = 0  # Inicializar contador
            # Limpiar registro multi-frame si existe (para ataque 2 del Warrior)
            if hasattr(self, 'attack2_frames_hit_record'):
                self.attack2_frames_hit_record.clear()
    
    def process_burn_effect(self):
        """
        Procesa los efectos de quemadura aplicados al personaje.
        Aplica daño gradual durante el tiempo especificado.
        """
        if self.burn_timer > 0:
            self.burn_counter += 1
            
            # Aplicar daño cada segundo (60 frames a 60 FPS)
            if self.burn_counter >= self.burn_interval:
                # Calcular daño por intervalo
                damage_per_interval = max(1, self.burn_damage_remaining // (self.burn_timer // self.burn_interval)) if self.burn_timer >= self.burn_interval else self.burn_damage_remaining

                # Aplicar daño mediante sistema centralizado
                self.apply_damage(damage_per_interval)
                self.burn_damage_remaining -= damage_per_interval
                
                # Reiniciar contador
                self.burn_counter = 0
                self.burn_timer -= self.burn_interval
                
                # Asegurar que no se aplique daño negativo
                if self.current_health < 0:
                    self.current_health = 0
                
                # Limpiar efecto si se completó
                if self.burn_timer <= 0 or self.burn_damage_remaining <= 0:
                    self.burn_timer = 0
                    self.burn_damage_remaining = 0
                    self.burn_counter = 0
    
    def apply_burn_effect(self, total_damage, duration_seconds):
        """
        Aplica un efecto de quemadura al personaje.
        
        Args:
            total_damage (int): Daño total a aplicar durante la duración
            duration_seconds (int): Duración en segundos del efecto
        """
        self.burn_damage_remaining = total_damage
        self.burn_timer = duration_seconds * 60  # Convertir a frames (60 FPS)
        self.burn_counter = 0

    # =============================
    # NUEVO SISTEMA DE DAÑO CENTRALIZADO
    # =============================
    def apply_damage(self, raw_damage):
        """Aplica daño al personaje usando el sistema de salud derivado.
        No permite que la salud efectiva sea menor que 0 ni mayor que max_health.

        Args:
            raw_damage (int): Cantidad de daño a aplicar (>= 0)
        """
        if raw_damage <= 0 or not self.is_alive:
            return
        self.damage_taken += raw_damage
        # Registro debug
        self.last_damage_applied = raw_damage
        self.last_damage_timestamp = pygame.time.get_ticks()
        # Clamp daño acumulado
        if self.damage_taken > self.max_health:
            self.damage_taken = self.max_health
        # Actualizar salud derivada inmediatamente
        self.current_health = max(self.max_health - self.damage_taken, 0)
        if self.current_health <= 0:
            self.is_alive = False

    def calculate_attack_damage(self):
        """
        Calcula el daño base del ataque.
        Las clases hijas pueden sobrescribir este método para ataques específicos.
        
        Returns:
            int: Cantidad de daño a aplicar
        """
        # Daño diferente según el tipo de ataque - MUY REDUCIDO PARA BALANCE
        # Incremento ~60% sobre valores previos (4,4,6 -> 6,6,9)
        damage_values = {
            1: 6,
            2: 6,
            3: 9
        }
        return damage_values.get(self.current_attack_type, 6)
    
    def update_current_action(self, new_action):
        """
        Actualiza la acción actual del personaje si es diferente a la anterior.
        Reinicia el índice de frame y el tiempo de actualización.
        
        Args:
            new_action (int): Nueva acción a establecer
        """
        if new_action != self.current_action:
            self.current_action = new_action
            # Reiniciar configuración de animación para la nueva acción
            self.frame_index = 0
            self.last_update_time = pygame.time.get_ticks()

    def draw(self, surface, camera_offset_x=0):
        """
        Dibuja el personaje en la superficie especificada.
        Maneja el volteo horizontal del sprite y aplica el offset correcto.
        NUEVO: Alineación automática sprite-hitbox para mejor posicionamiento visual.
        
        Args:
            surface: Superficie de pygame donde dibujar el personaje
            camera_offset_x: Offset horizontal de la cámara
        """
        # Manejar sprites invertidos (como el Slime Demon)
        actual_flip = self.flip_sprite
        if hasattr(self, 'sprites_inverted') and self.sprites_inverted:
            actual_flip = not self.flip_sprite
        
        # Voltear la imagen horizontalmente si es necesario
        final_image = pygame.transform.flip(self.current_image, actual_flip, False)
        
        # NUEVO ENFOQUE: Centrar el sprite en la hitbox automáticamente
        sprite_width = self.current_image.get_width()
        sprite_height = self.current_image.get_height()
        
        # Centrar horizontalmente el sprite en la hitbox
        draw_x = self.collision_rect.centerx - (sprite_width // 2) + camera_offset_x
        
        # Alinear verticalmente: hacer que el sprite "toque" el suelo igual que la hitbox
        # Colocar el sprite de manera que su parte inferior esté alineada con la hitbox
        draw_y = self.collision_rect.bottom - sprite_height + 20  # 20px de ajuste fino
        
        # Dibujar la imagen en la superficie
        surface.blit(final_image, (draw_x, draw_y))
    
    def draw_hitbox(self, surface, show_attack_area=False, camera_offset_x=0):
        """
        Dibuja las hitboxes del personaje para debugging.
        Útil para visualizar áreas de colisión y ataque.
        
        Args:
            surface: Superficie donde dibujar las hitboxes
            show_attack_area (bool): Si mostrar también el área de ataque
            camera_offset_x: Offset horizontal de la cámara
        """
        # Crear rectángulo de hitbox ajustado para cámara
        adjusted_rect = pygame.Rect(
            self.collision_rect.x + camera_offset_x,
            self.collision_rect.y,
            self.collision_rect.width,
            self.collision_rect.height
        )
        # Dibujar hitbox principal del personaje (verde)
        pygame.draw.rect(surface, (0, 255, 0), adjusted_rect, 2)
        
        # Dibujar área de ataque durante toda la animación de ataque
        if show_attack_area and self.current_action in [3, 4, 5]:  # Cualquier animación de ataque
            # Determinar el tipo de ataque basado en la acción actual
            attack_type_map = {3: 1, 4: 2, 5: 3}  # action -> attack_type
            temp_attack_type = attack_type_map.get(self.current_action, 1)
            
            # Usar el mismo sistema que check_collision_with_target para mostrar hitboxes reales
            attack_area = self.get_attack_area_for_display(temp_attack_type)
            if attack_area:
                # Ajustar para cámara
                adjusted_attack_rect = pygame.Rect(
                    attack_area.x + camera_offset_x,
                    attack_area.y,
                    attack_area.width,
                    attack_area.height
                )
                # Dibujar área de ataque (rojo)
                pygame.draw.rect(surface, (255, 0, 0), adjusted_attack_rect, 3)
    
    def get_attack_area(self):
        """
        Obtiene el área de ataque actual del personaje.
        Método base que puede ser sobrescrito por las clases hijas.
        
        Returns:
            pygame.Rect: Rectángulo del área de ataque o None si no está atacando
        """
        if not self.is_attacking:
            return None
            
        # Sistema básico de ataque (para personajes sin implementación específica)
        attack_width = 4 * self.collision_rect.width
        attack_y = self.collision_rect.y - 20
        attack_height = 550 - attack_y + 20
        
        if self.flip_sprite:
            attack_x = self.collision_rect.centerx - attack_width
        else:
            attack_x = self.collision_rect.centerx
            
        return pygame.Rect(attack_x, attack_y, attack_width, attack_height)
    
    def get_attack_area_for_display(self, attack_type):
        """
        Obtiene el área de ataque para visualización durante animaciones.
        Similar a get_attack_area pero funciona con cualquier tipo de ataque especificado.
        
        Args:
            attack_type (int): Tipo de ataque (1, 2, o 3)
            
        Returns:
            pygame.Rect: Rectángulo del área de ataque
        """
        # Sistema básico de ataque (para personajes sin implementación específica)
        attack_width = 4 * self.collision_rect.width
        attack_y = self.collision_rect.y - 20
        attack_height = 550 - attack_y + 20
        
        if self.flip_sprite:
            attack_x = self.collision_rect.centerx - attack_width
        else:
            attack_x = self.collision_rect.centerx
            
        return pygame.Rect(attack_x, attack_y, attack_width, attack_height)

    def check_collision_with_target(self, target):
        """Método base de colisión de ataque para personajes genéricos.
        Aplica un solo impacto por animación usando attack_has_hit.

        Args:
            target: El objetivo a verificar y aplicar daño si hay colisión.
        """
        if not self.is_attacking or not self.is_alive or not target.is_alive:
            return
        attack_area = self.get_attack_area()
        if attack_area is None:
            return
        if not attack_area.colliderect(target.collision_rect):
            return
        # Un solo golpe por animación
        if self.attack_has_hit:
            return
        damage = self.calculate_attack_damage()
        if damage > 0:
            target.apply_damage(damage)
            target.is_hit = True
            self.attack_has_hit = True


# Clases hijas para personajes específicos

class WarriorFighter(Fighter):
    """
    Clase específica para el personaje Warrior (Guerrero).
    Hereda de Fighter e implementa carga de sprites y características específicas.
    """
    def __init__(self, player_number, initial_x, initial_y, flip_sprite, attack_sound):
        # Datos específicos del Warrior - ajustado para mejor alineación con hitbox
        warrior_data = [162, 4, [72, 30]]  # [size, scale, offset] - reducido offset Y
        # Propiedades específicas de ataques del Warrior (definir antes de cargar sprites)
        self.attack2_hit_frames = [0, 2, 4, 6]
        self.attack2_final_frame = None

        # Inicializar la clase padre (carga sprites -> necesita atributos ya definidos)
        super().__init__(player_number, initial_x, initial_y, flip_sprite, warrior_data, attack_sound)
        
        # Características específicas del Warrior
        self.character_name = "Warrior"
        self.max_health = 120  # Más salud que otros personajes
        self.current_health = self.max_health
        
        # Flag para indicar orientación de sprites (False = sprites normales)
        self.sprites_inverted = False
        
    def load_individual_sprites(self):
        """
        Carga los sprites individuales del Warrior desde sus directorios.
        Cada animación está en un directorio separado con archivos PNG numerados.
        """
        base_path = "assets/images/warrior/Sprites"
        animation_directories = [
            "idle",      # 0: idle
            "run",       # 1: run  
            "jump_up",   # 2: jump (usamos jump_up como representativo)
            "1_atk",     # 3: attack1
            "2_atk",     # 4: attack2
            "3_atk",     # 5: attack3 (tercer ataque)
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
                # Ordenar numéricamente extrayendo el número del nombre de archivo  
                def extract_number(filename):
                    import re
                    numbers = re.findall(r'\d+', filename)
                    return int(numbers[0]) if numbers else 0
                files.sort(key=extract_number)  # Ordenar para secuencia correcta numéricamente
                
                for file_name in files:
                    file_path = os.path.join(directory_path, file_name)
                    # Cargar y escalar la imagen
                    sprite_image = pygame.image.load(file_path).convert_alpha()
                    scaled_sprite = pygame.transform.scale(
                        sprite_image, 
                        (self.character_size * self.image_scale, self.character_size * self.image_scale)
                    )
                    frame_list.append(scaled_sprite)
            
            # Si no hay frames, agregar un frame dummy para evitar errores
            if not frame_list:
                dummy_surface = pygame.Surface((self.character_size * self.image_scale, self.character_size * self.image_scale))
                dummy_surface.fill((255, 0, 255))  # Magenta para identificar frames faltantes
                frame_list.append(dummy_surface)
                
            animation_list.append(frame_list)
        
        # Calcular el frame final del segundo ataque para el golpe fuerte
        if len(animation_list) > 4:  # attack2 está en índice 4
            self.attack2_final_frame = len(animation_list[4]) - 1
            # Calcular dinámicamente frames de impacto para ataque 2: inicio, medio y final parcial
            if self.attack2_final_frame is not None:
                early = 0
                mid = max(1, self.attack2_final_frame // 2)
                late = max(mid+1, (3 * self.attack2_final_frame) // 4)
                # Asegurar unicidad y orden
                self.attack2_hit_frames = sorted(set([early, mid, late]))
        
        return animation_list
    
    def calculate_attack_damage(self):
        """
        Sobrescribe el cálculo de daño para ataques específicos del Warrior.
        Implementa el sistema de daño balanceado según especificaciones.
        
        Returns:
            int: Cantidad de daño a aplicar
        """
        if self.current_attack_type == 1:
            return 8  # Antes 5
        elif self.current_attack_type == 2:
            if self.frame_index in self.attack2_hit_frames:
                return 6  # Antes 4
            elif self.frame_index == self.attack2_final_frame:
                return 13  # Antes 8
            return 0
        elif self.current_attack_type == 3:
            return 11  # Antes 7
        return 8
    
    def check_collision_with_target(self, target):
        """
        Método base para detección de colisión de ataques.
        Implementa el sistema básico de ataque que puede ser sobrescrito por las clases hijas.
        
        Args:
            target: El objetivo a verificar colisión
        """
        if not self.is_attacking or not self.is_alive or not target.is_alive:
            return

        # Obtener el área de ataque específica según tipo y frame
        attack_area = self.get_attack_area()
        if attack_area is None:
            return  # No hay área activa en este frame

        # Si no hay colisión, salir
        if not attack_area.colliderect(target.collision_rect):
            return

        # Control de ventanas de impacto para cada tipo de ataque
        # Evitamos múltiples golpes por frame usando attack_has_hit y reglas por ataque
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
            # Ataque multi-frame: permitir impactos solo en frames definidos, pero máximo una vez por frame
            # Usamos un registro de frames ya aplicados
            if not hasattr(self, 'attack2_frames_hit_record'):
                self.attack2_frames_hit_record = set()
            # Solo frames de daño (definidos o final)
            is_damage_frame = (self.frame_index in self.attack2_hit_frames) or (self.frame_index == self.attack2_final_frame)
            if not is_damage_frame:
                return
            # Si ya golpeamos en este frame exacto, salir
            if self.frame_index in self.attack2_frames_hit_record:
                return
            damage = self.calculate_attack_damage()
            if damage > 0:
                target.apply_damage(damage)
                target.is_hit = True
                self.attack2_frames_hit_record.add(self.frame_index)
            # No usamos attack_has_hit aquí para permitir varios frames de impacto controlado

        elif self.current_attack_type == 3:
            # Retrasar impacto hasta segunda mitad de animación
            if self.attack_has_hit:
                return
            # Necesitamos conocer longitud de animación de ataque 3 (índice 5)
            total_frames_attack3 = len(self.animation_list[5]) if len(self.animation_list) > 5 else 0
            half_threshold = total_frames_attack3 // 2
            if self.frame_index < half_threshold:
                return  # Aún cargando el ataque, sin daño
            damage = self.calculate_attack_damage()
            if damage > 0:
                target.apply_damage(damage)
                target.is_hit = True
                # Aplicar quemadura sólo si no existe y después del umbral
                if target.burn_timer == 0:
                    target.apply_burn_effect(total_damage=6, duration_seconds=6)
                self.attack_has_hit = True

        # Seguridad: si la animación termina, limpiar registros
        if not self.is_attacking:
            if hasattr(self, 'attack2_frames_hit_record'):
                self.attack2_frames_hit_record.clear()
    
    def get_attack_area(self):
        """
        Sobrescribe el método para mostrar las hitboxes específicas del Warrior.
        Retorna el área de ataque actual según el tipo de ataque y frame.
        
        Returns:
            pygame.Rect: Rectángulo del área de ataque o None si no está atacando
        """
        if not self.is_attacking:
            return None
            
        # Usar la misma lógica que check_collision_with_target para visualización correcta
        if self.current_attack_type == 1:
            # Primer ataque: rango medio extendido hacia arriba y derecha
            attack_width = 200
            attack_y = self.collision_rect.y - 40
            attack_height = 550 - attack_y + 20
            
            if self.flip_sprite:
                attack_x = self.collision_rect.centerx - attack_width
            else:
                attack_x = self.collision_rect.centerx
                
        elif self.current_attack_type == 2:
            # Segundo ataque: área variable según el frame
            if self.frame_index in self.attack2_hit_frames:
                # Primeros frames: ataque hacia ambos lados
                attack_width = 320
                attack_y = self.collision_rect.y - 30
                attack_height = 550 - attack_y + 20
                attack_x = self.collision_rect.centerx - (attack_width // 2)
            elif self.frame_index == self.attack2_final_frame:
                # Último frame: solo hacia adelante
                attack_width = 180
                attack_y = self.collision_rect.y - 30
                attack_height = 550 - attack_y + 20
                if self.flip_sprite:
                    attack_x = self.collision_rect.centerx - attack_width
                else:
                    attack_x = self.collision_rect.centerx
            else:
                return None  # Sin área de ataque en otros frames
                
        elif self.current_attack_type == 3:
            # Tercer ataque: gran rango hacia adelante
            attack_width = 260
            attack_y = self.collision_rect.y - 40
            attack_height = 550 - attack_y + 20
            
            if self.flip_sprite:
                attack_x = self.collision_rect.centerx - attack_width
            else:
                attack_x = self.collision_rect.centerx
        else:
            return None
            
        return pygame.Rect(attack_x, attack_y, attack_width, attack_height)
    
    def get_attack_area_for_display(self, attack_type):
        """
        Sobrescribe el método para mostrar las hitboxes específicas del Warrior durante toda la animación.
        
        Args:
            attack_type (int): Tipo de ataque (1, 2, o 3)
            
        Returns:
            pygame.Rect: Rectángulo del área de ataque
        """
        # Usar la misma lógica que get_attack_area pero con el attack_type especificado
        if attack_type == 1:
            # Primer ataque: rango medio extendido hacia arriba y derecha
            attack_width = 200
            attack_y = self.collision_rect.y - 40
            attack_height = 550 - attack_y + 20
            
            if self.flip_sprite:
                attack_x = self.collision_rect.centerx - attack_width
            else:
                attack_x = self.collision_rect.centerx
                
        elif attack_type == 2:
            # Segundo ataque: para visualización, mostrar el área más grande (360°)
            attack_width = 320
            attack_y = self.collision_rect.y - 30
            attack_height = 550 - attack_y + 20
            attack_x = self.collision_rect.centerx - (attack_width // 2)
                
        elif attack_type == 3:
            # Tercer ataque: gran rango hacia adelante
            attack_width = 260
            attack_y = self.collision_rect.y - 40
            attack_height = 550 - attack_y + 20
            
            if self.flip_sprite:
                attack_x = self.collision_rect.centerx - attack_width
            else:
                attack_x = self.collision_rect.centerx
        else:
            # Fallback al método padre
            return super().get_attack_area_for_display(attack_type)
            
        return pygame.Rect(attack_x, attack_y, attack_width, attack_height)

class SlimeDemonFighter(Fighter):
    """
    Clase específica para el personaje Slime Demon.
    Hereda de Fighter e implementa carga de sprites y características específicas.
    NOTA: Los sprites del Slime Demon pueden estar orientados en dirección opuesta,
    por lo que sobrescribimos la lógica de flip.
    """
    def __init__(self, player_number, initial_x, initial_y, flip_sprite, attack_sound):
        # Datos específicos del Slime Demon - ajustado para mejor alineación con hitbox
        slime_demon_data = [150, 3, [75, 50]]  # [size, scale, offset] - reducido offset Y
        
        # Inicializar la clase padre
        super().__init__(player_number, initial_x, initial_y, flip_sprite, slime_demon_data, attack_sound)
        
        # Características específicas del Slime Demon
        self.character_name = "Slime Demon"
        self.max_health = 100  # Salud estándar
        self.current_health = self.max_health
        
        # Flag para indicar que este personaje tiene sprites invertidos
        self.sprites_inverted = True
        
    def load_individual_sprites(self):
        """
        Carga los sprites individuales del Slime Demon desde sus directorios.
        """
        base_path = "assets/images/slime_demon/Sprites"
        animation_directories = [
            "idle",      # 0: idle
            "run",       # 1: run  
            "idle",      # 2: jump (reutilizamos idle ya que no hay jump específico)
            "1_atk",     # 3: attack1
            "2_atk",     # 4: attack2
            "3_atk",     # 5: attack3 (tercer ataque)
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
                # Ordenar numéricamente extrayendo el número del nombre de archivo
                def extract_number(filename):
                    import re
                    numbers = re.findall(r'\d+', filename)
                    return int(numbers[0]) if numbers else 0
                files.sort(key=extract_number)  # Ordenar para secuencia correcta numéricamente
                
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
                dummy_surface.fill((255, 0, 255))  # Magenta para identificar frames faltantes
                frame_list.append(dummy_surface)
                
            animation_list.append(frame_list)
        
        return animation_list