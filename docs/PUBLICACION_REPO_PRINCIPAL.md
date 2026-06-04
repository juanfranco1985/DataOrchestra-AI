# Publicacion como repo principal

La carpeta canonica es:

```text
C:\Documentos\Aplicacion DATA ORCHESTRA\DataOrchestra_AI_v2_1_integrado
```

Para que CI y deploy funcionen, esta carpeta debe ser la raiz del repositorio Git publicado. Los workflows incluidos asumen esta estructura:

```text
.github/workflows/
src/
tests/
dataorchestra-web/
pyproject.toml
```

## Preparacion local

```powershell
git init -b main
git remote add origin https://github.com/juanfranco1985/DataOrchestra-AI.git
git status --short
```

Antes de subir:

```powershell
$env:PYTHONPATH="src"
python -m pytest -q
cd dataorchestra-web
cmd /c npm.cmd ci
cmd /c npm.cmd run build
```

## GitHub Pages

En GitHub:

```text
Settings -> Pages -> Build and deployment -> GitHub Actions
```

Variables recomendadas:

```text
DATAORCHESTRA_CONTACT_EMAIL
DATAORCHESTRA_CONTACT_WEBHOOK_URL
DATAORCHESTRA_CONTACT_INTEGRATION_NAME
```

Si no se configura webhook, el formulario debe usar email o copia manual. Si se configura webhook, usar un endpoint HTTPS con control anti-spam o rate-limit.
