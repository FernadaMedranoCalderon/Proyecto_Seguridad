# Proyecto Seguridad - A05:2025 Injection

Aplicacion web de demostracion con datos completamente ficticios para explicar fallas de inyeccion en un entorno de laboratorio.

## Estructura de ramas

- `main`: version demostrativa y deliberadamente insegura para la presentacion.
- `fixed`: version corregida con consultas parametrizadas y validaciones basicas.

## Ejecucion local

```bash
pip install -r requirements.txt
python mian.py
```

## Nota

El proyecto usa una base en memoria y registros simulados. No debe conectarse a datos reales ni exponerse a internet.