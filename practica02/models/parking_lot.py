"""
models/parking_lot.py
ParkingLot: clase central que administra spots, tickets activos y recaudación.
Composición: contiene colecciones de ParkingSpot y Ticket.
La política de cobro (RatePolicy) se inyecta (Dependency Injection).
"""

from datetime import datetime
from typing import Optional
from models.vehicle import Vehicle
from models.spot import ParkingSpot, SpotType
from models.ticket import Ticket, TicketStatus
from models.rates import RatePolicy, HourlyRatePolicy


def _build_default_spots() -> list[ParkingSpot]:
    """Crea la distribución de lugares por defecto del estacionamiento."""
    spots: list[ParkingSpot] = []
    # 5 lugares para autos (A1–A5)
    for i in range(1, 6):
        spots.append(ParkingSpot(f"A{i}", SpotType.CAR))
    # 3 lugares para motos (M1–M3)
    for i in range(1, 4):
        spots.append(ParkingSpot(f"M{i}", SpotType.MOTORCYCLE))
    # 2 lugares universales (B1–B2)
    for i in range(1, 3):
        spots.append(ParkingSpot(f"B{i}", SpotType.ANY))
    return spots


class ParkingLot:
    """
    Administra el ciclo de vida completo del estacionamiento.
    Encapsulación: el estado interno (_spots, _active_tickets, _total_revenue)
    solo se modifica a través de enter() y exit().
    Composición: ParkingLot tiene ParkingSpot y Ticket.
    """

    def __init__(
        self,
        spots: Optional[list[ParkingSpot]] = None,
        policy: Optional[RatePolicy] = None,
    ) -> None:
        self._spots: list[ParkingSpot] = spots if spots is not None else _build_default_spots()
        self._policy: RatePolicy = policy if policy is not None else HourlyRatePolicy()
        self._active_tickets: dict[int, Ticket] = {}
        self._closed_tickets: list[Ticket] = []
        self._next_ticket_id: int = 1
        self._total_revenue: float = 0.0

    # --- Accesores ---

    def get_spots(self) -> list[ParkingSpot]:
        return list(self._spots)

    def get_active_tickets(self) -> list[Ticket]:
        return list(self._active_tickets.values())

    def get_closed_tickets(self) -> list[Ticket]:
        return list(self._closed_tickets)

    def get_total_revenue(self) -> float:
        return self._total_revenue

    def get_policy(self) -> RatePolicy:
        return self._policy

    def set_policy(self, policy: RatePolicy) -> None:
        """Permite cambiar la política de cobro en tiempo de ejecución (OCP)."""
        self._policy = policy

    # --- Comportamiento principal ---

    def _find_available_spot(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        """Busca el primer lugar compatible disponible."""
        for spot in self._spots:
            if spot.is_available_for(vehicle):
                return spot
        return None

    def enter(self, vehicle: Vehicle, now: Optional[datetime] = None) -> Ticket:
        """
        Registra la entrada de un vehículo.
        - Busca spot compatible.
        - Crea ticket ACTIVE.
        - Invariante: nunca dos vehículos en el mismo spot.
        """
        if now is None:
            now = datetime.now()

        # Validar que el vehículo no esté ya adentro
        for ticket in self._active_tickets.values():
            if ticket.get_vehicle().get_plate() == vehicle.get_plate():
                raise ValueError(
                    f"El vehículo con placas {vehicle.get_plate()} ya está en el estacionamiento "
                    f"(Ticket #{ticket.get_id()})."
                )

        spot = self._find_available_spot(vehicle)
        if spot is None:
            raise ValueError(
                f"No hay lugares disponibles para {vehicle.get_type().value}. "
                "El estacionamiento está lleno para este tipo de vehículo."
            )

        spot.park(vehicle)
        ticket = Ticket(self._next_ticket_id, vehicle, spot, now)
        self._active_tickets[self._next_ticket_id] = ticket
        self._next_ticket_id += 1
        return ticket

    def exit(self, ticket_id: int, now: Optional[datetime] = None) -> tuple[Ticket, float]:
        """
        Registra la salida de un vehículo.
        - Cierra ticket.
        - Calcula costo usando la RatePolicy (polimorfismo).
        - Libera el spot.
        - Retorna (ticket, costo).
        """
        if now is None:
            now = datetime.now()

        if ticket_id not in self._active_tickets:
            raise ValueError(
                f"Ticket #{ticket_id} no encontrado o ya fue cerrado. "
                "Verifique el número de ticket."
            )

        ticket = self._active_tickets[ticket_id]
        ticket.close(now)

        hours = ticket.get_duration_hours()
        # Polimorfismo: calculate() se comporta distinto según la política activa
        cost = self._policy.calculate(hours, ticket.get_vehicle())

        ticket.get_spot().release()
        self._total_revenue += cost
        del self._active_tickets[ticket_id]
        self._closed_tickets.append(ticket)

        return ticket, cost

    # --- Consultas de estado ---

    def get_occupancy(self) -> dict:
        total = len(self._spots)
        occupied = sum(1 for s in self._spots if s.is_occupied())
        return {"total": total, "occupied": occupied, "free": total - occupied}

    def get_occupancy_str(self) -> str:
        occ = self.get_occupancy()
        return f"libres={occ['free']} ocupados={occ['occupied']}"

    def is_plate_active(self, plate: str) -> bool:
        return any(
            t.get_vehicle().get_plate() == plate.upper()
            for t in self._active_tickets.values()
        )
