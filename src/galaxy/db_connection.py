import asyncpg
from .config import config


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

            except Exception as e:
                print(e)

    async def fetch_rows(self, query: str):
        if not self._connection_pool:
            await self.connect()
        else:
            self.con = await self._connection_pool.acquire()
            try:
                
                result = await self.con.fetch(query)
             
                return result
            except Exception as e:
                print(e)
            finally:
                await self._connection_pool.release(self.con)