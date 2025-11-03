# 🛡️ Tank Fighter - Documentación Técnica

## 📋 Información General

**Clase**: `TankFighter`  
**Tipo**: Tank pesado con knockback masivo  
**Rol**: Controlador de espacio y disruptor  
**Dificultad**: ⭐⭐⭐☆☆ (Intermedio-Avanzado)

## 📊 Estadísticas Base

| Atributo | Valor | Descripción |
|----------|-------|-------------|
| **Salud Máxima** | 120 HP | La más alta del juego |
| **Velocidad** | 10 | Lenta pero imparable |
| **Tamaño Sprite** | 140x140 px | Escala 3.5x |
| **Hitbox** | 85x120 px | Compacta pero sólida |

## 📊 Estadísticas Balanceadas (v1.3)

- **Hitbox optimizada**: De múltiples iteraciones a 85x120 final
- **Sistema de knockback progresivo**: 60 → 90 → 160
- **Daño escalado**: 9 → 12 → 15 puntos
- **Timing perfeccionado**: 50% → 85% → 90%

## ⚔️ Sistema de Ataques Progresivos

### 🥊 Ataque 1 - Golpe Básico
- **Daño**: 9 puntos
- **Área**: 100x130 píxeles
- **Knockback**: 60 píxeles (moderado)
- **Timing**: 50% de la animación (rápido)
- **Tipo**: Ataque de entrada, rápido y confiable

### 💥 Ataque 2 - Impacto Medio
- **Daño**: 12 puntos
- **Área**: 170x180 píxeles (significativamente mayor)
- **Knockback**: 90 píxeles (alto)
- **Timing**: 85% de la animación (más lento)
- **Tipo**: Ataque intermedio con control de espacio

### 🌟 Ataque 3 - Devastación Total
- **Daño**: 15 puntos (máximo del juego)
- **Área**: 200x240 píxeles (enorme)
- **Knockback**: 160 píxeles (extremo)
- **Timing**: 90% de la animación (lento pero letal)
- **Tipo**: Finalizador con control de área masivo

## 🎨 Estructura de Sprites

```
tank/Sprites/
├── idle/                   # Animación de reposo
├── run/                    # Animación de carrera (pesada)
├── jump_down/              # Animación de caída
├── jump_up/                # Animación de salto
├── 1_atk/                  # Golpe básico
├── 2_atk/                  # Impacto medio
├── 3_atk/                  # Devastación total
├── take_hit/               # Animación de recibir daño
└── death/                  # Animación de muerte
```

## 💫 Sistema de Knockback Progresivo

### Filosofía del Diseño
El Tank utiliza **knockback como mecánica principal**:
- Cada ataque empuja más que el anterior
- Control de espacio más importante que daño puro
- Permite combos de reposicionamiento

### Mecánica de Knockback
```python
# Aplicación de knockback
knockback_force = {
    1: 60,   # Básico - reposicionamiento moderado
    2: 90,   # Intermedio - control significativo
    3: 160   # Extremo - lanza al otro lado del escenario
}

# Implementación
def apply_knockback(self, target, force):
    direction = 1 if target.collision_rect.centerx > self.collision_rect.centerx else -1
    target.collision_rect.x += force * direction
```

### Progresión de Áreas
- **Ataque 1**: 100x130 - Área básica para acercamiento
- **Ataque 2**: 170x180 - Control de espacio medio
- **Ataque 3**: 200x240 - Dominación total del área

## ⚙️ Balanceo Extensivo (Historial)

### Iteraciones de Hitbox
1. **Inicial**: 75x140 (muy estrecha)
2. **v1.1**: 85x120 (más cuadrada)
3. **v1.2**: Múltiples ajustes de áreas de ataque
4. **v1.3**: Balance final con progresión clara

### Iteraciones de Daño
1. **Inicial**: Daño alto uniforme
2. **v1.2**: Sistema progresivo 9/12/15
3. **v1.3**: Refinamiento de knockback y timing

## ⚙️ Características Técnicas

### Controles por Defecto
- **Jugador 1**: A/D (movimiento), W (salto), R/T/Y (ataques)
- **Jugador 2**: ←/→ (movimiento), ↑ (salto), 1/2/3 (ataques)

### Física Especializada
- **Velocidad Baja**: 10 (compensada por alcance)
- **Hitbox Sólida**: 85x120 - difícil de rodear
- **Peso Conceptual**: Movimiento pesado pero imparable

### Audio
- **Efecto de Sonido**: `sword.wav`
- **Volumen**: 50%
- **Estilo**: Impactos pesados y contundentes

## 🎯 Estrategia y Uso

