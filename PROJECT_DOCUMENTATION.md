# 🎮 Dungeon Fighters - Enhanced Edition
## Documentación General del Proyecto

---

## 📋 Información del Proyecto

**Nombre**: Dungeon Fighters - Enhanced Edition  
**Versión**: 1.3  
**Lenguaje**: Python 3.13  
**Framework**: Pygame 2.6.1  
**Tipo**: Juego de lucha 2D  
**Desarrollado**: Noviembre 2025  

---

## 🎯 Descripción General

Dungeon Fighters es un juego de lucha 2D avanzado que presenta combate táctico entre múltiples personajes únicos. Cada luchador tiene mecánicas especializadas, desde ataques cuerpo a cuerpo hasta sistemas complejos de proyectiles y control de área.

### Características Principales
- ✅ **5 Personajes Únicos** con mecánicas completamente diferentes
- ✅ **Sistema de Combate Avanzado** con efectos de estado
- ✅ **Sprites Frame-by-Frame** cargados dinámicamente
- ✅ **Cámara Dinámica** con seguimiento inteligente
- ✅ **Sistema de Rondas** con puntuación persistente
- ✅ **Selección de Personajes** con preview visual
- ✅ **Audio Integrado** con efectos por personaje
- ✅ **Debug Mode** con visualización de hitboxes

---

## 🏗️ Arquitectura del Proyecto

```
Dungeon-Figthers/
├── main.py                     # Archivo principal del juego
├── character_select.py         # Sistema de selección de personajes
├── README.md                   # Documentación básica
├── PROJECT_DOCUMENTATION.md    # Esta documentación
│
├── fighters/                   # Módulo de personajes
│   ├── __init__.py
│   ├── base_fighter.py         # Clase padre de todos los luchadores
│   ├── warrior_fighter.py      # Guerrero con quemadura
│   ├── slime_demon_fighter.py  # Demonio con proyectiles
│   ├── assassin_fighter.py     # Asesino con combos
│   ├── tank_fighter.py         # Tanque con knockback
│   ├── trapper_fighter.py      # Cazador con trampas
│   ├── WARRIOR_DOCUMENTATION.md
│   ├── SLIME_DEMON_DOCUMENTATION.md
│   ├── ASSASSIN_DOCUMENTATION.md
│   ├── TANK_DOCUMENTATION.md
│   └── TRAPPER_DOCUMENTATION.md
│
└── assets/                     # Recursos del juego
    ├── audio/
    │   ├── music.mp3
    │   ├── sword.wav
    │   └── magic.wav
    ├── fonts/
    │   └── turok.ttf
    └── images/
        ├── background/
        ├── icons/
        ├── warrior/Sprites/
        ├── slime_demon/Sprites/
        ├── assasin/Sprites/      # Nota: typo histórico
        ├── tank/Sprites/
        └── trapper/Sprites/
```

---

## 🎮 Personajes Disponibles

### 🗡️ Warrior - El Equilibrado
- **HP**: 100 (Alto) | **Velocidad**: 12 (Media) | **Dificultad**: ⭐⭐☆☆☆
- **Especialidad**: Tanque-DPS con quemadura
- **Ataques**: Básico (8) → Incendiario (10+DoT) → Devastador (15)
- **Efecto Único**: **Quemadura** - 8 daño en 4 segundos

### 🐉 Slime Demon - El Proyectilista  
- **HP**: 80 (Medio) | **Velocidad**: 12 (Media) | **Dificultad**: ⭐⭐⭐☆☆
- **Especialidad**: Mago con control de área
- **Ataques**: Tentáculo (7) → Gotas de Lava (6) → Explosión AoE (12)
- **Efecto Único**: **Proyectiles Parabólicos** con rebotes

### ⚡ Assassin - El Velocista
- **HP**: 75 (Bajo) | **Velocidad**: 14 (Alta) | **Dificultad**: ⭐⭐⭐⭐☆
- **Especialidad**: Burst damage con combos
- **Ataques**: Corte Rápido (6) → Combo Doble (8) → Finalizador (12)
- **Efecto Único**: **Ataques Consecutivos** con progresión de daño

### 🛡️ Tank - El Imparable
- **HP**: 120 (Máximo) | **Velocidad**: 10 (Baja) | **Dificultad**: ⭐⭐⭐☆☆
- **Especialidad**: Control de espacio con knockback
- **Ataques**: Básico (9) → Impacto (12) → Devastación (15)
- **Efecto Único**: **Knockback Progresivo** - 60/90/160 píxeles

### 🪤 Trapper - El Elusivo
- **HP**: 70 (Mínimo) | **Velocidad**: 16 (Máxima) | **Dificultad**: ⭐⭐⭐⭐⭐
- **Especialidad**: Control de área y ataques dirigidos
- **Ataques**: Sangrado (5+6DoT) → Trampa (8+Stun) → Proyectil (4)
- **Efectos Únicos**: **Sangrado**, **Trampas Persistentes**, **Proyectiles Rotativos**

