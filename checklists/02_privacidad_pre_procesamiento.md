# Checklist 02 - Privacidad antes de procesar

- [ ] Los archivos estan en `raw/`.
- [ ] Los archivos originales no fueron modificados.
- [ ] No hay nombres de personas.
- [ ] No hay telefonos, emails, DNI, CUIT/CUIL, direccion ni datos bancarios.
- [ ] Se ejecuto `python -m dataorchestra.cli preflight --client-dir clients/cliente_001`.
- [ ] El reporte de privacidad esta en estado `passed`.
- [ ] Si hubo hallazgos, el flujo quedo bloqueado y no se proceso nada.
