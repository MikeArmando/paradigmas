// ------------------- LIBRERIAS -------------------
#include <stdio.h>
#include <stdlib.h>
#include "tools.h"

#define MAX 10

// ------------------- STRUCTS -------------------
typedef struct
{
    int id;
    char usuario[32];
    char domicilio[82];
    int paginasTotales;
    int paginasRestantes;
    int copias;
    int prioridad;
    int estado;
} Trabajo;

typedef struct Nodo
{
    Trabajo dato;
    struct Nodo *siguiente;
} Nodo;

typedef struct
{
    Nodo *frente;
    Nodo *final;
    int cant;
} Queue;

// ------------------- PROTOTIPOS -------------------
int msg();
void menu();
Trabajo crearTrabajo(int *trabajoId);
void initQueue(Queue *queue);
void inQueue(Queue *queue, Trabajo trabajo);
void deQueue(Queue *queue);
void isEmpty(Queue *queue);
void isFull(Queue *queue);
void peek(Queue *queue);
void printQueue(Queue *queue);
void limpiarQueue(Queue *queue);

// ------------------- MAIN -------------------
int main()
{
    menu();
    return 0;
}

// ----------------------------------------------------------------------------
void menu(void)
{
    Queue queue;
    Trabajo trabajo;

    int trabajoId = 0;

    initQueue(&queue);

    int op;
    do
    {
        op = msg();
        switch (op)
        {
        case 1:
            trabajo = crearTrabajo(&trabajoId);
            inQueue(&queue, trabajo);
            break;
        case 2:
            deQueue(&queue);
            break;
        case 3:
            peek(&queue);
            pause("Presione una tecla para continuar...");
            break;
        case 4:
            isEmpty(&queue);
            pause("Presione una tecla para continuar...");
            break;
        case 5:
            isFull(&queue);
            pause("Presione una tecla para continuar...");
            break;
        case 6:
            printQueue(&queue);
            pause("Presione una tecla para continuar...");
            break;
        case 0:
            limpiarQueue(&queue);
            pause("Memoria limpiada correctamente.");
            op = 0;
            break;
        }
    } while (op != 0);
}

// ----------------------------------------------------------------------------
int msg()
{
    int op;
    printf("\nM  E  N  U\n");
    printf("1.- AGREGAR TRABAJO. \n");
    printf("2.- PROCESAR TRABAJO. \n");
    printf("3.- VER SIGUIENTE TRABAJO. \n");
    printf("4.- REVISAR SI LA COLA ESTA VACIA. \n");
    printf("5.- REVISAR SI LA COLA ESTA LLENA.  \n");
    printf("6.- LISTAR COLA.  \n");
    printf("0.- SALIR.  \n");
    op = validarNum(0, 7, "Escoge un opcion: ");
    return op;
}

// ----------------------------------------------------------------------------
Trabajo crearTrabajo(int *trabajoId)
{
    Trabajo trabajo;

    trabajo.id = ++(*trabajoId);

    validarString(trabajo.usuario, 32, "Usuario: ");

    validarString(trabajo.domicilio, 82, "Domicilio: ");

    trabajo.paginasTotales = validarNum(1, 500, "Total de páginas (1 a 500): ");

    trabajo.paginasRestantes = trabajo.paginasTotales;

    trabajo.copias = validarNum(1, 200, "Copias (1 a 200): ");

    trabajo.prioridad = validarNum(1, 2, "Prioridad (1 - Normal, 2 - Urgente): ");

    trabajo.estado = 1;

    return trabajo;
}

// ----------------------------------------------------------------------------
void initQueue(Queue *queue)
{
    queue->frente = NULL;
    queue->final = NULL;
    queue->cant = 0;
}

