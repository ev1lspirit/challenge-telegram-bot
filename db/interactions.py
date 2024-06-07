import asyncio
from .dbconnector import DBInteractor
from os import getenv
import logging


async def add_user_to_bot(*, user_id, username):
    loop = asyncio.get_event_loop()
    interactor = DBInteractor(db_password=getenv("DB_PASSWORD"))
    query = f"""INSERT INTO Participant (user_id, username, joined, reputation, completed_challenge) VALUES ({user_id}, '{username}', current_timestamp, 0, 0);"""
    try:
        await loop.run_in_executor(None, interactor.insert, query)
        logging.info(f"Inserted into Participant values ({user_id}, {username}, current_timestamp, 0)")
        return True
    except Exception as exc:
        logging.warning(f"An error occured while inserting into Participant values ({user_id}, {username}, current_timestamp, 0)")
        logging.warning(str(exc))
        return False


async def select_query(query: str):
    loop = asyncio.get_event_loop()
    interactor = DBInteractor(db_password=getenv("DB_PASSWORD"))
    logging.info(f"Executing {query}")
    result = await loop.run_in_executor(None, interactor.select, query)
    logging.info(f"Query result: {result}")
    return result


async def insert(query: str, return_last=False):
    loop = asyncio.get_event_loop()
    interactor = DBInteractor(db_password=getenv("DB_PASSWORD"))
    try:
         res = await loop.run_in_executor(None, interactor.insert, query, return_last)
         logging.info("Insertion successfully completed!")
         return res

    except Exception as exc:
        logging.error(str(exc))
        return None
