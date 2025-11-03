# 🗡️ Warrior Fighter - Documentación Técnica

## 📋 Información General

**Clase**: `WarriorFighter`  
**Tipo**: Luchador equilibrado cuerpo a cuerpo  
**Rol**: Tank-DPS híbrido con capacidades de quemadura  
**Dificultad**: ⭐⭐☆☆☆ (Principiante)

## 📊 Estadísticas Base

| Atributo | Valor | Descripción |
|----------|-------|-------------|
| **Salud Máxima** | 100 HP | Salud más alta del juego |
| **Velocidad** | 12 | Velocidad moderada |
| **Tamaño Sprite** | 162x162 px | Escala 2.7x |
| **Hitbox** | 80x180 px | Hitbox grande pero manejable |

## ⚔️ Sistema de Ataques

### 🥊 Ataque 1 - Golpe Básico
- **Daño**: 8 puntos
- **Alcance**: 90x70 píxeles
- **Velocidad**: Rápida
- **Efecto**: Daño directo sin efectos adicionales
- **Frames de Activación**: Frame medio de la animación

### 🔥 Ataque 2 - Golpe Incendiario
- **Daño**: 10 puntos + quemadura
- **Alcance**: 100x80 píxeles (mayor que ataque 1)
- **Velocidad**: Moderada
- **Efecto Especial**: **Quemadura** - 8 puntos durante 4 segundos
- **Frames de Activación**: 60% de la animación
- **Cooldown**: 30 frames entre aplicaciones de quemadura

### ⚡ Ataque 3 - Golpe Devastador
- **Daño**: 15 puntos
- **Alcance**: 120x90 píxeles (el mayor del Warrior)
- **Velocidad**: Lenta
- **Efecto**: Máximo daño directo
- **Frames de Activación**: 70% de la animación
- **Knockback**: Alto empuje

## 🎨 Estructura de Sprites

```
warrior/Sprites/
├── idle/           # Animación de reposo
├── run/            # Animación de carrera
├── jump_down/      # Animación de caída
├── jump_up/        # Animación de salto
├── 1_atk/          # Ataque básico
├── 2_atk/          # Ataque incendiario
├── 3_atk/          # Ataque devastador
├── take_hit/       # Animación de recibir daño
└── death/          # Animación de muerte
```

## 🔥 Sistema de Quemadura

### Mecánica
- **Activación**: Solo con Ataque 2
- **Daño Total**: 8 puntos repartidos en 4 segundos
- **Intervalo**: Cada 60 frames (1 segundo)
- **Acumulación**: No se acumula, se renueva la duración

### Implementación Técnica
```python
# Aplicación del efecto
target.apply_burn_effect(8, 240)  # 8 damage, 240 frames (4 seconds)

# Procesamiento por frame
if self.burn_timer > 0:
    if self.burn_counter >= self.burn_interval:
        damage_per_interval = max(1, self.burn_damage_remaining // intervals)
        self.apply_damage(damage_per_interval)
```

## ⚙️ Características Técnicas

### Controles por Defecto
- **Jugador 1**: A/D (movimiento), W (salto), R/T/Y (ataques)
- **Jugador 2**: ←/→ (movimiento), ↑ (salto), 1/2/3 (ataques)

### Física
- **Gravedad**: 2 puntos por frame
- **Fuerza de Salto**: -30 píxeles por frame
- **Colisión**: Rectángulo centrado en el sprite

### Audio
- **Efecto de Sonido**: `sword.wav`
- **Volumen**: 50%
- **Activación**: En cada ataque ejecutado

## 🎯 Estrategia y Uso

### Fortalezas
- ✅ **Alta resistencia** - Más HP que cualquier otro personaje
- ✅ **Daño sostenido** - Quemadura proporciona daño a largo plazo
- ✅ **Versatilidad** - Tres ataques con diferentes propósitos
- ✅ **Fácil de usar** - Mecánicas directas y comprensibles

### Debilidades
- ❌ **Velocidad limitada** - Más lento que Assassin y Trapper
- ❌ **Sin ataques a distancia** - Debe acercarse al enemigo
- ❌ **Dependiente de quemadura** - Menor burst damage que otros
- ❌ **Cooldowns** - Limitado por tiempos de recarga

### Matchups
- **vs Assassin**: Favorable - Su HP alto contrarresta el burst del Assassin
- **vs Slime Demon**: Neutral - Intercambio equilibrado de daño
- **vs Tank**: Desfavorable - El Tank tiene mejor knockback
- **vs Trapper**: Desfavorable - Problemas con ataques a distancia

## 🔧 Configuración Avanzada

### Modificación de Daño
```python
def calculate_attack_damage(self):
    if self.current_attack_type == 1:
        return 8   # Ataque básico
    elif self.current_attack_type == 2:
        return 10  # Ataque incendiario
    elif self.current_attack_type == 3:
        return 15  # Ataque devastador
```

### Ajuste de Hitboxes
```python
# Área de ataque variable según el tipo
attack_areas = {
    1: (90, 70),   # Básico
    2: (100, 80),  # Incendiario (mayor)
    3: (120, 90)   # Devastador (máximo)
}
```

## 📈 Historial de Cambios

### v1.3 (Actual)
- Optimización de hitboxes para mejor balance
- Ajuste de daño de quemadura (8 puntos en 4 segundos)
- Mejora en la progresión de áreas de ataque

### v1.2
- Implementación del sistema de quemadura
- Balanceo de daño base de ataques
- Corrección de animaciones

### v1.1
- Ajuste de velocidad de movimiento
- Optimización de colisiones
- Mejora en efectos de sonido

---

**Desarrollado para Dungeon Fighters - Enhanced Edition**  
**Clase implementada en**: `fighters/warrior_fighter.py`  
**Última actualización**: Noviembre 2025