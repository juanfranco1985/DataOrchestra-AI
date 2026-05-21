# Seguimiento de recomendaciones

## Objetivo

Registrar que ocurre con cada recomendacion generada por el diagnostico.

El objetivo es evitar que el informe quede solo como una lista de sugerencias. Cada recomendacion debe poder revisarse, aceptarse, descartarse o convertirse en una accion concreta, manteniendo trazabilidad y revision humana.

## Estado inicial

Cuando se ejecuta `analyze`, DataOrchestra AI genera:

- recomendaciones asociadas a alertas;
- evidencia vinculada;
- archivo de seguimiento en `diagnostics/recommendations/recommendation_tracking.json`;
- copia historica en `runs/<run_id>/analysis/recommendation_tracking.json`.

Todas las recomendaciones activas nacen en estado:

```text
pending_review
```

## Estados permitidos

- `pending_review`: pendiente de revision humana.
- `accepted`: recomendacion validada para incluir o sostener en la devolucion.
- `rejected`: recomendacion descartada por falta de contexto, baja utilidad o riesgo de interpretacion.
- `needs_client_context`: requiere una pregunta o aclaracion al cliente.
- `converted_to_action`: se transforma en accion operativa posterior al diagnostico.
- `completed`: accion o seguimiento cerrado.
- `superseded`: recomendacion ya no aparece en el analisis vigente.

## Comandos

Ver seguimiento:

```powershell
dataorchestra recommendations --client-dir clients/cliente_001
```

Actualizar una recomendacion:

```powershell
dataorchestra update-recommendation `
  --client-dir clients/cliente_001 `
  --recommendation-id rec_bajo_margen `
  --status accepted `
  --reviewer "Nombre responsable" `
  --notes "Validada para devolucion controlada" `
  --owner "Responsable comercial" `
  --due-date 2026-06-01 `
  --confirm-no-sensitive-values
```

## Controles

El comando de actualizacion exige:

- `client.yaml` existente;
- analisis ejecutado previamente;
- recomendacion activa;
- revisor informado;
- estado valido;
- confirmacion de que no se guardan valores sensibles.

No debe guardarse informacion personal, emails, telefonos, documentos o datos comerciales sensibles en notas de seguimiento.

## Uso en revision humana

Antes de aprobar una entrega, revisar especialmente:

- recomendaciones de prioridad alta que sigan en `pending_review`;
- recomendaciones con hallazgos de confianza baja;
- recomendaciones marcadas como `needs_client_context`;
- recomendaciones `rejected`, para decidir si deben eliminarse o explicarse.

## Relacion con el informe

El borrador y el informe aprobado muestran el estado de seguimiento cuando esta disponible.

El seguimiento no aprueba entregas por si solo. La aprobacion formal sigue dependiendo del comando `approve` con confirmacion humana.

## Estado

Implementado para `v2.0 - Primer Piloto Real Controlado`.

Siguiente mejora posible: ordenar el resumen ejecutivo por prioridad, confianza y estado de seguimiento.