---

## ⚙️ Sistemas del Juego

### 🎯 Sistema de Combate

#### Mecánicas Base
- **Colisión por Rectángulos**: Hitboxes precisas para cada personaje
- **Animaciones Frame-Perfect**: Timing específico para cada ataque
- **Efectos de Estado**: Quemadura, sangrado, stun
- **Proyectiles Físicos**: Gravedad, rebotes, colisiones realistas

#### Efectos de Estado
| Efecto | Duración | Daño | Intervalo | Personaje |
|--------|----------|------|-----------|-----------|
| **Quemadura** | 4 seg | 8 total | 60 frames | Warrior |
| **Sangrado** | 4 seg | 6 total | 45 frames | Trapper |
| **Stun** | 0.75 seg | - | - | Trapper |

### 🎮 Controles

#### Jugador 1
- **Movimiento**: A (izquierda), D (derecha)
- **Salto**: W
- **Ataques**: R (Ataque 1), T (Ataque 2), Y (Ataque 3)

#### Jugador 2
- **Movimiento**: ← (izquierda), → (derecha)
- **Salto**: ↑
- **Ataques**: 1 (Ataque 1), 2 (Ataque 2), 3 (Ataque 3)

#### Controles Globales
- **Z**: Toggle hitboxes (modo debug)
- **ESC**: Cancelar selección
- **ENTER**: Nueva ronda

### 📱 Sistema de Cámara

#### Seguimiento Dinámico
- **Punto Focal**: Centro entre ambos luchadores
- **Suavizado**: Transiciones fluidas con velocidad 0.15
- **Límites**: Previene mostrar áreas vacías
- **Offset**: ±300 píxeles máximo

### 🎵 Sistema de Audio

#### Música
- **Archivo**: `music.mp3`
- **Volumen**: 50%
- **Loop**: Infinito con fade-in

#### Efectos de Sonido
- **Sword**: Warrior, Assassin, Tank, Trapper (50%)
- **Magic**: Slime Demon (75%)

---

## 🔧 Características Técnicas

### 📊 Rendimiento
- **FPS**: 60 constantes
- **Resolución**: 1400x600 (escenario amplio)
- **Sprites**: Carga lazy, escalado dinámico
- **Memoria**: Gestión automática de proyectiles

### 🎨 Sistema de Sprites

#### Estructura Universal
```
[personaje]/Sprites/
├── idle/           # Reposo
├── run/            # Carrera  
├── jump_up/        # Salto ascendente
├── jump_down/      # Caída
├── 1_atk/          # Ataque primario
├── 2_atk/          # Ataque secundario
├── 3_atk/          # Ataque terciario
├── take_hit/       # Recibir daño
└── death/          # Muerte
```

#### Sprites Especiales (Trapper)
```
2_atk/
├── trap_throw/     # Trampa colocada
├── trap_land/      # Aterrizaje (3 frames)
└── trap_detonate/  # Explosión (5 frames)

3_atk/
├── projectile_throw/  # Proyectil volando
└── projectile_land/   # Impacto (5 frames)
```

### 🐛 Sistema de Debug

#### Modo Debug (Tecla Z)
- **Hitboxes**: Visualización de áreas de colisión
- **Áreas de Ataque**: Rectángulos de daño
- **Información de Frame**: Frame actual de ataque
- **Daño Aplicado**: Número de daño en tiempo real
- **Offset de Cámara**: Información de posicionamiento

---

## 🏆 Balance y Estrategia

### 📊 Tabla de Matchups

|           | Warrior | Slime | Assassin | Tank | Trapper |
|-----------|---------|-------|----------|------|---------|
| **Warrior**   | = | = | ✓ | ✗ | ✗ |
| **Slime**     | = | = | = | ✓ | = |
| **Assassin**  | ✗ | = | = | ✗✗ | ✓ |
| **Tank**      | ✓ | ✗ | ✓✓ | = | ✗ |
| **Trapper**   | ✓ | = | ✗ | ✓ | = |

**Leyenda**: ✓✓ Muy Favorable | ✓ Favorable | = Neutral | ✗ Desfavorable | ✗✗ Muy Desfavorable

### 🎯 Filosofías de Diseño

#### Rock-Paper-Scissors Extendido
- **Tank** domina **Assassin** (HP vs Burst)
- **Assassin** domina **Warrior** (Velocidad vs Resistencia)  
- **Trapper** domina **Tank** (Movilidad vs Lentitud)
- **Proyectilistas** dominan **Melees** (Rango vs Proximidad)

#### Especializaciones Únicas
- **Warrior**: Tanque híbrido con sustain
- **Slime Demon**: Control de área con proyectiles
- **Assassin**: Glass cannon con combos
- **Tank**: Disruptor con knockback masivo
- **Trapper**: Zoner elusivo con setup

---

## 🚀 Instalación y Ejecución

