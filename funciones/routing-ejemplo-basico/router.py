"""Clasificación de prompts con Gemini y salida JSON estructurada."""

from __future__ import annotations

import json
from typing import Any, Literal, TypedDict


Route = Literal["metric", "evidence", "transform", "clarify"]
# EJERCICIO: ¿qué modelo de Gemini es más adecuado para esta tarea? ¿Por qué? 
# ¿Qué ventajas y desventajas tiene frente a otros modelos?
DEFAULT_MODEL = "gemini-3.5-flash-lite"


class RouteDecision(TypedDict):
    route: Route
    period: str | None
    topic: str | None
    needs_clarification: bool

# EJERCICIO: ¿existe una alternativa a json para estructurar la salida? 
# Crea un esquema de validación con pydantic o marshmallow, por ejemplo, para que la 
# salida sea más robusta y fácil de validar. Esto permitiría definir tipos y restricciones 
# más complejas, y generar documentación automáticamente.

ROUTE_SCHEMA = {
    "type": "object",
    "properties": {
        "route": {
            "type": "string",
            "enum": ["metric", "evidence", "transform", "clarify"],
        },
        "period": {"type": ["string", "null"]},
        "topic": {"type": ["string", "null"]},
        "needs_clarification": {"type": "boolean"},
    },
    "required": ["route", "period", "topic", "needs_clarification"],
    "additionalProperties": False,
}

# EJERCICIO: ¿cómo podríamos mejorar las instrucciones para que el modelo entienda mejor la tarea?

ROUTER_INSTRUCTIONS = """
Clasifica la petición del usuario según su intención principal:

- metric: pide una cifra, KPI, agregado, comparación o evolución cuantitativa.
- evidence: pide fuentes, pruebas, citas o información que respalde una idea.
- transform: pide modificar contenido, por ejemplo resumir, traducir, extraer,
  reescribir, corregir, adaptar o cambiar su formato.
- clarify: no hay información suficiente para elegir una de las rutas anteriores.

En period devuelve el periodo temporal mencionado, conservando las palabras del
usuario, o null si no existe. En topic devuelve el asunto central de forma breve,
sin incluir el periodo, o null si no se puede inferir. needs_clarification debe
ser true únicamente cuando route sea clarify. Si hay varias señales, elige la
acción principal solicitada por el usuario.
""".strip()


class RouterResponseError(ValueError):
    """Gemini devolvió una respuesta que no cumple el contrato del router."""


def _validate(payload: Any) -> RouteDecision:
    expected_keys = {"route", "period", "topic", "needs_clarification"}
    if not isinstance(payload, dict) or set(payload) != expected_keys:
        raise RouterResponseError("La respuesta no contiene las claves esperadas")

    route = payload["route"]
    period = payload["period"]
    topic = payload["topic"]
    needs_clarification = payload["needs_clarification"]

    if route not in {"metric", "evidence", "transform", "clarify"}:
        raise RouterResponseError(f"Ruta no válida: {route!r}")
    if period is not None and not isinstance(period, str):
        raise RouterResponseError("period debe ser texto o null")
    if topic is not None and not isinstance(topic, str):
        raise RouterResponseError("topic debe ser texto o null")
    if not isinstance(needs_clarification, bool):
        raise RouterResponseError("needs_clarification debe ser booleano")
    if needs_clarification != (route == "clarify"):
        raise RouterResponseError("route y needs_clarification son incoherentes")

    return payload  # type: ignore[return-value]


def route_prompt(
    prompt: str,
    *,
    client: Any | None = None,
    model: str = DEFAULT_MODEL,
) -> RouteDecision:
    """Clasifica un prompt mediante Gemini.

    Si no se proporciona ``client``, el SDK toma la credencial de
    ``GEMINI_API_KEY`` o ``GOOGLE_API_KEY``. Aceptar un cliente externo permite
    reutilizar conexiones y probar la función sin hacer llamadas reales.
    """

    if not isinstance(prompt, str):
        raise TypeError("prompt debe ser una cadena de texto")
    if not prompt.strip():
        return {
            "route": "clarify",
            "period": None,
            "topic": None,
            "needs_clarification": True,
        }

    if client is None:
        from google import genai

        client = genai.Client()

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "system_instruction": ROUTER_INSTRUCTIONS,
            "response_mime_type": "application/json",
            "response_json_schema": ROUTE_SCHEMA,
        },
    )

    payload = response.parsed
    if payload is None:
        try:
            payload = json.loads(response.text)
        except (TypeError, json.JSONDecodeError) as error:
            raise RouterResponseError("Gemini no devolvió JSON válido") from error

    return _validate(payload)


if __name__ == "__main__":
    import sys

    result = route_prompt(" ".join(sys.argv[1:]))
    print(json.dumps(result, ensure_ascii=False, indent=2))
