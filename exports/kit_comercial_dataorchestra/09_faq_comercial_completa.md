# FAQ comercial para piloto controlado

## Objetivo

Centralizar respuestas prudentes para conversaciones con potenciales clientes piloto de DataOrchestra AI.

Este documento ayuda a mantener consistencia comercial: explicar valor, aclarar limites y evitar promesas que todavia no corresponden al estado del proyecto.

## Mensaje base

DataOrchestra AI es un servicio supervisado de diagnostico comercial para PyMEs. Trabaja con datos anonimizados de ventas, productos y stock para detectar hallazgos accionables, manteniendo privacidad, trazabilidad, auditoria y revision humana antes de entregar resultados.

## Preguntas frecuentes

### Es un SaaS?

No. En esta etapa no es una plataforma publica, autoservicio ni SaaS abierto. Es un servicio controlado para ejecutar pilotos con alcance limitado y supervision humana.

### Que datos necesita?

La base esperada es:

- `ventas.csv`
- `productos.csv`
- `stock.csv`

Los archivos deben estar anonimizados y contener datos suficientes para revisar ventas, margen, stock, categorias y concentracion.

### El cliente puede enviar datos personales?

No. No se deben recibir nombres de personas, telefonos, emails, direcciones, DNI, CUIT/CUIL, tarjetas, cuentas bancarias ni datos sensibles innecesarios.

Si aparecen datos sensibles, el flujo debe detenerse y solicitar correccion.

### El analisis es automatico?

El sistema puede generar metricas, alertas, recomendaciones y borradores. La entrega no es automatica. El informe debe quedar en revision humana hasta ser aprobado.

### Que recibe el cliente?

Un informe ejecutivo revisado con:

- resumen del diagnostico;
- metricas principales;
- alertas comerciales;
- recomendaciones;
- evidencia;
- limitaciones del analisis;
- proximos pasos sugeridos.

### Cuanto demora?

Depende de la calidad de los datos y del alcance acordado. En un primer piloto no conviene prometer tiempos cerrados antes de revisar archivos y completar preflight.

Respuesta recomendada:

> Primero validamos que los datos sean anonimizados y procesables. Con esa revision podemos estimar el esfuerzo real del diagnostico.

### Garantiza aumento de ventas o margen?

No. El diagnostico puede encontrar oportunidades y riesgos, pero no garantiza resultados. Las decisiones comerciales dependen del contexto del negocio y de la ejecucion posterior.

### Puede integrarse con mi sistema?

No en esta etapa. El piloto trabaja con CSV exportados. Integraciones directas pueden evaluarse mas adelante si el diagnostico demuestra valor.

### Que pasa despues del piloto?

Se revisa:

- si los hallazgos fueron utiles;
- si el cliente entiende el informe;
- que decisiones podria tomar;
- si conviene una segunda iteracion;
- si tiene sentido seguimiento mensual o mejora del alcance.

## Objeciones frecuentes

### Ya tengo planillas

Respuesta:

DataOrchestra AI no reemplaza la planilla. La usa como punto de partida para detectar señales que normalmente quedan ocultas: margen bajo, stock inmovilizado, concentracion y oportunidades de reposicion.

### Ya tengo dashboard

Respuesta:

Un dashboard muestra indicadores. El diagnostico busca convertir datos en hallazgos revisados y recomendaciones concretas, con evidencia y limitaciones claras.

### No quiero compartir informacion sensible

Respuesta:

El proceso esta diseñado justamente para trabajar con datos anonimizados. Si aparecen datos sensibles innecesarios, el analisis se bloquea.

### No se si mis datos sirven

Respuesta:

Ese es un buen punto de partida para un piloto. Primero se hace una validacion de estructura y privacidad. Si los datos no alcanzan, se informa que falta antes de prometer un diagnostico.

## Frases recomendadas

- "Diagnostico comercial controlado."
- "Datos anonimizados."
- "Revision humana antes de la entrega."
- "Hallazgos accionables respaldados por evidencia."
- "Primer piloto con alcance limitado."
- "Servicio supervisado, no autoservicio."

## Frases a evitar

- "Automatizacion total."
- "Garantizamos mejora de ventas."
- "Subi tus datos y obtene resultados al instante."
- "Plataforma SaaS lista para escalar."
- "IA que decide por tu negocio."

## Cierre recomendado

Si el cliente muestra interes, el siguiente paso no es pedir archivos directamente por email. Primero corresponde confirmar:

1. rubro y necesidad comercial;
2. existencia de ventas, productos y stock;
3. posibilidad de anonimizar datos;
4. aceptacion del alcance limitado;
5. canal acordado para intercambio de archivos.
