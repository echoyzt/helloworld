@echo "usage:%0 project"

set "CHECK_OUT=stcmd co -p"
set "project=%1"

for /f "tokens=1,2 delims==" %%i in (project.cfg) do set %%i=%%j

echo %pro203mNew% | find "%project%" >nul && goto l_203mNew
echo %pro205new%  | find "%project%" >nul && goto l_205new
echo %pro20516%   | find "%project%" >nul && goto l_20516
echo %pro206%     | find "%project%" >nul && goto l_206
echo %pro205c%    | find "%project%" >nul && goto l_205c
echo %pro301c%    | find "%project%" >nul && goto l_301c
echo "error project" %project%
goto :End

:l_205new
if "%project%" equ "205/3.3" (
	set "local_dir=D:\SSB500_30\205_SWS\3.3"
    set "starTeam=%ST205new%/3.3"
) else if "%project%" equ "205/3.4" (
	set "local_dir=D:\SSB500_30\205_SWS\3.4"
    set "starTeam=%ST205new%/3.4"
)
set "SIT=%SIT205new%"
set "src=%src205new%"
set vxworks=%vw205new%
set firmware=%fm205new%
goto checkout

:l_203mNew
if "%project%" equ "203M/3.3" (
    set "local_dir=D:\SSB500_10M\203M_SWS\3.3"
    set "starTeam=%ST203mNew%/3.3"
) else if "%project%" equ "203M/3.4" (
	set "local_dir=D:\SSB500_10M\203M_SWS\3.4"
    set "starTeam=%ST203mNew%/3.4"
)
set "SIT=%SIT203mNew%%"
set "src=%src203mNew%"
set "vxworks=%vw203mNew%"
set "firmware=%fm203mNew%"
goto checkout

:l_20516
if "%project%" equ "207999" (
    set "local_dir=D:\207999"
    set "starTeam=%ST20516%/207999"
) else if "%project%" equ "20516/1.x" (
    set "local_dir=D:\20516\1.x"
    set "starTeam=%ST20516%/1.x"
) else if "%project%" equ "20516/2.x" (
    set "local_dir=D:\20516\2.x"
    set "starTeam=%ST20516%/2.x"
)
set "SIT=%SIT20516%"
set "src=%src20516%"
set "vxworks=%vw20516%"
set "firmware=%fm20516%"
goto checkout

:l_206
set "local_dir=D:\%SSB545_10%\1.x"
set "starTeam=%ST206%/1.x"
set "SIT=%SIT206%"
set "src=%src206%"
set "vxworks=%vw206%"
set "firmware=%fm206%"
goto checkout

:l_205c
if "%project%" equ "211999" (
	set "local_dir=D:\211999"
    set "starTeam=%ST205c%/211999"
) else (
    set "local_dir=D:\205C\1.x"
    set "starTeam=%ST205c%/1.x"
)
set "SIT=%SIT205c%"
set "src=%src205c%"
set "vxworks=%vw205c%"
set "firmware=%fm205c%"
goto checkout

:l_301c
set "local_dir=I:\301C\1.x"
set "starTeam=%ST301c%/1.x"
set "SIT=%SIT301c%"
set "src=%src301c%"
set "vxworks=%vw301c%"
set "firmware=%fm301c%"
goto checkout

:checkout
del /s /f /q "%local_dir%\%SIT%"
del /s /f /q "%local_dir%\%src%
%CHECK_OUT% %starTeam%/%vxworks%"  -fp "%local_dir%\%vxworks%" -is -o "*"
%CHECK_OUT% %starTeam%/%firmware%"  -fp "%local_dir%\%firmware%" -is -o "*"
%CHECK_OUT% %starTeam%/%src%" -fp "%local_dir%\%src%" -is -o "*"
goto End

:End