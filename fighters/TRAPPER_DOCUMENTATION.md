# 🪤 Trapper Fighter - Documentación Técnica

## 📋 Información General

**Clase**: `TrapperFighter`  
**Tipo**: Especialista en control de área y ataques a distancia  
**Rol**: Zoner elusivo con mecánicas únicas  
**Dificultad**: ⭐⭐⭐⭐⭐ (Experto)

## 📊 Estadísticas Base

| Atributo | Valor | Descripción |
|----------|-------|-------------|
| **Salud Máxima** | 70 HP | La más baja - Glass cannon extremo |
| **Velocidad** | 16 | La más alta del juego |
| **Tamaño Sprite** | 130x130 px | Escala 3.5x (compacto) |
| **Hitbox** | 65x160 px | Muy pequeña - difícil de golpear |

## ⚔️ Sistema de Ataques Únicos

### ⚡ Ataque 1 - Corte Sangriento
- **Daño**: 5 puntos + 6 de sangrado
- **Daño Total**: 11 puntos (5 inmediato + 6 gradual)
- **Efecto Especial**: **Sangrado** - 6 puntos durante 4 segundos
- **Alcance**: 80x60 píxeles
- **Tipo**: Cuerpo a cuerpo con DoT (Damage over Time)
- **Cooldown Sangrado**: 45 frames (más rápido que quemadura)

### 🪤 Ataque 2 - Trampa Explosiva
- **Daño**: 8 puntos + stun
- **Tipo**: Entidad única colocada en el suelo
- **Efecto Especial**: **Stun** - 45 frames de inmovilización
- **Detección**: 50 píxeles de radio (pisada directa)
- **Duración**: 10 segundos activa
- **Máximo Simultáneo**: 3 trampas
- **Cooldown**: 120 frames (2 segundos)

### 🏹 Ataque 3 - Proyectil Dirigido
- **Daño**: 4 puntos (bajo pero preciso)
- **Tipo**: Proyectil en línea recta hacia el enemigo
- **Velocidad**: 12 píxeles por frame
- **Rotación**: Automática hacia el objetivo
- **Alcance**: Toda la pantalla
- **Cooldown**: 25 frames (rápido)

## 🎨 Estructura de Sprites

```
trapper/Sprites/
├── 01_idle/                # Animación de reposo
├── 02_run/                 # Animación de carrera
├── 03_jump_down/           # Animación de caída
├── 03_jump_up/             # Animación de salto
├── 1_atk/                  # Corte sangriento (6 frames)
├── 2_atk/                  # Colocación de trampa (10 frames)
│   ├── trap_throw/         # Sprite de trampa colocada
│   ├── trap_land/          # Animación de aterrizaje (3 frames)
│   └── trap_detonate/      # Animación de explosión (5 frames)
├── 3_atk/                  # Disparo de proyectil (7 frames)
│   ├── projectile_throw/   # Sprite del proyectil volando
│   └── projectile_land/    # Animación de impacto (5 frames)
├── 12_take_hit/            # Animación de recibir daño
└── 13_death/               # Animación de muerte
```

## 🩸 Sistema de Sangrado (Bleeding)

### Mecánica Nueva
- **Diferente a Quemadura**: Más rápido (45 frames vs 60 frames)
- **Daño Total**: 6 puntos repartidos en 4 segundos
- **Aplicación**: Solo con Ataque 1
- **Visual**: Sin indicadores adicionales, solo reducción de HP

### Implementación Técnica
```python
class Fighter:
    def apply_bleeding_effect(self, bleeding_damage, bleeding_duration_frames):
        self.bleeding_damage_remaining = bleeding_damage
        self.bleeding_timer = bleeding_duration_frames
        self.bleeding_counter = 0
    
    def process_bleeding_effect(self):
        if self.bleeding_timer > 0:
            if self.bleeding_counter >= self.bleeding_interval:  # 45 frames
                damage_per_interval = max(1, self.bleeding_damage_remaining // intervals)
                self.apply_damage(damage_per_interval)
```

## 🪤 Sistema de Trampas - Entidades Únicas

### Clase TrapProjectile
```python
class TrapProjectile(BaseProjectile):
    def __init__(self, x, y, damage, target, trap_sprite, land_sprites, detonate_sprites):
        # Estados: landing -> landed -> detonating -> dead
        self.trap_state = "landing"
        self.detection_radius = 50
        self.trap_active_time = 10000  # 10 segundos
```

