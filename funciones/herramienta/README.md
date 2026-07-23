# Herramienta de azar

`elegir_azar` ofrece dos operaciones sin depender de ningún modelo ni SDK:

- `dado`: lanza un dado de 6 caras por defecto.
- `carta`: elige una carta de una baraja francesa de 52 cartas.

## Uso desde Python

```python
from funciones.herramienta import elegir_azar

print(elegir_azar("dado"))
print(elegir_azar("dado", caras=20))
print(elegir_azar("carta"))
```

La salida siempre es un diccionario que puede convertirse directamente a JSON.

## Uso desde terminal

Ejecuta los comandos desde la raíz del repositorio:

```bash
python3 -m funciones.herramienta dado
python3 -m funciones.herramienta dado --caras 20
python3 -m funciones.herramienta carta
```

## Conexión con un modelo

`TOOL_DEFINITION` contiene el nombre, la descripción y el esquema JSON de los
argumentos. Una integración puede enviar esa definición al modelo y, cuando
este solicite la herramienta, ejecutar:

```python
import json

from funciones.herramienta import TOOL_DEFINITION, elegir_azar

# `argumentos_json` representa los argumentos generados por el modelo.
argumentos = json.loads(argumentos_json)
resultado = elegir_azar(**argumentos)
respuesta_para_el_modelo = json.dumps(resultado, ensure_ascii=False)
```

Cada proveedor envuelve la definición de herramientas de una forma ligeramente
distinta, pero la función Python y su esquema de parámetros son reutilizables.

## Pruebas

```bash
python3 -m unittest funciones.herramienta.test_azar
```
