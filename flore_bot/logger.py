import logging

# Создаём логгер
logger = logging.getLogger("flore_bot")
logger.setLevel(logging.INFO)

# Формат вывода
formatter = logging.Formatter(
    "%(asctime)s — %(levelname)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Консольный вывод
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Лог в файл
file_handler = logging.FileHandler("bot.log", encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
