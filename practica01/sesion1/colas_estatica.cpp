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

typedef struct
{
    Trabajo datos[MAX];
    int frente;
    int final;
    int cant;
} Queue;

// ------------------- PROTOTIPOS -------------------
int msg();
void menu();
void agregarTrabajo(Trabajo *trabajo);
void initQueue(Queue *queue);
void inQueue(Queue *queue, Trabajo *trabajo);
void deQueue(Queue *queue);
void isEmpty(Queue *queue);
void isFull(Queue *queue);
void peek(Queue *queue);
void printQueue(Queue *queue);

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
    Trabajo trabajo = {0};

    initQueue(&queue);

    int op;
    do
    {
        op = msg();
        switch (op)
        {
        case 1:
            inQueue(&queue, &trabajo);
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
void initQueue(Queue *queue)
{
    queue->frente = 0;
    queue->final = 0;
    queue->cant = 0;
}

// ----------------------------------------------------------------------------
void agregarTrabajo(Trabajo *trabajo)
{
    trabajo->id++;

    validarString(trabajo->usuario, 32, "Usuario: ");

    validarString(trabajo->domicilio, 82, "Domicilio: ");

    trabajo->paginasTotales = validarNum(1, 500, "Total de páginas (1 a 500): ");

    trabajo->paginasRestantes = trabajo->paginasTotales;

    trabajo->copias = validarNum(1, 200, "Copias (1 a 200): ");

    trabajo->prioridad = validarNum(1, 2, "Prioridad (1 - Normal, 2 - Urgente): ");

    trabajo->estado = 1;
}

// ----------------------------------------------------------------------------
void inQueue(Queue *queue, Trabajo *trabajo)
{
    if (queue->cant == MAX)
    {
        pause("Cola esta llena.");
        return;
    }

    agregarTrabajo(trabajo);

    queue->datos[queue->final] = *trabajo;
    queue->final = (queue->final + 1) % MAX;

    queue->cant++;

    pause("Se agrego el trabajo correctamente a la cola.");
}

// ----------------------------------------------------------------------------
void deQueue(Queue *queue)
{
    if (queue->cant == 0)
    {
        pause("Cola esta vacia.");
        return;
    }

    Trabajo valorTmp = queue->datos[queue->frente];
    queue->frente = (queue->frente + 1) % MAX;

    queue->cant--;

    pause("Se completo el trabajo.");
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

    Trabajo trabajo = queue->datos[queue->frente];

    printf("| %5s | %15s | %15s | %15s | %15s | %15s | %15s | %15s |\n", "ID", "USUARIO", "DOMICILIO", "PAG. TOTALES", "PAG. RESTANTES", "COPIAS", "PRIORIDAD", "ESTADO");
    printf("| %5d | %15s | %15s | %15d | %15d | %15d | %15s | %15s |\n", trabajo.id, trabajo.usuario, trabajo.domicilio, trabajo.paginasTotales, trabajo.paginasRestantes, trabajo.copias, prioridad[trabajo.prioridad - 1], estado[trabajo.estado - 1]);
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

    printf("| %5s | %15s | %15s | %15s | %15s | %15s | %15s | %15s |\n", "ID", "USUARIO", "DOMICILIO", "PAG. TOTALES", "PAG. RESTANTES", "COPIAS", "PRIORIDAD", "ESTADO");
    for (int i = 0; i < queue->cant; i++)
    {
        int idx = (queue->frente + i) % MAX;
        printf("| %5d | %15s | %15s | %15d | %15d | %15d | %15s | %15s |\n", queue->datos[idx].id, queue->datos[idx].usuario, queue->datos[idx].domicilio, queue->datos[idx].paginasTotales, queue->datos[idx].paginasRestantes, queue->datos[idx].copias, prioridad[queue->datos[idx].prioridad - 1], estado[queue->datos[idx].estado - 1]);
    }
}
