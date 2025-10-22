# Trabajo_Compi_Python

Implementación en Python de un generador/analizador LR(1) con traza detallada y árbol de derivación, más un API REST con FastAPI. Se mantienen también los módulos LL(1) originales como referencia.

## Principales características
- Construcción de la colección canónica de items LR(1) (closure/goto) con gramática aumentada.
- Generación de tablas ACTION y GOTO; reporte de conflictos si los hubiera.
- Parser LR(1) shift-reduce con traza paso a paso, incluyendo una fila adicional tras cada reducción mostrando el estado destino del GOTO (solo el número).
- Construcción del árbol de derivación y salida en dos formatos: ASCII y JSON.
- API REST (FastAPI) para construir estados/tablas y para parsear una cadena de tokens.
- Colección de Postman para probar los endpoints.

## Estructura del proyecto
- `grammar.py`: Carga gramáticas desde archivo o string, detecta terminales y no terminales, y expone reglas e inicial.
- `lr1.py`: Estructuras LR(1) (Producciones, Items, Estados) y algoritmos `closure`, `goto`, colección canónica, y construcción de tablas ACTION/GOTO.
- `lr_parser.py`: Parser LR(1) con traza y construcción del árbol. Expone `LRParser.last_trace` (JSON) y `LRParser.last_tree`.
- `main.py`: CLI de ejemplo. Carga `gramatica.txt`, construye LR(1), imprime estados/tablas y parsea una entrada.
- `api.py`: App FastAPI con endpoints `POST /build` y `POST /parse`.
- `utils.py`: Utilidades generales.
- `gramatica.txt`: Gramática de ejemplo usada por `main.py`.
- `first.py`, `follow.py`, `table.py`, `parser.py`: Módulos LL(1) (legado, útiles para referencia/estudio).
- `__main__.py`: Permite ejecutar como módulo (`python -m Trabajo_Compi_Python`).
- `Postman/`: Colección y ambiente para probar el API.

## Requisitos
- Python 3.8+ (probado con Python 3.13)
- Para usar el API: `fastapi`, `uvicorn`, `pydantic`

Instalación rápida de dependencias del API (opcional si sólo usas la CLI):

```powershell
pip install fastapi uvicorn pydantic
```

## Formato de gramática
- Cada producción en una línea con `->`, por ejemplo:
  
	S -> C C
	C -> c C
	C -> d

- Epsilon (producción vacía) puede representarse como `''` si se requiere.
- El símbolo de fin de entrada `$` se añade automáticamente si no está presente al final de la entrada.

## Uso por CLI (main.py)
Desde la raíz del workspace, en PowerShell:

```powershell
python Trabajo_Compi_Python/main.py
```

También puedes pasar la entrada como cadena completa (tokens separados por espacios). Ejemplo:

```powershell
python Trabajo_Compi_Python/main.py "c d d $"
```

Notas:
- Si no incluyes `$`, el parser lo añade automáticamente.
- `main.py` imprime: gramática, estados LR(1), tablas LR(1), y la traza del parseo. Al aceptar, imprime el árbol en ASCII.
- En algunas consolas Windows puede verse "mojibake" en los caracteres de árbol (├──, └──). Si sucede, usa el API (que entrega árbol JSON) o cambia a UTF-8.

## API REST (FastAPI)
Levanta el servidor (desde la raíz del workspace):

```powershell
python -m uvicorn Trabajo_Compi_Python.api:app --reload
```

Endpoints:

1) POST `/build`
- Request:

	{ "grammar": "{{grammar_default}}" }

	Donde `{{grammar_default}}` es un string con saltos de línea (ver Postman/Local.postman_environment.json), p. ej.:

	S -> C C
	C -> c C
	C -> d

- Response (resumen):
	- initial: símbolo inicial
	- terminals, nonterminals
	- rules: reglas crudas
	- states: lista de estados con items y transiciones
	- tables: `{ action: {state: {terminal: {type,to|lhs|rhs}}}, goto: {state: {NonTerm: state}} }`
	- conflicts: lista (si se detectan)

2) POST `/parse`
- Request:

	{
		"grammar": "{{grammar_default}}",
		"input": "c d d $"
	}

- Response (resumen):
	- accepted: boolean
	- trace: arreglo de pasos; cada paso tiene:
		- stackStates: [int,...]
		- stackSymbols: [str,...]
		- stackDisplay: string amigable (opcional para UI)
		- input: string con la entrada restante
		- action: objeto con `{type: 'shift'|'reduce'|'goto'|'accept'|'error', ...}`
			- shift: `{type:'shift', to:int, symbol:str}`
			- reduce: `{type:'reduce', production:{lhs:str, rhs:[str], text:str}}`
			- goto: `{type:'goto', to:int, on:str}` (se agrega justo después de cada reduce)
			- accept: `{type:'accept'}`
	- tree: árbol de derivación en JSON `{label, children[]}`
	- tree_ascii: árbol en texto (con caracteres ASCII extendidos)

## Postman
- Colección: `Postman/LR1_Parser_API.postman_collection.json`
- Ambiente: `Postman/Local.postman_environment.json`
	- Variables:
		- `base_url`: http://127.0.0.1:8000
		- `grammar_default`: gramática con saltos de línea (texto multilinea)
		- `input_default`: entrada por defecto, p. ej. `c d d $`

Ejemplo de body para `/build` usando variable con saltos de línea:

{
	"grammar": "{{grammar_default}}"
}

Ejemplo de body para `/parse` usando variables:

{
	"grammar": "{{grammar_default}}",
	"input": "{{input_default}}"
}

## Consejos y problemas comunes
- Si el árbol ASCII no se ve bien en Windows, preferir el `tree` JSON del API para renderizar en el frontend.
- Asegúrate de que todos los tokens en la entrada existan como terminales en la gramática.
- El parser añade `$` automáticamente al final si no está presente.

## Licencia
Uso educativo/demostrativo.
