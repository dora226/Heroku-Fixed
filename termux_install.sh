#!/data/data/com.termux/files/usr/bin/bash
echo "Установка Heroku на Termux..."
pkg update -y && pkg upgrade -y
pkg install python git rust binutils -y

cd ~
git clone https://github.com/dora226/Heroku-Fixed
cd Heroku-Fixed

pip install --upgrade pip setuptools wheel --break-system-packages

# Пробуем сначала бинарные колеса
pip install --prefer-binary -r requirements-termux.txt --break-system-packages || {
    echo "Бинарные колеса не нашли, пробуем собрать..."
    pip install -r requirements-termux.txt --break-system-packages
}

echo ""
echo "Установка завершена! Запусти бота:"
echo "python3 -m heroku --no-web"
