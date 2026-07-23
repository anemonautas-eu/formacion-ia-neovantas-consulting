# Router de prompts con Gemini

`route_prompt` usa Gemini con salida JSON estructurada para clasificar una
petición como `metric`, `evidence`, `transform` o `clarify`. El esquema enviado
al modelo es exactamente `ROUTE_SCHEMA`.

## Preparación

Instala las dependencias del proyecto y configura una clave de Gemini:

```bash
export GEMINI_API_KEY="tu-clave"
```

El SDK también reconoce `GOOGLE_API_KEY`. No guardes la clave en el repositorio.

## Uso

```python
from funciones.router import route_prompt

decision = route_prompt("¿Cuál fue la tasa de conversión en 2025?")
print(decision)
```

La respuesta tendrá esta forma:

```python
{
    "route": "metric",
    "period": "2025",
    "topic": "tasa de conversión",
    "needs_clarification": False,
}
```

El modelo predeterminado es `gemini-3.5-flash-lite`, pero se puede cambiar:

```python
decision = route_prompt(
    "Busca fuentes sobre el abandono de clientes",
    model="gemini-3.6-flash",
)
```

Desde terminal:

```bash
python3 -m funciones.router "Resume este informe para dirección"
```

Las pruebas usan un cliente simulado y no consumen cuota:

```bash
python3 -m unittest funciones.test_router
```
