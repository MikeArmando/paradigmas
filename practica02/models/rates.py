"""
models/rates.py
Abstracción de tarifa: RatePolicy como Protocolo (typing.Protocol).
Polimorfismo: múltiples implementaciones intercambiables.
Sesión 1: implementación inicial HourlyRatePolicy.
Sesión 2: FlatRatePolicy añadida — polimorfismo evidente.
"""

from typing import Protocol, runtime_checkable
from models.vehicle import Vehicle, VehicleType


@runtime_checkable
class RatePolicy(Protocol):
    """
    Interfaz común para políticas de cobro.
    Cualquier clase que implemente calculate() cumple este contrato (duck typing / Protocol).
    """

    def calculate(self, hours: float, vehicle: Vehicle) -> float:
        """Calcula el costo dado el tiempo en horas y el vehículo."""
        ...

    def describe(self) -> str:
        """Descripción legible de la política."""
        ...


class HourlyRatePolicy:
    """
    Política de cobro por hora diferenciada según tipo de vehículo.
    Polimorfismo: el mismo método calculate produce costos distintos
    dependiendo del subtipo de Vehicle recibido.
    """

    def __init__(self, car_rate: float = 20.0, moto_rate: float = 10.0) -> None:
        if car_rate < 0 or moto_rate < 0:
            raise ValueError("Las tarifas no pueden ser negativas.")
        self._car_rate: float = car_rate
        self._moto_rate: float = moto_rate

    def calculate(self, hours: float, vehicle: Vehicle) -> float:
        hours = max(hours, 0.0)
        rate = self._car_rate if vehicle.get_type() == VehicleType.CAR else self._moto_rate
        return round(hours * rate, 2)

    def describe(self) -> str:
        return (
            f"Tarifa por hora — Auto: ${self._car_rate:.2f}/hr | "
            f"Moto: ${self._moto_rate:.2f}/hr"
        )

    def __str__(self) -> str:
        return "HourlyRatePolicy"


class FlatRatePolicy:
    """
    Política de tarifa fija: mismo cobro sin importar el tiempo.
    Segundo subtipo de RatePolicy — demuestra polimorfismo en Sesión 2.
    """

    def __init__(self, flat_amount: float = 50.0) -> None:
        if flat_amount < 0:
            raise ValueError("El monto fijo no puede ser negativo.")
        self._flat_amount: float = flat_amount

    def calculate(self, hours: float, vehicle: Vehicle) -> float:
        return self._flat_amount

    def describe(self) -> str:
        return f"Tarifa fija — ${self._flat_amount:.2f} por visita"

    def __str__(self) -> str:
        return "FlatRatePolicy"


# Registro de políticas disponibles (facilita selección desde UI)
AVAILABLE_POLICIES: dict[str, RatePolicy] = {
    "hourly": HourlyRatePolicy(car_rate=20.0, moto_rate=10.0),
    "flat":   FlatRatePolicy(flat_amount=50.0),
}