// ----------------------------------------------------------------------------
void inQueue(Queue *queue, Trabajo trabajo)
{
    if (queue->cant == MAX)
    {
        pause("Ya se agrego la cantidad maxima de trabajos.");
        return;
    }

    Nodo *nuevoNodo = (Nodo *)malloc(sizeof(Nodo));
    if (nuevoNodo == NULL)
    {
        pause("Error al crear elemento.");
        return;
    }

    nuevoNodo->dato = trabajo;
    nuevoNodo->siguiente = NULL;

    if (queue->cant == 0)
    {
        queue->frente = nuevoNodo;
    }
    else
    {
        queue->final->siguiente = nuevoNodo;
    }

    queue->final = nuevoNodo;
    queue->cant++;

    pause("Trabajo agregado exitosamente.");
}

// ----------------------------------------------------------------------------
void deQueue(Queue *queue)
{
    if (queue->cant == 0)
    {
        pause("Cola esta vacia.");
        return;
    }

    Nodo *actual = queue->frente;
    queue->frente = queue->frente->siguiente;

    free(actual);

    queue->cant--;

    if (queue->cant == 0)
    {
        queue->final = NULL;
    }

    pause("Trabajo completado y liberado.");
}

// ----------------------------------------------------------------------------
void isEmpty(Queue *queue)
{
    if (queue->cant == 0)
    {
        pause("La cola esta vacia.");
    }
    else
    {
        pause("La cola NO esta vacia.");
    }
}

// ----------------------------------------------------------------------------
void isFull(Queue *queue)
{
    if (queue->cant == MAX)
    {
        pause("La cola esta llena.");
    }
    else
    {
        pause("La cola NO esta llena.");
    }
}

// ----------------------------------------------------------------------------
void peek(Queue *queue)
{
    const char *prioridad[] = {"Normal", "Urgente"};
    const char *estado[] = {"En cola"};

    if (queue->cant == 0)
    {
        pause("La cola esta vacia.");
        return;
    }

    printf("| %5s | %15s | %15s | %15s | %15s | %15s | %15s | %15s |\n",
           "ID", "USUARIO", "DOMICILIO", "PAG. TOTALES", "PAG. RESTANTES", "COPIAS", "PRIORIDAD", "ESTADO");
    printf("| %5d | %15s | %15s | %15d | %15d | %15d | %15s | %15s |\n",
           queue->frente->dato.id, queue->frente->dato.usuario, queue->frente->dato.domicilio, queue->frente->dato.paginasTotales, queue->frente->dato.paginasRestantes, queue->frente->dato.copias, prioridad[queue->frente->dato.prioridad - 1], estado[queue->frente->dato.estado - 1]);
}

// ----------------------------------------------------------------------------
void printQueue(Queue *queue)
{
    const char *prioridad[] = {"Normal", "Urgente"};
    const char *estado[] = {"En cola"};

    if (queue->cant == 0)
    {
        pause("La cola esta vacia.");
        return;
    }

    Nodo *actual = queue->frente;

    printf("| %5s | %15s | %15s | %15s | %15s | %15s | %15s | %15s |\n",
           "ID", "USUARIO", "DOMICILIO", "PAG. TOTALES", "PAG. RESTANTES", "COPIAS", "PRIORIDAD", "ESTADO");
    while (actual != NULL)
    {
        printf("| %5d | %15s | %15s | %15d | %15d | %15d | %15s | %15s |\n",
               actual->dato.id, actual->dato.usuario, actual->dato.domicilio, actual->dato.paginasTotales, actual->dato.paginasRestantes, actual->dato.copias, prioridad[actual->dato.prioridad - 1], estado[actual->dato.estado - 1]);

        actual = actual->siguiente;
    }
}

// ----------------------------------------------------------------------------
void limpiarQueue(Queue *queue)
{
    Nodo *actual = queue->frente;
    Nodo *anterior = NULL;

    while (actual != NULL)
    {
        anterior = actual;
        actual = actual->siguiente;

        free(anterior);
    }

    queue->frente = NULL;
    queue->final = NULL;
    queue->cant = 0;
}