### Requisitos del Sistema
- **Python**: 3.13+
- **Pygame**: 2.6.1+
- **Sistema Operativo**: Windows/Linux/Mac
- **RAM**: 512MB mínimo
- **Espacio**: 100MB para assets

### Instalación
```bash
# Clonar repositorio
git clone https://github.com/FP-507/Dungeon-Figthers.git
cd Dungeon-Figthers

# Instalar dependencias
pip install pygame

# Ejecutar juego
python main.py
```

### Estructura de Archivos Requerida
- ✅ Todos los sprites en `assets/images/[personaje]/Sprites/`
- ✅ Audio en `assets/audio/`
- ✅ Fuentes en `assets/fonts/`
- ✅ Módulo `fighters/` completo

---

## 📈 Historial de Versiones

### v1.3 (Actual - Noviembre 2025)
#### Nuevas Características
- ✅ **Trapper Fighter**: Personaje completamente nuevo con mecánicas únicas
- ✅ **Sistema de Sangrado**: DoT más rápido que quemadura
- ✅ **Proyectiles Rotativos**: Apuntan automáticamente al enemigo
- ✅ **Trampas Inteligentes**: Estados múltiples con detección precisa

#### Balanceo Mayor
- 🔄 **Slime Demon**: Reducido de 180px a 150px, hitbox optimizada
- 🔄 **Tank**: Sistema progresivo 9/12/15 daño, knockback 60/90/160
- 🔄 **Assassin**: Progresión de áreas 75x60 → 85x70 → 95x80
- 🔄 **Warrior**: Quemadura rebalanceada a 8 puntos en 4 segundos

#### Mejoras Técnicas
- 🔧 **Eliminación de Debug**: Círculos y elementos visuales removidos
- 🔧 **Sprites Originales**: Solo PNG de carpetas, sin generación por código
- 🔧 **Performance**: Optimización de carga de sprites
- 🔧 **Audio**: Volúmenes balanceados

### v1.2 (Octubre 2025)
- ✅ Tank Fighter con sistema de knockback
- ✅ Assassin Fighter con ataques consecutivos
- ✅ Sistema de efectos de estado (quemadura)
- ✅ Cámara dinámica con seguimiento

### v1.1 (Septiembre 2025)
- ✅ Slime Demon Fighter con proyectiles
- ✅ Sistema base de combate
- ✅ Selección de personajes
- ✅ Audio integrado

### v1.0 (Agosto 2025)
- ✅ Warrior Fighter básico
- ✅ Sistema de sprites frame-by-frame
- ✅ Mecánicas de movimiento y salto
- ✅ Estructura base del proyecto

---

## 🎯 Roadmap Futuro

### Características Planificadas
- 🔮 **Modo Torneo**: Bracket elimination
- 🔮 **Personajes Adicionales**: Archer, Mage, Berserker
- 🔮 **Escenarios Múltiples**: Diferentes backgrounds con hazards
- 🔮 **Modo Online**: Multijugador por red
- 🔮 **Sistema de Unlocks**: Desbloqueables y logros

### Mejoras Técnicas
- 🔧 **Netcode**: Rollback networking
- 🔧 **Replay System**: Grabación y reproducción
- 🔧 **Frame Data Display**: Información técnica avanzada
- 🔧 **Modding Support**: Personajes personalizados

---

## 👥 Créditos y Reconocimientos

### Desarrollo
- **Programación Principal**: Asistente IA especializado
- **Diseño de Personajes**: Colaboración usuario-IA
- **Balance**: Iterativo basado en feedback
- **Documentación**: Generada automáticamente

### Assets
- **Sprites**: Proporcionados por el usuario
- **Audio**: Recursos libres
- **Fuentes**: Turok.ttf (licencia libre)

### Tecnologías
- **Python**: Lenguaje principal
- **Pygame**: Framework de juegos 2D
- **Git**: Control de versiones

---

## 📞 Soporte y Contribución

### Reportar Bugs
- **GitHub Issues**: Crear issue detallado
- **Información requerida**: Versión, sistema, pasos para reproducir

### Contribuir
- **Pull Requests**: Bienvenidos con documentación
- **Nuevos Personajes**: Seguir estructura establecida
- **Balance**: Propuestas con justificación

### Community
- **Discord**: [Pendiente]
- **Reddit**: [Pendiente]  
- **YouTube**: [Pendiente]

---

## 📜 Licencia

**Tipo**: Open Source  
**Detalles**: [Pendiente especificar]  
**Uso Comercial**: [Pendiente autorización]

---

## 🎉 ¡Gracias por Jugar!

Dungeon Fighters - Enhanced Edition es un proyecto de pasión que combina mecánicas de combate profundas con sistemas únicos para cada personaje. Cada luchador ha sido cuidadosamente diseñado para ofrecer una experiencia de juego completamente diferente.

**¡Que comience la batalla!** ⚔️

---

*Documentación generada automáticamente - Noviembre 2025*  
*Dungeon Fighters Enhanced Edition v1.3*