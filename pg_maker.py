import pytz

from contextlib import asynccontextmanager
from config_data import config
import asyncpg

dbname = config.DB_NAME
user = config.DB_USER
password = config.DB_PASSWORD
host = config.DB_HOST

desired_timezone = pytz.timezone("Europe/Moscow")


@asynccontextmanager
async def db_connection():
    """Контекстный менеджер для асинхронного подключения к базе данных."""
    conn = await asyncpg.connect(
        database=dbname, user=user, password=password, host=host
    )
    try:
        yield conn
    finally:
        await conn.close()


async def new_table():
    async with db_connection() as conn:
        sql = """CREATE TABLE IF NOT EXISTS public.sublets 
        (
        id SERIAL PRIMARY KEY,
        username VARCHAR,
        user_id VARCHAR,
        city VARCHAR, 
        address VARCHAR, 
        type VARCHAR, 
        description VARCHAR NULL, 
        date_in DATE,
        date_out DATE,
        is_active BOOL DEFAULT TRUE,
        photo1 VARCHAR NULL,
        photo2 VARCHAR NULL,
        photo3 VARCHAR NULL,
        photo4 VARCHAR NULL,
        photo5 VARCHAR NULL,
        photo6 VARCHAR NULL,
        photo7 VARCHAR NULL,
        photo8 VARCHAR NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        await conn.execute(sql)


async def create_users():
    async with db_connection() as conn:
        sql = """
        CREATE TABLE IF NOT EXISTS public.users 
        (
        username VARCHAR,
        user_id VARCHAR,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        await conn.execute(sql)


async def add_user(username, user_id):
    async with db_connection() as conn:
        await create_users()
        sql = """SELECT * FROM public.users WHERE user_id = $1"""
        existing_user = await conn.fetchrow(sql, user_id)
        if existing_user:
            return
        else:
            sql = """
            INSERT INTO public.users
            (username, user_id)
            VALUES ($1, $2);
            """
            await conn.execute(sql, username, user_id)


async def all_users_from_db():
    async with db_connection() as conn:
        sql = """SELECT username, user_id FROM public.users"""
        all_us = await conn.fetch(sql)
        usernames = [
            f"@{record['username']} — {record['user_id']}" for record in all_us
        ]
        formatted_usernames = "\n".join(usernames)
        return formatted_usernames


async def delete_table():
    async with db_connection() as conn:
        await conn.execute("""DROP TABLE public.sublets;""")
        await new_table()
        await conn.execute("""DROP TABLE public.users;""")
        await create_users()


async def new_post(
    username, user_id, city, address, type, date_in, date_out, description, photos
):
    async with db_connection() as conn:
        await new_table()

        photo_values = photos[:8] if photos else [None] * 8
        photo_values += [None] * (8 - len(photo_values))

        sql = """INSERT INTO public.sublets 
        (
        username, 
        user_id, 
        city, 
        address,
        type,
        description,
        date_in, 
        date_out,
        photo1, photo2, photo3, photo4, photo5, photo6, photo7, photo8
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)"""

        await conn.execute(
            sql,
            username,
            user_id,
            city,
            address,
            type,
            description,
            date_in,
            date_out,
            *photo_values,
        )


async def delete_post(post_id):
    async with db_connection() as conn:
        sql = """DELETE FROM public.sublets WHERE id = $1;"""
        await conn.execute(sql, post_id)


async def find_my_sublets(user_id):
    async with db_connection() as conn:
        sql = """SELECT address, id 
                 FROM public.sublets 
                 WHERE user_id = $1"""
        result = await conn.fetch(sql, user_id)
        return result


async def find_all_sublets():
    async with db_connection() as conn:
        sql = """SELECT address, id 
                 FROM public.sublets;"""
        result = await conn.fetch(sql)
        return result


async def type_of_sublet(post_id):
    async with db_connection() as conn:
        sql = """SELECT type 
                 FROM public.sublets 
                 WHERE id = $1"""
        result = await conn.fetchrow(sql, int(post_id))
        return result["type"]


async def status_of_sublet(post_id):
    async with db_connection() as conn:
        sql = """SELECT is_active 
                 FROM public.sublets 
                 WHERE id = $1"""
        result = await conn.fetchrow(sql, int(post_id))
        return result["is_active"]


async def change_post(post_id, parameter_name, parameter):
    async with db_connection() as conn:
        sql = f"""UPDATE public.sublets
                SET {parameter_name} = $1
                WHERE id = $2"""
        result = await conn.execute(sql, parameter, int(post_id))

        rows_affected = result.split()[-1]
        if int(rows_affected) > 0:
            return True
        return False


async def change_dates_pg(date_in, date_out, post_id):
    async with db_connection() as conn:
        sql = """UPDATE public.sublets
                SET date_in = $1, date_out = $2
                WHERE id = $3"""
        await conn.execute(sql, date_in, date_out, post_id)


async def update_photos(post_id, photos):
    async with db_connection() as conn:
        sql = """UPDATE public.sublets
                SET photo1 = NULL,
                    photo2 = NULL,
                    photo3 = NULL,
                    photo4 = NULL,
                    photo5 = NULL,
                    photo6 = NULL,
                    photo7 = NULL,
                    photo8 = NULL
                WHERE id = $1"""
        await conn.execute(sql, post_id)

        sql_update = """UPDATE public.sublets
                        SET photo1 = $1,
                            photo2 = $2,
                            photo3 = $3,
                            photo4 = $4,
                            photo5 = $5,
                            photo6 = $6,
                            photo7 = $7,
                            photo8 = $8
                        WHERE id = $9"""

        photo_values = photos[:8] if photos else [None] * 8
        photo_values += [None] * (8 - len(photo_values))

        await conn.execute(sql_update, *photo_values, post_id)


async def get_active_sublets(
    flag="", city="", date="", year="", month="", post_id="", offset=0, limit=5
):
    async with db_connection() as conn:

        if flag == "by_date":
            sql = """
                    SELECT username, city, date_in, date_out, type, address, description, 
                    photo1, photo2, photo3, photo4, photo5, photo6, photo7, photo8 
                    FROM public.sublets 
                    WHERE city = $1 AND $2 >= date_in AND $3 < date_out AND is_active = True
                    LIMIT $4 OFFSET $5
                """
            result = await conn.fetch(sql, city, date, date, limit, offset)

        elif flag == "by_month":
            sql = f"""
                    SELECT username, city, date_in, date_out, type, address, description, 
                    photo1, photo2, photo3, photo4, photo5, photo6, photo7, photo8 
                    FROM public.sublets 
                    WHERE (
                        (date_in >= DATE '{year}-{month:02d}-01' AND date_in < DATE '{year}-{month:02d}-01' + INTERVAL '1 month')
                        OR
                        (date_out >= DATE '{year}-{month:02d}-01' AND date_out < DATE '{year}-{month:02d}-01' + INTERVAL '1 month')
                        OR
                        (date_in < DATE '{year}-{month:02d}-01' + INTERVAL '1 month' AND date_out > DATE '{year}-{month:02d}-01')
                    )
                    AND city = $1 AND is_active = True
                    LIMIT $2 OFFSET $3;
                """
            result = await conn.fetch(sql, city, limit, offset)

        elif flag == "by_active":
            sql = """
                    SELECT username, city, date_in, date_out, type, address, description, 
                    photo1, photo2, photo3, photo4, photo5, photo6, photo7, photo8 
                    FROM public.sublets 
                    WHERE city = $1 AND is_active = True AND date_out > CURRENT_DATE
                    LIMIT $2 OFFSET $3
                """
            result = await conn.fetch(sql, city, limit, offset)

        elif flag == "all_posts":
            sql = f"""
                    SELECT username, city, date_in, date_out, type, address, description, 
                    photo1, photo2, photo3, photo4, photo5, photo6, photo7, photo8 
                    FROM public.sublets
                    WHERE date_out > CURRENT_DATE AND is_active IS TRUE
                    LIMIT $1 OFFSET $2
                """
            result = await conn.fetch(sql, limit, offset)

        elif flag == "last_post":
            sql = """
                     SELECT username, city, date_in, date_out, type, address, description, 
                           photo1, photo2, photo3, photo4, photo5, photo6, photo7, photo8 
                    FROM public.sublets 
                    ORDER BY created_at DESC 
                    LIMIT 1;
                """
            result = await conn.fetch(sql)

        elif flag == "my_post":
            sql = """
                     SELECT username, city, date_in, date_out, type, address, description, 
                           photo1, photo2, photo3, photo4, photo5, photo6, photo7, photo8 
                    FROM public.sublets 
                    WHERE id = $1
                """
            result = await conn.fetch(sql, post_id)

        all_info_and_photos = result

    sublets = []
    for info_and_photos in all_info_and_photos:
        if info_and_photos:
            username, city, date_in, date_out, type, address, description, *photos = (
                info_and_photos
            )
            f_date_in = date_in.strftime("%d-%m-%Y")
            f_date_out = date_out.strftime("%d-%m-%Y")
            user_info = (
                f"🏠 Город: {city}\n🛌 Тип: {type}\n📬 Адрес: {address or 'Не указан'}\n"
                f"📅 Свободные даты: \n{f_date_in} — {f_date_out}\n\n{description}\n\nОпубликовал: @{username}"
            )
            user_photos = [photo for photo in photos if photo is not None]
            sublet = (user_info, user_photos)
            sublets.append(sublet)

    return sublets
