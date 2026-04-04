@echo off
setlocal
pushd "%~dp0"

set "PYTHON_EXE=%CD%\.venv_dev_v2_0\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    echo [offline-render] Missing required interpreter: .venv_dev_v2_0\Scripts\python.exe
    popd
    exit /b 1
)

set "PYTHONPATH=%CD%"
"%PYTHON_EXE%" -m viz3d_panda.export_video
set "EXIT_CODE=%ERRORLEVEL%"

popd
exit /b %EXIT_CODE%
