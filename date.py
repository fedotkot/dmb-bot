from sqlitefunc import Data_base
from model import Holiday

class Holiday_date():
    def __init__(self, data_name, bot):
        self.__bot = bot
        self.__db = Data_base(data_name,
                              """CREATE TABLE IF NOT EXISTS holiday(
                                    date TIMESTAMP, 
                                    time_congratulations TIMESTAMP,
                                    text_congratulations STRING, 
                                    name_holiday STRING 
                              )""")
        self.__user = Data_base('user.db',
                                """CREATE TABLE IF NOT EXISTS chat_id(
                                    id INTEGER,
                                    username STRING,
                                    name_soldier STRING,
                                    date TIMESTAMP,
                                    delta_date INTEGER,
                                    timer_status BOOLEAN,
                                    reminder_time TIMESTAMP
                                )""")

    def check_holiday(self, date):
        holidays = self.__db.select_data_all("""SELECT date FROM holiday""")
        if len(holidays) != 0:
            for holiday in holidays:
                if (date.strftime('2000-%m-%d') == holiday[0]):
                    return Holiday(holiday)
                else:
                    print('Не та запись')
            print('Такую дату не нашли')
            return None
        else:
            print('В таблице нет записей')
            return None

    def action(self, text):
        records = self.__user.select.all_records()
        for record in records:
            if record.holidays_status:
                self.__bot.send_message(record.id, text)
