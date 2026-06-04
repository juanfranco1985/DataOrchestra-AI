# Deploy web en GitHub Pages

## Objetivo

Dejar preparada la web institucional de DataOrchestra AI para publicacion estatica desde GitHub Pages, usando GitHub Actions y sin agregar backend.

## Estado

El repositorio incluye el workflow:

```text
.github/workflows/deploy-web.yml
```

El workflow:

- instala dependencias de `dataorchestra-web/`;
- ejecuta `npm run build`;
- genera export estatico en `dataorchestra-web/out`;
- agrega `.nojekyll` para que GitHub Pages sirva correctamente assets bajo `_next`;
- sube el artefacto a GitHub Pages;
- despliega el sitio con `actions/deploy-pages`.

## URL esperada

Cuando GitHub Pages este habilitado, la URL esperada es:

```text
https://juanfranco1985.github.io/DataOrchestra-AI/
```

## Activacion en GitHub

1. Abrir el repositorio:

```text
https://github.com/juanfranco1985/DataOrchestra-AI
```

2. Entrar en `Settings`.
3. Entrar en `Pages`.
4. En `Build and deployment`, seleccionar `GitHub Actions` como fuente.
5. Guardar la configuracion si GitHub lo solicita.
6. Ir a la pestaña `Actions`.
7. Ejecutar manualmente `Deploy web to GitHub Pages` o esperar al proximo push en `main` que modifique `dataorchestra-web/`.

## Configurar email de contacto

Para que el formulario prepare correos con destinatario, crear esta variable del repositorio:

```text
DATAORCHESTRA_CONTACT_EMAIL
```

Ruta:

```text
Settings -> Secrets and variables -> Actions -> Variables -> New repository variable
```

El valor debe ser el email operativo donde se recibiran solicitudes de evaluacion. Ver `docs/FORMULARIO_CONTACTO_CONTROLADO.md`.

## Configurar webhook o CRM

Si se quiere registrar solicitudes automaticamente, crear esta variable del repositorio:

```text
DATAORCHESTRA_CONTACT_WEBHOOK_URL
```

Ruta:

```text
Settings -> Secrets and variables -> Actions -> Variables -> New repository variable
```

El valor debe ser un endpoint HTTPS que acepte `POST` JSON desde navegador y permita CORS para la web publicada.

Variable opcional para mostrar el canal usado por el formulario:

```text
DATAORCHESTRA_CONTACT_INTEGRATION_NAME
```

Ejemplos:

```text
Formspree
Make
Zapier
CRM operativo
```

Si no se configura `DATAORCHESTRA_CONTACT_WEBHOOK_URL`, el formulario mantiene el modo `mailto:` y copia manual.

## Validacion local normal

Desde `dataorchestra-web/`:

```powershell
cmd /c npm.cmd install
cmd /c npm.cmd run build
```

## Validacion local simulando GitHub Pages

Desde la raiz del repositorio:

```powershell
$env:GITHUB_PAGES="true"
$env:NEXT_PUBLIC_BASE_PATH="/DataOrchestra-AI"
$env:NEXT_PUBLIC_CONTACT_EMAIL="tu-email-operativo@dominio.com"
$env:NEXT_PUBLIC_CONTACT_WEBHOOK_URL="https://endpoint-del-webhook-o-crm"
$env:NEXT_PUBLIC_CONTACT_INTEGRATION_NAME="CRM operativo"
cd dataorchestra-web
cmd /c npm.cmd run build
```

El resultado debe generar:

```text
dataorchestra-web/out/
```

## Consideraciones

- La web sigue siendo institucional y estatica.
- El formulario puede enviar una solicitud a webhook/CRM o preparar un correo estructurado; no sube archivos.
- No se publica ninguna carpeta de clientes, reportes, logs ni datos reales.
- El sitio no convierte DataOrchestra AI en SaaS ni autoservicio.
- El deploy publico solo mejora presencia comercial y confianza externa.

## Siguiente mejora relacionada

Activar GitHub Pages, configurar el endpoint real elegido y ejecutar una prueba completa desde la URL publica.
