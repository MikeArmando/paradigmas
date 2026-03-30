"""
models/vehicle.py
Abstracción del vehículo con subtipos Car y Motorcycle.
Sesión 1: clase base Vehicle.
Sesión 2: herencia y subtipos requeridos.
"""

from abc import ABC, abstractmethod
from enum import Enum


class VehicleType(Enum):
    CAR = "Car"
    MOTORCYCLE = "Motorcycle"


class Vehicle(ABC):
    """Abstracción del vehículo. Encapsula placas y tipo."""

    def __init__(self, plate: str, vehicle_type: VehicleType) -> None:
        if not plate or not plate.strip():
            raise ValueError("Las placas no pueden estar vacías.")
        self._plate: str = plate.strip().upper()
        self._type: VehicleType = vehicle_type

    # --- Accesores (encapsulación: atributos privados solo accesibles por métodos) ---

    def get_plate(self) -> str:
        return self._plate

    def get_type(self) -> VehicleType:
        return self._type

    def __str__(self) -> str:
        return f"{self._type.value}({self._plate})"

    def __repr__(self) -> str:
        return self.__str__()


class Car(Vehicle):
    """Subtipo Car — hereda de Vehicle."""

    def __init__(self, plate: str) -> None:
        super().__init__(plate, VehicleType.CAR)


class Motorcycle(Vehicle):
    """Subtipo Motorcycle — hereda de Vehicle."""

    def __init__(self, plate: str) -> None:
        super().__init__(plate, VehicleType.MOTORCYCLE)


def vehicle_factory(plate: str, vehicle_type: str) -> Vehicle:
    """Fábrica simple que devuelve el subtipo correcto según el string de tipo."""
    vt = vehicle_type.strip().lower()
    if vt in ("car", "carro", "automóvil", "auto"):
        return Car(plate)
    if vt in ("motorcycle", "moto", "motocicleta"):
        return Motorcycle(plate)
    raise ValueError(f"Tipo de vehículo desconocido: '{vehicle_type}'. Use 'Car' o 'Motorcycle'.")
