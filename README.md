# MonoCrypt

Бот для мониторинга криптовалюты на сайте bybit

### Базовые команды
- `/set_bybit_keys` — установка API ключей
- `/profile` — информация о портфеле (баланс, активы) | РАБОТАЕТ ТОЛЬКО С КЛЮЧАМИ БЕЗ НИХ НИЧЕГО НЕ БУДЕТ

### Мониторинг цен (без ключей!)
- `/mono BTCUSDT spot 60` — мониторинг цены каждую минуту
- `/check BTCUSDT spot 15:30` — уведомление каждый день в 15:30
- `/check BTCUSDT spot 19:03:2026` — уведомление в указанную дату
- `/check BTCUSDT spot 19:03:2026 15:30` — дата и время

### Управление (тоже без ключей)
- `/list` — список активных задач
- `/stop BTC` — остановить мониторинг
- `/resume BTC` — возобновить
- `/remove BTC` — удалить задачу

## Установка

```bash
git clone https://github.com/HollowWonder/MonoCrypt.git
cd MonoCrypt

python -m venv venv
source venv/bin/activate # Linux/Mac
.venv\Scripts\activate # Windows

pip install -r requirements.txt
```
## Быстрый старт

```bash
python3 -m bot.run
```

## Настройка

В файл .env добавить
```bash
# Telegram Bot Token (получить у @BotFather)
BOT_API = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"

# PostgreSQL (пример для локальной БД)
DATABASE_URL = "postgresql://user:password@localhost:5432/monocrypt"

# Прокси (если Telegram заблокирован)
PROXY = "socks5://user:pass@host:port"
# или удалите PROXY и измените код (см. ниже)

В bot/run.py, замените:
session = AiohttpSession(proxy=PROXY_URL)
bot = Bot(token=BOT_API, session=session)

НА:
bot = Bot(token=BOT_API)
```

## Структура

- `bot/` - Ядро бота
    - `handlers/`
        - `__init__.py`
        - `bybit.py` - bybit хандлер
        - `info.py` - информация (профиль, список и т.д)
        - `registration.py` - регистрация
    - `middlewares/`
        - `dependencies.py` - зависимости для бота
    - `utils/`
        - `bot_manager.py` - управление ботом
        - `bybit_manager.py` - bybit операции
    - `run.py`- запуск бота
- `database/`
    - `handler.py` - манипуляции с базой данных
- `tmp/`
    - `logs/` - логи
- .env - хранилище
- .gitignore
- LICENCE
- config.py - конфиги
- README.md

## Примечание

docker-compose создает новую локальную базу данных. Так что, если вы используйте внешнюю/онлайн базу данных, то используйте обычный dockerfile

## Лицензия

MIT License — используй, модифицируй, распространяй свободно.