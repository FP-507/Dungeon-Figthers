# 🐉 Slime Demon Fighter - Documentación Técnica

## 📋 Información General

**Clase**: `SlimeDemonFighter`  
**Tipo**: Mago proyectilista con control de área  
**Rol**: DPS a distancia con mecánicas únicas  
**Dificultad**: ⭐⭐⭐☆☆ (Intermedio)

## 📊 Estadísticas Base

| Atributo | Valor | Descripción |
|----------|-------|-------------|
| **Salud Máxima** | 80 HP | Salud moderada |
| **Velocidad** | 12 | Velocidad estándar |
| **Tamaño Sprite** | 150x150 px | Escala 3.2x (compacto) |
| **Hitbox** | 90x190 px | Hitbox alta pero estrecha |

## 📊 Estadísticas Ajustadas (v1.3)

- **Tamaño reducido**: De 180px a 150px (más balanceado)
- **Escala optimizada**: De 4x a 3.2x para mejor proporción
- **Hitbox ajustada**: De 110x220 a 90x190 (menos área vulnerable)

## ⚔️ Sistema de Ataques

### 🌊 Ataque 1 - Tentáculo Básico
- **Daño**: 7 puntos
- **Alcance**: 85x65 píxeles
- **Tipo**: Cuerpo a cuerpo directo
- **Velocidad**: Rápida
- **Frames de Activación**: Frame medio de la animación

### 🔮 Ataque 2 - Gotas de Lava
- **Daño**: 6 puntos por proyectil
- **Tipo**: Proyectil parabólico
- **Cantidad**: 1 proyectil por ataque
- **Alcance**: Medio-largo
- **Velocidad Inicial**: (8, -12) píxeles por frame
- **Gravedad**: 0.8 píxeles por frame²
- **Efecto**: Proyectil con física realista

### 💥 Ataque 3 - Explosión de Área
- **Daño**: 12 puntos
- **Tipo**: Área de efecto retardada
- **Zona**: 150x100 píxeles
- **Delay**: 30 frames después de activación
- **Efecto**: Explosión en área fija frente al personaje
- **Frames de Activación**: 80% de la animación

## 🎨 Estructura de Sprites

```
slime_demon/Sprites/
├── idle/           # Animación de reposo
├── run/            # Animación de carrera
├── jump_down/      # Animación de caída
├── jump_up/        # Animación de salto
├── 1_atk/          # Ataque tentáculo
├── 2_atk/          # Lanzamiento de lava
├── 3_atk/          # Explosión de área
├── take_hit/       # Animación de recibir daño
└── death/          # Animación de muerte
```

## 🌋 Sistema de Proyectiles - Gotas de Lava

### Clase LavaDropProjectile

```python
class LavaDropProjectile(BaseProjectile):
    def __init__(self, x, y, velocity_x, velocity_y, damage, frames, target):
        # Proyectil con física parabólica
        self.gravity = 0.8
        self.bounce_factor = 0.6
        self.max_bounces = 2
```

### Mecánicas Avanzadas
- **Trayectoria Parabólica**: Afectada por gravedad realista
- **Rebotes**: Hasta 2 rebotes con factor 0.6
- **Colisión Inteligente**: Detecta suelo y objetivos
- **Sprites Animados**: Rotación durante el vuelo

### Estados del Proyectil
1. **Vuelo**: Movimiento parabólico con gravedad
2. **Rebote**: Reducción de velocidad al tocar suelo
3. **Impacto**: Colisión con objetivo o muerte natural

## 💥 Sistema de Explosión de Área

### Mecánica Única
- **Delay Temporal**: 30 frames entre activación y daño
- **Área Fija**: 150x100 píxeles frente al personaje
- **Indicador Visual**: Rectángulo naranja durante debug
- **No Acumulativo**: Una explosión por ataque

### Implementación
```python
# Activación retardada
if self.frame_index == explosion_frame and not self.attack3_explosion_triggered:
    self.attack3_explosion_triggered = True
    self.attack3_explosion_timer = 30  # Delay de explosión

# Ejecución de daño
if self.attack3_explosion_timer == 1:
    if explosion_rect.colliderect(target.collision_rect):
        target.apply_damage(12)
```

## ⚙️ Características Técnicas

### Controles por Defecto
- **Jugador 1**: A/D (movimiento), W (salto), R/T/Y (ataques)
- **Jugador 2**: ←/→ (movimiento), ↑ (salto), 1/2/3 (ataques)

### Audio
- **Efecto de Sonido**: `magic.wav`
- **Volumen**: 75% (más alto que sword)
- **Tipo**: Efectos mágicos

### Física Especial
- **Proyectiles**: Gravedad 0.8, rebotes hasta 2 veces
- **Explosiones**: Área fija, delay de 30 frames
- **Movimiento**: Estándar con hitbox optimizada

## 🎯 Estrategia y Uso

### Fortalezas
- ✅ **Control de área** - Explosión de área y proyectiles
- ✅ **Ataques a distancia** - No necesita acercarse
- ✅ **Versatilidad** - Cuerpo a cuerpo + proyectiles + AoE
- ✅ **Crowd control** - Explosión maneja múltiples enemigos

### Debilidades
- ❌ **HP moderado** - Menos resistente que Warrior y Tank
- ❌ **Proyectiles predecibles** - Trayectoria parabólica fija
- ❌ **Delay en explosión** - Enemigos pueden escapar
- ❌ **Dependiente de distancia** - Vulnerable en combate cercano

### Matchups
- **vs Warrior**: Favorable - Mantener distancia y usar proyectiles
- **vs Assassin**: Neutral - Velocidad vs control de área
- **vs Tank**: Favorable - Proyectiles evitan el knockback
- **vs Trapper**: Desfavorable - Menor movilidad vs trampas

## 🔧 Configuración Avanzada

### Ajuste de Proyectiles
```python
# Velocidad inicial de gotas de lava
initial_velocity = (8, -12)  # (horizontal, vertical)
gravity = 0.8
bounce_factor = 0.6
max_bounces = 2
```

### Modificación de Explosión
```python
# Área de explosión
explosion_width = 150
explosion_height = 100
explosion_delay = 30  # frames
```

### Optimización de Hitbox
```python
# Hitbox más pequeña y balanceada
self.collision_rect.width = 90   # Reducido de 110
self.collision_rect.height = 190  # Reducido de 220
```

## 📈 Historial de Cambios

### v1.3 (Actual)
- **Rebalanceo mayor**: Tamaño reducido de 180px a 150px
- **Escala optimizada**: De 4x a 3.2x para mejor proporción
- **Hitbox mejorada**: De 110x220 a 90x190 píxeles
- **Eliminación de elementos debug**: Círculos naranjas removidos

### v1.2
- Implementación del sistema de rebotes en proyectiles
- Optimización de la explosión de área
- Mejora en colisiones de proyectiles

### v1.1
- Sistema de proyectiles con física parabólica
- Explosión retardada para balance
- Efectos de sonido mágicos

## 🐛 Notas de Debug

### Elementos Removidos
- **Círculos naranjas**: Fallback visual eliminado en v1.3
- **Indicadores de explosión**: Rectángulos de debug opcionales
- **Proyectiles simples**: Solo sprites, sin formas geométricas

### Performance
- **Proyectiles**: Máximo 5 simultáneos por eficiencia
- **Rebotes**: Limitados a 2 para evitar bucles infinitos
- **Explosiones**: Una por ataque para prevenir spam

---

**Desarrollado para Dungeon Fighters - Enhanced Edition**  
**Clase implementada en**: `fighters/slime_demon_fighter.py`  
**Última actualización**: Noviembre 2025