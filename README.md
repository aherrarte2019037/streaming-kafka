# Laboratorio Estación Meteorológica con Kafka

## Estado del Proyecto

### ✅ Completado (Persona 1 - Producer)

1. **Configuración del Entorno**
   - Entorno virtual creado (`venv`)
   - Dependencias instaladas (`requirements.txt`)

2. **Sección 3.1: Simulación de Sensores** ✅
   - `sensor_simulator.py` implementado
   - Generación de temperatura (0-110°C, distribución gaussiana)
   - Generación de humedad (0-100%, distribución gaussiana)
   - Generación de dirección del viento (8 opciones)
   - Formato JSON implementado

3. **Sección 3.2: Kafka Producer** ✅
   - `producer.py` implementado
   - Conexión a `iot.redesuvg.cloud:9092`
   - Topic: `22873`
   - Envío periódico cada 15-30 segundos
   - Modo JSON funcionando

4. **Sección 3.4: Codificación (Parte Producer)** ✅
   - `encoder.py` implementado
   - Codificación de JSON a 3 bytes (24 bits)
   - Distribución: temperatura (14 bits), humedad (7 bits), viento (3 bits)
   - Decodificación implementada y probada

### 📋 Pendiente (Persona 2 - Consumer)

1. **Sección 3.3: Kafka Consumer y Visualización**
   - Implementar `consumer.py`
   - Implementar `visualizer.py` con gráficos en tiempo real
   - Responder preguntas de la sección 3.3

2. **Sección 3.4: Decodificación (Parte Consumer)**
   - Integrar `decoder.py` en el consumer (usar `encoder.py` que ya tiene decode)
   - Actualizar visualización para trabajar con datos decodificados

3. **Trabajo Conjunto**
   - Pruebas de integración completa
   - Documentación final en PDF

---

## Configuración del Proyecto

- **Número de carné (Topic):** `22873`
- **Servidor Kafka:** `iot.redesuvg.cloud:9092`
- **Lenguaje:** Python
- **Entorno virtual:** `venv` (ya creado)

---

## División de Responsabilidades

### Persona 1: Producer (Primera Parte)

**Responsabilidades:**
- Sección 3.1: Simulación de sensores
- Sección 3.2: Kafka Producer
- Sección 3.4 (Parte Producer): Codificación para payload de 3 bytes

**Archivos creados:**
- `sensor_simulator.py` - Generación de datos de sensores
- `producer.py` - Kafka Producer que envía datos
- `encoder.py` - Codificación de JSON a 3 bytes (también incluye decodificación)

---

### Persona 2: Consumer (Segunda Parte)

**Responsabilidades:**
- Sección 3.3: Kafka Consumer y Visualización
- Sección 3.4 (Parte Consumer): Decodificación de payload de 3 bytes

**Archivos a crear:**
- `consumer.py` - Kafka Consumer que recibe datos
- `visualizer.py` - Módulo de gráficos en tiempo real
- Nota: `decoder.py` no es necesario, usar `encoder.py` que ya tiene la función `decode()`

---

## Pasos Detallados

### Persona 1: Pasos a Seguir

#### Paso 1: Configurar Entorno
```bash
source venv/bin/activate
pip install -r requirements.txt
```

#### Paso 2: Sección 3.1 - Simulación de Sensores
- Implementar `sensor_simulator.py` con:
  - Generación de temperatura (0-110°C, float 2 decimales) con distribución gaussiana
  - Generación de humedad (0-100%, entero) con distribución gaussiana
  - Generación de dirección del viento (8 opciones: N, NO, O, SO, S, SE, E, NE)
  - Formateo en JSON: `{"temperatura":56.32, "humedad":51, "direccion_viento":"SO"}`

**📸 Documentar:**
- Captura de pantalla de datos generados (ejemplo de JSON generado, mostrar varios ejemplos)

**❓ Responder (al finalizar 3.1):**
- ¿A qué capa pertenece JSON/SOAP según el Modelo OSI y porque?
- ¿Qué beneficios tiene utilizar un formato como JSON/SOAP?

#### Paso 3: Sección 3.2 - Kafka Producer
- Implementar `producer.py` con:
  - Conexión a `iot.redesuvg.cloud:9092`
  - Envío de datos cada 15-30 segundos
  - Topic: `22873`
  - Envío de mensajes con key y value (JSON stringificado)

**📸 Documentar:**
- Captura de código del Producer funcionando
- Captura de logs mostrando mensajes enviados exitosamente
- Evidencia de que el Producer se mantiene corriendo enviando datos periódicamente (mostrar timestamps de múltiples envíos)

#### Paso 4: Sección 3.4 (Parte Producer) - Codificación
- Implementar `encoder.py` con función `encode()` que:
  - Convierte JSON a 3 bytes (24 bits)
  - Distribución: temperatura (14 bits), humedad (7 bits), dirección viento (3 bits)
  - Convierte temperatura float a entero escalado (0-110°C → 0-16383)
  - Convierte humedad (0-100) a 7 bits
  - Mapea dirección viento a 3 bits (8 opciones)
- Modificar `producer.py` para usar encoding antes de enviar (cambiar `USE_ENCODING = True`)

**📸 Documentar:**
- Captura de código de la función encode()
- Captura mostrando ejemplo: JSON original → 3 bytes codificados (mostrar valores antes y después)
- Captura de logs del Producer enviando datos codificados

