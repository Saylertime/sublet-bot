from config_data import config
import psycopg2
import pytz

dbname = config.DB_NAME
user = config.DB_USER
password = config.DB_PASSWORD
host = config.DB_HOST

desired_timezone = pytz.timezone('Europe/Moscow')

def connect_to_db():
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
    cursor = conn.cursor()
    conn.autocommit = True
    return conn, cursor

def close_db_connection(conn, cursor):
    cursor.close()
    conn.close()


def new_table():
    conn, cursor = connect_to_db()

    sql = """CREATE TABLE IF NOT EXISTS public.sublets 
    (
    id SERIAL PRIMARY KEY,
    username VARCHAR, 
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
    cursor.execute(sql)
    close_db_connection(conn, cursor)


def create_users():
    conn, cursor = connect_to_db()

    sql = """CREATE TABLE IF NOT EXISTS public.users 
    (
    username VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(sql)
    close_db_connection(conn, cursor)

def add_user(username):
    conn, cursor = connect_to_db()
    create_users()
    cursor.execute('''SELECT * FROM public.users WHERE username = %s''', (username,))
    existing_user = cursor.fetchone()
    if existing_user:
        return
    else:
        sql = """INSERT INTO public.users 
    (username)
    VALUES (%s);
        """
        cursor.execute(sql, (username,))
    close_db_connection(conn, cursor)

def all_users_from_db():
    conn, cursor = connect_to_db()
    cursor.execute('''SELECT username FROM public.users''')
    all_us = cursor.fetchall()
    all_users = [i for i in all_us]
    close_db_connection(conn, cursor)
    return all_users


def delete_table():
    conn, cursor = connect_to_db()
    cursor.execute("""DROP TABLE public.sublets;""")
    new_table()
    close_db_connection(conn, cursor)


def new_post(username, city, address, type, date_in, date_out, description, **photos):
    conn, cursor = connect_to_db()
    new_table()

    photo_values = [None] * 8
    for key, value in photos.items():
        index = int(key.replace('photo', '')) - 1
        photo_values[index] = value

    sql = """INSERT INTO public.sublets 
    (
    username, 
    city, 
    address,
    type,
    description,
    date_in, 
    date_out,
    photo1, photo2, photo3, photo4, photo5, photo6, photo7, photo8
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    cursor.execute(sql, (username, city, address, type, description, date_in, date_out, *photo_values))
    close_db_connection(conn, cursor)


def delete_post(post_id):
    conn, cursor = connect_to_db()

    sql = """DELETE FROM public.sublets WHERE id = %s;"""

    cursor.execute(sql, (post_id,))
    close_db_connection(conn, cursor)

def find_my_sublets(username):
    conn, cursor = connect_to_db()

    sql = """SELECT address, id 
             FROM public.sublets 
             WHERE username = %s"""

    cursor.execute(sql, (username,))
    result = cursor.fetchall()

    close_db_connection(conn, cursor)
    return result


def type_of_sublet(post_id):
    conn, cursor = connect_to_db()

    sql = """SELECT type 
             FROM public.sublets 
             WHERE id = %s"""

    cursor.execute(sql, (post_id,))
    result = cursor.fetchone()

    close_db_connection(conn, cursor)
    return result


def status_of_sublet(post_id):
    conn, cursor = connect_to_db()

    sql = """SELECT is_active 
             FROM public.sublets 
             WHERE id = %s"""

    cursor.execute(sql, (post_id,))
    result = cursor.fetchone()

    close_db_connection(conn, cursor)
    return result


def change_post(post_id, parameter_name, parameter):
    conn, cursor = connect_to_db()

    sql = f"""UPDATE public.sublets
            SET {parameter_name} = %s
            WHERE id = %s"""
    cursor.execute(sql, (parameter, post_id))
    close_db_connection(conn, cursor)


def change_dates_pg(post_id, date_in, date_out):
    conn, cursor = connect_to_db()

    sql = """UPDATE public.sublets
            SET date_in = %s, date_out = %s
            WHERE id = %s"""
    cursor.execute(sql, (date_in, date_out, post_id))
    conn.commit()
    close_db_connection(conn, cursor)


def update_photos(post_id, photos):
    conn, cursor = connect_to_db()

    sql = """UPDATE public.sublets
            SET photo1 = NULL,
                photo2 = NULL,
                photo3 = NULL,
                photo4 = NULL,
                photo5 = NULL,
                photo6 = NULL,
                photo7 = NULL,
                photo8 = NULL
            WHERE id = %s"""
    cursor.execute(sql, (post_id,))

    sql_update = """UPDATE public.sublets
                    SET photo1 = %s,
                        photo2 = %s,
                        photo3 = %s,
                        photo4 = %s,
                        photo5 = %s,
                        photo6 = %s,
                        photo7 = %s,
                        photo8 = %s
                    WHERE id = %s"""

    photo_values = [None] * 8
    for i, photo_path in enumerate(photos):
        photo_values[i] = photo_path
    photo_values.append(post_id)
    cursor.execute(sql_update, photo_values)

    close_db_connection(conn, cursor)


def get_user_info_and_photos(post_id):
    conn, cursor = connect_to_db()

    sql = """SELECT username, city, date_in, date_out, type, address, description, 
             photo1, photo2, photo3, photo4, photo5, photo6, photo7, photo8 
             FROM public.sublets 
             WHERE id = %s"""

    cursor.execute(sql, (post_id,))
    info_and_photos = cursor.fetchone()

    if info_and_photos:
        username, city, date_in, date_out, type, address, description, *photos = info_and_photos
        f_date_in = date_in.strftime("%d-%m-%Y")
        f_date_out = date_out.strftime("%d-%m-%Y")
        user_info = f"🏠 Город: {city}\n🛌 Тип: {type}\n📬 Адрес: {address}\n" \
                    f"📅 Свободные даты: \n{f_date_in} — {f_date_out}\n\n{description}\n\nОпубликовал: @{username}"
        user_photos = [photo for photo in photos if photo is not None]
    else:
        user_info = "Информация о пользователе не найдена"
        user_photos = []

    close_db_connection(conn, cursor)
    return user_info, user_photos


def get_active_sublets(flag='', city='', date='', year='', month='', offset=0, limit=5):
    conn, cursor = connect_to_db()

    if flag == 'by_date':
        sql = """
                SELECT username, city, date_in, date_out, type, address, description, 
                photo1, photo2, photo3, photo4, photo5, photo6, photo7, photo8 
                 FROM public.sublets 
                 WHERE city = %s AND %s >= date_in AND %s < date_out AND is_active = True
                 LIMIT %s OFFSET %s
            """
        cursor.execute(sql, (city, date, date, limit, offset))

    elif flag == 'by_month':
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
                AND city = %s AND is_active = True
                LIMIT %s OFFSET %s;
            """
        cursor.execute(sql, (city, limit, offset))

    elif flag == 'by_active':
        sql = f"""
                SELECT username, city, date_in, date_out, type, address, description, 
                photo1, photo2, photo3, photo4, photo5, photo6, photo7, photo8 
                FROM public.sublets 
                WHERE city = %s AND is_active = True AND date_out > CURRENT_DATE
                LIMIT %s OFFSET %s
            """
        cursor.execute(sql, (city, limit, offset))

    elif flag == 'all_posts':
        sql = f"""
                SELECT username, city, date_in, date_out, type, address, description, 
                photo1, photo2, photo3, photo4, photo5, photo6, photo7, photo8 
                FROM public.sublets
                WHERE date_out > CURRENT_DATE
                LIMIT %s OFFSET %s
            """
        cursor.execute(sql, (limit, offset))

    elif flag == 'last_post':
        sql = """
                 SELECT username, city, date_in, date_out, type, address, description, 
                       photo1, photo2, photo3, photo4, photo5, photo6, photo7, photo8 
                FROM public.sublets 
                ORDER BY created_at DESC 
                LIMIT 1;
            """
        cursor.execute(sql)

    all_info_and_photos = cursor.fetchall()

    sublets = []
    for info_and_photos in all_info_and_photos:
        if info_and_photos:
            username, city, date_in, date_out, type, address, description, *photos = info_and_photos
            f_date_in = date_in.strftime("%d-%m-%Y")
            f_date_out = date_out.strftime("%d-%m-%Y")
            user_info = f"🏠 Город: {city}\n🛌 Тип: {type}\n📬 Адрес: {address}\n" \
                        f"📅 Свободные даты: \n{f_date_in} — {f_date_out}\n\n{description}\n\nОпубликовал: @{username}"
            user_photos = [photo for photo in photos if photo is not None]
            sublet = (user_info, user_photos)
            sublets.append(sublet)

    return sublets
