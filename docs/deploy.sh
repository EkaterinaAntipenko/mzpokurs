#!/usr/bin/env bash
# Заливка сайта на Beget — http://mzpokurs.ekaterxo.beget.tech
# Собирает страницы (docs/build.py) и копирует *.html, favicon.ico и assets/ в mzpokurs/public_html
# по SSH-ключу ~/.ssh/beget_mzpokurs_ed25519, без пароля. Публичная часть ключа лежит
# на сервере в ~/.ssh/authorized_keys; чтобы закрыть доступ, удалите там эту строку.
# На сервере файлы только добавляются и перезаписываются: удалённые из проекта остаются.
# Запуск из корня проекта: bash docs/deploy.sh
set -euo pipefail
cd "$(dirname "$0")/.."

KEY="$HOME/.ssh/beget_mzpokurs_ed25519"
HOST="ekaterxo@ekaterxo.beget.tech"
DEST="mzpokurs/public_html"

PYTHONIOENCODING=utf-8 python docs/build.py > /dev/null
tar czf - *.html favicon.ico assets \
  | ssh -i "$KEY" -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new "$HOST" \
      "cd $DEST && tar xzf - && echo \"залито: \$(ls *.html | wc -l) страниц\""
