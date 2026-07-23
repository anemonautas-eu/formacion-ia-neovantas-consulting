"""Herramienta de azar: lanza un dado o saca una carta de una baraja."""

from __future__ import annotations

import argparse
import json
import random
from typing import Literal, TypedDict, cast


Accion = Literal["dado", "carta"]


class ResultadoDado(TypedDict):
    accion: Literal["dado"]
    resultado: int
    caras: int


class ResultadoCarta(TypedDict):
    accion: Literal["carta"]
    resultado: str
    valor: str
    palo: str


ResultadoAzar = ResultadoDado | ResultadoCarta

VALORES = (
    "As",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "Jota",
    "Reina",
    "Rey",
)
PALOS = ("corazones", "diamantes", "tréboles", "picas")
BARAJA = tuple((valor, palo) for palo in PALOS for valor in VALORES)

# Contrato neutral: cada SDK puede adaptar este diccionario a su formato de tools.
TOOL_DEFINITION = {
    "name": "elegir_azar",
    "description": (
        "Genera un resultado al azar: lanza un dado o elige una carta de una "
        "baraja francesa estándar de 52 cartas."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "accion": {
                "type": "string",
                "enum": ["dado", "carta"],
                "description": "Operación que debe realizar la herramienta.",
            },
            "caras": {
                "type": "integer",
                "minimum": 2,
                "maximum": 1000,
                "default": 6,
                "description": (
                    "Número de caras del dado. Solo se utiliza cuando accion "
                    "es 'dado'."
                ),
            },
        },
        "required": ["accion"],
        "additionalProperties": False,
    },
}

_RANDOM = random.SystemRandom()


def elegir_azar(accion: Accion, caras: int = 6) -> ResultadoAzar:
    """Lanza un dado o elige una carta y devuelve un resultado serializable.

    Args:
        accion: ``"dado"`` o ``"carta"``.
        caras: Número de caras del dado, entre 2 y 1000.

    Raises:
        ValueError: Si la acción o el número de caras no son válidos.
        TypeError: Si ``caras`` no es un número entero.
    """

    if accion not in ("dado", "carta"):
        raise ValueError("accion debe ser 'dado' o 'carta'")

    if not isinstance(caras, int) or isinstance(caras, bool):
        raise TypeError("caras debe ser un número entero")
    if not 2 <= caras <= 1000:
        raise ValueError("caras debe estar entre 2 y 1000")

    if accion == "dado":
        return {
            "accion": "dado",
            "resultado": _RANDOM.randint(1, caras),
            "caras": caras,
        }

    valor, palo = _RANDOM.choice(BARAJA)
    return {
        "accion": "carta",
        "resultado": f"{valor} de {palo}",
        "valor": valor,
        "palo": palo,
    }


def _main() -> None:
    parser = argparse.ArgumentParser(description=TOOL_DEFINITION["description"])
    parser.add_argument("accion", choices=("dado", "carta"))
    parser.add_argument(
        "--caras",
        type=int,
        default=6,
        help="número de caras del dado (por defecto: 6)",
    )
    arguments = parser.parse_args()

    resultado = elegir_azar(cast(Accion, arguments.accion), arguments.caras)
    print(json.dumps(resultado, ensure_ascii=False))


if __name__ == "__main__":
    _main()
