# Estado web v0.1

## Nombre de la version

DataOrchestra AI Web v0.1 - Landing institucional.

## Objetivo

Crear una primera presencia comercial profesional para explicar DataOrchestra AI como servicio supervisado de diagnostico comercial para PyMEs.

## Que incluye

- Landing de una pagina.
- Header con navegacion por anclas.
- Pagina de servicio.
- Pagina de privacidad.
- Pagina de terminos y privacidad.
- Pagina de caso demo ficticio.
- Pagina de preguntas frecuentes y objeciones comerciales.
- Hero institucional con mensaje principal prudente.
- Secciones de problema, solucion, proceso, analisis, privacidad, diferenciacion, piloto y contacto.
- Formulario de contacto controlado por email o webhook configurable, sin backend propio ni carga de archivos.
- SEO basico en `app/layout.tsx`.
- Diseño responsive con Tailwind CSS.
- Documentacion comercial y de diseño.
- Export estatico de Next.js.
- Workflow de GitHub Pages preparado.

## Que no incluye

- Backend propio.
- Base de datos propia de leads.
- CRM real ya conectado.
- Blog.
- Contrato legal definitivo.
- Panel privado web.
- Area de clientes.
- Funcionalidad SaaS o autoservicio.

## Estado del producto

La web comunica el estado real de DataOrchestra AI: v2.1 - Version Integradora para primer piloto real controlado.

El proyecto se presenta como diagnostico comercial controlado con datos anonimizados, trazabilidad, auditoria y revision humana. No se presenta como plataforma final escalable.

## Rutas actuales

- `/`
- `/servicio`
- `/privacidad`
- `/terminos-privacidad`
- `/demo`
- `/faq`

## Limitaciones actuales

- El formulario depende del cliente de correo si no se configura webhook.
- El envio automatico depende de un endpoint real compatible con CORS.
- Sin analytics.
- Sin revision legal profesional final.
- Sin captacion automatizada.
- Sin sistema de gestion de leads.
- GitHub Pages pendiente de activacion manual en el repositorio.

## Proximos pasos recomendados

1. Activar GitHub Pages con fuente `GitHub Actions`.
2. Configurar `DATAORCHESTRA_CONTACT_EMAIL` en variables del repositorio.
3. Configurar `DATAORCHESTRA_CONTACT_WEBHOOK_URL` si se usara CRM o automatizacion externa.
4. Validar el copy con potenciales clientes piloto.
5. Revisar terminos y privacidad con soporte legal.
6. Medir visitas y conversiones.
