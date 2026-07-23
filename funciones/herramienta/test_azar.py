"""Pruebas de la herramienta de azar."""

import unittest
from unittest.mock import patch

from funciones.herramienta.azar import BARAJA, TOOL_DEFINITION, elegir_azar


class ElegirAzarTests(unittest.TestCase):
    @patch("funciones.herramienta.azar._RANDOM.randint", return_value=4)
    def test_lanza_un_dado(self, randint) -> None:
        resultado = elegir_azar("dado")

        self.assertEqual(
            resultado,
            {"accion": "dado", "resultado": 4, "caras": 6},
        )
        randint.assert_called_once_with(1, 6)

    @patch(
        "funciones.herramienta.azar._RANDOM.choice",
        return_value=("As", "corazones"),
    )
    def test_elige_una_carta(self, choice) -> None:
        resultado = elegir_azar("carta")

        self.assertEqual(
            resultado,
            {
                "accion": "carta",
                "resultado": "As de corazones",
                "valor": "As",
                "palo": "corazones",
            },
        )
        choice.assert_called_once_with(BARAJA)

    def test_admite_dados_con_otro_numero_de_caras(self) -> None:
        resultado = elegir_azar("dado", caras=20)

        self.assertGreaterEqual(resultado["resultado"], 1)
        self.assertLessEqual(resultado["resultado"], 20)

    def test_rechaza_una_accion_desconocida(self) -> None:
        with self.assertRaisesRegex(ValueError, "accion"):
            elegir_azar("moneda")  # type: ignore[arg-type]

    def test_rechaza_un_dado_no_valido(self) -> None:
        with self.assertRaisesRegex(ValueError, "entre 2 y 1000"):
            elegir_azar("dado", caras=1)

    def test_publica_un_esquema_para_modelos(self) -> None:
        self.assertEqual(TOOL_DEFINITION["name"], "elegir_azar")
        self.assertEqual(
            TOOL_DEFINITION["parameters"]["properties"]["accion"]["enum"],
            ["dado", "carta"],
        )


if __name__ == "__main__":
    unittest.main()
