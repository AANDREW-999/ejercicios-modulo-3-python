<!-- Encabezado con badges y estilo centrado -->
<h1 align="center">📘 Ejercicios — Módulo 3 (Python)</h1>

<p align="center">
  Prácticas del Módulo 3 (SENA): control de flujo, funciones, colecciones, E/S y modularidad.
</p>
<p align="center">
  <img src="https://img.shields.io/badge/Dependencias-rich%20|%20pytest%20|%20ruff-2E8B57" alt="Dependencias"/>
  <br/>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white" alt="Python"/></a>
  <a href="https://docs.astral.sh/uv/"><img src="https://img.shields.io/badge/Entorno-uv-7F52FF" alt="uv"/></a>
  <a href="https://github.com/Textualize/rich"><img src="https://img.shields.io/badge/rich-CLI%20UI-4E9A06" alt="rich"/></a>
  <a href="https://docs.pytest.org/"><img src="https://img.shields.io/badge/tests-pytest-0A9EDC" alt="pytest"/></a>
  <a href="https://docs.astral.sh/ruff/"><img src="https://img.shields.io/badge/lint-ruff-000000" alt="ruff"/></a>
</p>
<hr/>

## 🧰 Tecnologías y entorno
- 🐍 Python 3.x
- 🚀 uv (gestión de entorno y dependencias)
- 🎨 rich (salida de consola enriquecida)
- ✅ pytest (pruebas)
- 🧹 ruff (formato y lint)

## ⚡ Ejecución rápida
- Ejecutar ejercicios:
```bash
python -m src.bloque1.ejercicio_1_refactorizacion_calculadora_imc
```

- Ejecutar pruebas:
```bash
pytest -v
```

- Revisar estilo/lint:
```bash
ruff check .
ruff format .
```

## 📦 Instalación (con uv)
```bash
# Crear entorno virtual
uv venv

# Activar entorno
# PowerShell
. .venv/Scripts/Activate.ps1
# cmd
.venv\Scripts\activate.bat
# Linux/Mac
source .venv/bin/activate

# Instalar dependencias
uv add rich pytest ruff
```

<details>
<summary>Alternativa con pip (opcional)</summary>

```bash
python -m venv .venv
# Activar:
# PowerShell:  . .venv/Scripts/Activate.ps1
# cmd:         .venv\Scripts\activate.bat
# Linux/Mac:   source .venv/bin/activate

pip install rich pytest ruff
```
</details>

## 🗂️ Estructura (resumen)
- src/                  Código fuente
- tests/                Pruebas unitarias (pytest)
- README.md             Documentación

## 🎯 Objetivos
- Practicar conceptos clave del módulo.
- Proveer ejercicios reproducibles con pruebas.
- Mantener calidad con ruff.

## 👤 Autor
Andres Felipe Gonzalez Pedraza  
andresfelipegonzalez5a@gmail.com
