import asyncio
import asyncpg

async def test_conn():
    conn = await asyncpg.connect(
        user='postgres',
        password='1234',  # здесь твой пароль
        database='app_db',
        host='localhost',
        port=5432
    )
    print("Connected!")
    await conn.close()

asyncio.run(test_conn())
