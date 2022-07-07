import asyncpg
from .config import config
import logging


class Database:
    def __init__(self):
        self.db_params = dict(config.items("RAW_DATA"))
        self._cursor = None
        self._connection_pool = None
        self.con = None

    async def connect(self):
        if not self._connection_pool:
            try:
                self._connection_pool = await asyncpg.create_pool(
                    min_size=1,
                    max_size=10,
                    **self.db_params
                )
                logging.debug("Connection pooling has been established")

            except Exception as e:
                logging.error(e)

    async def get_db_conn_from_pool(self):
        try:
            db_con = await self._connection_pool.acquire()
            return db_con
        except Exception as ex :
            logging.error(ex)
            raise ex


    async def fetch_rows(self, query: str):
        logging.debug("fetch rows has been called")
        if not self._connection_pool:
            await self.connect()
        else:
            self.con = await self._connection_pool.acquire()
            try:
                result = await self.con.fetch(query)
                return result
            except Exception as e:
                logging.error(e)
            finally:
                await self._connection_pool.release(self.con)