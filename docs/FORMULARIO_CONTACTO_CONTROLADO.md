# Formulario de contacto controlado

## Objetivo

Convertir el formulario de la web institucional en un primer canal funcional para solicitudes de evaluacion, sin permitir carga de archivos y manteniendo compatibilidad con GitHub Pages.

## Estado

Implementado en:

```text
dataorchestra-web/components/ContactForm.tsx
```

El formulario:

- valida campos obligatorios;
- bloquea envios demasiado rapidos para reducir spam basico;
- exige confirmar que el piloto trabaja con datos anonimizados y revision humana;
- limita el mensaje;
- detecta patrones obvios de datos sensibles en el mensaje;
- envia la solicitud a un webhook/CRM configurable cuando existe `NEXT_PUBLIC_CONTACT_WEBHOOK_URL` HTTPS;
- prepara un correo estructurado con `mailto:` cuando existe `NEXT_PUBLIC_CONTACT_EMAIL`;
- permite copiar la solicitud para pegarla en email o CRM;
- no guarda datos en servidor;
- no sube archivos;
- mantiene compatibilidad con GitHub Pages.

## Configuracion del webhook o CRM

Para registrar solicitudes automaticamente, crear una variable del repositorio:

```text
DATAORCHESTRA_CONTACT_WEBHOOK_URL
```

Ruta en GitHub:

```text
Settings -> Secrets and variables -> Actions -> Variables -> New repository variable
```

Nombre:

```text
DATAORCHESTRA_CONTACT_WEBHOOK_URL
```

Valor:

```text
https://endpoint-del-webhook-o-crm
```

Opcionalmente, configurar un nombre visible para el canal:

```text
DATAORCHESTRA_CONTACT_INTEGRATION_NAME
```

Ejemplos de valor:

```text
Formspree
Make
Zapier
CRM operativo
```

El workflow de Pages expone esas variables como:

```text
NEXT_PUBLIC_CONTACT_WEBHOOK_URL
NEXT_PUBLIC_CONTACT_INTEGRATION_NAME
```

Requisitos tecnicos:

- el endpoint debe usar HTTPS;
- el endpoint debe aceptar `POST` JSON desde navegador;
- el endpoint debe permitir CORS para la URL publicada;
- el endpoint debe tener controles propios de abuso o rate-limit;
- si el servicio elegido no soporta CORS, mantener el modo email/copia o usar un backend intermedio.

Nota: una URL `NEXT_PUBLIC_*` queda embebida en la web estatica. No usar secretos privados en esta variable.

## Configuracion del email destino

Para que el correo salga con destinatario preconfigurado en GitHub Pages, crear una variable del repositorio:

```text
DATAORCHESTRA_CONTACT_EMAIL
```

Ruta en GitHub:

```text
Settings -> Secrets and variables -> Actions -> Variables -> New repository variable
```

Nombre:

```text
DATAORCHESTRA_CONTACT_EMAIL
```

Valor:

```text
tu-email-operativo@dominio.com
```

El workflow de Pages expone esa variable como:

```text
NEXT_PUBLIC_CONTACT_EMAIL
```

Nota: al ser un email de contacto publico de la web, no debe tratarse como secreto.

## Validacion local con email destino

Desde `dataorchestra-web/`:

```powershell
$env:NEXT_PUBLIC_CONTACT_EMAIL="tu-email-operativo@dominio.com"
cmd /c npm.cmd run build
cmd /c npm.cmd run dev
```

## Validacion local con webhook

Desde `dataorchestra-web/`:

```powershell
$env:NEXT_PUBLIC_CONTACT_WEBHOOK_URL="https://endpoint-del-webhook-o-crm"
$env:NEXT_PUBLIC_CONTACT_INTEGRATION_NAME="CRM operativo"
cmd /c npm.cmd run build
cmd /c npm.cmd run dev
```

## Limitaciones

- Si no hay webhook ni email configurado, el formulario permite copiar la solicitud pero bloquea el envio directo.
- Si no hay webhook configurado, depende del cliente de correo del usuario.
- Si hay webhook configurado, la confirmacion depende de la respuesta del endpoint.
- No incluye base de datos propia.
- No resuelve autenticacion ni gestion multiusuario.
- No reemplaza un proceso formal de admision.

## Uso operativo recomendado

1. Recibir la solicitud inicial por email.
2. Responder con criterios de admision y aviso de no enviar datos sensibles.
3. Confirmar si el cliente tiene `ventas.csv`, `productos.csv` y `stock.csv`.
4. Si corresponde, enviar instrucciones de anonimizacion.
5. Recibir archivos solamente mediante el proceso acordado.

## Siguiente mejora

Conectar un proveedor real y definir el flujo comercial posterior: responsable asignado, estado del lead, respuesta inicial y criterios de admision.
