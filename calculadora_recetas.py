import re
from typing import Dict, Tuple, Optional


# Tabla de conversión de unidades a gramos
TABLA_CONVERSION: Dict[str, float | str] = {
    "kg": 1000, "kilogramo": 1000, "kilogramos": 1000,
    "g": 1, "gramo": 1, "gramos": 1,
    "lb": 453.592, "libra": 453.592, "libras": 453.592,
    "oz": 28.3495, "onza": 28.3495, "onzas": 28.3495,
    "litro": "volumen", "litros": "volumen", "l": "volumen",
    "ml": "volumen", "mililitro": "volumen", "mililitros": "volumen",
    "taza": "volumen", "tazas": "volumen",
    "cucharada": "volumen", "cucharadas": "volumen",
    "cucharadita": "volumen", "cucharaditas": "volumen",
    "caja": "especifico", "cajas": "especifico",
}

DENSIDADES: Dict[str, float] = {
    "leche": 1.03, "agua": 1.0, "aceite": 0.92, "harina": 0.6,
    "azucar": 0.85, "azúcar": 0.85, "arequipe": 1.2, "natilla": 1.0,
}

VOLUMEN_A_ML: Dict[str, int] = {
    "litro": 1000, "litros": 1000, "l": 1000,
    "ml": 1, "mililitro": 1, "mililitros": 1,
    "taza": 250, "tazas": 250,
    "cucharada": 15, "cucharadas": 15,
    "cucharadita": 5, "cucharaditas": 5,
}

PRODUCTOS_ESPECIFICOS: Dict[str, int] = {
    "natilla maizena": 200, "natilla": 200, "maizena": 200,
}


def parsear_cantidad(cantidad_string: str) -> Tuple[Optional[float], Optional[str]]:
    """Extrae la cantidad numérica y la unidad de un string."""
    if not cantidad_string or isinstance(cantidad_string, (int, float)):
        return None, None
    
    cantidad_string = cantidad_string.lower().strip()
    
    if any(palabra in cantidad_string for palabra in ["gusto", "opcional", "consideracion"]):
        return None, "a_gusto"
    
    match = re.search(r'(\d+\.?\d*)', cantidad_string)
    if not match:
        return None, None
    
    cantidad = float(match.group(1))
    unidad = re.sub(r'\d+\.?\d*\s*', '', cantidad_string).strip()
    
    return cantidad, unidad


def obtener_densidad(ingrediente: str) -> float:
    """Obtiene la densidad aproximada de un ingrediente."""
    ingrediente_lower = ingrediente.lower()
    for key, densidad in DENSIDADES.items():
        if key in ingrediente_lower:
            return densidad
    return 1.0


def convertir_a_gramos(cantidad: Optional[float], unidad: Optional[str], ingrediente: str = "") -> float:
    """Convierte una cantidad con unidad a gramos."""
    if cantidad is None or unidad == "a_gusto":
        return 0.0
    
    unidad_lower = unidad.lower() if unidad else ""
    if unidad_lower not in TABLA_CONVERSION:
        return 0.0
    
    conversion = TABLA_CONVERSION[unidad_lower]
    
    if isinstance(conversion, (int, float)):
        return cantidad * conversion
    
    if conversion == "volumen":
        if unidad_lower in VOLUMEN_A_ML:
            ml = cantidad * VOLUMEN_A_ML[unidad_lower]
            return ml * obtener_densidad(ingrediente)
        return 0.0
    
    if conversion == "especifico":
        ingrediente_lower = ingrediente.lower()
        for producto, gramos in PRODUCTOS_ESPECIFICOS.items():
            if producto in ingrediente_lower:
                return cantidad * gramos
        return 0.0
    
    return 0.0


def calcular_gramos_receta(receta: Dict[str, str]) -> Dict[str, float]:
    """Calcula los gramos totales de todos los ingredientes de una receta."""
    return {
        ingrediente: round(convertir_a_gramos(*parsear_cantidad(cantidad_string), ingrediente), 2)
        for ingrediente, cantidad_string in receta.items()
    }


def calcular_gramos_plato(receta: Dict[str, str], num_porciones: int) -> Dict[str, float]:
    """Calcula los gramos para una porción individual (plato) de una receta."""
    if num_porciones <= 0:
        raise ValueError("El número de porciones debe ser mayor a 0")
    
    gramos_receta = calcular_gramos_receta(receta)
    return {
        ingrediente: round(gramos / num_porciones, 2)
        for ingrediente, gramos in gramos_receta.items()
    }

