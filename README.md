# End to End ML Pipeline For Price Prediction using ZenML and  Mlflow

This project includes a pinned `requirements.txt` that reproduces the working virtual environment used during development.

The steps below recreate the same environment on Windows (PowerShell / pwsh). They assume you have a compatible Python interpreter installed (this environment was created with CPython 3.13 on Windows x86_64). If you prefer Python 3.11 or conda, see the notes below.

1. Create a venv and upgrade packaging tools

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip setuptools wheel
```

2. Install pinned dependencies

```powershell
.\.venv\Scripts\python -m pip install -r requirements.txt
```

3. Verify the environment

```powershell
.\.venv\Scripts\python -m pip check
.\.venv\Scripts\python -m pip freeze > installed-freeze.txt
```

If `pip check` reports no broken requirements, the environment matches the pinned set.

Notes & alternatives

- Python version: This repository's `requirements.txt` was produced on CPython 3.13 (Windows). If you need to match older, exact upstream pins, consider using Python 3.11 and recreating a new venv with that interpreter.

- Using conda/mamba: For the scientific stack (numpy/scipy/matplotlib/statsmodels), `conda` or `mamba` with `conda-forge` often provides a smoother experience on Windows because it ships binary packages for many compiled dependencies. Example (optional):

```powershell
mamba create -n price-pred python=3.13
mamba activate price-pred
mamba install --file requirements.txt -c conda-forge
```

- If you want flexible (minimum) constraints instead of pinned exact versions, keep a separate `requirements-min.txt` that lists minima (e.g. `numpy>=2.3.4`) and use it for future upgrades.

- Add `.venv/` to `.gitignore` before committing the virtualenv to the repo.

Contact / debugging

If installation fails on your machine, copy the failing pip output and open an issue (or paste it here). Common fixes: upgrade pip (`pip install -U pip`), use `--prefer-binary` when pip is trying to build from source, or use conda for compiled packages.
