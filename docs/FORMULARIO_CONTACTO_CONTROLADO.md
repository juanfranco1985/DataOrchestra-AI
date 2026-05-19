# Formulario de contacto controlado

## Objetivo

Convertir el formulario de la web institucional en un primer canal funcional para solicitudes de evaluacion, sin agregar backend, sin servicios pagos y sin permitir carga de archivos.

## Estado

Implementado en:

```text
dataorchestra-web/components/ContactForm.tsx
```

El formulario:

- valida campos obligatorios;
- exige confirmar que el piloto trabaja con datos anonimizados y revision humana;
- limita el mensaje;
- detecta patrones obvios de datos sensibles en el mensaje;
- prepara un correo estructurado con `mailto:`;
- permite copiar la solicitud para pegarla en email o CRM;
- no guarda datos en servidor;
- no sube archivos;
- mantiene compatibilidad con GitHub Pages.

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

## Limitaciones

- No confirma recepcion automaticamente.
- No registra leads en base de datos.
- No integra CRM todavia.
- Depende del cliente de correo del usuario.
- No reemplaza un proceso formal de admision.

## Uso operativo recomendado

1. Recibir la solicitud inicial por email.
2. Responder con criterios de admision y aviso de no enviar datos sensibles.
3. Confirmar si el cliente tiene `ventas.csv`, `productos.csv` y `stock.csv`.
4. Si corresponde, enviar instrucciones de anonimizacion.
5. Recibir archivos solamente mediante el proceso acordado.

## Siguiente mejora

Integrar backend, webhook o CRM para registrar solicitudes con trazabilidad, estado comercial y responsable asignado.
