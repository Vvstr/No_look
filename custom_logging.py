import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("query_logs")


def log_request(func):
    async def wrapper(*args, **kwargs):
        logger.info(f"Request data: args={args}, kwargs={kwargs}")
        return await func(*args, **kwargs)

    return wrapper
