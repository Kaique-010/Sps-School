@echo off
echo ========================================
echo  Verificando Configuracao Android
echo ========================================
echo.

echo Verificando variaveis de ambiente...
echo ANDROID_HOME: %ANDROID_HOME%
echo ANDROID_SDK_ROOT: %ANDROID_SDK_ROOT%
echo.

echo Verificando se os diretorios existem...
if exist "%ANDROID_HOME%" (
    echo ✓ ANDROID_HOME existe
) else (
    echo ✗ ANDROID_HOME nao existe
)

if exist "%ANDROID_HOME%\platform-tools" (
    echo ✓ platform-tools existe
) else (
    echo ✗ platform-tools nao existe
)

if exist "%ANDROID_HOME%\cmdline-tools" (
    echo ✓ cmdline-tools existe
) else (
    echo ✗ cmdline-tools nao existe - pode precisar instalar via Android Studio
)

echo.
echo Testando comandos...

echo Testando adb...
adb version >nul 2>&1
if errorlevel 1 (
    echo ✗ adb nao encontrado no PATH
) else (
    echo ✓ adb funcionando
    adb version
)

echo.
echo Executando flutter doctor...
flutter doctor

echo.
echo ========================================
echo  Verificacao Concluida!
echo ========================================
pause