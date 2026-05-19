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

## Estructura

```text
dataorchestra-web/
  app/
    page.tsx
    servicio/page.tsx
    privacidad/page.tsx
    demo/page.tsx
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

Versión v0.1: landing institucional de una página, sin backend y sin envío real de formulario.

La version integrada agrega paginas informativas para servicio, privacidad y caso demo ficticio.

## Próximos pasos

- Integrar formulario real con email o CRM.
- Agregar página de privacidad y términos.
- Crear caso demo con dataset ficticio.
- Preparar una sección de servicios.
- Evaluar un panel privado para pilotos cuando el flujo comercial lo justifique.
