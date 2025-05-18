from loguru import logger


def setup_logger():
    logger.add("logs/bot.log", rotation="1 week", encoding="utf-8", enqueue=True)
    logger.info("🚀 Логгер инициализирован")
