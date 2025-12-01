# 🎮 Dungeon Fighters
Un juego de lucha 2D competitivo multijugador local con 5 personajes únicos, mecánicas especializadas, y profundidad estratégica.

## 🎯 Descripción Rápida

Dungeon Fighters es un juego de lucha 2D emocionante que combina:
- **5 Personajes Únicos** con roles especializados
- **Sistema de Escudo Defensivo** con cooldown y absorción de daño
- **Movimiento Normalizado** para control consistente
- **Ataques Dinámicos** con efectos de estado
- **Proyectiles Avanzados** con física realista
- **Selección de Escenarios** antes de cada ronda

## 🚀 Inicio Rápido

### Requisitos

- **Python**: 3.13 o superior
- **Pygame**: 2.6.1
- **OS**: Windows, Linux o macOS
- **RAM**: 512 MB mínimo

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/FP-507/Dungeon-Figthers.git
cd Dungeon-Figthers

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar el juego
python main.py
```

## 🎮 Controles

### Jugador 1 (WASD)

| Acción | Tecla |
|--------|-------|
| Izquierda | A |
| Derecha | D |
| Saltar | W |
| Escudo | S |
| Ataque 1 | R |
| Ataque 2 | T |
| Ataque 3 | Y |

### Jugador 2 (Flechas + Numpad)

| Acción | Tecla |
|--------|-------|
| Izquierda | ← |
| Derecha | → |
| Saltar | ↑ |
| Escudo | ↓ |
| Ataque 1 | KP1 |
| Ataque 2 | KP2 |
| Ataque 3 | KP3 |

### Controles Globales

| Acción | Tecla |
|--------|-------|
| Debug (Hitboxes) | Z |
| Cancelar | ESC |
| Nueva Ronda | ENTER |

## 🎭 Personajes

### 🗡️ Warrior
- **HP**: 100 | **Velocidad**: 12 | **Dificultad**: ⭐⭐
- **Especialidad**: Tanque híbrido con quemadura
- **Descripción**: Personaje equilibrado ideal para principiantes

### 🐉 SlimeDemon
- **HP**: 80 | **Velocidad**: 12 | **Dificultad**: ⭐⭐⭐
- **Especialidad**: Proyectilista de control de área
- **Descripción**: Domina a distancia con proyectiles parabólicos

### ⚡ Assassin
- **HP**: 75 | **Velocidad**: 14 | **Dificultad**: ⭐⭐⭐⭐
- **Especialidad**: Glass cannon con combos rápidos
- **Descripción**: Requiere precisión pero ofrece daño explosivo

### 🛡️ Tank
- **HP**: 120 | **Velocidad**: 10 | **Dificultad**: ⭐⭐⭐
- **Especialidad**: Disruptor con knockback masivo
- **Descripción**: Controla el espacio y domina el close-range

### 🪤 Trapper
- **HP**: 70 | **Velocidad**: 16 | **Dificultad**: ⭐⭐⭐⭐⭐
- **Especialidad**: Zoner elusivo con setup
- **Descripción**: Máxima complejidad pero gran potencial

## 🛡️ Sistema de Escudo

Todos los personajes cuentan con un sistema defensivo avanzado:

- **Salud**: 20 HP (20% de HP máximo)
- **Absorción**: Recibe 75% del daño entrante
- **Penetración**: El 25% atraviesa al personaje
- **Cooldown**: 5 segundos después de romperse
- **Activación**: Mantener presionada la tecla de escudo

### Ejemplo

```
Ataque enemigo: 20 de daño
↓
Escudo recibe: 15 de daño (75%)
Personaje recibe: 5 de daño (25%)
```

## 📊 Estados del Juego

```
CHARACTER_SELECT
    ↓ (Ambos jugadores seleccionan personaje)
SCENARIO_SELECT
    ↓ (Ambos seleccionan escenario o se elige aleatoriamente)
COUNTDOWN (3 segundos)
    ↓
FIGHTING (Combate principal)
    ↓
ROUND_OVER (Muestra ganador)
    ↓ (Regresa a SCENARIO_SELECT para nueva ronda)
```

## 💥 Mecánicas Principales

### Efectos de Estado

| Efecto | Duración | Daño | Personaje |
|--------|----------|------|-----------|
| **Quemadura** | 4s | 8 HP | Warrior |
| **Sangrado** | 4s | 6 HP | Trapper |
| **Stun** | 0.75s | - | Tank, Trapper |

### Proyectiles

- Física realista con gravedad
- Rebotes elásticos en el suelo
- Colisiones con enemigos
- Destrucción automática al salir de pantalla

### Normalización Diagonal

El juego normaliza automáticamente el movimiento diagonal para mantener velocidad consistente en todas las direcciones.

## 📁 Estructura del Proyecto

```
Dungeon-Figthers/
├── main.py                    # Bucle principal
├── character_select.py        # Selección de personajes
├── scenario_select.py         # Selección de escenarios
├── README.md                  # Este archivo
├── requirements.txt           # Dependencias
│
├── fighters/                  # Módulo de personajes
│   ├── base_fighter.py        # Clase padre
│   ├── warrior_fighter.py
│   ├── slime_demon_fighter.py
│   ├── assassin_fighter.py
│   ├── tank_fighter.py
│   └── trapper_fighter.py
│
└── assets/                    # Recursos
    ├── audio/
    │   ├── music.mp3
    │   ├── sword.wav
    │   └── magic.wav
    ├── fonts/
    │   └── turok.ttf
    └── images/
        ├── background/
        └── [personaje]/Sprites/
