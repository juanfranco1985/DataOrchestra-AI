# Estado web v0.2

La web v0.2 es la version integrada dentro de `DataOrchestra_AI_v2_1_integrado`.

## Estado

- Landing institucional.
- Paginas `/servicio`, `/privacidad`, `/terminos-privacidad`, `/demo` y `/faq`.
- Export estatico con Next.js.
- Preparada para GitHub Pages.
- Formulario con webhook HTTPS configurable o fallback por email/copia.

## Mejoras v0.2

- El formulario no usa webhooks no HTTPS.
- Timeout de webhook para evitar esperas indefinidas.
- Envio sin credenciales del navegador.
- Bloqueo si no hay email operativo ni webhook configurado.
- Opcion de copiar solicitud para operacion manual.

## Pendientes

- Revisar terminos y privacidad con soporte legal.
- Configurar canal real de contacto.
- Activar GitHub Pages desde el repo principal.
- Probar conversiones con clientes reales.
