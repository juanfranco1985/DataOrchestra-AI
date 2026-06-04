# Roadmap web

## Estado de deploy

- v0.1 landing institucional: implementada.
- v0.1.1 deploy publico preparado: export estatico de Next.js y workflow de GitHub Pages implementados.
- v0.3.1 FAQ comercial: implementada como pagina `/faq`.
- v0.4 formulario funcional inicial: implementado con email estructurado, copia para CRM y webhook configurable.
- v0.6 terminos y privacidad: base publica implementada como pagina `/terminos-privacidad`.
- Pendiente operativo: activar Pages en GitHub con fuente `GitHub Actions`.
- Pendiente operativo: configurar `DATAORCHESTRA_CONTACT_EMAIL`.
- Pendiente operativo opcional: configurar `DATAORCHESTRA_CONTACT_WEBHOOK_URL` si se usara CRM o automatizacion externa.

## v0.1 - Landing institucional

Landing de una pagina para explicar el proyecto, su estado real, beneficios, privacidad y piloto controlado.

Estado: implementado.

## v0.2 - Pagina de servicios

Detalle del diagnostico piloto, alcance, entregables, requisitos de datos y criterios de admision.

Estado: implementado como pagina inicial `/servicio`.

## v0.3 - Caso demo con dataset ficticio

Pagina con ejemplo completo usando datos simulados, sin datos reales de clientes.

Estado: implementado como pagina inicial `/demo`.

## v0.4 - Formulario funcional

Integracion inicial con email mediante `mailto:`, validaciones de campos, confirmacion de alcance, copia de solicitud para CRM y envio configurable a webhook compatible.

Estado: implementado sin backend propio.

## v0.4.1 - FAQ comercial y objeciones

Pagina publica con preguntas frecuentes sobre alcance, privacidad, tiempos, entregables y limites del piloto.

Estado: implementado como pagina `/faq`.

## v0.5 - Blog educativo

Contenido sobre ventas, margen, stock, calidad de datos y decisiones comerciales para PyMEs.

## v0.6 - Pagina de privacidad y terminos

Explicacion formal del uso de datos anonimizados, alcance del servicio, limitaciones y responsabilidades.

Estado: pagina `/privacidad` y base publica `/terminos-privacidad` implementadas. Falta revision legal profesional antes de usar como contrato definitivo.

## v0.7 - Integracion con CRM/email

Registro y seguimiento de leads con flujo comercial controlado.

Estado: preparado a nivel web con webhook configurable. Pendiente operativo: elegir proveedor real, configurar endpoint y probar el flujo desde la URL publica.

## v0.8 - Panel privado para pilotos

Area privada para seguimiento de pilotos, estado de revision y entregables aprobados.

## v1.0 - Sitio comercial listo para captacion controlada

Web lista para captacion de clientes piloto, con formularios funcionales, privacidad, caso demo y operacion comercial definida.
