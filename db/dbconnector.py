import asyncio
from functools import wraps, partial
from os import getenv

import psycopg2 as pg
from dataclasses import dataclass
import logging

__all__ = "DBInteractor"

logging.basicConfig(level=logging.INFO)


def make_async(function):
    @wraps(function)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        if not kwargs:
            return await loop.run_in_executor(None, function,  *args)
        return await loop.run_in_executor(None, partial(function, **kwargs), *args)
    return wrapper


class SingletonDBInteractor:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logging.info(f"{cls.__class__.__name__} is created")
        else:
            logging.info(f"{cls.__class__.__name__} is returned")
        return cls._instance


class BaseConnectionState:
    def __init__(self, db_name="postgres", db_user="postgres", db_password="", host="127.0.0.1", port="5432",):
        self.new_state(ClosedConnectionState)
        self.host = host
        self.port = port
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.logger = logging.getLogger(self.__class__.__name__)
        self.conn = None
        self.cur = None

    def new_state(self, state):
        self.__class__ = state

    def conn_open(self):
        raise NotImplementedError

    def conn_close(self):
        raise NotImplementedError

    @make_async
    def select(self, query: str):
        raise NotImplementedError

    @make_async
    def execute(self, query: str, autocommit=False, returning=False):
        raise NotImplementedError

    def __enter__(self):
        raise RuntimeError("Can't use context manager with {self.__class__.__name__}".format(self=self))

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise RuntimeError("Can't use context manager with {self.__class__.__name__}".format(self=self))


class ClosedConnectionState(BaseConnectionState):

    def __enter__(self) -> BaseConnectionState:
        self.logger.debug("Connection to {name} has been opened!".format(name=self.db_name))
        self.conn_open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.debug("Connection to {name} has been closed!".format(name=self.db_name))
        self.conn_close()

    def conn_open(self):
        self.new_state(OpenConnectionState)
        self.conn = pg.connect(host=self.host, port=self.port,
                                dbname=self.db_name, user=self.db_user,
                                password=self.db_password)
        self.cur = self.conn.cursor()
        self.logger.info("Cursor for {name} is opened!".format(name=self.db_name))

    def conn_close(self):
        raise RuntimeError("Already closed!")


class OpenConnectionState(BaseConnectionState):

    def __init__(self, database=None, host=None, port=None, user=None, password=""):
        super().__init__(db_name=database, host=host, port=port, db_user=user, db_password=password)

    def conn_open(self):
        raise RuntimeError("Already open!")

    def conn_close(self):
        self.logger.debug("Cursor for {name} is closed!".format(name=self.db_name))
        self.conn.close()
        self.conn, self.cur = None, None
        self.new_state(ClosedConnectionState)

    @make_async
    def select(self, query: str):
        self.cur.execute(query)
        result = self.cur.fetchall()
        logging.info(f"Query result: {result}")
        return result

    @make_async
    def execute(self, query: str, autocommit=False, returning=False):
        self.cur.execute(query)
        ret = None
        if returning:
            ret = self.cur.fetchall()
        if autocommit:
            self.conn.commit()
        return ret


ChallengeDB = partial(BaseConnectionState, db_user=getenv("DB_USER"),
                             db_name=getenv("DB_NAME"),
                             db_password=getenv("DB_PASSWORD"))



class DBInteractor(SingletonDBInteractor):

    def __init__(self, db_name="postgres", db_user="postgres", db_password="", host="127.0.0.1", port="5432",):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self._conn = None

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
