@echo off
chcp 65001 >nul
echo ============================================
echo   🎸 Metallica Archive Bot - Запуск
echo ============================================
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    pause
    exit /b 1
)

REM Создание директорий
if not exist data mkdir data
if not exist logs mkdir logs

echo 🚀 Запуск бота...
echo.
echo Для остановки нажмите Ctrl+C
echo.

python bot\main.py
