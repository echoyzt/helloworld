@echo "usage:%0 project"

set "CHECK_OUT=stcmd co -p"
set "project=%1"

for /f "tokens=1,2 delims==" %%i in (project.cfg) do set %%i=%%j

echo %pro205%     | find "%project%" >nul && goto l_205
echo %pro203m%    | find "%project%" >nul && goto l_203m
echo %pro203mNew% | find "%project%" >nul && goto l_203mNew
echo %pro203m_13%  | find "%project%" >nul && goto l_203m_13
echo %pro205new%  | find "%project%" >nul && goto l_205new
echo %pro20516%   | find "%project%" >nul && goto l_20516
echo %pro206%     | find "%project%" >nul && goto l_206
echo %pro205c%    | find "%project%" >nul && goto l_205c
echo %pro509%     | find "%project%" >nul && goto l_509
echo %pro301%     | find "%project%" >nul && goto l_301
echo %pro301c%    | find "%project%" >nul && goto l_301c
echo "error project" %project%
goto :End

:l_205
set "local_dir=C:\%project%\"
set "SIT=%SIT205%"
set "src=%src205%"
set "starTeam=%ST205%"
set "vxworks=%vw205%"
set "firmware=%fm205%"
goto checkout

:l_203m
set "local_dir=C:\%project%\"
set "SIT=%SIT203m%"
set "src=%src203m%"
set "starTeam=%ST203m%"
set "vxworks=%vw203m%"
set "firmware=%fm203m%"
goto checkout

:l_203mNew
set "local_dir=C:\%project%\"
set "SIT=%SIT203mNew%"
set "src=%src203mNew%"
set "starTeam=%ST203mNew%"
set "vxworks=%vw203mNew%"
set "firmware=%fm203mNew%"
goto checkout

:l_203m_13
set "local_dir=C:\%project%\"
set "SIT=%SIT203m_13%"
set "src=%src203m_13%"
set "starTeam=%ST203m_13%"
set "vxworks=%vw203m_13%"
set "firmware=%fm203m_13%"
goto checkout

:l_205new
set "local_dir=C:\%project%\"
set "SIT=%SIT205new%"
set "src=%src205new%"
set "starTeam=%ST205new%"
set "vxworks=%vw205new%"
set "firmware=%fm205new%"
goto checkout

:l_20516
set "local_dir=C:\%project%\"
set "SIT=%SIT20516%"
set "src=%src20516%"
set "starTeam=%ST20516%"
set "vxworks=%vw20516%"
set "firmware=%fm20516%"
goto checkout

:l_206
set "local_dir=C:\%project%\"
set "SIT=%SIT206%"
set "src=%src206%"
set "starTeam=%ST206%"
set "vxworks=%vw206%"
set "firmware=%fm206%"
goto checkout

:l_205c
set "local_dir=C:\%project%\"
set "SIT=%SIT205c%"
set "src=%src205c%"
set "starTeam=%ST205c%"
set "vxworks=%vw205c%"
set "firmware=%fm205c%"
goto checkout

:l_509
set "local_dir=C:\%project%\"
set "SIT=%SIT509%"
set "src=%src509%"
set "starTeam=%ST509%"
set "vxworks=%vw509%"
set "firmware=%fm509%"
goto checkout

:l_301
set "local_dir=I:\SSB300\%project%\default\"
set "SIT=%SITvw301%"
set "src=%srcvw301%"
set "starTeam=%ST301%"
set "vxworks=%vw301%"
set "firmware=%fm301%"
goto checkout

:l_301c
set "local_dir=I:\%project%\"
set "SIT=%SIT301c%"
set "src=%src301c%"
set "starTeam=%ST301c%"
set "vxworks=%vw301c%"
set "firmware=%fm301c%"
goto checkout

:checkout
%CHECK_OUT% %starTeam%/"%project%/SMEE/CI" -fp "%local_dir%SMEE\CI" -is -o "configuration_item.xml"
goto End

:End