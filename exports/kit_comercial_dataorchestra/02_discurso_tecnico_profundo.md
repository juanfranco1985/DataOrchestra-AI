# Discurso tecnico para profundizar

## Explicacion profesional

DataOrchestra AI es una herramienta interna de diagnostico comercial supervisado para PyMEs. Trabaja con archivos simples de ventas, productos y stock, preferentemente en CSV, y ejecuta un flujo controlado:

1. admision del cliente;
2. recepcion de datos anonimizados;
3. validacion de privacidad;
4. validacion de estructura;
5. validacion de consistencia comercial;
6. analisis de ventas, margen y stock;
7. generacion de alertas y recomendaciones;
8. revision humana;
9. aprobacion del informe;
10. devolucion controlada.

## Que datos necesita

La base esperada son tres archivos:

- `ventas.csv`: fecha, producto, categoria, cantidad, precio unitario y costo unitario;
- `productos.csv`: producto, categoria, precio unitario y costo unitario;
- `stock.csv`: producto, stock actual, stock minimo y costo unitario.

Los archivos no deben incluir nombres de clientes, telefonos, emails, DNI, CUIT/CUIL personales, direcciones, tarjetas, cuentas bancarias ni datos sensibles innecesarios.

## Que valida antes de analizar

Antes de interpretar los datos, el sistema revisa:

- columnas obligatorias;
- fechas con formato correcto;
- cantidades y precios no negativos;
- productos vendidos que no aparecen en el catalogo;
- margenes imposibles;
- precios en cero;
- duplicados;
- productos con nombres muy parecidos;
- stock bajo o inconsistente;
- presencia de patrones sensibles.

Si la privacidad o la estructura fallan, el analisis se bloquea.

## Que analiza

El diagnostico puede revisar:

- facturacion total;
- costos estimados;
- margen bruto;
- margen por producto;
- ticket o venta promedio;
- productos con mayor facturacion;
- productos con bajo margen;
- productos con stock bajo;
- productos con exceso de stock;
- concentracion de ventas;
- ventas por categoria;
- comparacion de periodos;
- calidad general de datos;
- confianza operativa por hallazgo.

## Que recibe el cliente

El cliente recibe un informe ejecutivo revisado, con:

- resumen general;
- principales metricas;
- alertas comerciales;
- recomendaciones;
- evidencia usada;
- limitaciones del analisis;
- proximos pasos sugeridos.

## Punto importante sobre IA

El valor no esta en prometer una IA autonoma que decide por el negocio. El valor esta en ordenar datos simples, detectar patrones utiles, documentar evidencia y entregar una lectura revisada por una persona.

## Diferencia con un dashboard

Un dashboard muestra indicadores. DataOrchestra AI genera un diagnostico controlado: interpreta senales, marca alertas, sugiere acciones y deja evidencia para que el dueño pueda decidir.

## Diferencia con un contador o gestor

No reemplaza al contador ni al sistema de gestion. El foco es comercial y operativo: ventas, margen, stock, concentracion y oportunidades de decision.

## Limites tecnicos actuales

- No es una plataforma autoservicio.
- No hay integracion directa con sistemas del cliente.
- No se procesan datos sensibles.
- No garantiza resultados comerciales.
- No reemplaza criterio humano.
- No hace prediccion avanzada.
- La entrega requiere revision humana.

## Como explicarlo si preguntan por seguridad

El proceso esta diseñado para trabajar con datos anonimizados. Si aparecen datos sensibles, se detiene. Los archivos originales no se modifican. Cada corrida genera trazabilidad y el informe queda bloqueado hasta revision humana.