### Fortalezas
- ✅ **HP Máximo** - 120 HP, el más resistente
- ✅ **Control de Espacio** - Knockback masivo reposiciona enemigos
- ✅ **Daño Máximo** - 15 puntos en ataque 3 (récord del juego)
- ✅ **Áreas Enormes** - 200x240 píxeles en ataque final
- ✅ **Progresión Clara** - Cada ataque mejora al anterior

### Debilidades
- ❌ **Velocidad Baja** - 10 vs 12+ de otros personajes
- ❌ **Timing Lento** - Ataques 2 y 3 son predecibles
- ❌ **Sin Efectos Especiales** - Solo daño y knockback
- ❌ **Vulnerable a Kiting** - Problemas vs enemigos rápidos
- ❌ **Cooldowns** - No puede spamear ataques fuertes

### Matchups Detallados

#### vs Warrior (Favorable)
- **Estrategia**: Intercambio directo, usar HP superior
- **Ventaja**: Knockback interrumpe combos de quemadura
- **Táctica**: Ataque 3 para dominar el centro

#### vs Slime Demon (Neutral)
- **Estrategia**: Cerrar distancia, presionar con knockback
- **Problema**: Proyectiles parabólicos difíciles de evitar
- **Táctica**: Usar ataque 2 para interrumpir cast de explosión

#### vs Assassin (Muy Favorable)
- **Estrategia**: Un solo combo mata al Assassin (75 HP)
- **Ventaja**: Knockback rompe cadenas de combo
- **Táctica**: Timing defensivo, luego contraataque devastador

#### vs Trapper (Desfavorable)
- **Estrategia**: Agresión temprana antes de setup de trappas
- **Problema**: Velocidad baja vs movilidad del Trapper
- **Táctica**: Sacrificar HP para cerrar distancia

## 🔧 Configuración Avanzada

### Sistema de Progresión
```python
# Daño progresivo
damage_values = [9, 12, 15]  # Escalado lineal +3

# Áreas progresivas
attack_areas = {
    1: (100, 130),  # Base
    2: (170, 180),  # +70/+50 - gran salto
    3: (200, 240)   # +30/+60 - área máxima
}

# Knockback progresivo
knockback_forces = [60, 90, 160]  # Escalado exponencial
```

### Timing Balanceado
```python
# Frames de activación progresivos
activation_timing = {
    1: 0.5,   # 50% - rápido
    2: 0.85,  # 85% - lento
    3: 0.9    # 90% - muy lento pero devastador
}
```

### Optimización de Hitbox
```python
# Balance final después de múltiples iteraciones
self.collision_rect.width = 85   # Ni muy ancha ni muy estrecha
self.collision_rect.height = 120  # Proporción equilibrada
```

## 📊 Análisis de Efectividad

### Daño Total por Combo
- **3 Ataques Seguidos**: 36 puntos (9+12+15)
- **Knockback Total**: 310 píxeles de desplazamiento
- **Tiempo Total**: ~4-5 segundos (lento pero letal)

### Control de Espacio
- **Área Dominada**: Hasta 200x240 píxeles
- **Reposicionamiento**: Hasta 160 píxeles por ataque
- **Zona de Peligro**: Centro del escenario

### Comparativa de HP-to-Kill
- **vs Assassin (75 HP)**: 2-3 ataques (muy favorable)
- **vs Slime Demon (80 HP)**: 3 ataques (favorable)
- **vs Warrior (100 HP)**: 3-4 ataques (equilibrado)
- **vs Trapper (70 HP)**: 2-3 ataques (si alcanza)

## 📈 Historial de Cambios

### v1.3 (Actual)
- **Balance final**: Sistema progresivo 9/12/15 daño
- **Knockback optimizado**: 60/90/160 progresión
- **Áreas refinadas**: 100x130, 170x180, 200x240
- **Timing perfeccionado**: 50%/85%/90%
- **Efecto berserker removido**: Sin elementos visuales adicionales

### v1.2
- **Múltiples iteraciones**: Ajustes de hitbox y áreas
- **Sistema de knockback**: Implementación progresiva
- **Balance de daño**: Primer sistema progresivo

### v1.1
- **Hitbox inicial**: 75x140 → 85x120
- **Mecánicas básicas**: Ataques con knockback
- **Audio y efectos**: Implementación inicial

## 🎮 Guía de Juego

### Para Principiantes
1. **Usa HP**: No temas recibir daño, eres el más resistente
2. **Centro del escenario**: Domina el espacio central
3. **Progresión**: 1→2→3 para máximo efecto

### Para Avanzados
1. **Timing defensivo**: Espera el momento perfecto
2. **Control de espacio**: Usa knockback para reposicionar
3. **Mind games**: Amenaza con ataque 3 para controlar movimiento

---

**Desarrollado para Dungeon Fighters - Enhanced Edition**  
**Clase implementada en**: `fighters/tank_fighter.py`  
**Última actualización**: Noviembre 2025