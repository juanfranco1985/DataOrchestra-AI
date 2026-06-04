# Archivos necesarios

DataOrchestra AI trabaja con tres CSV obligatorios.

## 1. ventas.csv

Columnas obligatorias:

```text
fecha,producto,categoria,cantidad,precio_unitario,costo_unitario
```

Ejemplo:

```csv
fecha,producto,categoria,cantidad,precio_unitario,costo_unitario
2026-01-01,Producto A,Categoria 1,2,1000,700
```

## 2. productos.csv

Columnas obligatorias:

```text
producto,categoria,precio_unitario,costo_unitario
```

Ejemplo:

```csv
producto,categoria,precio_unitario,costo_unitario
Producto A,Categoria 1,1000,700
```

## 3. stock.csv

Columnas obligatorias:

```text
producto,stock_actual,stock_minimo,ventas_ultimos_30_dias
```

Ejemplo:

```csv
producto,stock_actual,stock_minimo,ventas_ultimos_30_dias
Producto A,20,5,12
```

## Plantillas disponibles

En el proyecto existen plantillas:

```text
templates/ventas_template.csv
templates/productos_template.csv
templates/stock_template.csv
```

## Reglas de privacidad

No incluir:

- nombres de personas;
- telefonos;
- emails;
- direcciones;
- DNI;
- CUIT/CUIL personales;
- tarjetas;
- cuentas bancarias;
- datos medicos, laborales, legales o financieros sensibles.

## Reglas de formato

- Fechas en formato `YYYY-MM-DD`.
- Numeros no negativos.
- Importes con punto o coma decimal.
- Producto y categoria como etiquetas comerciales anonimizadas.
- No cambiar nombres de columnas.
- No mezclar datos de varios clientes.

## Que hacer si el cliente no tiene los tres archivos

- Si faltan ventas: no hacer diagnostico.
- Si faltan productos: se pierde contraste de catalogo; pedir correccion.
- Si falta stock: se puede evaluar un analisis parcial, pero no es el flujo recomendado.
- Si los datos estan muy desordenados: presupuestar limpieza aparte o postergar.
