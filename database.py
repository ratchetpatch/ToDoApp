import sqlite3


def initialize_db():
    try:
        connection = sqlite3.connect("main.db")
        cursor = connection.cursor()
        create_tables(cursor)
        return (connection, cursor)
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None, None


def create_tables(cursor):
    current_task_list = """
    CREATE TABLE IF NOT EXISTS current_task_list(
        id_num INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        first_step TEXT,
        second_step TEXT,
        third_step TEXT,
        task_date TEXT,
        repeat_toggle INTEGER,
        interval_index INTEGER
    )
    """

    cursor.execute(current_task_list)

    repeat_task_list = """
    CREATE TABLE IF NOT EXISTS repeat_task_list(
        id_num INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        first_step TEXT,
        second_step TEXT,
        third_step TEXT,
        task_date TEXT,
        repeat_toggle INTEGER,
        interval_index INTEGER
    )
    """

    cursor.execute(repeat_task_list)

    item_list = """
    CREATE TABLE IF NOT EXISTS item_list(
        id_num INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        quantity TEXT,
        item_location TEXT,
        interval_index INTEGER
    )
    """

    cursor.execute(item_list)

    stats_screen = """
    CREATE TABLE IF NOT EXISTS stats_screen(
        id_num INTEGER PRIMARY KEY AUTOINCREMENT,
        current_level INTEGER,
        current_xp INTEGER,
        start_level INTEGER,
        next_level INTEGER
    )
    """

    cursor.execute(stats_screen)

    completed_tasks = """
    CREATE TABLE IF NOT EXISTS completed_tasks(
        id_num INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL UNIQUE,
        count INTEGER
    )
    """

    cursor.execute(completed_tasks)

    purchased_items = """
    CREATE TABLE IF NOT EXISTS purchased_items(
        id_num INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL UNIQUE,
        count INTEGER
    )
    """

    cursor.execute(purchased_items)

    item_locations = """
    CREATE TABLE IF NOT EXISTS item_locations(
        id_num INTEGER PRIMARY KEY AUTOINCREMENT,
        location TEXT NOT NULL UNIQUE
    )
    """

    cursor.execute(item_locations)


def save_task_list(cursor, task_list, list_name):
    sql = f"""
    INSERT INTO {list_name} (title, first_step, second_step, third_step, task_date, repeat_toggle, interval_index) VALUES (?,?,?,?,?,?,?);
    """

    data_list = [
        (
            task.title,
            task.first_step,
            task.second_step,
            task.third_step,
            task.start_date,
            task.repeat_toggle,
            task.interval_index,
        )
        for task in task_list
    ]

    cursor.executemany(sql, data_list)
    cursor.connection.commit()


def save_item_list(cursor, item_list):
    sql = """
    INSERT INTO item_list (title, quantity, item_location, interval_index) VALUES (?,?,?,?);
    """

    data_list = [
        (
            item.title,
            item.quantity,
            item.item_location,
            item.interval_index,
        )
        for item in item_list
    ]

    cursor.executemany(sql, data_list)
    cursor.connection.commit()


def save_stats_data(cursor, stats_screen):
    sql = """
    INSERT INTO stats_screen (current_level, current_xp, start_level, next_level) VALUES (?,?,?,?);
    """

    data_list = (
        stats_screen.current_level,
        stats_screen.current_xp,
        stats_screen.start_level,
        stats_screen.next_level,
    )

    cursor.execute(sql, data_list)
    cursor.connection.commit()


def save_stats_maps(cursor, task_map, map_name):
    sql = f"""
    INSERT INTO {map_name} (title, count) VALUES (?,?);
    """

    data_list = [(title, count) for title, count in task_map.items()]

    cursor.executemany(sql, data_list)
    cursor.connection.commit()


def save_item_locations(cursor, locations_set):
    sql = """
    INSERT INTO item_locations (location) VALUES (?);
    """

    data_list = [(location,) for location in locations_set]

    cursor.executemany(sql, data_list)
    cursor.connection.commit()


def close_db(connection, cursor):
    if cursor:
        cursor.close()
    if connection:
        connection.commit()
        connection.close()


def get_task_list(cursor, list_name):
    cursor.execute(
        f"SELECT id_num, title, first_step, second_step, third_step, task_date, repeat_toggle, interval_index FROM {list_name}"
    )
    rows = cursor.fetchall()

    return rows


def get_item_list(cursor):
    cursor.execute(
        "SELECT id_num, title, quantity, item_location, interval_index FROM item_list"
    )
    rows = cursor.fetchall()

    return rows


def get_stats_data(cursor):
    cursor.execute(
        "SELECT current_level, current_xp, start_level, next_level FROM stats_screen"
    )
    row = cursor.fetchall()

    return row


def get_stats_maps(cursor, table_name):
    cursor.execute(f"SELECT title, count FROM {table_name}")
    rows = cursor.fetchall()

    return rows


def get_item_locations(cursor):
    cursor.execute(f"SELECT location FROM item_locations")
    rows = cursor.fetchall()

    return [row[0] for row in rows]
