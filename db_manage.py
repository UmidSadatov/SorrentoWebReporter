import sqlite3
import locale

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


def get_general_name(unique_name):
    db_con = sqlite3.connect('reports.db')
    db_con.row_factory = sqlite3.Row
    cursor = db_con.cursor()
    # try:
    while unique_name[-1] == ' ':
        unique_name = unique_name[:-1]
    # except TypeError:
    #     print(f'TypeError: {unique_name}')

    cursor.execute(
        f"""SELECT name 
        FROM General_Names INNER JOIN All_names 
        ON General_Names.id = All_names.general_id 
        WHERE unique_name = '{unique_name}'"""
    )

    result = cursor.fetchone()
    db_con.commit()
    return result[0] if result is not None else None


def get_general_region(unique_region: str):
    db_con = sqlite3.connect('reports.db')
    db_con.row_factory = sqlite3.Row
    cursor = db_con.cursor()

    try:
        unique_region = unique_region.replace('\n', '')
    except AttributeError:
        pass

    if unique_region == 0:
        return None

    try:
        unique_region = unique_region.replace('\t', '')
    except AttributeError:
        pass

    try:
        while unique_region[-1] == ' ':
            unique_region = unique_region[:-1]
        while unique_region[0] == ' ':
            unique_region = unique_region[1:]
    except:
        pass


    # unique_region = unique_region.replace("'", "\'")

    cursor.execute(
        f"""SELECT region 
        FROM General_Regions INNER JOIN All_Regions 
        ON General_Regions.id = All_Regions.general_id 
        WHERE unique_region = (?)""",
        (unique_region,)
    )

    result = cursor.fetchone()
    db_con.commit()
    return result[0] if result is not None else None


def get_general_regions() -> list:
    db_con = sqlite3.connect('reports.db')
    db_con.row_factory = sqlite3.Row
    cursor = db_con.cursor()

    cursor.execute(
        f"""SELECT region FROM General_Regions"""
    )

    result = cursor.fetchall()
    db_con.commit()

    return [r['region'] for r in result]


def get_general_region_by_id(region_id):
    db_con = sqlite3.connect('reports.db')
    db_con.row_factory = sqlite3.Row
    cursor = db_con.cursor()

    cursor.execute(
        f"""SELECT region 
        FROM General_Regions
        WHERE id = {region_id}"""
    )

    result = cursor.fetchone()
    db_con.commit()

    return result['region'] if result is not None else None


def get_all_names(sort_by_group=True):
    db_con = sqlite3.connect('reports.db')
    db_con.row_factory = sqlite3.Row
    cursor = db_con.cursor()

    regions = [
        'Total',
        'Алмазарский р. (Ташкент)',
        'Бектемирский р. (Ташкент)',
        'Мирабадский р. (Ташкент)',
        'М.Улугбекский р. (Ташкент)',
        'Сергелийский р. (Ташкент)',
        'Чиланзарский р. (Ташкент)',
        'Шайхантахурский р. (Ташкент)',
        'Юнусабадский р. (Ташкент)',
        'Яккасарайский р. (Ташкент)',
        'Яшнабадский р. (Ташкент)',
        'Учтепинский р. (Ташкент)',
        'Ташкентская обл.',
        'Андижанская обл.',
        'Наманганская обл.',
        'Ферганская обл.',
        'Сырдарьинская обл.',
        'Джизакская обл.',
        'Самаркандская обл.',
        'Кашкадарьинская обл.',
        'Сурхандарьинская обл.',
        'Бухарская обл.',
        'Навоинская обл.',
        'Хорезмская обл.',
        'Респ. Каракалпакстан',
        'Неизвестный р.'
    ]

    result = {}

    if sort_by_group:
        cursor.execute(
            """SELECT * 
            FROM Groups"""
        )

        groups = cursor.fetchall()
        for group in groups:
            result[group['group']] = {}
            cursor.execute(
                f"""SELECT name 
                FROM General_Names 
                WHERE group_id={group['group_id']}"""
            )
            names_in_group = cursor.fetchall()
            names_sorted = sorted([name['name'] for name in names_in_group])
            for name in names_sorted:
                if name not in result[group['group']]:
                    result[group['group']][name] = {}
                for region in regions:
                    result[group['group']][name][region] = 0
    else:
        cursor.execute(
            f"""SELECT name 
            FROM General_Names"""
        )
        names_unsorted = cursor.fetchall()
        names_sorted = sorted([name['name'] for name in names_unsorted])
        for name in names_sorted:
            result[name] = {}
            for region in regions:
                result[name][region] = 0

    return result


def check_name(input_name):
    db_con = sqlite3.connect('reports.db')
    db_con.row_factory = sqlite3.Row
    cursor = db_con.cursor()

    cursor.execute(
        f"""SELECT *
        FROM All_names 
        WHERE unique_name = '{input_name}'"""
    )

    return bool(cursor.fetchone())


def check_region(input_region):
    db_con = sqlite3.connect('reports.db')
    db_con.row_factory = sqlite3.Row
    cursor = db_con.cursor()

    cursor.execute(
        f"""SELECT *
        FROM All_Regions 
        WHERE unique_region = '{input_region}'"""
    )

    return bool(cursor.fetchone())


def insert_region(unique: str, general: str):
    db_con = sqlite3.connect('reports.db')
    db_con.row_factory = sqlite3.Row
    cursor = db_con.cursor()

    cursor.execute(
        """
        SELECT id 
        FROM General_Regions 
        WHERE region = ?
        """,
        (general,)
    )
    general_id = cursor.fetchone()['id']

    cursor.execute(
        """
        INSERT INTO All_Regions (unique_region, general_id) 
        VALUES (?, ?)
        """,
        (unique, general_id)
    )
    db_con.commit()



# def insert_unique_name(unique_name: str, general_name: str):
#     pass

# print(get_general_region_by_id(18))

# print(get_all_names(sort_by_group=True))

# print(get_general_name('Вессел Дуэ Ф р-р 600ЛЕ/2мл №10'))

# print(get_general_name("ashgsfdcaxc"))
