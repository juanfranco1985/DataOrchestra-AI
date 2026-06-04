# Continuidad para Codex - DataOrchestra AI

Actualizacion integradora: 2026-06-03

La version canonica de trabajo es:

```text
C:\Documentos\Aplicacion DATA ORCHESTRA\DataOrchestra_AI_v2_1_integrado
```

Esta carpeta integra backend, CLI, tests, web, documentacion, contratos, demos y kits. Los paths historicos que aparezcan mas abajo quedaron como contexto heredado de v2.0 y no deben usarse como base para trabajo nuevo.

Fecha de corte heredada: 2026-05-26

Este documento resume el estado del proyecto y lo realizado en la ultima etapa para que una proxima sesion de Codex pueda continuar sin reconstruir contexto.

## Ubicacion operativa anterior, solo referencia

```text
C:\Documentos\Aplicacion DATA ORCHESTRA\DataOrchestra_AI_Proyecto_Consolidado_para_Codex_v1_95\v2_0_primer_piloto_real_controlado
```

Repositorio Git:

```text
juanfranco1985/DataOrchestra-AI
branch: main
```

## Estado general

DataOrchestra AI v2.1 integrado es la base operativa actual para pilotos comerciales controlados con PyMEs.

No debe presentarse como SaaS, plataforma autoservicio ni producto final escalable. La presentacion correcta es:

```text
Servicio supervisado de diagnostico comercial para PyMEs con datos anonimizados, revision humana y entrega controlada.
```

## Decisiones importantes

- Se decidio pausar desarrollo tecnico nuevo y pasar a foco comercial.
- La herramienta es suficiente para salir a validar con clientes reales locales de bajo riesgo.
- La prioridad ahora es vender, conversar con comercios, registrar objeciones y conseguir 1 o 2 pilotos reales.
- No seguir agregando funcionalidad hasta tener feedback real.

## Trabajo tecnico reciente

### Formulario web

Archivo principal:

```text
dataorchestra-web/components/ContactForm.tsx
```

Se agrego soporte para:

- envio a webhook/CRM configurable mediante `NEXT_PUBLIC_CONTACT_WEBHOOK_URL`;
- nombre visible de integracion mediante `NEXT_PUBLIC_CONTACT_INTEGRATION_NAME`;
- fallback a email mediante `NEXT_PUBLIC_CONTACT_EMAIL`;
- validaciones existentes de campos y datos sensibles.

Workflow actualizado:

```text
.github/workflows/deploy-web.yml
```

Variables esperadas en GitHub Actions:

```text
DATAORCHESTRA_CONTACT_EMAIL
DATAORCHESTRA_CONTACT_WEBHOOK_URL
DATAORCHESTRA_CONTACT_INTEGRATION_NAME
```

Tambien se agrego `.nojekyll` en el workflow para servir assets `_next` correctamente en GitHub Pages.

### Documentacion actualizada

Archivos modificados o agregados:

```text
README.md
docs/FORMULARIO_CONTACTO_CONTROLADO.md
docs/DEPLOY_WEB_GITHUB_PAGES.md
docs/ESTADO_ACTUAL_v2_0.md
docs/MEJORAS_PROFESIONALIZACION.md
dataorchestra-web/README.md
dataorchestra-web/docs/ROADMAP_WEB.md
dataorchestra-web/docs/ESTADO_WEB_V0_1.md
docs/PROPUESTA_COMERCIAL_PILOTO.md
```

## Verificaciones realizadas

Comandos ejecutados correctamente:

```powershell
cmd /c npm.cmd run build
python -m pytest -q
git diff --check
```

Tambien se ejecuto build simulando GitHub Pages con:

```powershell
$env:GITHUB_PAGES='true'
$env:NEXT_PUBLIC_BASE_PATH='/DataOrchestra-AI'
$env:NEXT_PUBLIC_CONTACT_WEBHOOK_URL='https://example.com/webhook'
$env:NEXT_PUBLIC_CONTACT_INTEGRATION_NAME='CRM operativo'
cmd /c npm.cmd run build
```

Resultado conocido:

- tests Python: `68 passed`;
- build web: OK;
- URL publica esperada `https://juanfranco1985.github.io/DataOrchestra-AI/` respondia 404 al momento de revisar, por falta de activacion/despliegue de GitHub Pages.

## Pendientes tecnicos no bloqueantes

1. Activar GitHub Pages en GitHub:

```text
Settings -> Pages -> Build and deployment -> GitHub Actions
```

2. Configurar variable:

```text
DATAORCHESTRA_CONTACT_EMAIL
```

3. Opcionalmente configurar:

```text
DATAORCHESTRA_CONTACT_WEBHOOK_URL
DATAORCHESTRA_CONTACT_INTEGRATION_NAME
```

4. Ejecutar workflow:

```text
Deploy web to GitHub Pages
```

5. Probar formulario desde URL publica.

## Trabajo comercial reciente

Se creo propuesta comercial:

```text
docs/PROPUESTA_COMERCIAL_PILOTO.md
```

