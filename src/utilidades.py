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
Para agregar otra función: añadir una entrada a FUNCIONES (debe ser creciente y cóncava).
"""
import math

FUNCIONES = {
    "log": lambda w, p: (lambda i, x: w[i] * math.log1p(x)),
    "sqrt": lambda w, p: (lambda i, x: w[i] * (math.sqrt(1 + x) - 1)),
    "saturacion": lambda w, p: (lambda i, x: w[i] * x / (1 + x)),
    "potencia": lambda w, p: (lambda i, x: w[i] * ((1 + x) ** p["exponente"] - 1)),
}

DESCRIPCION = {
    "log": "w_i*ln(1+x)",
    "sqrt": "w_i*(sqrt(1+x)-1)",
    "saturacion": "w_i*x/(1+x)",
    "potencia": "w_i*((1+x)^p-1)",
}


def validar(spec):
    """spec = {"tipo": ..., ["exponente": p]}. Devuelve spec normalizada o lanza ValueError."""
    spec = dict(spec or {"tipo": "log"})
    tipo = spec.get("tipo", "log")
    if tipo not in FUNCIONES:
        raise ValueError(f"funcion_utilidad.tipo desconocido '{tipo}'; opciones: {', '.join(FUNCIONES)}")
    if tipo == "potencia":
        p = spec.get("exponente")
        if not isinstance(p, (int, float)) or not 0 < p < 1:
            raise ValueError("funcion_utilidad 'potencia' exige 'exponente' p con 0 < p < 1 "
                             "(con p >= 1 no sería cóncava)")
    return spec


def construir(spec, w):
    """Devuelve u(i, x) para los coeficientes w (indexados por posición)."""
    spec = validar(spec)
    return FUNCIONES[spec["tipo"]](w, spec)


def describir(spec):
    spec = validar(spec)
    d = DESCRIPCION[spec["tipo"]]
    return d.replace("p", str(spec["exponente"])) if spec["tipo"] == "potencia" else d
