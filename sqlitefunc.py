import sqlite3
from model import Record

class Data_base:
    def __init__(self, data_name, request):
        self.__data_name = data_name
        connect = sqlite3.connect(self.__data_name)
        cursor = connect.cursor()
        cursor.execute(request)
        connect.commit()
        cursor.close()
        connect.close()
        print('Таблица создана')
        self.select = _Select(data_name)
        self.write = _Write(data_name)
        self.__action_db = _Action_data_base(data_name)

    def create_new_user(self, id, username):
        connect = sqlite3.connect(self.__data_name)
        cursor = connect.cursor()
        cursor.execute(f"SELECT id FROM chat_id WHERE id = {id}")
        if cursor.fetchone() is None:
            notification = 'notification = True\n' \
                           'holidays = True'
            data = [id, username, None, None, None, None, None, notification]
            cursor.execute("INSERT INTO chat_id VALUES (?,?,?,?,?,?,?,?)", data)
            connect.commit()
            print('Новая запись создана.')
        else:
            print('Запись уже существует.')
        cursor.close()
        connect.close()

    def delete_user(self, chat_id):
        connect = sqlite3.connect(self.__data_name)
        cursor = connect.cursor()
        cursor.execute(f"SELECT id FROM chat_id WHERE id = {chat_id}")
        if cursor.fetchone() is not None:
            cursor.execute(f"DELETE FROM chat_id WHERE id = {chat_id}")
            connect.commit()
            print('Пользователь удален!')
        else:
            print('Такого пользователя нет')
        cursor.close()
        connect.close()

    def write_report(self, id, user_name, date_time, text_message):
        connect = sqlite3.connect(self.__data_name)
        cursor = connect.cursor()
        data = (id, user_name, date_time, text_message)
        cursor.execute("INSERT INTO report VALUES (?,?,?,?)", data)
        connect.commit()
        print(f'Репорт от пользователя: {user_name} создан.')

    def select_data_all(self, request):
        connect = sqlite3.connect(self.__data_name)
        cursor = connect.cursor()
        records = cursor.execute(request).fetchall()
        cursor.close()
        connect.close()
        return records

    def select_data_where(self, request, where):
        connect = sqlite3.connect(self.__data_name)
        cursor = connect.cursor()
        cursor.execute(request, where)
        records = cursor.fetchone()
        cursor.close()
        connect.close()
        return records

#Подкласс: Вывод из БД
class _Select():
    def __init__(self, data_name):
        self.__action_db = _Action_data_base(data_name)

    def timer_status(self, id):
        record = self.__action_db.select_one_data(f"""SELECT timer_status FROM chat_id WHERE id = {id} """)
        return record[0]

    def holidays_status(self, id):
        record = self.__action_db.select_one_data(f"""SELECT notification_status FROM chat_id WHERE id = {id} """)
        match self.__select_parametr(record, 'holidays').split(' = ')[1]:
            case 'True':
                return True
            case 'False':
                return False

    def notification_status(self, id):
        record = self.__action_db.select_one_data(f"""SELECT notification_status FROM chat_id WHERE id = {id} """)
        match self.__select_parametr(record, 'notification').split(' = ')[1]:
            case 'True':
                return True
            case 'False':
                return False

    def one_record(self, id):
        record = self.__action_db.select_one_data(f"""SELECT * FROM chat_id WHERE id = {id}""")
        if record is not None:
            return Record(record)
        else:
            return None

    def all_records(self):
        list = []
        records = self.__action_db.select_all_data("""SELECT * FROM chat_id""")
        for record in records:
            list.append(Record(record))
        return list
    def __select_parametr(self, record, search_parametr):
        list = record[0].split('\n')
        for l in list:
            if l.split(' = ')[0] == search_parametr:
                return l
        return None

