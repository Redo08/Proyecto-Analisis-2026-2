"""
Funciones de utilidad individual u_i(x) disponibles (todas con u(0)=0, crecientes y cóncavas,
es decir, con ganancias marginales g(x) = u(x+1)-u(x) >= 0 y no crecientes, como exige el problema).

  tipo          u_i(x)                      parámetros
  log           w_i * ln(1 + x)             (ninguno)               [por defecto]
  sqrt          w_i * (sqrt(1 + x) - 1)     (ninguno)
  saturacion    w_i * x / (1 + x)           (ninguno)   tiende a w_i: rendimientos que se agotan
  potencia      w_i * ((1 + x)^p - 1)       exponente p, 0 < p < 1

Se elige en el JSON del caso:  "funcion_utilidad": {"tipo": "saturacion"}
o desde la línea de comandos:  python src/ejecutar_casos.py --utilidad potencia --exponente 0.5
Para agregar otra función: escribir su fábrica, registrarla en FUNCIONES y DESCRIPCION
(debe ser creciente y cóncava, con u(0)=0).

Toda función se construye con la misma firma: fabrica(w, spec) -> u, donde w[i] es el coeficiente
del nodo i y u(i, x) devuelve la utilidad del nodo i con x unidades; cada llamada cuesta O(1).
"""
import math


def _log(w, spec):
    """u_i(x) = w_i * ln(1 + x). Usa log1p, que es exacta para x pequeño."""
    return lambda i, x: w[i] * math.log1p(x)


def _sqrt(w, spec):
    """u_i(x) = w_i * (sqrt(1 + x) - 1)."""
    return lambda i, x: w[i] * (math.sqrt(1 + x) - 1)


def _saturacion(w, spec):
    """u_i(x) = w_i * x / (1 + x) = w_i * (1 - 1/(1+x)); crece hacia el techo w_i."""
    return lambda i, x: w[i] * x / (1 + x)


def _potencia(w, spec):
    """u_i(x) = w_i * ((1 + x)^p - 1) con p = spec["exponente"] en (0, 1)."""
    p = spec["exponente"]
    return lambda i, x: w[i] * ((1 + x) ** p - 1)


FUNCIONES = {"log": _log, "sqrt": _sqrt, "saturacion": _saturacion, "potencia": _potencia}

DESCRIPCION = {
    "log": "w_i*ln(1+x)",
    "sqrt": "w_i*(sqrt(1+x)-1)",
    "saturacion": "w_i*x/(1+x)",
    "potencia": "w_i*((1+x)^p-1)",
}


def validar(spec):
    """Valida y normaliza una especificación de utilidad.

    Args:
        spec: dict {"tipo": ..., ["exponente": p]}, o None/vacío para usar la función por defecto (log).

    Returns:
        Copia de la especificación con "tipo" presente.

    Raises:
        ValueError: tipo desconocido, o 'potencia' sin exponente en (0, 1) (con p >= 1 no sería cóncava).
    """
    spec = dict(spec or {"tipo": "log"})
    tipo = spec.get("tipo", "log")
    spec["tipo"] = tipo
    if tipo not in FUNCIONES:
        raise ValueError(f"funcion_utilidad.tipo desconocido '{tipo}'; opciones: {', '.join(FUNCIONES)}")
    if tipo == "potencia":
        p = spec.get("exponente")
        if not isinstance(p, (int, float)) or not 0 < p < 1:
            raise ValueError("funcion_utilidad 'potencia' exige 'exponente' p con 0 < p < 1 "
                             "(con p >= 1 no sería cóncava)")
    return spec


def construir(spec, w):
    """Crea la función u(i, x) para los coeficientes `w`.

    Args:
        spec: especificación (se valida; None equivale a log).
        w:    w[i] = coeficiente_utilidad del nodo i (por posición en la lista).

    Returns:
        Función u(i, x) -> float, con costo O(1) por llamada.
    """
    spec = validar(spec)
    return FUNCIONES[spec["tipo"]](w, spec)


def describir(spec):
    """Fórmula legible de la utilidad, p. ej. 'w_i*((1+x)^0.5-1)'; se usa en la salida y la traza."""
    spec = validar(spec)
    d = DESCRIPCION[spec["tipo"]]
    return d.replace("p", str(spec["exponente"])) if spec["tipo"] == "potencia" else d
