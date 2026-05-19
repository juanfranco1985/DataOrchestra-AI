# Plan de profesionalizacion

Este plan convierte DataOrchestra AI de paquete consolidado a sistema profesional operable. La prioridad es reducir riesgo antes de sumar funciones.

## Fase 1 - Base operativa v2.0

Objetivo: ejecutar un primer piloto real controlado.

- Crear estructura separada para piloto real.
- Bloquear privacidad antes de analizar.
- Validar archivos raw con esquemas claros.
- Mantener logs de auditoria.
- Mantener informe en `pending_human_review`.
- Registrar aprobacion humana antes de crear artefactos `approved_for_delivery`.
- Documentar admision, runbook, checklists y criterios de cierre.
- Crear clientes piloto separados desde CLI.
- Mantener historial de corridas por `run_id`.

Estado: base operativa implementada para piloto controlado, con soporte multi-cliente e historial de artefactos.

## Fase 2 - Motor analitico unificado

Objetivo: reemplazar scripts historicos por un paquete unico.

- Migrar metricas de ventas, margen, stock y alertas a `src/dataorchestra/analytics/`. Estado: iniciado con motor deterministico basico.
- Cubrir cada metrica con tests.
- Conectar recomendaciones a evidencia trazable.
- Separar reportes ejecutivos de anexos tecnicos. Estado: iniciado con Markdown, JSON tecnico y HTML ejecutivo imprimible.

## Fase 2.5 - Entrega comercial profesional

Objetivo: mejorar la presentacion al cliente sin prometer automatizacion total.

- Informe ejecutivo HTML aprobado. Estado: implementado.
- Guia para exportar PDF desde navegador. Estado: implementado.
- Exportacion PDF automatica con navegador Chromium/Edge/Chrome. Estado: implementado.
- Aceptacion de piloto controlado. Estado: implementado.
- Checklist de recepcion de datos. Estado: implementado.
- Paquete comercial del piloto. Estado: implementado.
- Caso demo ficticio reproducible. Estado: implementado.

## Fase 3 - What-if realista

Objetivo: transformar el modulo demo en simulador conectado a datos procesados.

- Eliminar baseline fijo.
- Leer metricas reales del diagnostico.
- Guardar supuestos visibles.
- Marcar escenarios como simulaciones, nunca predicciones.
- Bloquear escenarios sin datos suficientes.

## Fase 4 - Panel interno profesional

Objetivo: operar sin tocar consola en tareas frecuentes.

- Carga de archivos por cliente.
- Preview de datos.
- Resultado de preflight visible.
- Estado del diagnostico.
- Boton de generar borrador solo si el estado lo permite.
- Bloqueo de entrega hasta aprobacion humana.

## Fase 5 - Piloto y aprendizaje

Objetivo: validar valor comercial real.

- Registrar tiempo operativo.
- Registrar calidad de datos.
- Registrar preguntas y objeciones del cliente.
- Medir si el cliente entiende las recomendaciones.
- Decidir continuidad, ajuste o descarte.

## Fase 6 - Producto comercial minimo

Objetivo: solo despues de validar el piloto.

- Versionado Git formal. Estado: preparado con `.gitignore`; falta inicializar/publicar repositorio.
- CI con tests. Estado: workflow GitHub Actions agregado; falta ejecutarlo en repositorio Git remoto.
- Paquetes/release reproducibles.
- Plantilla de contrato/alcance.
- Precio inicial basado en esfuerzo real y valor percibido.
- Manual de operacion.
