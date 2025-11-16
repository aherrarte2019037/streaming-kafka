"""
Kafka Consumer para la estacion meteorologica.
Consume mensajes del topic configurado, los decodifica (JSON o payload de 3 bytes)
y alimenta al visualizador en tiempo real.
"""

import argparse
import json
import signal
from datetime import datetime
from typing import Any, Dict, Optional

from kafka import KafkaConsumer
from kafka.errors import KafkaError

from encoder import Encoder
from visualizer import WeatherDataVisualizer


class WeatherStationConsumer:
    """Consumer que lee del topic, decodifica y opcionalmente grafica los datos."""

    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        group_id: str,
        auto_offset_reset: str = 'latest',
        payload_format: str = 'auto',
        enable_visualizer: bool = True,
        max_points: int = 120,
        log_payloads: bool = True,
    ) -> None:
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.auto_offset_reset = auto_offset_reset
        payload_format = payload_format.lower()
        if payload_format not in {'auto', 'json', 'encoded'}:
            raise ValueError(f"Formato de payload no soportado: {payload_format}")
        self.payload_format = payload_format
        self.log_payloads = log_payloads

        self.visualizer = WeatherDataVisualizer(max_points=max_points, enable_plot=enable_visualizer) if enable_visualizer else None
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=[bootstrap_servers],
            group_id=group_id,
            auto_offset_reset=auto_offset_reset,
            enable_auto_commit=True,
            consumer_timeout_ms=1000,
            value_deserializer=None,
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
        )

        self.running = True
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def _handle_signal(self, signum, frame) -> None:
        """Detiene el loop principal ante senales de finalizacion."""
        print("\n\nSenal recibida, deteniendo consumer...")
        self.running = False

    def _decode_message(self, value: Any) -> Optional[Dict[str, Any]]:
        """Decodifica el payload segun el formato configurado."""
        if value is None:
            return None

        try:
            if self.payload_format == 'encoded':
                return json.loads(Encoder.decode(bytes(value)))

            if self.payload_format == 'json':
                text = value.decode('utf-8') if isinstance(value, (bytes, bytearray)) else str(value)
                return json.loads(text)

            # Modo auto: detectar por longitud
            if isinstance(value, (bytes, bytearray)) and len(value) == 3:
                return json.loads(Encoder.decode(bytes(value)))

            text = value.decode('utf-8') if isinstance(value, (bytes, bytearray)) else str(value)
            return json.loads(text)

        except (ValueError, json.JSONDecodeError) as exc:
            print(f"[WARN] No fue posible decodificar el mensaje: {exc}")
            return None

    def _print_reading(self, reading: Dict[str, Any], message) -> None:
        """Imprime los datos ya decodificados."""
        timestamp = datetime.fromtimestamp(message.timestamp / 1000.0)
        received_at = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        payload = json.dumps(reading, ensure_ascii=False)
        print(f"[{received_at}] key={message.key} partition={message.partition} offset={message.offset}")
        print(f"  Datos: {payload}")

    def _handle_message(self, message) -> None:
        """Procesa un registro del topic."""
        reading = self._decode_message(message.value)
        if reading is None:
            return

        if self.log_payloads:
            self._print_reading(reading, message)

        timestamp = datetime.fromtimestamp(message.timestamp / 1000.0)
        if self.visualizer:
            self.visualizer.add_reading(reading, timestamp=timestamp)

    def run(self) -> None:
        """Loop principal de consumo."""
        self._print_banner()

        try:
            while self.running:
                try:
                    for message in self.consumer:
                        if not self.running:
                            break
                        self._handle_message(message)
                    # La iteracion termina cuando se alcanza consumer_timeout_ms
                except KafkaError as err:
                    print(f"[ERROR] Kafka consumer reporto un error: {err}")
        except KeyboardInterrupt:
            print("\nInterrupcion por teclado recibida.")
        finally:
            self.close()

    def _print_banner(self) -> None:
        """Muestra informacion basica de configuracion."""
        print("=" * 60)
        print("Estacion Meteorologica - Kafka Consumer")
        print("=" * 60)
        print(f"Servidor: {self.bootstrap_servers}")
        print(f"Topic: {self.topic}")
        print(f"Grupo: {self.group_id}")
        print(f"Formato payload: {self.payload_format}")
        print(f"Visualizacion: {'habilitada' if self.visualizer else 'deshabilitada'}")
        print("=" * 60)
        print("Esperando mensajes...\n")

    def close(self) -> None:
        """Libera recursos del consumer y del visualizador."""
        if self.visualizer:
            self.visualizer.close()
        if self.consumer:
            self.consumer.close()
        print("Consumer cerrado correctamente.")


def parse_args() -> argparse.Namespace:
    """Construye el parser de argumentos de linea de comandos."""
    parser = argparse.ArgumentParser(description="Kafka Consumer para la estacion meteorologica.")
    parser.add_argument('--bootstrap-servers', default='iot.redesuvg.cloud:9092', help='Servidor Kafka (host:puerto)')
    parser.add_argument('--topic', default='22873', help='Topic a consumir')
    parser.add_argument('--group-id', default='weather-station-consumer', help='Nombre del consumer group')
    parser.add_argument('--auto-offset-reset', choices=['earliest', 'latest'], default='latest', help='Offset inicial si no hay commits previos')
    parser.add_argument('--format', choices=['auto', 'json', 'encoded'], default='auto', help='Tipo de payload esperado')
    parser.add_argument('--max-points', type=int, default=120, help='Numero maximo de muestras en pantalla')
    parser.add_argument('--no-plot', action='store_true', help='Desactiva los graficos en tiempo real')
    parser.add_argument('--no-log', action='store_true', help='No imprime cada payload decodificado en consola')
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    consumer = WeatherStationConsumer(
        bootstrap_servers=args.bootstrap_servers,
        topic=args.topic,
        group_id=args.group_id,
        auto_offset_reset=args.auto_offset_reset,
        payload_format=args.format,
        enable_visualizer=not args.no_plot,
        max_points=args.max_points,
        log_payloads=not args.no_log,
    )
    consumer.run()


if __name__ == '__main__':
    main()
