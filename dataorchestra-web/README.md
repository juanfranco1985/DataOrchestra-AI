# DataOrchestra AI Web v0.2

Web institucional integrada en `DataOrchestra_AI_v2_1_integrado`.

Esta es la web vigente del proyecto unico. La carpeta suelta `dataorchestra-web/` en la raiz del workspace queda como referencia anterior.

## Descripcion

DataOrchestra AI se presenta como servicio supervisado de diagnostico comercial para PyMEs con datos anonimizados, trazabilidad y revision humana.

No se presenta como SaaS, plataforma autoservicio ni producto final escalable.

## Stack

- Next.js
- TypeScript
- Tailwind CSS
- Componentes reutilizables
- Export estatico para hosting simple

## Comandos

```powershell
cmd /c npm.cmd install
cmd /c npm.cmd run dev
cmd /c npm.cmd run build
```

La web de desarrollo queda normalmente en:

```text
http://localhost:3000
```

## Paginas

- `/`
- `/servicio`
- `/privacidad`
- `/terminos-privacidad`
- `/demo`
- `/faq`

## Formulario de contacto

El formulario valida campos en navegador, exige aceptar el alcance de datos anonimizados y puede operar en dos modos:

- webhook/CRM configurable con `NEXT_PUBLIC_CONTACT_WEBHOOK_URL`;
- correo estructurado con `mailto:` si no hay webhook configurado.

Variables opcionales:

```powershell
$env:NEXT_PUBLIC_CONTACT_EMAIL="tu-email-operativo@dominio.com"
$env:NEXT_PUBLIC_CONTACT_WEBHOOK_URL="https://endpoint-del-webhook"
$env:NEXT_PUBLIC_CONTACT_INTEGRATION_NAME="CRM operativo"
```

Ver `../docs/FORMULARIO_CONTACTO_CONTROLADO.md`.

## Deploy

Workflow:

```text
../.github/workflows/deploy-web.yml
```

Build local simulando GitHub Pages:

```powershell
$env:GITHUB_PAGES="true"
$env:NEXT_PUBLIC_BASE_PATH="/DataOrchestra-AI"
cmd /c npm.cmd run build
```

Guia: `../docs/DEPLOY_WEB_GITHUB_PAGES.md`.

## Estado

Version v0.2: web institucional integrada en la version canonica `v2.1 - Version Integradora`.
