from loguru import logger


logger.add('logger/debug.json', format="{time} {level} {message}",
           level="DEBUG", rotation="10:00", compression="zip")

