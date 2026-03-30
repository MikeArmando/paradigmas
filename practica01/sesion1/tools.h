#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void pause(const char *frase);
int validarNum(int min, int max, const char *mensaje);
void validarString(char *destino, int max_tam, const char *mensaje);

// ----------------------------------------------------------------------------
void pause(const char *frase)
{
    printf("\n%s", frase);
    getchar();
    getchar();
    printf("\033[H\033[2J");
}

// ----------------------------------------------------------------------------
int validarNum(int min, int max, const char *mensaje)
{
    int num;
    int status;

    do
    {
        printf("%s", mensaje);

        status = scanf("%d", &num);

        if (status != 1)
        {
            printf("Error: Ingrese un numero valido.\n");
            while (getchar() != '\n')
                ;
            continue;
        }

        if (num < min || num > max)
        {
            printf("Error: Valor debe estar entre %d y %d.\n", min, max);
        }

    } while (status != 1 || num < min || num > max);

    return num;
}

// ----------------------------------------------------------------------------
void validarString(char *destino, int max_tam, const char *mensaje)
{
    int valida = 0;
    do
    {
        printf("%s", mensaje);

        char formato[20];
        sprintf(formato, " %%%d[^\n]", max_tam - 1);

        if (scanf(formato, destino) == 1)
        {
            if (strlen(destino) > 0)
            {
                valida = 1;
            }
        }
        else
        {
            printf("Error: Entrada no valida.\n");
        }

        if (!valida)
        {
            printf("Error: Este campo no puede quedar vacio.\n");
            while (getchar() != '\n')
                ;
        }

    } while (!valida);
}