# Paso a paso como conductor de una herramienta nueva

DataOrchestra AI ya esta armado como base operativa, pero se usa como una herramienta profesional, no como piloto automatico. Tu rol es conducir: preparar datos, controlar riesgos, ejecutar analisis, revisar resultados y decidir que se entrega.

## Flujo completo

```text
buscar cliente
-> validar si tiene datos
-> aceptar alcance
-> recibir CSV anonimizados
-> crear cliente en runtime externo
-> cargar archivos en raw
-> readiness
-> preflight
-> data-quality
-> analyze o full-run
-> revision humana
-> approve
-> export-pdf / devolucion
-> mark-delivered
-> feedback
-> posible seguimiento mensual
-> close-pilot
-> record-retention
```

## 1. Preparar la conversacion

Usar el kit comercial antes de hablar con clientes:

```text
exports/kit_comercial_dataorchestra/
```

La pregunta inicial es:

> Ustedes llevan ventas o stock en algun sistema, Excel o planilla?

## 2. Confirmar que el cliente sirve

El cliente ideal tiene:

- ventas registradas;
- productos identificables;
- stock o inventario;
- posibilidad de exportar datos;
- disposicion a anonimizar;
- expectativas realistas.

## 3. No recibir datos sensibles

Antes de recibir archivos, aclarar:

> No necesito nombres de clientes, telefonos, emails, DNI, CUIT/CUIL personales, direcciones, tarjetas ni cuentas bancarias.

## 4. Usar runtime externo

El repositorio es para codigo y documentacion. Los datos reales van afuera, por ejemplo:

```text
C:\Documentos\DataOrchestra_Runtime
```

## 5. Ejecutar el flujo tecnico

Primero se crea el cliente, se cargan CSV anonimizados y se ejecutan controles. Si algo falla, no se avanza.

## 6. Revisar como analista

El sistema genera borradores, pero no decide solo. Revisar:

- sentido comercial;
- calidad de datos;
- confianza por hallazgo;
- recomendaciones;
- limites;
- posibles riesgos de interpretacion.

## 7. Aprobar solo si corresponde

La aprobacion humana crea los entregables finales. Nunca entregar borradores.

## 8. Devolver con explicacion

La devolucion ideal incluye:

- 3 hallazgos principales;
- riesgos o limitaciones;
- recomendaciones prudentes;
- proximos pasos.

Despues de entregar el informe aprobado, registrar destinatario y canal con `mark-delivered`.

## 9. Cerrar piloto

Registrar feedback, resultado y decision de continuidad. Despues revisar retencion o borrado de datos y dejar evidencia con `record-retention`.
