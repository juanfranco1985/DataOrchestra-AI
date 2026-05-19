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
cd dataorchestra-web
cmd /c npm.cmd run build
```

El resultado debe generar:

```text
dataorchestra-web/out/
```

## Consideraciones

- La web sigue siendo institucional y estatica.
- El formulario prepara un correo estructurado y no sube archivos.
- No se publica ninguna carpeta de clientes, reportes, logs ni datos reales.
- El sitio no convierte DataOrchestra AI en SaaS ni autoservicio.
- El deploy publico solo mejora presencia comercial y confianza externa.

## Siguiente mejora relacionada

Integrar backend, webhook o CRM para registrar solicitudes con trazabilidad comercial.
