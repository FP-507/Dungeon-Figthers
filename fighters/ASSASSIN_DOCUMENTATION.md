# 🗡️ Assassin Fighter - Documentación Técnica

## 📋 Información General

**Clase**: `AssassinFighter`  
**Tipo**: DPS rápido con ataques consecutivos  
**Rol**: Burst damage y movilidad alta  
**Dificultad**: ⭐⭐⭐⭐☆ (Avanzado)

## 📊 Estadísticas Base

| Atributo | Valor | Descripción |
|----------|-------|-------------|
| **Salud Máxima** | 75 HP | Baja - Glass cannon |
| **Velocidad** | 14 | Alta velocidad |
| **Tamaño Sprite** | 140x140 px | Escala 3.5x |
| **Hitbox** | 70x170 px | Hitbox pequeña y ágil |

## ⚔️ Sistema de Ataques Consecutivos

### ⚡ Ataque 1 - Corte Rápido
- **Daño**: 6 puntos
- **Alcance**: 75x60 píxeles
- **Velocidad**: Muy rápida
- **Tipo**: Ataque de apertura
- **Frames de Activación**: Frame medio (rápido)
- **Cooldown**: Mínimo para combos

### 🌪️ Ataque 2 - Combo Doble
- **Daño**: 8 puntos
- **Alcance**: 85x70 píxeles (mayor que ataque 1)
- **Velocidad**: Rápida
- **Tipo**: Continuación de combo
- **Frames de Activación**: 60% de la animación
- **Efecto**: Mejor alcance que ataque básico

### ⚔️ Ataque 3 - Finalizador
- **Daño**: 12 puntos
- **Alcance**: 95x80 píxeles (máximo del Assassin)
- **Velocidad**: Moderada
- **Tipo**: Remate de combo
- **Frames de Activación**: 70% de la animación
- **Efecto**: Máximo daño y alcance

## 🎨 Estructura de Sprites

```
assasin/Sprites/            # Nota: carpeta con typo histórico
├── idle/                   # Animación de reposo
├── run/                    # Animación de carrera
├── jump_down/              # Animación de caída
├── jump_up/                # Animación de salto
├── 1_atk/                  # Corte rápido
├── 2_atk/                  # Combo doble
├── 3_atk/                  # Finalizador
├── take_hit/               # Animación de recibir daño
└── death/                  # Animación de muerte
```

## ⚡ Sistema de Combos

### Filosofía de Diseño
El Assassin está diseñado para **ataques consecutivos rápidos**:
- Cada ataque tiene mayor daño y alcance que el anterior
- Cooldowns mínimos para permitir cadenas fluidas
- Progresión de daño: 6 → 8 → 12 puntos

### Mecánica de Progresión
```python
# Progresión de áreas de ataque
attack_areas = {
    1: (75, 60),   # Básico - pequeño pero rápido
    2: (85, 70),   # Intermedio - mejor alcance
    3: (95, 80)    # Finalizador - máximo alcance
}

# Progresión de daño
damage_values = {
    1: 6,    # Opener
    2: 8,    # Builder
    3: 12    # Finisher
}
```

### Estrategia de Combo
1. **Ataque 1**: Iniciador rápido para acercarse
2. **Ataque 2**: Mantener presión con mejor alcance
3. **Ataque 3**: Remate con máximo daño
4. **Repetir**: Cooldowns bajos permiten spam

## ⚙️ Características Técnicas

### Controles por Defecto
- **Jugador 1**: A/D (movimiento), W (salto), R/T/Y (ataques)
- **Jugador 2**: ←/→ (movimiento), ↑ (salto), 1/2/3 (ataques)

### Física Optimizada
- **Velocidad Alta**: 14 (más rápido que Warrior/Slime Demon)
- **Hitbox Pequeña**: 70x170 - difícil de golpear
- **Movilidad**: Excelente para hit-and-run

### Audio
- **Efecto de Sonido**: `sword.wav`
- **Volumen**: 50%
- **Estilo**: Cortes rápidos de espada

## 🎯 Estrategia y Uso

