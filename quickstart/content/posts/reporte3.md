+++
draft = false
title = 'Reporte No. 3'

[header]
  featured = true
summary = "Práctica 2: Programación Orientada a Objetos"
+++

# Práctica 2: Simulador de Estacionamiento

Link de portafolio en GitHub: [Asignatura Paradigmas](https://github.com/MikeArmando/asignatura-paradigmas)

Link de portafolio en GitHub Pages (página estática): [Asignatura Paradigmas](https://mikearmando.github.io/asignatura-paradigmas/)

## 1. Introducción

### Problema

Se requiere diseñar e implementar un **Simulador de Estacionamiento** que administre los lugares físicos (spots), los vehículos que ingresan y los tickets que documentan cada visita. El sistema debe registrar entradas y salidas de vehículos, calcular cobros según una política de tarifas configurable, y mostrar en todo momento el estado de ocupación del estacionamiento.

El sistema parte de dos restricciones fundamentales: un lugar solo puede ser ocupado por un vehículo a la vez, y un ticket activo representa a un vehículo que se encuentra dentro del estacionamiento en ese momento.

### Objetivos

El objetivo principal de la práctica es diseñar e implementar un sistema completo aplicando el **paradigma de Programación Orientada a Objetos (POO)**, abarcando los siguientes conceptos:

- Modelado del dominio mediante clases con atributos y métodos.
- Encapsulación de datos internos y validación de invariantes.
- Abstracción mediante interfaces de cobro desacopladas del resto del sistema.
- Composición entre objetos del dominio.
- Herencia y subtipos entre vehículos.
- Polimorfismo con diferentes políticas de tarifa.
- Integración del modelo en una interfaz web con Flask bajo un patrón MVC simple.

La práctica se desarrolló en tres sesiones iterativas: la primera establece el modelo y un prototipo funcional en consola; la segunda introduce polimorfismo y subtipos; la tercera agrega la interfaz web con Flask.

---

## 2. Modelo del dominio

### Diagrama UML (clases y relaciones)

```
┌─────────────────┐        ┌───────────────────────────────────────────┐
│  <<enumeration>>│        │                 ParkingLot                │
│   VehicleType   │        │  ─ _spots: List[ParkingSpot]              │
│─────────────────│        │  ─ _active_tickets: Dict[int, Ticket]     │
│  CAR            │        │  ─ _policy: RatePolicy                    │
│  MOTORCYCLE     │        │  ─ _next_ticket_id: int                   │
└─────────────────┘        │  ─ _total_revenue: float                  │
                           │  ────────────────────────────────────────  │
┌─────────────────┐        │  + enter(v: Vehicle, now): Ticket         │
│  <<enumeration>>│        │  + exit(ticket_id, now): (Ticket, float)  │
│    SpotType     │        │  + get_occupancy(): dict                  │
│─────────────────│        │  + get_active_tickets(): List[Ticket]     │
│  CAR            │        └───────────────┬───────────────────────────┘
│  MOTORCYCLE     │                        │ manages (composición)
│  ANY            │              ┌─────────┴──────────┐
└─────────────────┘              ▼                    ▼
                        ┌────────────────┐   ┌──────────────────────────┐
                        │  ParkingSpot   │   │         Ticket            │
                        │────────────────│   │──────────────────────────│
                        │ ─ _spot_id     │   │ ─ _ticket_id: int        │
                        │ ─ _allowed     │   │ ─ _vehicle: Vehicle      │
                        │ ─ _occupied    │   │ ─ _spot: ParkingSpot     │
                        │ ─ _current_veh │   │ ─ _entry_time: datetime  │
                        │────────────────│   │ ─ _exit_time: datetime   │
                        │ + is_available │   │ ─ _status: TicketStatus  │
                        │ + park(v)      │   │──────────────────────────│
                        │ + release()    │   │ + close(exit_time)       │
                        └───────┬────────┘   │ + get_duration_hours()   │
                                │ current    └──────────┬───────────────┘
                                ▼                       │ has a
                        ┌───────────────┐               ▼
                        │  <<abstract>> │       ┌───────────────┐
                        │    Vehicle    │       │  <<Protocol>> │
                        │───────────────│       │  RatePolicy   │
                        │ ─ _plate: str │       │───────────────│
                        │ ─ _type       │       │ + calculate() │
                        │───────────────│       │ + describe()  │
                        │ + get_plate() │       └───────┬───────┘
                        │ + get_type()  │               │ implements
                        └───────┬───────┘     ┌─────────┴──────────────┐
                                │ herencia     ▼                        ▼
                    ┌───────────┴──────┐  ┌────────────────┐  ┌─────────────────┐
                    ▼                  ▼  │HourlyRatePolicy│  │ FlatRatePolicy  │
               ┌─────────┐   ┌──────────┐│────────────────│  │─────────────────│
               │   Car   │   │Motorcycle││ ─ _car_rate    │  │ ─ _flat_amount  │
               └─────────┘   └──────────┘│ ─ _moto_rate  │  │ + calculate()   │
                                         │ + calculate()  │  └─────────────────┘
                                         └────────────────┘
```

### Lista de clases y responsabilidades

| Clase              | Responsabilidad                                                                                                |
| ------------------ | -------------------------------------------------------------------------------------------------------------- |
| `Vehicle`          | Abstracción base del vehículo. Encapsula placa y tipo. No se instancia directamente.                           |
| `Car`              | Subtipo concreto de Vehicle para automóviles.                                                                  |
| `Motorcycle`       | Subtipo concreto de Vehicle para motocicletas.                                                                 |
| `ParkingSpot`      | Representa un lugar físico. Protege la invariante de ocupación única.                                          |
| `Ticket`           | Documenta la visita de un vehículo: tiempo, spot asignado y estado (ACTIVE/CLOSED).                            |
| `ParkingLot`       | Clase central. Coordina la asignación de spots, creación y cierre de tickets, y delega el cobro a la política. |
| `RatePolicy`       | Interfaz (Protocol) común para políticas de cobro. Define el contrato `calculate(hours, vehicle)`.             |
| `HourlyRatePolicy` | Implementación de tarifa por hora, diferenciada por tipo de vehículo.                                          |
| `FlatRatePolicy`   | Implementación de tarifa fija sin importar tiempo ni tipo.                                                     |

---

## 3. Evidencia de Conceptos POO

### 3.1 Encapsulación

La encapsulación se aplica en la clase `ParkingSpot`. Sus atributos internos `_occupied` y `_current_vehicle` solo pueden modificarse a través del método `park()`, el cual valida la invariante antes de cambiar el estado. Ninguna parte externa del sistema puede escribir directamente `spot._occupied = True`.

```python
# models/spot.py

class ParkingSpot:
    def __init__(self, spot_id: str, allowed: SpotType) -> None:
        self._spot_id: str = spot_id
        self._allowed: SpotType = allowed
        self._occupied: bool = False               # atributo privado
        self._current_vehicle: Optional[Vehicle] = None  # atributo privado

    def park(self, vehicle: Vehicle) -> None:
        """
        Único camino para ocupar el lugar.
        Valida la invariante ANTES de modificar el estado:
        nunca dos vehículos en el mismo spot.
        """
        if self._occupied:
            raise RuntimeError(
                f"Invariante violada: el lugar {self._spot_id} ya está ocupado."
            )
        if not self.is_available_for(vehicle):
            raise ValueError(
                f"El vehículo {vehicle} no es compatible con el lugar {self._spot_id}."
            )
        self._occupied = True
        self._current_vehicle = vehicle

    def release(self) -> None:
        """Libera el lugar de forma controlada."""
        self._occupied = False
        self._current_vehicle = None
```

**Invariante protegida:** el sistema nunca puede quedar con dos vehículos en el mismo spot, porque `park()` lanza una excepción antes de permitirlo. Esta validación vive dentro del objeto, no en el código que lo usa.

---

### 3.2 Abstracción

La lógica de cobro está completamente separada del resto del sistema mediante la interfaz `RatePolicy`, definida como un `Protocol` de Python. Esto significa que cualquier clase que implemente `calculate(hours, vehicle)` y `describe()` cumple el contrato, sin necesidad de heredar de ninguna clase base.

```python
# models/rates.py

from typing import Protocol, runtime_checkable
from models.vehicle import Vehicle

@runtime_checkable
class RatePolicy(Protocol):
    """
    Interfaz común para políticas de cobro.
    Define el contrato: qué debe poder hacer cualquier política.
    No dice cómo — eso lo decide cada implementación.
    """

    def calculate(self, hours: float, vehicle: Vehicle) -> float:
        """Calcula el costo dado el tiempo en horas y el vehículo."""
        ...

    def describe(self) -> str:
        """Descripción legible de la política activa."""
        ...
```

`ParkingLot` trabaja exclusivamente con este contrato, sin saber qué implementación está usando:

```python
# models/parking_lot.py

class ParkingLot:
    def __init__(self, policy: RatePolicy):
        self._policy = policy   # recibe cualquier cosa que cumpla el contrato

    def exit(self, ticket_id, now):
        ...
        hours = ticket.get_duration_hours()
        cost = self._policy.calculate(hours, ticket.get_vehicle())  # abstracción pura
        ...
```

**Ventaja:** si mañana se necesita una nueva política (por ejemplo, `WeekendRatePolicy`), se crea la clase nueva y se inyecta en `ParkingLot`. El resto del sistema no se modifica.

---

### 3.3 Composición

`ParkingLot` está construido a partir de colecciones de otros objetos. Esta relación "tiene un" / "está formado por" es composición. El estacionamiento no es un spot ni un ticket — los tiene y los administra.

```python
# models/parking_lot.py

class ParkingLot:
    def __init__(
        self,
        spots: Optional[list[ParkingSpot]] = None,
        policy: Optional[RatePolicy] = None,
    ) -> None:
        # Composición: ParkingLot TIENE una colección de ParkingSpot
        self._spots: list[ParkingSpot] = spots if spots is not None else _build_default_spots()

        # Composición: ParkingLot TIENE un diccionario de Ticket activos
        self._active_tickets: dict[int, Ticket] = {}

        # Inyección de dependencia: la política de cobro se pasa desde afuera
        self._policy: RatePolicy = policy if policy is not None else HourlyRatePolicy()

        self._next_ticket_id: int = 1
        self._total_revenue: float = 0.0
```

A su vez, `Ticket` también usa composición: tiene referencias a un `Vehicle` y a un `ParkingSpot`.

```python
# models/ticket.py

class Ticket:
    def __init__(self, ticket_id, vehicle, spot, entry_time):
        self._vehicle: Vehicle = vehicle       # Ticket TIENE un Vehicle
        self._spot: ParkingSpot = spot         # Ticket TIENE un ParkingSpot
        self._entry_time: datetime = entry_time
        self._status: TicketStatus = TicketStatus.ACTIVE
```

---

### 3.4 Herencia y subtipos

`Vehicle` es una clase abstracta (ABC). No puede instanciarse directamente porque no tiene sentido crear un "vehículo genérico" sin saber si es auto o moto. `Car` y `Motorcycle` son sus subtipos concretos, y heredan todos los atributos y métodos de la clase base sin duplicar código.

```python
# models/vehicle.py

from abc import ABC

class Vehicle(ABC):
    """Clase abstracta — no se puede instanciar directamente."""

    def __init__(self, plate: str, vehicle_type: VehicleType) -> None:
        if not plate or not plate.strip():
            raise ValueError("Las placas no pueden estar vacías.")
        self._plate: str = plate.strip().upper()
        self._type: VehicleType = vehicle_type

    def get_plate(self) -> str:    # método heredado por Car y Motorcycle
        return self._plate

    def get_type(self) -> VehicleType:
        return self._type


class Car(Vehicle):
    """Subtipo Car — hereda estructura y comportamiento de Vehicle."""

    def __init__(self, plate: str) -> None:
        super().__init__(plate, VehicleType.CAR)   # llama al constructor del padre


class Motorcycle(Vehicle):
    """Subtipo Motorcycle — hereda estructura y comportamiento de Vehicle."""

    def __init__(self, plate: str) -> None:
        super().__init__(plate, VehicleType.MOTORCYCLE)
```

**Principio de Sustitución de Liskov:** en cualquier lugar donde el sistema espera un `Vehicle`, puede recibir un `Car` o una `Motorcycle` sin que nada se rompa. Por ejemplo, `ParkingSpot.park(vehicle)` acepta cualquier subtipo sin cambiar su código.

---

### 3.5 Polimorfismo

El polimorfismo se evidencia en dos niveles:

**Nivel 1 — Política de cobro:** `HourlyRatePolicy` y `FlatRatePolicy` implementan el mismo método `calculate(hours, vehicle)`. El resultado es diferente según qué implementación esté activa, pero `ParkingLot` llama siempre al mismo mensaje.

```python
# models/rates.py

class HourlyRatePolicy:
    """Cobra según las horas y el tipo de vehículo."""

    def __init__(self, car_rate: float = 20.0, moto_rate: float = 10.0) -> None:
        self._car_rate = car_rate
        self._moto_rate = moto_rate

    def calculate(self, hours: float, vehicle: Vehicle) -> float:
        rate = self._car_rate if vehicle.get_type() == VehicleType.CAR else self._moto_rate
        return round(hours * rate, 2)


class FlatRatePolicy:
    """Siempre cobra el mismo monto sin importar tiempo ni tipo."""

    def __init__(self, flat_amount: float = 50.0) -> None:
        self._flat_amount = flat_amount

    def calculate(self, hours: float, vehicle: Vehicle) -> float:
        return self._flat_amount   # horas y tipo son irrelevantes aquí
```

**Nivel 2 — Subtipo de vehículo:** dentro de `HourlyRatePolicy`, el costo ya varía según el subtipo recibido:

```python
# El mismo método, distinto resultado según el subtipo:
rate = self._car_rate if vehicle.get_type() == VehicleType.CAR else self._moto_rate
```

**Demostración del polimorfismo en ejecución:**

```
# Con HourlyRatePolicy activa (Auto $20/hr, Moto $10/hr):
Salida Auto  2h → costo = $40.00
Salida Moto  2h → costo = $20.00

# Misma llamada, política cambiada a FlatRatePolicy ($50 fija):
Salida Auto 12h → costo = $50.00   ← las horas no importan
Salida Moto 12h → costo = $50.00   ← el tipo no importa
```

El cambio de política se hace inyectando el nuevo objeto sin tocar el código de `ParkingLot`:

```python
# app.py / cli.py

lot.set_policy(FlatRatePolicy(flat_amount=50.0))
# A partir de aquí, todas las salidas usarán la tarifa fija.
# ParkingLot.exit() no cambió ni una línea.
```

---

## 4. MVC con Flask

### Separación de capas

La arquitectura de la sesión 3 sigue el patrón **Model-View-Controller**:

| Capa           | Archivos                                                                                              | Responsabilidad                                                                                              |
| -------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| **Model**      | `models/vehicle.py`, `models/spot.py`, `models/ticket.py`, `models/parking_lot.py`, `models/rates.py` | Toda la lógica de negocio: crear vehículos, asignar spots, calcular cobros. No sabe nada de HTTP ni de HTML. |
| **View**       | `templates/base.html`, `templates/dashboard.html`, `templates/entry.html`, `templates/exit.html`      | Presentación pura. Recibe datos ya procesados y los muestra. No contiene lógica de negocio.                  |
| **Controller** | `app.py`                                                                                              | Recibe peticiones HTTP, llama al modelo, pasa resultados a la vista. Delgado por diseño.                     |

### Rutas implementadas

| Método | Ruta      | Descripción                                                                                |
| ------ | --------- | ------------------------------------------------------------------------------------------ |
| GET    | `/`       | Dashboard: muestra ocupación de spots y tickets activos.                                   |
| GET    | `/entry`  | Muestra el formulario de entrada de vehículo.                                              |
| POST   | `/entry`  | Procesa el formulario: valida datos, llama a `parking_lot.enter()`, redirige al dashboard. |
| GET    | `/exit`   | Muestra el formulario de salida con la lista de tickets activos.                           |
| POST   | `/exit`   | Procesa la salida: llama a `parking_lot.exit()`, muestra el costo calculado.               |
| POST   | `/policy` | Cambia la política de cobro en tiempo de ejecución (demostración de polimorfismo).         |

### Pantallas implementadas

**Dashboard (`/`):** muestra tarjetas de estadísticas (spots libres, ocupados, total, recaudación), el mapa visual de todos los lugares con su estado (verde = libre, rojo = ocupado), la tabla de tickets activos y un registro de las últimas operaciones. También permite cambiar la política de cobro desde aquí.

![EVIDENCIA](img/p2_dashboard.png)

**Registrar entrada (`/entry`):** formulario con campo de placas y selector de tipo de vehículo (Car / Motorcycle) con tarjetas visuales. Al enviarlo, el controlador delega toda la validación de compatibilidad y disponibilidad al modelo.

![EVIDENCIA](img/p2_entry.png)

**Registrar salida (`/exit`):** formulario para ingresar el número de ticket a cerrar. Muestra una tabla con todos los tickets activos; al hacer clic en una fila se autocompleta el campo. Al procesar, el sistema calcula el costo con la `RatePolicy` activa y muestra el resultado mediante un mensaje flash.

![EVIDENCIA](img/p2_exit.png)

---

## 5. Pruebas manuales

### Flujo completo 1 — Entrada y salida normal con tarifa horaria

**Configuración:** HourlyRatePolicy (Auto $20/hr, Moto $10/hr), spots disponibles A1–A5, M1–M3, B1–B2.

| Paso | Acción                                               | Resultado esperado                          | Resultado obtenido      |
| ---- | ---------------------------------------------------- | ------------------------------------------- | ----------------------- |
| 1    | Registrar entrada: placas=`ABC-123`, tipo=Car        | Ticket #1 asignado a spot A1, estado ACTIVE | ✔ Ticket #1, spot=A1    |
| 2    | Registrar entrada: placas=`XYZ-777`, tipo=Motorcycle | Ticket #2 asignado a spot M1, estado ACTIVE | ✔ Ticket #2, spot=M1    |
| 3    | Consultar ocupación                                  | libres=8, ocupados=2                        | ✔ libres=8, ocupados=2  |
| 4    | Ver tickets activos                                  | Lista con tickets #1 y #2                   | ✔ [#1, #2]              |
| 5    | Registrar salida ticket #1 (2h transcurridas)        | Costo=$40.00, spot A1 liberado              | ✔ $40.00, spot A1 libre |
| 6    | Consultar ocupación                                  | libres=9, ocupados=1                        | ✔ libres=9, ocupados=1  |
| 7    | Ver tickets activos                                  | Solo ticket #2                              | ✔ [#2]                  |

**Evidencia de consola:**

- Consulta:
 
![EVIDENCIA](img/p2_cli1.png)

- Tickets activos:

![EVIDENCIA](img/p2_cli2.png)

- Registrar salida:

![EVIDENCIA](img/p2_cli3.png)

- Consulta actualizada:

![EVIDENCIA](img/p2_cli4.png)

- Tickets activos:

![EVIDENCIA](img/p2_cli5.png)


### Flujo completo 2 — Demostración de polimorfismo: cambio de política en caliente

**Objetivo:** demostrar que el mismo código de `ParkingLot.exit()` produce resultados distintos según la política activa.

| Paso | Acción                                         | Resultado esperado                  | Resultado obtenido   |
| ---- | ---------------------------------------------- | ----------------------------------- | -------------------- |
| 1    | Activar HourlyRatePolicy ($20 auto / $10 moto) | Política confirmada                 | ✔                    |
| 2    | Entrada: `POL-001` tipo=Car                    | Ticket #1 creado                    | ✔ Ticket #1, spot A1 |
| 3    | Entrada: `POL-002` tipo=Motorcycle             | Ticket #2 creado                    | ✔ Ticket #2, spot M1 |
| 4    | Salida ticket #1 (2h), política=Hourly         | Costo Auto 2h = $40.00              | ✔ $40.00             |
| 5    | Salida ticket #2 (2h), política=Hourly         | Costo Moto 2h = $20.00              | ✔ $20.00             |
| 6    | Cambiar política a FlatRatePolicy ($50 fija)   | Política cambiada                   | ✔                    |
| 7    | Entrada: `FLAT-001` tipo=Car                   | Ticket #3 creado                    | ✔ Ticket #35, spot A1 |
| 8    | Salida ticket #3 (12h), política=Flat          | Costo = $50.00 (horas irrelevantes) | ✔ $50.00             |

**Conclusión del flujo 2:** el método `parking_lot.exit()` no se modificó en ningún paso. El cambio de comportamiento ocurrió exclusivamente por sustituir el objeto `_policy`. Esto es polimorfismo en su expresión más directa.

**Evidencia de consola:**

- Activar HourlyRatePolicy:
 
![EVIDENCIA](img/p2_cli6.png)

- Entrada: `POL-001`:
 
![EVIDENCIA](img/p2_cli7.png)

- Entrada: `POL-002`:

![EVIDENCIA](img/p2_cli8.png)

- Salida ticket #1:

![EVIDENCIA](img/p2_cli9.png)

- Salida ticket #2:

![EVIDENCIA](img/p2_cli10.png)

- Cambiar política a FlatRatePolicy:

![EVIDENCIA](img/p2_cli11.png)

- Entrada: `FLAT-001`:

![EVIDENCIA](img/p2_cli12.png)

- Salida ticket #3:

![EVIDENCIA](img/p2_cli13.png)

---

## 6. Conclusiones

El primer paso y el más importante fue identificar correctamente las entidades del problema y asignar a cada clase una única responsabilidad. La clase `ParkingLot` actúa como coordinadora sin duplicar lógica que pertenece a `ParkingSpot` o `Ticket`. Esta separación hizo que el código fuera legible y fácil de extender. Proteger los atributos internos con el prefijo `_` y forzar el acceso a través de métodos con validación demostró su valor especialmente en `ParkingSpot.park()`. Definir `RatePolicy` como un `Protocol` fue la decisión de diseño con mayor impacto en extensibilidad. Cuando se añadió `FlatRatePolicy` en la sesión 2, no fue necesario tocar ni una línea de `ParkingLot`. El mismo `exit()` funcionó con la nueva política sin modificarse. Esto confirmó en la práctica el Principio Abierto/Cerrado: el sistema estaba abierto a extensión y cerrado a modificación. Usar `Vehicle` como clase abstracta forzó a que siempre se trabaje con subtipos concretos (`Car`, `Motorcycle`), eliminando estados ambiguos. La herencia evitó duplicación de código: la validación de placas, los accesores y la representación en cadena se escribieron una sola vez en `Vehicle`. La sesión 3 demostró el verdadero valor de haber diseñado bien el modelo primero. Las rutas en `app.py` quedaron delgadas porque toda la lógica ya existía en `models/`. Si el modelo hubiera estado acoplado al menú de consola, migrar a Flask habría requerido reescribir todo. Al tener el modelo independiente, la migración fue añadir un controlador nuevo sin cambiar nada en `models/`. En conjunto, la práctica mostró que los conceptos de POO no son elementos aislados: la encapsulación protege el estado que la composición conecta, la abstracción habilita el polimorfismo, y la herencia organiza los subtipos. El MVC es la consecuencia natural de aplicar bien estos principios: cuando cada clase tiene una sola responsabilidad, la separación en capas surge de forma casi automática.

## 7. Referencias
 
Fowler, M. (2004). *Inversion of Control Containers and the Dependency Injection pattern*. https://martinfowler.com/articles/injection.html
 
Pallets Projects. (2026). *Welcome to Flask — Flask Documentation (3.1.x)*. https://flask.palletsprojects.com/
 
Pallets Projects. (2026). *Quickstart — Flask Documentation (3.1.x)*. https://flask.palletsprojects.com/en/stable/quickstart/
 
Python Software Foundation. (2026). *dataclasses — Data Classes*. https://docs.python.org/3/library/dataclasses.html
 
Python Typing Team. (2026). *Protocols — typing specification*. https://typing.python.org/en/latest/spec/protocol.html
 
Flask-es Read the Docs. (2026). *Plantillas — Documentación de Flask (Tutorial)*. https://flask-es.readthedocs.io/tutorial/templates/