---

### Persona 2: Pasos a Seguir

#### Paso 1: Configurar Entorno
```bash
source venv/bin/activate
pip install -r requirements.txt
```

#### Paso 2: Sección 3.3 - Kafka Consumer y Visualización
- Implementar `consumer.py` con:
  - Conexión a `iot.redesuvg.cloud:9092`
  - Suscripción al topic `22873`
  - Loop que consume mensajes continuamente
  - Parseo de JSON recibido
- Implementar `visualizer.py` con:
  - Mantener listas históricas de temperatura, humedad y dirección viento
  - Gráficos en tiempo real que se actualicen con cada nuevo mensaje

**📸 Documentar:**
- Captura de código del Consumer funcionando
- Captura de logs mostrando mensajes recibidos y parseados
- Captura de gráficos en tiempo real mostrando al menos 3-5 actualizaciones (mostrar evolución temporal)
- Evidencia de que los gráficos se actualizan automáticamente con nuevos datos

**❓ Responder (al finalizar 3.3):**
- ¿Qué ventajas y desventajas considera que tiene este acercamiento basado en Pub/Sub de Kafka?
- ¿Para qué aplicaciones tiene sentido usar Kafka? ¿Para cuáles no?

#### Paso 3: Sección 3.4 (Parte Consumer) - Decodificación
- Usar `encoder.py` que ya tiene la función `decode()`:
  - Convierte 3 bytes a JSON
  - Extrae bits: temperatura (14 bits), humedad (7 bits), dirección viento (3 bits)
  - Convierte temperatura de entero escalado a float (0-16383 → 0-110°C)
  - Convierte humedad de 7 bits a entero (0-100)
  - Mapea dirección viento de 3 bits a string (8 opciones)
- Modificar `consumer.py` para usar decoding después de recibir
- Actualizar `visualizer.py` para trabajar con datos decodificados

**📸 Documentar:**
- Captura de código de la función decode() (ya está en encoder.py)
- Captura mostrando ejemplo: 3 bytes recibidos → JSON decodificado (mostrar valores antes y después)
- Captura de gráficos funcionando con datos decodificados (comparar con versión sin restricción)
- Evidencia de que se logra lo mismo que en pasos anteriores pero con payload de 3 bytes

---

### Trabajo Conjunto

#### Integración y Pruebas
- Probar integración completa: Producer → Kafka → Consumer
- Validar que encoding/decoding funciona correctamente (verificar que datos originales = datos decodificados)

**📸 Documentar:**
- Captura de ambos programas corriendo simultáneamente
- Captura mostrando flujo completo: Producer envía → Consumer recibe y grafica
- Captura de prueba de encoding/decoding: mostrar que un JSON codificado y luego decodificado produce el mismo resultado (o valores equivalentes dentro de la precisión permitida)

#### Documentación Final
- Crear documento PDF con todas las explicaciones, capturas de pantalla y respuestas

**❓ Responder (al finalizar 3.4):**
- ¿Qué complejidades introduce el tener un payload restringido (pequeño)?
- ¿Cómo podemos hacer que el valor de temperatura quepa en 14 bits?
- ¿Qué sucedería si ahora la humedad también es tipo float con un decimal? ¿Qué decisiones tendríamos que tomar en ese caso?
- ¿Qué parámetros o herramientas de Kafka podrían ayudarnos si las restricciones fueran aún más fuertes?

---

## Consideraciones Técnicas

**Servidor Kafka:**
- Host: `iot.redesuvg.cloud`
- Puerto: `9092`
- Topic: `22873`

**Distribución de bits (3.4):**
- Temperatura: 14 bits (0-16383, escalado a 0-110°C con resolución ~0.0067°C)
- Humedad: 7 bits (0-127, pero solo usamos 0-100)
- Dirección viento: 3 bits (0-7, mapeado a 8 direcciones)

**Mapeo de dirección del viento:**
- 0: N, 1: NO, 2: O, 3: SO, 4: S, 5: SE, 6: E, 7: NE

---

## Archivos del Proyecto

- `requirements.txt` - Dependencias del proyecto
- `sensor_simulator.py` - Simulación de sensores meteorológicos
- `producer.py` - Kafka Producer
- `encoder.py` - Codificación/Decodificación de 3 bytes
- `README.md` - Este archivo

---

## Cómo Usar

### Activar Entorno Virtual
```bash
source venv/bin/activate
```

### Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Ejecutar Producer (Modo JSON)
```bash
python producer.py
```

### Ejecutar Producer (Modo Codificado - 3 bytes)
Editar `producer.py` y cambiar:
```python
USE_ENCODING = True  # Cambiar a True para la sección 3.4
```

### Probar Simulador de Sensores
```bash
python sensor_simulator.py
```

### Probar Codificación/Decodificación
```bash
python encoder.py
```

---

## Checklist de Documentación

- [ ] Capturas de generación de datos (3.1)
- [ ] Capturas de Producer enviando datos (3.2)
- [ ] Capturas de Consumer recibiendo y graficando (3.3)
- [ ] Capturas de funciones encode/decode (3.4)
- [ ] Capturas de integración completa con restricción de 3 bytes (3.4)
- [ ] Respuestas a todas las preguntas del laboratorio
