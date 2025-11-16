"""
Módulo para simular sensores de una estación meteorológica.
Genera datos de temperatura, humedad y dirección del viento.
"""

import json
import random
import numpy as np
from typing import Dict


class SensorSimulator:
    """Simula sensores meteorológicos generando datos aleatorios."""
    
    # Direcciones del viento posibles
    DIRECCIONES_VIENTO = ['N', 'NO', 'O', 'SO', 'S', 'SE', 'E', 'NE']
    
    def __init__(self, temp_mean: float = 25.0, temp_std: float = 10.0,
                 humedad_mean: float = 50.0, humedad_std: float = 15.0):
        """
        Inicializa el simulador de sensores.
        
        Args:
            temp_mean: Media de la distribución gaussiana para temperatura (°C)
            temp_std: Desviación estándar para temperatura (°C)
            humedad_mean: Media de la distribución gaussiana para humedad (%)
            humedad_std: Desviación estándar para humedad (%)
        """
        self.temp_mean = temp_mean
        self.temp_std = temp_std
        self.humedad_mean = humedad_mean
        self.humedad_std = humedad_std
        
    def generar_temperatura(self) -> float:
        """
        Genera una temperatura usando distribución gaussiana.
        Rango: [0, 110.00]°C con 2 decimales.
        
        Returns:
            Temperatura en grados Celsius (float con 2 decimales)
        """
        temp = np.random.normal(self.temp_mean, self.temp_std)
        # Asegurar que esté en el rango [0, 110.00]
        temp = max(0.0, min(110.0, temp))
        # Redondear a 2 decimales
        return round(temp, 2)
    
    def generar_humedad(self) -> int:
        """
        Genera una humedad relativa usando distribución gaussiana.
        Rango: [0, 100]% (entero).
        
        Returns:
            Humedad relativa en porcentaje (entero)
        """
        humedad = np.random.normal(self.humedad_mean, self.humedad_std)
        # Asegurar que esté en el rango [0, 100]
        humedad = max(0, min(100, int(round(humedad))))
        return humedad
    
    def generar_direccion_viento(self) -> str:
        """
        Genera una dirección del viento aleatoria.
        Opciones: N, NO, O, SO, S, SE, E, NE
        
        Returns:
            Dirección del viento (string)
        """
        return random.choice(self.DIRECCIONES_VIENTO)
    
    def generar_datos(self) -> Dict[str, any]:
        """
        Genera un conjunto completo de datos de sensores.
        
        Returns:
            Diccionario con temperatura, humedad y dirección del viento
        """
        datos = {
            'temperatura': self.generar_temperatura(),
            'humedad': self.generar_humedad(),
            'direccion_viento': self.generar_direccion_viento()
        }
        return datos
    
    def generar_json(self) -> str:
        """
        Genera datos de sensores y los retorna como string JSON.
        
        Returns:
            String JSON con los datos de los sensores
        """
        datos = self.generar_datos()
        return json.dumps(datos, ensure_ascii=False)


if __name__ == '__main__':
    # Ejemplo de uso
    print("=== Simulador de Sensores Meteorológicos ===\n")
    
    simulator = SensorSimulator(temp_mean=25.0, temp_std=10.0,
                               humedad_mean=50.0, humedad_std=15.0)
    
    print("Generando 10 muestras de datos:\n")
    for i in range(10):
        datos = simulator.generar_datos()
        json_str = simulator.generar_json()
        print(f"Muestra {i+1}: {json_str}")

