from os import getenv

from db import DBInteractor
import logging


def is_user_registered(user_id: int, username: str) -> bool:
    interactor = DBInteractor(db_password=getenv("DB_PASSWORD"))
    if not interactor.select("select {} from participant;".format(user_id)):
        logging.info("User @{username} with id {user_id} is not a participant".format(username=username, user_id=user_id))
        return False
    return True
