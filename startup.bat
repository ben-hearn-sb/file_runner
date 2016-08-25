@echo off
setlocal enabledelayedexpansion

set CYGWIN=nodosfilewarning

set ROOTDIR=file_runner

set cwd=%~dp0
set splitsub=@
call set tempstring=!cwd:%ROOTDIR%=%splitsub%!
for /f "tokens=1* delims=%splitsub%" %%A in ("%tempstring%") do set CGROOT=%%A & set part2=%%B
for /l %%a in (1,1,100) do if "!CGROOT:~-1!"==" " set CGROOT=!CGROOT:~0,-1!

set PROJECT_APP_DIR=_FILE_RUNNER_
set APPDATA_SOURCE=asset_source_location.p
set STYLE_LIB=%CGROOT%\%ROOTDIR%\style

set PYTHONPATH=C:\Anaconda\Lib\site-packages;%CGROOT%\%ROOTDIR%

python %CGROOT%\%ROOTDIR%\file_runner.py