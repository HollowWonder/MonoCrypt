import psycopg

QUERIES: dict[str, str] = {
    'profiles': """create table if not exists profiles (
        id bigint primary key,
        name text not null,
        bybit_api text,
        bybit_secret_key text
    )""",
    'admins': """create table if not exists admins (
        id bigint primary key,
        foreign key (id) references profiles(id) on delete cascade
    )"""
}

ALLOWED_COLUMNS: list[str] = ['bybit_api', 'bybit_secret_key']

async def db_init(conn: psycopg.AsyncConnection) -> None:
    """ creating all necessary tables """
    async with conn.cursor() as cursor:
        for query in QUERIES.values():
            await cursor.execute(query=query)
    await conn.commit()

async def add_user(conn: psycopg.AsyncConnection, uid: int, name: str, bybit_api: str, bybit_secret_key: str) -> None:
    """ adding user in database 
    
    args:
        uid: user id
        nameL username
        bybit_api: api of bybit
        bybit_secret_key: api secret key
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("insert into profiles (id, name, bybit_api, bybit_secret_key) values (%s, %s, %s, %s)", (uid, name, bybit_api, bybit_secret_key))
        await conn.commit()
    except psycopg.errors.UniqueViolation:
        # raise psycopg.errors.UniqueViolation("this user already in system")
        await conn.rollback()
        return None

async def change_userdata(conn: psycopg.AsyncConnection, uid: int, column: str, value: str) -> None:
    """ changing data of user
    
    args:
        uid: user id
        column: name of allowed to change column
        value: new value
    """
    if column not in ALLOWED_COLUMNS:
        raise ValueError(f'column {column} is not allowed to replace')

    async with conn.cursor() as cursor:
        await cursor.execute(f"update profiles set {column} = %s where id = %s", (value, uid))
    await conn.commit()

async def rm_user(conn: psycopg.AsyncConnection, uid: int, user_type: str = 'user') -> None:
    """ remove user from database 
    args:
        user_type: user/admin
    """
    types: list[str] = ['user', 'admin']
    if user_type not in types:
        raise ValueError(f'wrong user type, must be one of {types}')
    
    async with conn.cursor() as cursor:
        await cursor.execute("delete from profiles where id = %s", (uid,))
    await conn.commit()

async def add_admin(conn: psycopg.AsyncConnection, nauid: int) -> None:
    """ adding new admin user id (nauid) in database"""
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("insert into admins (id) values (%s)", (nauid,))
        await conn.commit()
    except psycopg.errors.UniqueViolation:
        # raise psycopg.errors.UniqueViolation("this user already in system")
        await conn.rollback()
        return None

async def check_user(conn: psycopg.AsyncConnection, uid: int) -> bool:
    """ checking user in system or not """
    async with conn.cursor() as cursor:
        await cursor.execute("select id from profiles where id = %s", (uid,))
        user: str | None = await cursor.fetchone()
    check: bool = True if user else False
    return check

async def get_user_data(conn: psycopg.AsyncConnection, uid: int) -> dict[str, str]:
    """ gettong data like bybit_api from database """
    async with conn.cursor() as cursor:
        await cursor.execute("select * from profiles where id = %s", (uid,))
        data = await cursor.fetchone()
    print(data)
    return {
        'bybit_api': data[2],
        'bybit_secret_key': data[3]
    }
