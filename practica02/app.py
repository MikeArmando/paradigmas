"""
app.py — Controlador Flask (Sesión 3).
MVC simple:
  Model      → models/  (ParkingLot, Vehicle, Ticket, etc.)
  View       → templates/
  Controller → rutas definidas aquí

El modelo ya existente se reutiliza sin modificar la lógica de negocio.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session

from models.parking_lot import ParkingLot
from models.vehicle import vehicle_factory
from models.rates import HourlyRatePolicy, FlatRatePolicy

app = Flask(__name__)
app.secret_key = "parking_lot_secret_2024"

# ── Estado global del estacionamiento (en memoria) ──────────────────────────
# En producción esto se persistiría en BD; aquí vive en RAM como pide la práctica.
parking_lot = ParkingLot(policy=HourlyRatePolicy(car_rate=20.0, moto_rate=10.0))

# Historial de operaciones para mostrar en el dashboard
operation_log: list[dict] = []


def log_operation(message: str, kind: str = "info") -> None:
    operation_log.insert(0, {
        "message": message,
        "kind": kind,
        "time": datetime.now().strftime("%H:%M:%S"),
    })
    # Mantener solo los últimos 20 eventos
    if len(operation_log) > 20:
        operation_log.pop()


# ── Rutas ───────────────────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    """GET / — Dashboard: ocupación + tickets activos."""
    occ = parking_lot.get_occupancy()
    spots = [s.to_dict() for s in parking_lot.get_spots()]
    active_tickets = [t.to_dict() for t in parking_lot.get_active_tickets()]
    policy_desc = parking_lot.get_policy().describe()
    return render_template(
        "dashboard.html",
        occupancy=occ,
        spots=spots,
        active_tickets=active_tickets,
        total_revenue=parking_lot.get_total_revenue(),
        policy=policy_desc,
        log=operation_log[:10],
    )


@app.route("/entry", methods=["GET"])
def entry_get():
    """GET /entry — Formulario de entrada de vehículo."""
    return render_template("entry.html")


@app.route("/entry", methods=["POST"])
def entry_post():
    """POST /entry — Registrar entrada."""
    plate = request.form.get("plate", "").strip()
    vehicle_type = request.form.get("vehicle_type", "").strip()

    # Validación de campos
    if not plate:
        flash("Las placas son obligatorias.", "error")
        return render_template("entry.html"), 400
    if vehicle_type not in ("Car", "Motorcycle"):
        flash("Selecciona un tipo de vehículo válido.", "error")
        return render_template("entry.html"), 400

    try:
        vehicle = vehicle_factory(plate, vehicle_type)
        ticket = parking_lot.enter(vehicle, datetime.now())
        msg = (
            f"Entrada registrada — Ticket #{ticket.get_id()} | "
            f"{vehicle} | Spot: {ticket.get_spot().get_id()}"
        )
        flash(msg, "success")
        log_operation(msg, "success")
        return redirect(url_for("dashboard"))
    except ValueError as e:
        flash(str(e), "error")
        log_operation(f"Error de entrada ({plate}): {e}", "error")
        return render_template("entry.html"), 400


@app.route("/exit", methods=["GET"])
def exit_get():
    """GET /exit — Formulario de salida."""
    active_tickets = [t.to_dict() for t in parking_lot.get_active_tickets()]
    return render_template("exit.html", active_tickets=active_tickets)


@app.route("/exit", methods=["POST"])
def exit_post():
    """POST /exit — Registrar salida."""
    raw_id = request.form.get("ticket_id", "").strip()

    # Validar formato
    if not raw_id.isdigit():
        flash("El número de ticket debe ser un entero positivo.", "error")
        active_tickets = [t.to_dict() for t in parking_lot.get_active_tickets()]
        return render_template("exit.html", active_tickets=active_tickets), 400

    ticket_id = int(raw_id)
    try:
        ticket, cost = parking_lot.exit(ticket_id, datetime.now())
        hours = ticket.get_duration_hours()
        msg = (
            f"Salida registrada — Ticket #{ticket_id} | "
            f"{ticket.get_vehicle()} | Tiempo: {hours:.2f}h | "
            f"Costo: ${cost:.2f} | Spot liberado: {ticket.get_spot().get_id()}"
        )
        flash(msg, "success")
        log_operation(msg, "success")
        return redirect(url_for("dashboard"))
    except ValueError as e:
        flash(str(e), "error")
        log_operation(f"Error de salida (ticket #{ticket_id}): {e}", "error")
        active_tickets = [t.to_dict() for t in parking_lot.get_active_tickets()]
        return render_template("exit.html", active_tickets=active_tickets), 404


@app.route("/policy", methods=["POST"])
def change_policy():
    """POST /policy — Cambiar política de cobro (demo de polimorfismo)."""
    policy_key = request.form.get("policy", "hourly")
    if policy_key == "flat":
        parking_lot.set_policy(FlatRatePolicy(flat_amount=50.0))
        msg = "Política cambiada a: Tarifa Fija ($50 por visita)"
    else:
        parking_lot.set_policy(HourlyRatePolicy(car_rate=20.0, moto_rate=10.0))
        msg = "Política cambiada a: Tarifa por Hora (Auto $20/hr, Moto $10/hr)"
    flash(msg, "info")
    log_operation(msg, "info")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    print("\n  Simulador de Estacionamiento — Flask\n")
    print("  Abre en tu navegador: http://127.0.0.1:5000\n")
    app.run(debug=True)
