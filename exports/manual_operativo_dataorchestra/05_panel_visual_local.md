# Panel visual local

El panel local sirve para operar pilotos desde una interfaz visual. No es un portal de clientes y no debe exponerse en internet.

## Instalacion

Desde la raiz del proyecto:

```powershell
python -m pip install -e .[panel]
```

## Ejecucion

```powershell
cd "C:\Documentos\Aplicacion DATA ORCHESTRA\DataOrchestra_AI_v2_1_integrado"
$env:PYTHONPATH="src"
python -m streamlit run tools/internal_panel.py
```

Normalmente abre:

```text
http://localhost:8501
```

## Que permite hacer

- Preparar runtime seguro.
- Crear cliente piloto.
- Seleccionar raiz externa de clientes.
- Ver estado operativo.
- Cargar `ventas.csv`, `productos.csv` y `stock.csv`.
- Ejecutar preflight.
- Ejecutar analisis.
- Ejecutar full-run.
- Aprobar entrega.
- Exportar PDF.
- Cerrar piloto.
- Ver entregables y audit log.

## Reglas

- Usar solo localmente.
- No compartir la URL en internet.
- No cargar datos personales.
- No aprobar sin leer el informe.
- No reemplazar archivos `raw/` sin repetir preflight.

## Cuando usar CLI y cuando panel

Usar CLI si:

- queres maxima trazabilidad;
- queres copiar comandos;
- estas depurando errores;
- queres repetir un flujo exacto.

Usar panel si:

- queres operar visualmente;
- queres cargar archivos con interfaz;
- estas haciendo una demo interna;
- queres reducir uso de terminal.

