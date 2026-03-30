"""
models/spot.py
Lugar de estacionamiento (ParkingSpot).
Encapsula estado libre/ocupado e invariante: un solo vehículo por lugar.
"""

from enum import Enum
from typing import Optional
from models.vehicle import Vehicle, VehicleType


class SpotType(Enum):
    CAR = "Car"
    MOTORCYCLE = "Motorcycle"
    ANY = "Any"


class ParkingSpot:
    """
    Representa un lugar físico del estacionamiento.
    Encapsulación: el estado (_occupied, _current_vehicle) solo se modifica
    mediante park() y release(), garantizando la invariante de ocupación única.
    """

    def __init__(self, spot_id: str, allowed: SpotType) -> None:
        self._spot_id: str = spot_id
        self._allowed: SpotType = allowed
        self._occupied: bool = False
        self._current_vehicle: Optional[Vehicle] = None

    # --- Accesores ---

    def get_id(self) -> str:
        return self._spot_id

    def get_allowed(self) -> SpotType:
        return self._allowed

    def is_occupied(self) -> bool:
        return self._occupied

    def get_current_vehicle(self) -> Optional[Vehicle]:
        return self._current_vehicle

    # --- Comportamiento (métodos que cambian estado con validación) ---

    def is_available_for(self, vehicle: Vehicle) -> bool:
        """Comprueba compatibilidad de tipo e disponibilidad."""
        if self._occupied:
            return False
        if self._allowed == SpotType.ANY:
            return True
        return self._allowed.value == vehicle.get_type().value

    def park(self, vehicle: Vehicle) -> None:
        """
        Asigna el vehículo al lugar.
        Invariante: lanza excepción si ya está ocupado (nunca dos vehículos).
        """
        if self._occupied:
            raise RuntimeError(
                f"Invariante violada: el lugar {self._spot_id} ya está ocupado."
            )
        if not self.is_available_for(vehicle):
            raise ValueError(
                f"El vehículo {vehicle} no es compatible con el lugar {self._spot_id} ({self._allowed.value})."
            )
        self._occupied = True
        self._current_vehicle = vehicle

    def release(self) -> None:
        """Libera el lugar."""
        self._occupied = False
        self._current_vehicle = None

    def __str__(self) -> str:
        status = "OCUPADO" if self._occupied else "LIBRE"
        vehicle_info = f" — {self._current_vehicle.get_plate()}" if self._occupied else ""
        return f"[{self._spot_id} | {self._allowed.value} | {status}{vehicle_info}]"

    def to_dict(self) -> dict:
        """Serializa el spot para la vista Flask."""
        return {
            "id": self._spot_id,
            "allowed": self._allowed.value,
            "occupied": self._occupied,
            "vehicle_plate": self._current_vehicle.get_plate() if self._current_vehicle else None,
        }
