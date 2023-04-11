mkdir .\build
timeout /t 1
call .\compiler\JackCompiler.bat .\code
timeout /t 1
move .\code\*.vm .\build
call .\compiler\VMEmulator.bat
exit