### Estados de la Trampa
1. **Landing**: Animación de aterrizaje (`trap_land_1.png` a `trap_land_3.png`)
2. **Landed**: Trampa activa usando `trap_throw.png`
3. **Detonating**: Explosión usando `trap_detonate_1.png` a `trap_detonate_5.png`

### Mecánica de Activación
- **Detección**: Enemigo debe pisar directamente la trampa (no proximidad)
- **Condiciones**: Enemigo en el suelo + distancia horizontal ≤ 50 píxeles
- **Efecto**: Daño + stun de 45 frames (0.75 segundos)
- **Explosión**: A nivel del suelo (y=550)

## 🏹 Sistema de Proyectiles - Entidades Dirigidas

### Clase RangedProjectile
```python
class RangedProjectile(BaseProjectile):
    def __init__(self, x, y, velocity_x, velocity_y, damage, target, projectile_sprite, land_sprites):
        # Cálculo de rotación automática
        self.rotation_angle = math.degrees(math.atan2(velocity_y, velocity_x))
        self.rotated_sprite = pygame.transform.rotate(projectile_sprite, -self.rotation_angle)
```

### Mecánica de Rotación
- **Cálculo**: `math.atan2(velocity_y, velocity_x)` para dirección exacta
- **Aplicación**: Sprite se rota una vez al crear el proyectil
- **Consistencia**: Tanto proyectil volando como animación de impacto mantienen rotación
- **Performance**: Rotación única, no por frame

### Estados del Proyectil
1. **Flying**: Usa sprite rotado `projectile_throw.png`
2. **Landing**: Animación rotada `projectile_land_1.png` a `projectile_land_5.png`
3. **Death**: Desaparece después de impacto o salir de pantalla

## ⚙️ Características Técnicas Avanzadas

### Movilidad Superior
- **Velocidad Base**: 16 (vs 12-14 de otros)
- **Salto Mejorado**: -35 fuerza (vs -30 estándar)
- **Hitbox Pequeña**: 65x160 - la más elusiva

### Audio
- **Efecto de Sonido**: `sword.wav`
- **Volumen**: 50%
- **Estilo**: Cortes rápidos y ágiles

### Gestión de Entidades
```python
# Límites de entidades
self.max_traps = 3
self.active_traps = []
self.active_projectiles = []

# Limpieza automática
self.active_traps = [trap for trap in self.active_traps if trap.is_alive]
```

## 🎯 Estrategia y Uso

### Fortalezas
- ✅ **Movilidad Extrema** - Velocidad 16 + salto mejorado
- ✅ **Control de Área** - Trampas controlan espacio
- ✅ **Ataques a Distancia** - Proyectiles precisos
- ✅ **DoT y Stun** - Efectos de estado únicos
- ✅ **Hitbox Pequeña** - Muy difícil de golpear
- ✅ **Versatilidad** - 3 tipos de ataque completamente diferentes

### Debilidades
- ❌ **HP Mínimo** - Solo 70 HP, cualquier error es fatal
- ❌ **Daño Individual Bajo** - Proyectiles solo 4 puntos
- ❌ **Setup Dependiente** - Necesita tiempo para colocar trappas
- ❌ **Cooldowns** - Limitado por tiempos de recarga
- ❌ **Complejidad** - Requiere gestión de múltiples sistemas

### Matchups Extremos

#### vs Tank (Favorable)
- **Estrategia**: Kiting con proyectiles, trampas para control
- **Ventaja**: Velocidad neutraliza el knockback
- **Táctica**: Nunca intercambiar golpes directos

#### vs Assassin (Neutral-Favorable)
- **Estrategia**: Trampas interrumpen combos, movilidad escapa
- **Cuidado**: Un combo del Assassin puede ser letal (26 vs 70 HP)
- **Táctica**: Sangrado + proyectiles para chip damage

#### vs Warrior (Desfavorable)
- **Estrategia**: Hit-and-run extremo, evitar quemadura
- **Problema**: HP del Warrior (100) requiere muchos ataques
- **Táctica**: Paciencia, usar todas las herramientas disponibles

