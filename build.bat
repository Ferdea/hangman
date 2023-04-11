echo "" | python .\compiler\spritesload.py ".\\sprites\\"
timeout /t 1
move .\sprites\*.jack .\code
call .\compiler\JackCompiler.bat .\code
timeout /t 1
move .\code\*.vm .\build
call .\compiler\VMEmulator.bat
exit