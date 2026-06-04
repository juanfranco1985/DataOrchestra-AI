# Confianza por hallazgo

## Objetivo

Agregar una lectura de confianza operativa a cada alerta del diagnostico comercial.

El objetivo no es prometer certeza automatica. La confianza indica que tan respaldado esta un hallazgo por la calidad de los datos, la evidencia disponible y la consistencia entre `ventas.csv`, `productos.csv` y `stock.csv`.

## Salida generada

Cada alerta incluye:

- `confidence.level`: `alta`, `media` o `baja`.
- `confidence.score`: valor entre 0 y 100.
- `confidence.reasons`: motivos que elevan la confianza.
- `confidence.limitations`: restricciones que deben revisarse antes de entregar.

Ejemplo conceptual:

```json
{
  "confidence": {
    "level": "media",
    "score": 74,
    "reasons": [
      "Calidad general de datos: 82/100 (media).",
      "La alerta conserva evidencia estructurada con metrica, valor y umbral."
    ],
    "limitations": [
      "La muestra de ventas es reducida; conviene revisar representatividad antes de entregar."
    ]
  }
}
```

## Criterios utilizados

La confianza se calcula con reglas deterministicas:

- score general de calidad de datos;
- existencia de evidencia estructurada por alerta;
- presencia del producto en catalogo;
- ventas, precios y costos positivos para alertas de margen;
- stock actual, stock minimo y ventas recientes para alertas de stock;
- facturacion positiva, cantidad de operaciones y cantidad de productos para concentracion;
- limitaciones de muestra reducida o cobertura incompleta.

## Interpretacion comercial

- `alta`: el hallazgo tiene buen respaldo operativo, aunque sigue requiriendo revision humana.
- `media`: el hallazgo es util, pero debe leerse junto con limitaciones o muestra reducida.
- `baja`: el hallazgo puede ser una senal inicial, no una recomendacion fuerte para entregar sin correccion o explicacion.

## Uso en el informe

El borrador Markdown y el HTML muestran la confianza en cada alerta.

La revision humana debe mirar especialmente:

- alertas de prioridad alta con confianza baja;
- alertas de margen con costos incompletos;
- alertas de stock sin ventas recientes;
- concentracion calculada sobre pocos productos o pocas operaciones.

## Limites

- No es un modelo predictivo.
- No reemplaza criterio humano.
- No mide impacto economico futuro.
- No garantiza que una recomendacion produzca resultado.
- No debe ocultar problemas de calidad de datos.

## Estado

Implementado y vigente en `v2.1 - Version Integradora`.

El siguiente paso natural es usar esta confianza para ordenar el resumen ejecutivo y destacar primero hallazgos de alta prioridad con confianza suficiente.
