"""Pruebas del router sin llamadas reales ni consumo de cuota."""

import unittest
from types import SimpleNamespace
from typing import Any

from funciones.router import (
    DEFAULT_MODEL,
    ROUTE_SCHEMA,
    RouterResponseError,
    route_prompt,
)


class FakeModels:
    def __init__(self, response: Any) -> None:
        self.response = response
        self.request: dict[str, Any] | None = None

    def generate_content(self, **kwargs: Any) -> Any:
        self.request = kwargs
        return self.response


class FakeClient:
    def __init__(self, response: Any) -> None:
        self.models = FakeModels(response)


class RoutePromptTests(unittest.TestCase):
    def test_returns_gemini_structured_response(self) -> None:
        decision = {
            "route": "metric",
            "period": "2025",
            "topic": "tasa de conversión",
            "needs_clarification": False,
        }
        client = FakeClient(SimpleNamespace(parsed=decision, text=None))

        result = route_prompt(
            "¿Cuál fue la tasa de conversión en 2025?",
            client=client,
        )

        self.assertEqual(result, decision)
        self.assertEqual(client.models.request["model"], DEFAULT_MODEL)
        self.assertEqual(
            client.models.request["config"]["response_json_schema"],
            ROUTE_SCHEMA,
        )
        self.assertEqual(
            client.models.request["config"]["response_mime_type"],
            "application/json",
        )

    def test_model_can_be_changed(self) -> None:
        decision = {
            "route": "evidence",
            "period": None,
            "topic": "abandono de clientes",
            "needs_clarification": False,
        }
        client = FakeClient(SimpleNamespace(parsed=decision, text=None))

        route_prompt("Busca evidencias", client=client, model="otro-modelo")

        self.assertEqual(client.models.request["model"], "otro-modelo")

    def test_uses_text_if_parsed_is_unavailable(self) -> None:
        response = SimpleNamespace(
            parsed=None,
            text=(
                '{"route":"transform","period":null,'
                '"topic":"informe","needs_clarification":false}'
            ),
        )

        result = route_prompt("Resume el informe", client=FakeClient(response))

        self.assertEqual(result["route"], "transform")

    def test_empty_prompt_does_not_call_gemini(self) -> None:
        result = route_prompt("   ")

        self.assertEqual(
            result,
            {
                "route": "clarify",
                "period": None,
                "topic": None,
                "needs_clarification": True,
            },
        )

    def test_rejects_incoherent_response(self) -> None:
        decision = {
            "route": "metric",
            "period": None,
            "topic": "ventas",
            "needs_clarification": True,
        }
        client = FakeClient(SimpleNamespace(parsed=decision, text=None))

        with self.assertRaises(RouterResponseError):
            route_prompt("Dame las ventas", client=client)

    def test_rejects_extra_properties(self) -> None:
        decision = {
            "route": "metric",
            "period": None,
            "topic": "ventas",
            "needs_clarification": False,
            "explanation": "propiedad no permitida",
        }
        client = FakeClient(SimpleNamespace(parsed=decision, text=None))

        with self.assertRaises(RouterResponseError):
            route_prompt("Dame las ventas", client=client)


if __name__ == "__main__":
    unittest.main()