#### vs Slime Demon (Neutral)
- **Estrategia**: Movilidad vs proyectiles parabólicos
- **Ventaja**: Velocidad para esquivar explosiones
- **Táctica**: Presión con proyectiles, trampas para zoning

## 🔧 Configuración Avanzada

### Sistema de Sangrado
```python
# Más rápido que quemadura
self.bleeding_interval = 45  # vs 60 de burn
bleeding_effect = (6, 240)   # 6 damage over 4 seconds
```

### Gestión de Trampas
```python
# Configuración de trampas
trap_config = {
    'detection_radius': 50,
    'active_time': 10000,      # 10 segundos
    'max_simultaneous': 3,
    'cooldown': 120,           # 2 segundos
    'stun_duration': 45        # 0.75 segundos
}
```

### Proyectiles Precisos
```python
# Cálculo de dirección exacta
dx = target_x - start_x
dy = target_y - start_y
distance = (dx ** 2 + dy ** 2) ** 0.5
vel_x = (dx / distance) * self.projectile_speed  # 12
vel_y = (dy / distance) * self.projectile_speed
```

## 📊 Análisis de Complejidad

### Gestión de Recursos
- **Trampas Activas**: Máximo 3 simultáneas
- **Cooldowns Múltiples**: Diferentes para cada ataque
- **Posicionamiento**: Crítico para supervivencia
- **Timing**: Combinación de setup y ejecución

### Curva de Aprendizaje
1. **Básico**: Movilidad y proyectiles
2. **Intermedio**: Colocación efectiva de trampas
3. **Avanzado**: Combinación de todas las herramientas
4. **Maestro**: Gestión perfecta de espacio y recursos

## 📈 Historial de Cambios

### v1.3 (Actual)
- **Sprites originales**: Uso exclusivo de PNG de carpetas
- **Rotación automática**: Proyectiles apuntan al enemigo
- **Sistema de sangrado**: DoT único más rápido que burn
- **Eliminación de debug**: Sin círculos, líneas o elementos adicionales
- **Sprites más grandes**: Trampas 2.5x, proyectiles 2.0x
- **Explosión a nivel de suelo**: Detonación correctamente posicionada

### v1.2
- **Entidades únicas**: Trampas y proyectiles como objetos independientes
- **Estados avanzados**: Sistema completo de estados para cada entidad
- **Colisión inteligente**: Detección precisa de pisada vs proximidad

### v1.1
- **Implementación inicial**: Sistema básico de trampas y proyectiles
- **Movilidad superior**: Velocidad 16 y salto mejorado
- **Hitbox ágil**: 65x160 para máxima evasión

## 🎮 Guía de Maestría

### Para Principiantes
1. **Enfócate en movilidad**: Usa velocidad para sobrevivir
2. **Proyectiles básicos**: Aprende el rango y timing
3. **Una trampa a la vez**: No te compliques al inicio

### Para Intermedio
1. **Control de espacio**: Usa trampas para limitar movimiento
2. **Combos básicos**: Sangrado + proyectiles
3. **Gestión de cooldowns**: Alterna entre ataques

### Para Avanzado
1. **Setup perfecto**: 3 trampas posicionadas estratégicamente
2. **Kiting maestro**: Nunca dejes que te alcancen
3. **Maximización de DoT**: Mantén sangrado activo siempre

### Para Experto
1. **Gestión de recursos**: Trampas como recursos limitados
2. **Predición**: Anticipa movimiento enemigo
3. **Frame perfection**: Uso óptimo de todos los cooldowns

---

**Desarrollado para Dungeon Fighters - Enhanced Edition**  
**Clase implementada en**: `fighters/trapper_fighter.py`  
**Última actualización**: Noviembre 2025

## 🔥 "Muy molesto de enfrentar" - Objetivo Cumplido

El Trapper ha sido diseñado específicamente para ser **"muy molesto de enfrentar"** como solicitado:

- **Movilidad extrema** para escapar constantemente
- **Trampas persistentes** que limitan el movimiento enemigo  
- **Ataques a distancia** que mantienen presión sin riesgo
- **Efectos de estado** que causan daño y control continuo
- **Hitbox pequeña** que frustra intentos de contraataque

**Resultado**: Un personaje que requiere paciencia extrema para vencer, cumpliendo perfectamente el objetivo de diseño.