```

## 🎨 Desarrollo

### Requisitos de Desarrollo

```bash
pip install -r requirements.txt
```

### Estructura de Sprites

Cada personaje requiere carpetas en `assets/images/[personaje]/Sprites/`:

- `idle/` - Reposo
- `run/` - Carrera
- `jump_up/` - Salto ascendente
- `jump_down/` - Caída
- `1_atk/` - Ataque 1
- `2_atk/` - Ataque 2
- `3_atk/` - Ataque 3
- `take_hit/` - Recibir daño
- `death/` - Muerte

### Configuración Técnica

- **Resolución**: 1400x600 píxeles
- **FPS**: 60 constantes
- **Escala**: Dinámico según collision rect
- **Debug**: Tecla Z para visualizar hitboxes

## 🎓 Guía de Juego

### Para Principiantes

1. **Elige Warrior**: Es el más fácil de jugar
2. **Domina el Movimiento**: Practica saltar y esquivar
3. **Aprende los Ataques**: Cada uno tiene timing diferente
4. **Usa el Escudo**: Press S/DOWN para defender
5. **Predice**: Anticipa los movimientos del enemigo

### Estrategia Competitiva

- **Distancia**: Mantén el rango óptimo para tu personaje
- **Timing**: Usa el cooldown del escudo a tu favor
- **Combos**: Encadena ataques para máximo daño
- **Proyectiles**: Úsalos para control de área
- **Knockback**: Crea distancia cuando sea necesario

## 🐛 Troubleshooting

### El juego no inicia

```bash
# Verifica la versión de Python
python --version  # Debe ser 3.13+

# Reinstala las dependencias
pip install --upgrade -r requirements.txt

# Intenta ejecutar directamente
python -m pygame
```

### Sonido no funciona

- Verifica que `assets/audio/` tenga los archivos MP3/WAV
- Comprueba tu volumen del sistema
- Algunos sistemas pueden requerir codificadores adicionales

### Sprites no cargan

- Verifica que existan carpetas en `assets/images/[personaje]/Sprites/`
- Asegúrate de que todos los archivos PNG estén presentes
- Comprueba que los nombres de carpetas coincidan exactamente

## 📊 Balance

### Tabla de Matchups

|           | Warrior | SlimeDemon | Assassin | Tank | Trapper |
|-----------|---------|-----------|----------|------|---------|
| **Warrior**   | =   |    =      | ✓        | ✗    | ✗      |
| **SlimeDemon**| =   |   =       | =        | ✓    | =       |
| **Assassin**  | ✗  |  =         | =        | ✗✗  | ✓      |
| **Tank**      | ✓   |  ✗       | ✓✓       | =    | ✗      |
| **Trapper**   | ✓  |  =         | ✗        | ✓    | =      |

Leyenda: ✓✓ Muy Favorable | ✓ Favorable | = Neutral | ✗ Desfavorable | ✗✗ Muy Desfavorable

## 🎯 Roadmap Futuro

### Corto Plazo
- [ ] Inputs personalizables
- [ ] Modo práctica
- [ ] Estadísticas avanzadas

### Mediano Plazo
- [ ] Modo torneo
- [ ] Más escenarios
- [ ] Hazards ambientales

### Largo Plazo
- [ ] Multijugador online
- [ ] Personajes adicionales
- [ ] Sistema de progresión

## 📝 Notas Importantes

### Limitaciones

- Resolución fija: 1400x600
- Local multijugador solamente (v2.0)
- Requiere 2 controladores o teclado compartido

### Rendimiento

- Optimizado para 60 FPS constantes
- Gestión automática de memoria de proyectiles
- Carga dinámica de sprites

### Debugging

Presiona **Z** durante el juego para:
- Ver hitboxes (verde)
- Ver áreas de ataque (rojo)
- Información de frames
- Daño en tiempo real

## 👥 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 🎉 Créditos

- **Desarrollo**: Dungeon Fighters Team
- **Sprites**: Assets personalizados
- **Motor**: Pygame 2.6.1
- **Framework**: Python 3.13

---

**¿Disfrutas del juego?** ⭐ Dale una estrella en GitHub

**Última actualización**: Diciembre 2025  
**Versión**: 2.0  