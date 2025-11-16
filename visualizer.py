"""
Visualizador en tiempo real para los datos de la estacion meteorologica.
Mantiene un historial de muestras y actualiza los graficos de temperatura,
humedad y direccion del viento conforme llegan nuevos mensajes.
"""

from collections import deque
from datetime import datetime
from typing import Any, Deque, Dict, Optional

import matplotlib.dates as mdates
import matplotlib.pyplot as plt


class WeatherDataVisualizer:
    """Administra el estado de los datos y la visualizacion en tiempo real."""

    DIRECCIONES = ['N', 'NO', 'O', 'SO', 'S', 'SE', 'E', 'NE']
    DIRECCION_TO_INDEX = {dir_: idx for idx, dir_ in enumerate(DIRECCIONES)}

    def __init__(self, max_points: int = 120, enable_plot: bool = True):
        self.max_points = max_points
        self.enable_plot = enable_plot

        self.timestamps: Deque[datetime] = deque(maxlen=max_points)
        self.temperaturas: Deque[float] = deque(maxlen=max_points)
        self.humedades: Deque[float] = deque(maxlen=max_points)
        self.direcciones: Deque[int] = deque(maxlen=max_points)

        self._fig = None
        self._axes = None
        self._temp_line = None
        self._hum_line = None
        self._wind_line = None
        self._summary_text = None

        if self.enable_plot:
            self._init_plot()

    def _init_plot(self) -> None:
        """Inicializa los ejes y estilos de Matplotlib."""
        plt.ion()
        self._fig, self._axes = plt.subplots(3, 1, figsize=(11, 10), sharex=True)

        temp_ax, hum_ax, wind_ax = self._axes

        self._temp_line, = temp_ax.plot([], [], color='tab:red', label='Temperatura (C)', linewidth=2)
        temp_ax.set_ylabel('C')
        temp_ax.grid(True, linestyle='--', alpha=0.4)
        temp_ax.legend(loc='upper left')

        self._hum_line, = hum_ax.plot([], [], color='tab:blue', label='Humedad (%)', linewidth=2)
        hum_ax.set_ylabel('%')
        hum_ax.set_ylim(0, 100)
        hum_ax.grid(True, linestyle='--', alpha=0.4)
        hum_ax.legend(loc='upper left')

        self._wind_line, = wind_ax.step([], [], where='post', color='tab:green', label='Direccion del viento')
        wind_ax.set_yticks(list(range(len(self.DIRECCIONES))))
        wind_ax.set_yticklabels(self.DIRECCIONES)
        wind_ax.set_ylim(-0.5, len(self.DIRECCIONES) - 0.5)
        wind_ax.set_ylabel('Direccion')
        wind_ax.set_xlabel('Tiempo (hh:mm:ss)')
        wind_ax.grid(True, linestyle='--', alpha=0.4)
        wind_ax.legend(loc='upper left')

        formatter = mdates.DateFormatter('%H:%M:%S')
        wind_ax.xaxis.set_major_formatter(formatter)

        self._summary_text = temp_ax.text(
            0.02,
            0.95,
            '',
            transform=temp_ax.transAxes,
            fontsize=10,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8)
        )

        self._fig.tight_layout()
        plt.show(block=False)

    def add_reading(self, reading: Dict[str, Any], timestamp: Optional[datetime] = None) -> None:
        """
        Agrega una muestra al historial y actualiza los graficos.

        Args:
            reading: Diccionario con llaves temperatura, humedad y direccion_viento.
            timestamp: Momento asociado a la muestra. Si es None se usa datetime.now().
        """
        if timestamp is None:
            timestamp = datetime.now()

        temperatura = float(reading.get('temperatura', 0.0))
        humedad = float(reading.get('humedad', 0))
        direccion_raw = str(reading.get('direccion_viento', 'N')).upper()
        direccion_idx = self.DIRECCION_TO_INDEX.get(direccion_raw, 0)

        self.timestamps.append(timestamp)
        self.temperaturas.append(temperatura)
        self.humedades.append(humedad)
        self.direcciones.append(direccion_idx)

        if self.enable_plot:
            self._refresh_plot()

    def _refresh_plot(self) -> None:
        """Redibuja las curvas con los datos mas recientes."""
        if not self.enable_plot or self._fig is None:
            return

        x_values = mdates.date2num(list(self.timestamps))

        self._temp_line.set_data(x_values, list(self.temperaturas))
        self._hum_line.set_data(x_values, list(self.humedades))
        self._wind_line.set_data(x_values, list(self.direcciones))

        for axis, data in zip(self._axes[:2], [self.temperaturas, self.humedades]):
            if data:
                axis.relim()
                axis.autoscale_view()

        if self.timestamps:
            latest_time = self.timestamps[-1].strftime('%H:%M:%S')
            latest_temp = self.temperaturas[-1]
            latest_hum = self.humedades[-1]
            latest_dir = self.DIRECCIONES[self.direcciones[-1]]
            summary = (
                f'Ultima lectura ({latest_time})\n'
                f'Temp: {latest_temp:.2f} C | Hum: {latest_hum:.0f}% | Viento: {latest_dir}'
            )
            self._summary_text.set_text(summary)

        if len(x_values) > 0:
            span = x_values[-1] - x_values[0]
            if span == 0:
                span = 1 / (24 * 60 * 60)  # ~1 segundo
            padding = max(span * 0.05, 1 / (24 * 60 * 60))
            xmin = x_values[0] if len(x_values) > 1 else x_values[0] - span
            xmax = x_values[-1] + padding
            self._axes[2].set_xlim(xmin, xmax)

        self._fig.canvas.draw_idle()
        self._fig.canvas.flush_events()
        plt.pause(0.05)

    def close(self) -> None:
        """Cierra la ventana de Matplotlib si esta activa."""
        if self.enable_plot and self._fig is not None:
            plt.close(self._fig)
            self._fig = None
