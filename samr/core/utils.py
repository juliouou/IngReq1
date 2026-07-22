"""Utilidades generales del proyecto SAMR."""
import random
import string


def generar_codigo(prefijo="", longitud=8):
    """Genera un codigo alfanumerico en mayusculas con prefijo opcional."""
    caracteres = string.ascii_uppercase + string.digits
    aleatorio = "".join(random.choice(caracteres) for _ in range(longitud))
    return "{0}{1}".format(prefijo, aleatorio)


def generar_cedula_valida():
    """
    Genera una cedula ecuatoriana valida (10 digitos con verificador correcto).

    Se usa en el seed para no incrustar cedulas fijas en el codigo.
    """
    provincia = random.randint(1, 24)
    digitos = [provincia // 10, provincia % 10, random.randint(0, 5)]
    digitos += [random.randint(0, 9) for _ in range(6)]

    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    total = 0
    for indice in range(9):
        producto = digitos[indice] * coeficientes[indice]
        if producto >= 10:
            producto -= 9
        total += producto

    verificador = (10 - (total % 10)) % 10
    digitos.append(verificador)
    return "".join(str(digito) for digito in digitos)


def generar_telefono_ec():
    """Genera un numero de telefono movil ecuatoriano valido para pruebas."""
    return "09" + "".join(str(random.randint(0, 9)) for _ in range(8))