Lectura de precios:

- ARS 25.000 por diagnostico: usar solo como precio piloto/fundador para primeros 2 o 3 clientes.
- ARS 45.000 a ARS 75.000: precio base sugerido posterior.
- ARS 50.000 a ARS 70.000 mensual: seguimiento opcional despues de demostrar valor.
- Revisar precios cada 15 a 30 dias por inflacion y esfuerzo real.

## Kits exportados

Carpeta:

```text
exports
```

ZIP comercial:

```text
exports/kit_comercial_dataorchestra.zip
```

Carpeta editable:

```text
exports/kit_comercial_dataorchestra/
```

Incluye:

- discurso simple de venta en calle;
- discurso tecnico;
- preguntas y objeciones;
- precios y paquetes;
- checklist de primer contacto;
- mensajes WhatsApp/email;
- ficha de una pagina;
- propuesta comercial completa;
- FAQ comercial;
- aceptacion de piloto;
- checklists de datos y seguridad;
- entrevista extensa de preguntas y respuestas;
- flyers y frases publicitarias.

Manual operativo:

```text
exports/manual_operativo_dataorchestra.zip
exports/manual_operativo_dataorchestra/
```

Incluye:

- paso a paso general;
- requisitos y software;
- archivos necesarios;
- carga de datos;
- CLI PowerShell;
- panel visual local;
- modelos/tipos de analisis;
- revision, entrega y cierre;
- solucion de problemas;
- checklist operativo.

## Documentos clave del kit comercial

```text
exports/kit_comercial_dataorchestra/01_discurso_simple_calle.md
exports/kit_comercial_dataorchestra/02_discurso_tecnico_profundo.md
exports/kit_comercial_dataorchestra/03_preguntas_y_objeciones.md
exports/kit_comercial_dataorchestra/04_precios_y_paquetes.md
exports/kit_comercial_dataorchestra/14_entrevista_preguntas_y_respuestas.md
exports/kit_comercial_dataorchestra/15_flyers_y_frases_publicitarias.md
```

## Frase comercial principal

```text
Ayudo a comercios y PyMEs a transformar datos simples de ventas, productos y stock en un diagnostico claro, con hallazgos concretos y recomendaciones practicas.
```

## Version para publicidad fisica recomendada

```text
Sabes que productos realmente le dejan ganancia a tu negocio?

Analizo ventas, stock y margenes con datos que tu comercio ya tiene.
Recibis un informe claro con alertas, oportunidades y recomendaciones practicas.

Diagnostico comercial para comercios y PyMEs de la zona.
Primeros trabajos con precio piloto.

WhatsApp: [tu numero]
```

Linea opcional:

```text
No necesitas cambiar tu sistema. Trabajamos con datos simples y sin informacion personal.
```

## Paso a paso operativo resumido

```powershell
cd "C:\Documentos\Aplicacion DATA ORCHESTRA\DataOrchestra_AI_Proyecto_Consolidado_para_Codex_v1_95\v2_0_primer_piloto_real_controlado"
$env:PYTHONPATH="src"
python -m dataorchestra.cli prepare-runtime --runtime-dir "C:\Documentos\DataOrchestra_Runtime"
python -m dataorchestra.cli init-client --clients-root "C:\Documentos\DataOrchestra_Runtime\clients" --client-id cliente_001 --display-name "Nombre comercio" --business-type "Retail"
```

Luego cargar en:

```text
C:\Documentos\DataOrchestra_Runtime\clients\cliente_001\raw\
```

Archivos:

```text
ventas.csv
productos.csv
stock.csv
```

Ejecutar:

```powershell
python -m dataorchestra.cli readiness --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001" --repo-root .
python -m dataorchestra.cli preflight --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001"
python -m dataorchestra.cli data-quality --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001"
python -m dataorchestra.cli analyze --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001"
```

Despues de revision humana:

```powershell
python -m dataorchestra.cli approve --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001" --reviewer "Juan" --notes "Revision humana completada" --confirm-human-review
python -m dataorchestra.cli export-pdf --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001"
```

Cerrar:

```powershell
python -m dataorchestra.cli close-pilot --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001" --reviewer "Juan" --notes "Cierre registrado" --outcome completed --confirm-close
```

## Proximo foco recomendado

No programar mas salvo necesidad concreta. En la proxima etapa:

1. Revisar este documento.
2. Revisar kit comercial.
3. Practicar entrevista Q&A.
4. Activar GitHub Pages si se quiere presencia web.
5. Salir a hablar con comercios.
6. Registrar objeciones y feedback.
7. Buscar 1 o 2 pilotos reales de bajo riesgo.

## Criterio para volver a programar

Volver a desarrollo solo si aparece una necesidad validada por clientes reales, por ejemplo:

- el formato de datos local no coincide con las plantillas;
- los clientes no entienden el informe;
- se necesita un tipo de grafico o resumen especifico;
- el flujo manual se vuelve repetitivo;
- hay que integrar un canal real de leads;
- el primer piloto demuestra que vale la pena escalar.
