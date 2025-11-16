"""
Kafka Producer para enviar datos de sensores meteorológicos.
Envía datos cada 15-30 segundos al servidor Kafka.
"""

import json
import time
import random
import signal
import sys
from kafka import KafkaProducer
from kafka.errors import KafkaError
from sensor_simulator import SensorSimulator
from encoder import Encoder


class WeatherStationProducer:
    """Producer de Kafka para estación meteorológica."""
    
    def __init__(self, bootstrap_servers: str, topic: str, use_encoding: bool = False):
        """
        Inicializa el producer.
        
        Args:
            bootstrap_servers: Servidor Kafka (ej: 'iot.redesuvg.cloud:9092')
            topic: Nombre del topic (ej: '22873')
            use_encoding: Si True, codifica los datos en 3 bytes antes de enviar
        """
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.use_encoding = use_encoding
        self.running = True
        
        # Configurar producer
        self.producer = KafkaProducer(
            bootstrap_servers=[bootstrap_servers],
            value_serializer=lambda v: v if isinstance(v, bytes) else v.encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        
        # Inicializar simulador de sensores
        self.simulator = SensorSimulator(
            temp_mean=25.0,
            temp_std=10.0,
            humedad_mean=50.0,
            humedad_std=15.0
        )
        
        # Configurar manejo de señales para cierre graceful
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Maneja señales de interrupción."""
        print("\n\nRecibida señal de interrupción. Cerrando producer...")
        self.running = False
    
    def send_data(self):
        """Envía un mensaje con datos de sensores."""
        try:
            # Generar datos
            datos = self.simulator.generar_datos()
            json_str = self.simulator.generar_json()
            
            # Codificar si es necesario
            if self.use_encoding:
                value = Encoder.encode(json_str)
                print(f"[ENCODED] Enviando datos codificados ({len(value)} bytes): {value.hex()}")
            else:
                value = json_str
                print(f"[JSON] Enviando datos: {json_str}")
            
            # Enviar mensaje
            future = self.producer.send(
                self.topic,
                key='sensor1',
                value=value
            )
            
            # Esperar confirmación (opcional, para debugging)
            record_metadata = future.get(timeout=10)
            
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] Mensaje enviado exitosamente:")
            print(f"  Topic: {record_metadata.topic}")
            print(f"  Partición: {record_metadata.partition}")
            print(f"  Offset: {record_metadata.offset}")
            print(f"  Datos: {json.dumps(datos, ensure_ascii=False)}")
            print()
            
        except KafkaError as e:
            print(f"Error al enviar mensaje: {e}")
        except Exception as e:
            print(f"Error inesperado: {e}")
    
    def run(self):
        """Ejecuta el producer en loop, enviando datos periódicamente."""
        print("=" * 60)
        print("Estación Meteorológica - Kafka Producer")
        print("=" * 60)
        print(f"Servidor: {self.bootstrap_servers}")
        print(f"Topic: {self.topic}")
        print(f"Modo: {'Codificado (3 bytes)' if self.use_encoding else 'JSON'}")
        print("=" * 60)
        print("\nPresiona Ctrl+C para detener el producer.\n")
        
        try:
            while self.running:
                # Enviar datos
                self.send_data()
                
                # Esperar entre 15 y 30 segundos antes del siguiente envío
                wait_time = random.uniform(15, 30)
                print(f"Esperando {wait_time:.1f} segundos antes del siguiente envío...\n")
                
                # Esperar con posibilidad de interrupción
                elapsed = 0
                while elapsed < wait_time and self.running:
                    time.sleep(1)
                    elapsed += 1
                    
        except KeyboardInterrupt:
            print("\n\nInterrupción por teclado detectada.")
        finally:
            self.close()
    
    def close(self):
        """Cierra el producer."""
        print("\nCerrando producer...")
        self.producer.close()
        print("Producer cerrado correctamente.")


def main():
    """Función principal."""
    # Configuración
    BOOTSTRAP_SERVERS = 'iot.redesuvg.cloud:9092'
    TOPIC = '22873'
    
    # Cambiar a True para usar codificación de 3 bytes (Sección 3.4)
    USE_ENCODING = True  
    
    # Crear y ejecutar producer
    producer = WeatherStationProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        topic=TOPIC,
        use_encoding=USE_ENCODING
    )
    
    producer.run()


if __name__ == '__main__':
    main()

