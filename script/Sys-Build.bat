@echo "usage:%0 project"

set "CHECK_OUT=stcmd co -p"
set "project=%1"
set "label=%2"

for /f "tokens=1,2 delims==" %%i in (project.cfg) do set %%i=%%j

echo %pro203mNew% | find "%project%" >nul && goto l_203mNew
echo %pro205new%  | find "%project%" >nul && goto l_205new
echo %pro20516%   | find "%project%" >nul && goto l_20516
echo %pro206%     | find "%project%" >nul && goto l_206
echo %pro205c%    | find "%project%" >nul && goto l_205c
echo %pro301c%    | find "%project%" >nul && goto l_301c
echo "error project" %project%
goto :End

:l_203mNew
if "%project%" equ "203M/3.3" (
	cd /d D:\SSB500_10M\203M_SWS\3.3
) else if "%project%" equ "203M/3.4" (
	cd /d D:\SSB500_10M\203M_SWS\3.4
)
qbBuild.bat %label%
goto :End

:l_205new
if "%project%" equ "205/3.3" (
	cd /d D:\SSB500_30\205_SWS\3.3
) else if "%project%" equ "205/3.4" (
	cd /d D:\SSB500_30\205_SWS\3.4
)
qbBuild.bat %label%
goto :End

:l_20516
if "%project%" equ "207999" (
	cd /d D:\207999
	build.bat 207999 %label% 203build 203smeebuild
) else if "%project%" equ "20516/1.x" (
	cd /d D:\20516\1.x
	build.bat %label%
) else if "%project%" equ "20516/2.x" (
    cd /d D:\20516\2.x
    build.bat %label%
)
goto :End

:l_206
cd /d D:\SSB545_10\1.x	
build.bat %label%
goto :End

:l_205c
if "%project%" equ "211999" (
	cd /d D:\211999
	build.bat 211999 %label% 203build 203smeebuild
) else (
	cd /d D:\205C\1.x
	build.bat %label%
)
goto :End


:l_301c
cd /d D:\301C\1.x
build.bat %label%
goto :End

:End
