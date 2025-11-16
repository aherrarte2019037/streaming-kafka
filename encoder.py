"""
Módulo para codificar datos de sensores en 3 bytes (24 bits).
Distribución de bits:
- Temperatura: 14 bits (0-16383, escalado a 0-110°C)
- Humedad: 7 bits (0-127, pero solo usamos 0-100)
- Dirección viento: 3 bits (0-7, mapeado a 8 direcciones)
"""

import json
from typing import Dict


class Encoder:
    """Codifica datos de sensores en 3 bytes (24 bits)."""
    
    # Mapeo de dirección del viento a bits (3 bits = 0-7)
    DIRECCION_TO_BITS = {
        'N': 0, 'NO': 1, 'O': 2, 'SO': 3,
        'S': 4, 'SE': 5, 'E': 6, 'NE': 7
    }
    
    # Mapeo inverso (bits a dirección)
    BITS_TO_DIRECCION = {v: k for k, v in DIRECCION_TO_BITS.items()}
    
    # Constantes para escalado
    TEMP_MAX = 110.0  # Temperatura máxima en °C
    TEMP_BITS = 14    # Bits para temperatura
    TEMP_MAX_ENCODED = (2 ** TEMP_BITS) - 1  # 16383
    
    HUMEDAD_BITS = 7
    VIENTO_BITS = 3
    
    @staticmethod
    def encode(json_str: str) -> bytes:
        """
        Codifica un string JSON con datos de sensores en 3 bytes.
        
        Args:
            json_str: String JSON con formato {"temperatura": X.XX, "humedad": Y, "direccion_viento": "Z"}
        
        Returns:
            bytes: 3 bytes codificados
        """
        # Parsear JSON
        datos = json.loads(json_str)
        
        temperatura = datos['temperatura']
        humedad = datos['humedad']
        direccion_viento = datos['direccion_viento']
        
        # Validar rangos
        if not (0 <= temperatura <= Encoder.TEMP_MAX):
            raise ValueError(f"Temperatura fuera de rango: {temperatura}")
        if not (0 <= humedad <= 100):
            raise ValueError(f"Humedad fuera de rango: {humedad}")
        if direccion_viento not in Encoder.DIRECCION_TO_BITS:
            raise ValueError(f"Dirección de viento inválida: {direccion_viento}")
        
        # 1. Codificar temperatura (14 bits)
        # Escalar de 0-110°C a 0-16383
        temp_encoded = int((temperatura / Encoder.TEMP_MAX) * Encoder.TEMP_MAX_ENCODED)
        temp_encoded = min(temp_encoded, Encoder.TEMP_MAX_ENCODED)  # Asegurar que no exceda
        
        # 2. Codificar humedad (7 bits)
        humedad_encoded = min(humedad, 127)  # Asegurar que no exceda 7 bits
        
        # 3. Codificar dirección viento (3 bits)
        viento_encoded = Encoder.DIRECCION_TO_BITS[direccion_viento]
        
        # Empaquetar en 24 bits (3 bytes)
        # Bits 0-13: Temperatura (14 bits)
        # Bits 14-20: Humedad (7 bits)
        # Bits 21-23: Dirección viento (3 bits)
        
        # Construir el valor de 24 bits
        # temp en bits 0-13 (sin desplazamiento)
        # humedad en bits 14-20 (desplazamiento de 14)
        # viento en bits 21-23 (desplazamiento de 21)
        valor_24_bits = temp_encoded | (humedad_encoded << 14) | (viento_encoded << 21)
        
        # Convertir a 3 bytes (big-endian)
        bytes_result = valor_24_bits.to_bytes(3, byteorder='big')
        
        return bytes_result
    
    @staticmethod
    def decode(bytes_data: bytes) -> str:
        """
        Decodifica 3 bytes a string JSON con datos de sensores.
        
        Args:
            bytes_data: 3 bytes codificados
        
        Returns:
            str: String JSON con los datos decodificados
        """
        if len(bytes_data) != 3:
            raise ValueError(f"Se esperaban 3 bytes, se recibieron {len(bytes_data)}")
        
        # Convertir bytes a entero de 24 bits
        valor_24_bits = int.from_bytes(bytes_data, byteorder='big')
        
        # Extraer bits
        # Temperatura: bits 0-13 (14 bits)
        temp_encoded = valor_24_bits & 0x3FFF  # Máscara para 14 bits (0x3FFF = 16383)
        
        # Humedad: bits 14-20 (7 bits)
        humedad_encoded = (valor_24_bits >> 14) & 0x7F  # Máscara para 7 bits
        
        # Dirección viento: bits 21-23 (3 bits)
        viento_encoded = (valor_24_bits >> 21) & 0x07  # Máscara para 3 bits
        
        # Decodificar valores
        # Temperatura: de 0-16383 a 0-110°C
        temperatura = (temp_encoded / Encoder.TEMP_MAX_ENCODED) * Encoder.TEMP_MAX
        temperatura = round(temperatura, 2)  # Redondear a 2 decimales
        
        # Humedad: ya está en el rango correcto (0-127, pero solo usamos 0-100)
        humedad = min(humedad_encoded, 100)
        
        # Dirección viento: de bits a string
        direccion_viento = Encoder.BITS_TO_DIRECCION.get(viento_encoded, 'N')
        
        # Construir JSON
        datos = {
            'temperatura': temperatura,
            'humedad': humedad,
            'direccion_viento': direccion_viento
        }
        
        return json.dumps(datos, ensure_ascii=False)


if __name__ == '__main__':
    # Prueba de encoding/decoding
    print("=== Prueba de Codificación/Decodificación ===\n")
    
    # Datos de prueba
    datos_prueba = {
        'temperatura': 56.32,
        'humedad': 51,
        'direccion_viento': 'SO'
    }
    
    json_original = json.dumps(datos_prueba, ensure_ascii=False)
    print(f"JSON original: {json_original}")
    
    # Codificar
    bytes_codificados = Encoder.encode(json_original)
    print(f"Bytes codificados (3 bytes): {bytes_codificados.hex()}")
    print(f"Tamaño: {len(bytes_codificados)} bytes")
    
    # Decodificar
    json_decodificado = Encoder.decode(bytes_codificados)
    print(f"JSON decodificado: {json_decodificado}")
    
    # Verificar
    datos_original = json.loads(json_original)
    datos_decodificado = json.loads(json_decodificado)
    
    print("\n=== Comparación ===")
    print(f"Temperatura: {datos_original['temperatura']} -> {datos_decodificado['temperatura']}")
    print(f"Humedad: {datos_original['humedad']} -> {datos_decodificado['humedad']}")
    print(f"Dirección viento: {datos_original['direccion_viento']} -> {datos_decodificado['direccion_viento']}")

