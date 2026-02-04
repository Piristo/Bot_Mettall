@echo off
chcp 65001 >nul
echo ============================================
echo   🎸 Metallica Archive Bot - Установка
echo ============================================
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo.
    echo Пожалуйста, установите Python 3.11+ с сайта:
    echo https://www.python.org/downloads/
    echo.
    echo После установки добавьте Python в PATH
    echo.
    pause
    exit /b 1
)

echo ✅ Python найден
echo.

REM Создание директорий
if not exist data mkdir data
if not exist logs mkdir logs

echo 📦 Установка зависимостей...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Ошибка установки зависимостей!
    pause
    exit /b 1
)

echo.
echo ✅ Установка завершена!
echo.
echo 📝 Следующие шаги:
echo 1. Откройте файл .env и добавьте ваши токены
echo 2. Запустите: python bot\main.py
echo.
pause
