import asyncpg
from typing import Optional, List, Any

from app.api_v1.settings.config import Config

pool: Optional[asyncpg.pool.Pool] = None

async def init_db_pool() -> None:
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(
            f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}",
            min_size=Config.DB_POOL_MIN_SIZE,
            max_size=Config.DB_POOL_MAX_SIZE,
        )

async def close_db_pool() -> None:
    global pool
    if pool is not None:
        await pool.close()
        pool = None

def get_pool() -> asyncpg.pool.Pool:
    if pool is None:
        raise RuntimeError("DB pool is not initialized. Call init_db_pool() first.")
    return pool

async def fetch(query: str, *args: Any) -> List[asyncpg.Record]:
    p = get_pool()
    async with p.acquire() as conn:
        return await conn.fetch(query, *args)

async def execute(query: str, *args: Any) -> str:
    p = get_pool()
    async with p.acquire() as conn:
        return await conn.execute(query, *args)
