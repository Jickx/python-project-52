#!/usr/bin/env bash
set -euo pipefail

# скачиваем uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"

# здесь добавьте все необходимые команды для установки вашего проекта
# команду установки зависимостей, сборки статики, применения миграций и другие
uv sync
uv run python manage.py compilemessages
uv run python manage.py collectstatic --noinput
uv run python manage.py migrate
