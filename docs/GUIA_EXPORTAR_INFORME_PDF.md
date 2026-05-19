# Guia para exportar informe a PDF

DataOrchestra AI genera informes HTML aprobados listos para imprimir o guardar como PDF.

## Archivo de entrada

Despues de aprobar un diagnostico, abrir:

```text
clients/<cliente>/reports/diagnostico_aprobado.html
```

## Exportar desde navegador

1. Abrir el archivo HTML en el navegador.
2. Presionar `Ctrl + P`.
3. Elegir destino `Guardar como PDF`.
4. Activar fondos o graficos de fondo si el navegador lo permite.
5. Guardar el archivo con nombre:

```text
DataOrchestra_AI_Diagnostico_<cliente>_<fecha>.pdf
```

## Reglas de entrega

- Entregar solo informes aprobados.
- No entregar `diagnostico_borrador.*`.
- No entregar archivos `raw/`.
- No entregar logs internos salvo acuerdo especifico.
- No entregar diagnosticos con dudas de privacidad o calidad de datos.

## Nota

La generacion HTML evita depender de librerias externas de PDF. En una version posterior puede agregarse exportacion PDF automatica si el flujo comercial lo justifica.
