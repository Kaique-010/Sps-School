@echo off
echo ========================================
echo  Configurando Variaveis de Ambiente Android
echo ========================================
echo.

REM Detectar o caminho do Android SDK
set "ANDROID_SDK_ROOT=%LOCALAPPDATA%\Android\Sdk"
set "ANDROID_HOME=%LOCALAPPDATA%\Android\Sdk"

echo Verificando se o Android SDK existe...
if not exist "%ANDROID_SDK_ROOT%" (
    echo ERRO: Android SDK nao encontrado em %ANDROID_SDK_ROOT%
    echo.
    echo Por favor, verifique se o Android Studio foi instalado corretamente.
    echo O caminho padrao e: %LOCALAPPDATA%\Android\Sdk
    echo.
    pause
    exit /b 1
)

echo Android SDK encontrado em: %ANDROID_SDK_ROOT%
echo.

echo Configurando variaveis de ambiente...

REM Configurar ANDROID_HOME
setx ANDROID_HOME "%ANDROID_HOME%" >nul
echo ✓ ANDROID_HOME configurado: %ANDROID_HOME%

REM Configurar ANDROID_SDK_ROOT
setx ANDROID_SDK_ROOT "%ANDROID_SDK_ROOT%" >nul
echo ✓ ANDROID_SDK_ROOT configurado: %ANDROID_SDK_ROOT%

REM Adicionar ferramentas do Android ao PATH
set "ANDROID_TOOLS=%ANDROID_SDK_ROOT%\tools"
set "ANDROID_PLATFORM_TOOLS=%ANDROID_SDK_ROOT%\platform-tools"
set "ANDROID_CMDLINE_TOOLS=%ANDROID_SDK_ROOT%\cmdline-tools\latest\bin"

REM Obter PATH atual
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "CURRENT_PATH=%%b"

REM Verificar se os caminhos ja estao no PATH
echo %CURRENT_PATH% | find "%ANDROID_PLATFORM_TOOLS%" >nul
if errorlevel 1 (
    setx PATH "%CURRENT_PATH%;%ANDROID_PLATFORM_TOOLS%" >nul
    echo ✓ platform-tools adicionado ao PATH
) else (
    echo ✓ platform-tools ja esta no PATH
)

echo %CURRENT_PATH% | find "%ANDROID_CMDLINE_TOOLS%" >nul
if errorlevel 1 (
    setx PATH "%CURRENT_PATH%;%ANDROID_CMDLINE_TOOLS%" >nul
    echo ✓ cmdline-tools adicionado ao PATH
) else (
    echo ✓ cmdline-tools ja esta no PATH
)

echo.
echo ========================================
echo  Configuracao Concluida!
echo ========================================
echo.
echo IMPORTANTE: Feche e reabra o terminal/IDE para aplicar as mudancas.
echo.
echo Proximos passos:
echo 1. Feche este terminal
echo 2. Abra um novo terminal
echo 3. Execute: flutter doctor
echo 4. Execute: flutter doctor --android-licenses
echo.
pause