### Fortalezas
- ✅ **Burst Damage Extremo** - 26 puntos en combo completo (6+8+12)
- ✅ **Velocidad Superior** - Más rápido que casi todos
- ✅ **Hitbox Pequeña** - Difícil de golpear
- ✅ **Combos Fluidos** - Ataques consecutivos sin lag
- ✅ **Hit-and-Run** - Atacar y escapar rápidamente

### Debilidades
- ❌ **HP Muy Bajo** - Solo 75 HP (el más frágil)
- ❌ **Sin Rango** - Debe estar en cuerpo a cuerpo
- ❌ **Sin Efectos Especiales** - Solo daño directo
- ❌ **Dependiente de Combos** - Ataques individuales débiles
- ❌ **Alto Riesgo** - Una equivocación puede ser fatal

### Matchups Detallados

#### vs Warrior (Favorable)
- **Estrategia**: Hit-and-run, evitar la quemadura
- **Ventaja**: Velocidad superior para escapar
- **Cuidado**: No intercambiar golpes - el Warrior resiste más

#### vs Slime Demon (Neutral)
- **Estrategia**: Presión constante, evitar proyectiles
- **Ventaja**: Velocidad para esquivar gotas de lava
- **Cuidado**: Explosión de área puede interrumpir combos

#### vs Tank (Desfavorable)
- **Estrategia**: Combos rápidos y escape inmediato
- **Problema**: Knockback del Tank rompe combos
- **Cuidado**: Un solo combo del Tank puede ser letal

#### vs Trapper (Muy Desfavorable)
- **Estrategia**: Agresión extrema antes de que coloque trampas
- **Problema**: Trampas limitan movilidad
- **Cuidado**: Proyectiles a distancia neutralizan ventaja de velocidad

## 🔧 Configuración Avanzada

### Optimización de Combos
```python
# Cooldowns mínimos para combos fluidos
self.attack_cooldown_timer = 15  # Muy rápido

# Progresión de frames de activación
activation_frames = {
    1: "middle",     # 50% - muy rápido
    2: "60%",        # 60% - rápido
    3: "70%"         # 70% - moderado
}
```

### Ajuste de Movilidad
```python
# Velocidad superior
self.base_movement_speed = 14  # vs 12 estándar

# Hitbox ágil
collision_size = (70, 170)  # Estrecha y alta
```

### Balance de Daño
```python
def calculate_attack_damage(self):
    damage_progression = [6, 8, 12]  # Escalado lineal
    return damage_progression[self.current_attack_type - 1]
```

## 📊 Análisis de DPS

### Daño por Segundo (Teórico)
- **Combo Completo**: 26 puntos en ~2 segundos = **13 DPS**
- **Spam Ataque 1**: 6 puntos cada 0.5 segundos = **12 DPS**
- **Comparación**: Mayor burst, DPS sostenido comparable

### Eficiencia de Combos
- **3 Ataques Seguidos**: 26 daño total
- **vs Warrior Básico**: 8x3 = 24 (similar pero sin efectos)
- **vs Tank Máximo**: 15x2 = 30 (menos frecuente)

## 📈 Historial de Cambios

### v1.3 (Actual)
- Optimización de hitbox para mejor evasión
- Ajuste de cooldowns para combos más fluidos
- Balance de progresión de daño

### v1.2
- Implementación del sistema de progresión de áreas
- Velocidad aumentada a 14
- Mejora en la responsividad de ataques

### v1.1
- Sistema de ataques consecutivos
- Hitbox reducida para mayor agilidad
- Balanceo inicial de daño

## 🎮 Guía de Juego

### Para Principiantes
1. **Practica el timing**: Aprende la velocidad de cada ataque
2. **Usa la movilidad**: No te quedes quieto
3. **Combos básicos**: 1→2→3, luego escapa

### Para Avanzados
1. **Mix-ups**: Alterna entre ataques para confundir
2. **Spacing perfecto**: Mantén distancia exacta
3. **Frame traps**: Usa cooldowns para presionar

---

**Desarrollado para Dungeon Fighters - Enhanced Edition**  
**Clase implementada en**: `fighters/assassin_fighter.py`  
**Última actualización**: Noviembre 2025