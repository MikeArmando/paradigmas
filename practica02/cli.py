"""
cli.py — Menú de consola (Sesión 1 y 2).
Demuestra el funcionamiento del modelo antes de añadir Flask (Sesión 3).
"""

import sys
from datetime import datetime

# Agrega el directorio raíz al path para que los imports funcionen
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.vehicle import vehicle_factory
from models.parking_lot import ParkingLot
from models.rates import HourlyRatePolicy, FlatRatePolicy, AVAILABLE_POLICIES


# ── Color helpers (ANSI) ────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
RED    = "\033[91m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
GRAY   = "\033[90m"


def cprint(msg: str, color: str = RESET) -> None:
    print(f"{color}{msg}{RESET}")


def separator(char: str = "─", width: int = 60) -> None:
    cprint(char * width, GRAY)


# ── Inicialización ──────────────────────────────────────────────────────────

def init_parking_lot() -> ParkingLot:
    """Crea el estacionamiento con política horaria por defecto."""
    policy = HourlyRatePolicy(car_rate=20.0, moto_rate=10.0)
    lot = ParkingLot(policy=policy)
    return lot


# ── Operaciones del menú ────────────────────────────────────────────────────

def registrar_entrada(lot: ParkingLot) -> None:
    separator()
    cprint("  REGISTRAR ENTRADA", BOLD)
    separator()
    plate = input("  Placas del vehículo: ").strip()
    print("  Tipo: 1) Car   2) Motorcycle")
    opt = input("  Selecciona tipo [1/2]: ").strip()
    vehicle_type = "Car" if opt == "1" else "Motorcycle"

    try:
        vehicle = vehicle_factory(plate, vehicle_type)
        ticket = lot.enter(vehicle, datetime.now())
        cprint(
            f"\n  ✔ Entrada registrada → {ticket} | Spot: {ticket.get_spot().get_id()}",
            GREEN,
        )
        cprint(f"  {lot.get_occupancy_str()}", CYAN)
    except ValueError as e:
        cprint(f"\n  ✘ Error: {e}", RED)


def registrar_salida(lot: ParkingLot) -> None:
    separator()
    cprint("  REGISTRAR SALIDA", BOLD)
    separator()

    activos = lot.get_active_tickets()
    if not activos:
        cprint("  No hay tickets activos.", YELLOW)
        return

    print("  Tickets activos:")
    for t in activos:
        print(f"    #{t.get_id()} — {t.get_vehicle()} | Spot: {t.get_spot().get_id()} | Entrada: {t.get_entry_time().strftime('%H:%M:%S')}")

    try:
        ticket_id = int(input("\n  Número de ticket a cerrar: "))
    except ValueError:
        cprint("  ✘ Ingresa un número válido.", RED)
        return

    try:
        ticket, cost = lot.exit(ticket_id, datetime.now())
        hours = ticket.get_duration_hours()
        cprint(
            f"\n  ✔ Salida registrada — Ticket #{ticket_id} | "
            f"Tiempo: {hours:.2f}h | Costo: ${cost:.2f} | "
            f"Spot liberado: {ticket.get_spot().get_id()}",
            GREEN,
        )
        cprint(f"  Política: {lot.get_policy().describe()}", GRAY)
        cprint(f"  {lot.get_occupancy_str()}", CYAN)
    except ValueError as e:
        cprint(f"\n  ✘ Error: {e}", RED)


def ver_ocupacion(lot: ParkingLot) -> None:
    separator()
    cprint("  OCUPACIÓN ACTUAL", BOLD)
    separator()
    occ = lot.get_occupancy()
    cprint(f"  Total: {occ['total']} | Libres: {occ['free']} | Ocupados: {occ['occupied']}", CYAN)
    print()
    for spot in lot.get_spots():
        color = RED if spot.is_occupied() else GREEN
        cprint(f"  {spot}", color)


def ver_tickets_activos(lot: ParkingLot) -> None:
    separator()
    cprint("  TICKETS ACTIVOS", BOLD)
    separator()
    tickets = lot.get_active_tickets()
    if not tickets:
        cprint("  No hay vehículos en el estacionamiento.", YELLOW)
        return
    for t in tickets:
        print(f"  {t}")
    print()
    ids = [f"#{t.get_id()}" for t in tickets]
    cprint(f"  Tickets activos: {ids}", CYAN)


def cambiar_politica(lot: ParkingLot) -> None:
    """Sesión 2: demostración de polimorfismo cambiando la política en caliente."""
    separator()
    cprint("  CAMBIAR POLÍTICA DE COBRO  (Demostración de polimorfismo)", BOLD)
    separator()
    cprint(f"  Política actual: {lot.get_policy().describe()}", CYAN)
    print()
    print("  1) Tarifa por hora  (Auto $20/hr, Moto $10/hr)")
    print("  2) Tarifa fija      ($50 por visita)")
    opt = input("  Selecciona [1/2]: ").strip()
    if opt == "1":
        lot.set_policy(HourlyRatePolicy(car_rate=20.0, moto_rate=10.0))
    elif opt == "2":
        lot.set_policy(FlatRatePolicy(flat_amount=50.0))
    else:
        cprint("  Opción no válida.", RED)
        return
    cprint(f"\n  ✔ Política cambiada → {lot.get_policy().describe()}", GREEN)


def ver_recaudacion(lot: ParkingLot) -> None:
    separator()
    cprint("  RECAUDACIÓN TOTAL", BOLD)
    separator()
    cprint(f"  Total recaudado: ${lot.get_total_revenue():.2f}", CYAN)
    cerrados = lot.get_closed_tickets()
    if cerrados:
        print(f"  Tickets cerrados: {len(cerrados)}")
        for t in cerrados[-5:]:          # últimos 5
            print(f"    {t}")


# ── Menú principal ──────────────────────────────────────────────────────────

MENU = """
  {b}╔══════════════════════════════════════╗{r}
  {b}║   SIMULADOR DE ESTACIONAMIENTO       ║{r}
  {b}╚══════════════════════════════════════╝{r}
  {c}1.{r} Registrar entrada
  {c}2.{r} Registrar salida
  {c}3.{r} Ver ocupación
  {c}4.{r} Ver tickets activos
  {c}5.{r} Cambiar política de cobro  {y}[Polimorfismo]{r}
  {c}6.{r} Ver recaudación
  {c}0.{r} Salir
""".format(b=BOLD, r=RESET, c=CYAN, y=YELLOW)


def main() -> None:
    lot = init_parking_lot()
    cprint(
        f"\n  Estacionamiento iniciado con {len(lot.get_spots())} lugares | "
        f"Política: {lot.get_policy().describe()}",
        GREEN,
    )

    actions = {
        "1": registrar_entrada,
        "2": registrar_salida,
        "3": ver_ocupacion,
        "4": ver_tickets_activos,
        "5": cambiar_politica,
        "6": ver_recaudacion,
    }

    while True:
        print(MENU)
        choice = input("  Opción: ").strip()
        if choice == "0":
            cprint("\n  ¡Hasta luego!\n", GREEN)
            break
        action = actions.get(choice)
        if action:
            action(lot)
        else:
            cprint("  Opción no válida. Intenta de nuevo.", RED)
        print()


if __name__ == "__main__":
    main()
