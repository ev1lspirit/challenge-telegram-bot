import psycopg2 as pg
from dataclasses import dataclass
import logging

__all__ = "DBInteractor"

import redis


class SingletonDBInteractor:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logging.info(f"{cls.__class__.__name__} is created")
        else:
            logging.info(f"{cls.__class__.__name__} is returned")
        return cls._instance


class DBInteractor(SingletonDBInteractor):

    def __init__(self, db_name="postgres", db_user="postgres", db_password="", host="127.0.0.1", port="5432",):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password

    def select(self, query: str):
        assert isinstance(query, str) and query.lower().startswith("select"), "Query must be a str and start with select"
        with pg.connect(host=self.host, port=self.port,
                        dbname=self.db_name, user=self.db_user,
                        password=self.db_password) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return cursor.fetchall()

    def insert(self, query: str, return_last=False):
        last = True
        with pg.connect(host=self.host, port=self.port,
                        dbname=self.db_name, user=self.db_user,
                        password=self.db_password) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            if return_last:
                last = cursor.fetchone()[0]
        return last
