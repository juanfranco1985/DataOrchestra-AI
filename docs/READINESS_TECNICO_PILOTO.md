# Readiness tecnico de piloto

## Objetivo

Ejecutar una verificacion tecnica y operativa antes de avanzar con un cliente real o antes de entregar resultados.

## Comando

```powershell
python -m dataorchestra.cli readiness --client-dir clients/cliente_001
```

Para un runtime externo:

```powershell
python -m dataorchestra.cli readiness --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_002" --repo-root .
```

## Que verifica

- Estructura de carpetas del cliente.
- Existencia de `client.yaml`.
- Presencia de `ventas.csv`, `productos.csv` y `stock.csv`.
- Estado del preflight.
- Score de calidad de datos.
- Existencia de borrador y bloqueo por revision humana.
- Existencia de aprobacion humana si ya se llego a entrega.
- Incidentes operativos abiertos.
- Cierre operativo y revision de retencion si corresponde.
- Documentacion critica del repositorio.
- Advertencia si se intenta operar datos reales dentro de `clients/` del repositorio.

## Interpretacion

Resultado posible:

- `ready`: sin bloqueos ni advertencias.
- `ready_with_warnings`: no hay bloqueos, pero conviene revisar advertencias.
- `blocked`: hay bloqueos que deben resolverse antes de continuar.

Campo clave:

```json
"can_continue": true
```

Si `can_continue` es `false`, no avanzar con analisis, aprobacion o entrega hasta resolver el bloqueo.

## Uso recomendado

Ejecutar readiness:

1. despues de recibir archivos;
2. despues de `preflight`;
3. antes de `analyze`;
4. antes de aprobar entrega;
5. antes de cerrar el piloto;
6. despues de cualquier incidente operativo.

Si hay incidentes abiertos con severidad `alta` o `media`, `readiness` queda bloqueado hasta ejecutar `resolve-incident`.

Si existe un score de calidad por debajo del objetivo configurado, `readiness` queda bloqueado hasta revisar o corregir los datos.

## Limite

El readiness no reemplaza la revision humana. Su funcion es detectar condiciones tecnicas y operativas repetibles para reducir errores.
