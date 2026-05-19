# Panel interno local

El panel interno local permite operar pilotos controlados desde una interfaz visual privada.

No es un portal de clientes, no es SaaS y no debe exponerse publicamente sin autenticacion, permisos y revision de seguridad.

## Instalacion

Desde la raiz del proyecto:

```powershell
python -m pip install -e .[panel]
```

## Ejecucion

```powershell
$env:PYTHONPATH="src"
python -m streamlit run tools/internal_panel.py
```

Streamlit mostrara una URL local, normalmente:

```text
http://localhost:8501
```

## Funciones incluidas

- Crear cliente piloto.
- Preparar runtime seguro.
- Seleccionar raiz externa de clientes.
- Seleccionar cliente.
- Ver estado operativo y proxima accion.
- Ver archivos raw esperados.
- Cargar `ventas.csv`, `productos.csv` y `stock.csv`.
- Ejecutar preflight.
- Ejecutar analisis.
- Ejecutar full-run.
- Aprobar entrega con revisor, notas y confirmacion humana.
- Exportar PDF aprobado.
- Cerrar piloto con registro.
- Ver entregables y audit log.

## Reglas operativas

- Usar solo en maquina local o entorno privado.
- No exponer por internet.
- No cargar datos personales innecesarios.
- No reemplazar archivos `raw/` despues de preflight sin volver a ejecutar preflight.
- No aprobar informes sin revision humana real.

## Limitaciones actuales

- No tiene autenticacion.
- No tiene gestion de usuarios.
- No tiene permisos por rol.
- No reemplaza revision legal ni procedimiento de privacidad.
- No esta pensado para clientes finales.

## Proximo paso

Si el flujo se usa con clientes reales, el siguiente paso seria convertir este panel en una herramienta privada con autenticacion, permisos, almacenamiento de configuracion y despliegue controlado.
