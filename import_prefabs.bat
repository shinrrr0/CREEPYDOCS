@echo off
REM ====================================================================
REM import_prefabs.bat
REM
REM Scans story_prefabs/ and images_prefabs/ folders next to this file
REM and imports their contents into the DB. Idempotent - safe to run
REM repeatedly. Pass --force as the first argument to replace existing
REM rows that match by title (stories) or filename (gallery images).
REM
REM Usage:
REM     import_prefabs.bat
REM     import_prefabs.bat --force
REM
REM This is also invoked automatically by app.py when you run
REM "python app.py" - drop new content into the prefab folders and
REM restart the dev server.
REM ====================================================================

setlocal enableextensions

REM Always operate from the directory this .bat lives in.
pushd "%~dp0"

REM ---- Locate and activate the virtual environment ------------------
REM Tries the conventional locations; if none are found we still try
REM to run flask directly (it might be on PATH).
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else if exist "..\.venv\Scripts\activate.bat" (
    call "..\.venv\Scripts\activate.bat"
) else if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
)

REM ---- Configure Flask ----------------------------------------------
set "FLASK_APP=app:create_app"

REM Sentinel that prevents app.py from re-launching this batch file
REM when "flask import-prefabs" is run from inside it (avoids recursion).
set "CREEPYDOCS_AUTOIMPORT_RUNNING=1"

REM ---- Run ----------------------------------------------------------
echo [import_prefabs] running flask import-prefabs %*
flask import-prefabs %*
set "EXITCODE=%ERRORLEVEL%"

popd
endlocal & exit /b %EXITCODE%
