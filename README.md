# End to End ML Pipeline For Price Prediction

This repository contains an end-to-end example pipeline for house price prediction using the Ames Housing dataset. It includes data ingestion, feature engineering, model training, evaluation, and small helper scripts.

Prerequisites

- Python (development used CPython 3.13). If you experience binary wheel issues on Windows, consider using Python 3.11 or a conda environment (see Troubleshooting below).
- PowerShell (pwsh) for the example commands shown here on Windows.

Quick start (Windows PowerShell)

1) Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
```

2) Install runtime dependencies

```powershell
python -m pip install -r requirements.txt
```

3) (Optional) Install developer dependencies (tests, linters)

```powershell
python -m pip install -r requirements-dev.txt
```

Run tests

```powershell
.\.venv\Scripts\pytest -q
```

Run the pipeline

- To run the example training pipeline:

```powershell
python run_pipeline.py
```

- To run the deployment-related script (if used):

```powershell
python run_deployment.py
```

ZenML integrations (MLflow)

This project can use MLflow for experiment tracking and model deployment. To register the necessary ZenML components, you can run (after activating the venv):

```powershell
# if zenml is installed in the venv, use the zenml CLI directly
.\.venv\Scripts\zenml.exe integration install mlflow -y
.\.venv\Scripts\zenml.exe experiment-tracker register mlflow_tracker --flavor=mlflow
.\.venv\Scripts\zenml.exe model-deployer register mlflow --flavor=mlflow
.\.venv\Scripts\zenml.exe stack register local-mlflow-stack -a default -o default -d mlflow -e mlflow_tracker --set
```

If you prefer to call `zenml` directly from PATH (for example after `pip install zenml` globally or via an activated venv), drop the explicit `.venv\Scripts\` prefix.

Troubleshooting: MLflow / ZenML on Windows

- The `zenml integration install mlflow` command installs MLflow and several binary dependencies. On Windows you may encounter pip build errors for packages that require native compilation (for example `python-rapidjson` or older packages without wheels for very new Python versions).
- Recommended approaches:
	- Use conda (or mamba) to create an environment with a compatible Python and install MLflow and ZenML from conda-forge. Conda often provides prebuilt binaries and avoids compilation issues.

		Example (conda / mamba):

		```powershell
		conda create -n zenml-mlflow python=3.11 -y
		conda activate zenml-mlflow
		conda install -c conda-forge mlflow zenml -y
		```

	- If you must use pip on Windows, run the failing pip install with verbose output to see which package fails and then either:
		- install the required build tools (Microsoft C++ Build Tools) so binary extensions can compile, or
		- install a wheel for the failing package if available, or
		- pin to an older Python version (3.11) that has wheels for the problematic packages.

	- Common quick fix: some ZenML internals import `sqlalchemy-utils`; if ZenML complains about `sqlalchemy_utils` missing, install it manually inside the venv:

		```powershell
		.\.venv\Scripts\python -m pip install sqlalchemy-utils
		```

Notes & next steps

- `requirements.txt` pins a working runtime environment. If you plan to reproduce or extend this project on Windows, the conda path is usually the fastest way to avoid wheel/build tool issues.
- If you want, I can: regenerate a minimal runtime-only `requirements.txt`, add CI to install and run tests, or add a short section describing how to run the EDA notebook headlessly.

