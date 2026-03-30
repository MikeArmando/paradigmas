"""
models/ticket.py
Ticket de estacionamiento: representa el tiempo de una visita.
Encapsula estado ACTIVE/CLOSED y validaciones de ciclo de vida.
"""

from datetime import datetime
from enum import Enum
from models.vehicle import Vehicle
from models.spot import ParkingSpot


class TicketStatus(Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


class Ticket:
    """
    Composición: contiene referencias a Vehicle y ParkingSpot.
    Encapsulación: el estado solo cambia mediante close().
    """

    def __init__(
        self,
        ticket_id: int,
        vehicle: Vehicle,
        spot: ParkingSpot,
        entry_time: datetime,
    ) -> None:
        self._ticket_id: int = ticket_id
        self._vehicle: Vehicle = vehicle
        self._spot: ParkingSpot = spot
        self._entry_time: datetime = entry_time
        self._exit_time: datetime | None = None
        self._status: TicketStatus = TicketStatus.ACTIVE

    # --- Accesores ---

    def get_id(self) -> int:
        return self._ticket_id

    def get_vehicle(self) -> Vehicle:
        return self._vehicle

    def get_spot(self) -> ParkingSpot:
        return self._spot

    def get_entry_time(self) -> datetime:
        return self._entry_time

    def get_exit_time(self) -> datetime | None:
        return self._exit_time

    def get_status(self) -> TicketStatus:
        return self._status

    # --- Comportamiento ---

    def close(self, exit_time: datetime) -> None:
        """
        Cierra el ticket.
        Valida: no se puede cerrar un ticket ya cerrado (invariante de estado).
        """
        if self._status == TicketStatus.CLOSED:
            raise ValueError(f"El ticket #{self._ticket_id} ya está cerrado.")
        if exit_time < self._entry_time:
            raise ValueError("La hora de salida no puede ser anterior a la de entrada.")
        self._exit_time = exit_time
        self._status = TicketStatus.CLOSED

    def get_duration_hours(self) -> float:
        """Calcula duración en horas. Mínimo 1 minuto para evitar cobro 0."""
        if self._exit_time is None:
            raise ValueError("El ticket aún no ha sido cerrado.")
        delta = self._exit_time - self._entry_time
        hours = delta.total_seconds() / 3600
        return max(round(hours, 4), 1 / 60)

    def __str__(self) -> str:
        return (
            f"Ticket #{self._ticket_id} | {self._vehicle} | "
            f"Spot: {self._spot.get_id()} | {self._status.value}"
        )

    def to_dict(self) -> dict:
        """Serializa el ticket para la vista Flask."""
        duration = None
        if self._exit_time:
            duration = round(self.get_duration_hours(), 2)
        return {
            "id": self._ticket_id,
            "plate": self._vehicle.get_plate(),
            "vehicle_type": self._vehicle.get_type().value,
            "spot_id": self._spot.get_id(),
            "entry_time": self._entry_time.strftime("%Y-%m-%d %H:%M:%S"),
            "exit_time": self._exit_time.strftime("%Y-%m-%d %H:%M:%S") if self._exit_time else None,
            "status": self._status.value,
            "duration_hours": duration,
        }
