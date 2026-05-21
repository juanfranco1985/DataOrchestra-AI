# Contratos de datos v1.0

## Objetivo

Definir formalmente los archivos CSV que DataOrchestra AI acepta para un diagnostico comercial controlado.

El contrato evita interpretar archivos "parecidos" como si fueran equivalentes. Cada cliente debe entregar datos anonimizados que respeten estos nombres de archivo, columnas y reglas minimas.

## Version vigente

- Version: `1.0`
- Artefacto tecnico: `contracts/data_contracts_v1.json`
- Modulo runtime: `src/dataorchestra/contracts.py`
- Comando de consulta:

```powershell
python -m dataorchestra.cli data-contracts
python -m dataorchestra.cli data-contracts --dataset ventas
```

## Principios

- Los datos deben estar anonimizados.
- No se aceptan nombres de personas, emails, telefonos, DNI, CUIT/CUIL personales, cuentas bancarias ni informacion sensible.
- Los archivos `raw/` no deben modificarse despues del `preflight`.
- Los cambios de contrato deben crear una nueva version, no cambiar silenciosamente la version vigente.

## Archivos requeridos

### ventas.csv

Descripcion: operaciones comerciales anonimizadas usadas para calcular ventas, margen, volumen y periodo.

Columnas obligatorias:

| Columna | Tipo | Regla | Ejemplo |
|---|---:|---|---|
| `fecha` | `date_iso` | `YYYY-MM-DD`, no vacio | `2026-01-01` |
| `producto` | `string` | no vacio, etiqueta anonima | `Producto A` |
| `categoria` | `string` | no vacio, etiqueta anonima | `Categoria 1` |
| `cantidad` | `number` | no vacio, no negativo | `1` |
| `precio_unitario` | `money` | no vacio, no negativo | `1000` |
| `costo_unitario` | `money` | no vacio, no negativo | `700` |

### productos.csv

Descripcion: catalogo comercial anonimizado usado para contrastar categorias, precios y costos.

Columnas obligatorias:

| Columna | Tipo | Regla | Ejemplo |
|---|---:|---|---|
| `producto` | `string` | no vacio, etiqueta anonima | `Producto A` |
| `categoria` | `string` | no vacio, etiqueta anonima | `Categoria 1` |
| `precio_unitario` | `money` | no vacio, no negativo | `1000` |
| `costo_unitario` | `money` | no vacio, no negativo | `700` |

### stock.csv

Descripcion: existencias y rotacion reciente usadas para detectar stock bajo o capital inmovilizado.

Columnas obligatorias:

| Columna | Tipo | Regla | Ejemplo |
|---|---:|---|---|
| `producto` | `string` | no vacio, etiqueta anonima | `Producto A` |
| `stock_actual` | `number` | no vacio, no negativo | `20` |
| `stock_minimo` | `number` | no vacio, no negativo | `5` |
| `ventas_ultimos_30_dias` | `number` | no vacio, no negativo | `12` |

## Tipos permitidos

- `string`: texto comercial anonimizado.
- `number`: numero no negativo. Se acepta punto o coma decimal.
- `money`: importe no negativo. Se acepta punto o coma decimal.
- `date_iso`: fecha en formato `YYYY-MM-DD`.

## Relacion con preflight

El `preflight` valida contra este contrato y registra:

- `validation.contract_version`
- `data_contract.version`
- archivos requeridos del contrato

Si falta un archivo, una columna obligatoria o un valor no cumple tipo/regla minima, el flujo queda en `data_fix_required`.

Despues de validar el contrato, el `preflight` ejecuta validacion avanzada de consistencia comercial. Ver `docs/VALIDACION_AVANZADA_DATOS.md`.

## Relacion con calidad de datos

El contrato valida estructura minima. El score de calidad de datos evalua consistencia adicional:

- cobertura entre ventas, productos y stock;
- periodo analizado;
- duplicados;
- costos en cero;
- datos de rotacion.

Por lo tanto:

- contrato invalido: no avanzar;
- contrato valido pero baja calidad: revisar antes de entregar;
- contrato valido y calidad suficiente: avanzar con revision humana.

## Politica de versionado

Usar versionado semantico simple:

- `1.0`: contrato inicial para primer piloto controlado.
- `1.x`: agrega columnas opcionales o aclaraciones compatibles.
- `2.0`: cambia columnas obligatorias, tipos, reglas bloqueantes o nombres de archivos.

Nunca cambiar `contracts/data_contracts_v1.json` de forma incompatible. Para cambios no compatibles, crear un nuevo archivo versionado, por ejemplo:

```text
contracts/data_contracts_v2.json
docs/CONTRATOS_DATOS_v2.md
```

## Plantillas asociadas

- `templates/ventas_template.csv`
- `templates/productos_template.csv`
- `templates/stock_template.csv`

Las pruebas automatizadas verifican que las plantillas coincidan con las columnas obligatorias del contrato vigente.
