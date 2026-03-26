@echo off
setlocal
pushd "%~dp0"

set "PYTHON_EXE=%CD%\.venv_dev_v2_0\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    echo [viewer-launch] Missing required interpreter: .venv_dev_v2_0\Scripts\python.exe
    echo [viewer-launch] Expected bootstrap commands:
    echo   py -3 -m venv .venv_dev_v2_0
    echo   .\.venv_dev_v2_0\Scripts\python.exe -m pip install --upgrade pip panda3d
    popd
    exit /b 1
)

set "PYTHONPATH=%CD%"
"%PYTHON_EXE%" -m viz3d_panda.app %*
set "EXIT_CODE=%ERRORLEVEL%"

popd
exit /b %EXIT_CODE%
