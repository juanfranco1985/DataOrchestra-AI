# DataOrchestra AI Web

Landing institucional v0.1 para presentar DataOrchestra AI como servicio supervisado de diagnóstico comercial para PyMEs.

## Descripción

DataOrchestra AI es una unidad operativa para realizar diagnósticos comerciales controlados a partir de datos anonimizados de ventas, productos y stock. La web comunica el estado real del proyecto: v2.0 - Primer Piloto Real Controlado.

No presenta el proyecto como SaaS, plataforma autoservicio ni producto listo para escalar masivamente.

## Stack

- Next.js
- TypeScript
- Tailwind CSS
- Componentes reutilizables
- SEO básico con metadata en `app/layout.tsx`

## Instalación

```bash
npm install
```

En PowerShell con ejecución de scripts restringida, usar:

```powershell
cmd /c npm.cmd install
```

## Desarrollo

```bash
npm run dev
```

En PowerShell:

```powershell
cmd /c npm.cmd run dev
```

La web queda disponible normalmente en:

```text
http://localhost:3000
```

## Build

```bash
npm run build
```

En PowerShell:

```powershell
cmd /c npm.cmd run build
```

El build genera una exportacion estatica en `out/`, preparada para hosting estatico.

## Formulario de contacto

El formulario de contacto valida campos en el navegador, exige aceptar el alcance de datos anonimizados y prepara un correo estructurado con `mailto:`. No sube archivos ni guarda datos en servidor.

Para configurar el destinatario en build:

```powershell
$env:NEXT_PUBLIC_CONTACT_EMAIL="tu-email-operativo@dominio.com"
```

En GitHub Pages, usar la variable del repositorio `DATAORCHESTRA_CONTACT_EMAIL`. Ver `../docs/FORMULARIO_CONTACTO_CONTROLADO.md`.

## Deploy en GitHub Pages

El repositorio principal incluye un workflow para publicar esta web en GitHub Pages:

```text
../.github/workflows/deploy-web.yml
```

URL esperada una vez activado Pages:

```text
https://juanfranco1985.github.io/DataOrchestra-AI/
```

Para probar localmente el mismo `basePath` usado por GitHub Pages:

```powershell
$env:GITHUB_PAGES="true"
$env:NEXT_PUBLIC_BASE_PATH="/DataOrchestra-AI"
cmd /c npm.cmd run build
```

La activacion en GitHub esta documentada en:

```text
../docs/DEPLOY_WEB_GITHUB_PAGES.md
```

## Estructura

```text
dataorchestra-web/
  app/
    page.tsx
    servicio/page.tsx
    privacidad/page.tsx
    terminos-privacidad/page.tsx
    demo/page.tsx
    faq/page.tsx
    layout.tsx
    globals.css
  components/
    Header.tsx
    Hero.tsx
    ProblemSection.tsx
    SolutionSection.tsx
    ProcessSection.tsx
    AnalysisScopeSection.tsx
    PrivacySection.tsx
    DifferentiationSection.tsx
    PilotSection.tsx
    ContactSection.tsx
    Footer.tsx
  docs/
    ESTADO_WEB_V0_1.md
    COPY_COMERCIAL.md
    ROADMAP_WEB.md
    DECISIONES_DE_DISENO.md
  public/images/
  package.json
  tailwind.config.ts
  tsconfig.json
```

## Estado actual

Versión v0.1: landing institucional de una página, sin backend propio.

La version integrada agrega paginas informativas para servicio, privacidad y caso demo ficticio.

Tambien queda preparada para deploy estatico en GitHub Pages.

El formulario actual prepara solicitudes por email y copia para CRM, sin backend propio.

La pagina `/faq` agrega preguntas frecuentes y objeciones comerciales para explicar alcance, privacidad y limites del piloto.

La pagina `/terminos-privacidad` agrega una base publica de terminos, privacidad, limitaciones y criterios de uso de datos.

## Proximos pasos

- Integrar backend, webhook o CRM para registrar solicitudes.
- Activar GitHub Pages y probar la web publicada.
- Configurar `DATAORCHESTRA_CONTACT_EMAIL`.
- Revisar terminos y privacidad con soporte legal.
- Medir visitas y conversiones.