# Подкласс: Запись в ДБ
class _Write():
    def __init__(self, data_name):
        self.__action_db = _Action_data_base(data_name)

    # Запись Имени Солдата
    def name_soldier(self, id, name):
        self.__action_db.update_one_data("""UPDATE chat_id SET name_soldier = ? WHERE id = ? """, (name, id))

    # Запись Даты
    def date(self, id, date):
        self.__action_db.update_one_data("""UPDATE chat_id SET date = ? WHERE id = ? """, (date, id))
        print(f'Пользователь: {id} добавил дату.')

    # Запись Времени
    def time(self, id, time):
        self.__action_db.update_one_data("""UPDATE chat_id SET reminder_time = ? WHERE id = ? """, (time, id))
        print(f'Пользователь: {id} добавил время.')

    # Запись Делты
    def delta_date(self, id, delta):
        self.__action_db.update_one_data("""UPDATE chat_id SET delta_date = ? WHERE id = ? """, (delta, id))

    # Запись Статуса таймера
    def timer_status(self, id , status):
        self.__action_db.update_one_data("""UPDATE chat_id SET timer_status = ? WHERE id = ? """, (status, id))

    #Запись статуса Уведомлений
    def notification_status(self, id, status):
        record = self.__action_db.select_one_data(f"""SELECT notification_status FROM chat_id WHERE id = {id} """)
        new_record = self.__paste_parametr(record,'notification', status)
        self.__action_db.update_one_data(f"""UPDATE chat_id SET notification_status = ? WHERE id = ? """, (new_record, id))

    # Запись статуса Праздников
    def holidays_status(self, id, status):
        record = self.__action_db.select_one_data(f"""SELECT notification_status FROM chat_id WHERE id = {id} """)
        new_record = self.__paste_parametr(record, 'holidays', status)
        self.__action_db.update_one_data(f"""UPDATE chat_id SET notification_status = ? WHERE id = ? """, (new_record, id))

    # Вспомогательные функции
    # Внесение нового параметра в запись
    def __paste_parametr(self, record, paste_parametr, param):
        # Создаем лист со всеми строками из записи
        list = record[0].split('\n')
        for idx, l in enumerate(list):
            # Ищем нужную нам строку
            if l.split(' = ')[0] == paste_parametr:
                # Если нашли то меняем параметр на новый
                list[idx] = paste_parametr + ' = ' + str(param)
                # Из листа собираем запись обратно и возвращаем
                return '\n'.join(list)
        # Если не нашли нужную строку None
        return None

class _Action_data_base():
    def __init__(self, data_name):
        self.__data_name = data_name

    def update_one_data(self, request, data):
        connect = sqlite3.connect(self.__data_name)
        cursor = connect.cursor()
        cursor.execute(request, data)
        connect.commit()
        cursor.close()
        connect.close()
        print('Данные обновлены!')

    def select_one_data(self, request):
        connect = sqlite3.connect(self.__data_name)
        cursor = connect.cursor()
        cursor.execute(request)
        record = cursor.fetchone()
        cursor.close()
        connect.close()
        print('Запись изьята')
        return record

    def select_all_data(self, request):
        connect = sqlite3.connect(self.__data_name)
        cursor = connect.cursor()
        cursor.execute(request)
        records = cursor.fetchall()
        cursor.close()
        connect.close()
        print('Записи изьята')
        return records

# connect = sqlite3.connect('user.db')
# cursor = connect.cursor()
# cursor.execute("""CREATE TABLE IF NOT EXISTS report(
#                                         id INTEGER,
#                                         username STRING,
#                                         date_time TIMESTAMP,
#                                         text TEXT
#                                     )""")
# connect.commit()
# cursor.close()
# connect.close()

# connect = sqlite3.connect('user.db')
# cursor = connect.cursor()
# text = 'notification = True\n' \
#        'holidays = True'
# id = -1001803641025
# cursor.execute(f"""SELECT id FROM  chat_id""")
# records = cursor.fetchall()
# for record in records:
#     cursor.execute(f"""UPDATE chat_id SET notification_status = ? WHERE id = ?""", (text, record[0]))
# connect.commit()
# cursor.close()
# connect.close()
#
#
# def paste_parametr(record, paste_parametr, param):
#     list = record.notification_status.split('\n')
#     for idx, l in enumerate(list):
#         if l.split(' = ')[0] == paste_parametr:
#             list[idx] = paste_parametr + ' = ' + str(param)
#             return '\n'.join(list)
#     return None
#
# print(paste_parametr(record, 'holidays', True))