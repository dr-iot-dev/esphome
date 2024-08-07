## Set up ESPHome dev environment

# Enable strict error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Change to the parent directory of the script's location
cd (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "..")

$location = "venv\Scripts\Activate.ps1"
if (-not $env:DEVCONTAINER -and -not $env:VIRTUAL_ENV -and -not $env:ESPHOME_NO_VENV) {
    python -m venv venv
    if (Test-Path "venv\Scripts\Activate.ps1") {
        $location = "venv\Scripts\Activate.ps1"
    }
    . $location
}

pip install -r requirements.txt -r requirements_optional.txt -r requirements_test.txt -r requirements_dev.txt
pip install setuptools wheel
pip install -e ".[dev,test,displays]" --config-settings editable_mode=compat

pre-commit install

python script/platformio_install_deps.py platformio.ini --libraries --tools --platforms

Write-Output ""
Write-Output ""
Write-Output "Virtual environment created. Run '. $location' to use it."