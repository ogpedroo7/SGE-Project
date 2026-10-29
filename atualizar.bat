@echo off
cd /d "%~dp0"

echo.
echo === Salvando alteracoes do SGE ===
git add .

git diff --cached --quiet
if %errorlevel%==0 (
    echo Nenhuma alteracao nova para salvar.
    pause
    exit /b 0
)

git commit -m "Atualizacao do SGE"
if errorlevel 1 (
    echo Erro ao criar o commit.
    pause
    exit /b 1
)

git push
if errorlevel 1 (
    echo Erro ao enviar para o GitHub.
    pause
    exit /b 1
)

echo.
echo Projeto atualizado no GitHub com sucesso!
pause
