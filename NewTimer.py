from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import datetime

from sqlitefunc import Data_base
from date import Holiday_date

class Timers():
    def __init__(self, data_name, func, bot, notification_func):
        self.__func = func
        self.__holidays = Holiday_date('Holidays_data_base.db', bot)
        self.__notification_func = notification_func
        self.__data_base = Data_base(data_name,
                                     """CREATE TABLE IF NOT EXISTS chat_id(
                                        id INTEGER,
                                        username STRING,
                                        name_soldier STRING,
                                        date TIMESTAMP,
                                        delta_date INTEGER,
                                        timer_status BOOLEAN,
                                        reminder_time TIMESTAMP
                                    )""")
        self.__scheduler = BackgroundScheduler()
        self.__scheduler.add_job(self.__notification_func,
                                 'cron', hour='12', minute='01',
                                 args=[self.__data_base.select.all_records()],
                                 id='notification_timer'
                                 )
        self.__scheduler.add_job(self.__create_all_timer,
                                 'cron', hour='00', minute='00',
                                 id= 'work_timer'
                                 )

    def start(self):
        self.__create_all_timer()
        self.__scheduler.start()

    def __create_all_timer(self):
        records = self.__data_base.select.all_records()
        self.__create_holidays_timer()
        for record in records:
            self.__create_timer(record.id)
    def __create_holidays_timer(self):
        if self.__scheduler.get_job('Holidays_timer') is not None:
            self.__scheduler.remove_job('Holidays_timer')
        # Проверяем наличие праздника на сегодняшнюю дату
        holiday = self.__holidays.check_holiday(datetime.datetime.now().date())
        if holiday is not None:
            # Если в записи есть время
            if holiday.time_congratulations is not None:
                time = datetime.datetime.strptime(holiday.time_congratulations, '%H:%M')
            else:
                time = datetime.datetime.strptime('10:00', '%H:%M')
            hour = str(time.hour)
            minute = str(time.minute)
            # Создаем таймер
            self.__scheduler.add_job(self.__holidays.action,
                                     'cron', hour=hour, minute=minute,
                                     id='Holidays_timer', args=holiday.text)

    def __create_timer(self, id):
        record = self.__data_base.select.one_record(id)
        # Провереям статус таймера
        if record.timer_status == True:
            # Проверяем дату, чтобы она была меьнше текущей
            if datetime.datetime.strptime(record.date, '%Y-%m-%d').date() <= datetime.date.today():
                # Проверяем налличие времени срабатывания
                if self.__scheduler.get_job(str(record.id)) is None:
                    if record.reminder_time is not None:
                        time = datetime.datetime.strptime(record.reminder_time, '%H:%M')
                    else:
                        time = datetime.time(12, 00)
                    self.__scheduler.add_job(self.__func,
                                             'cron', hour=time.hour, minute=time.minute,
                                             id=str(record.id), args=[record]
                                             )
                    print(f'Создали таймер  пользователя: {record.user_name} на {time.hour}:{time.minute}.')
                else:
                    print(f'Таймер пользователя: {record.user_name} уже существует.')
            #else:
                #print(f'{record[0]} таймер не надо включать')
        else:
            #Если статус таймера "ВЫКЛЮЧЕНО", и таймер существует, то удаляем его
            if self.__scheduler.get_job(str(record.id)) is not None:
                self.__scheduler.remove_job(str(record.id))
                print(f'Таймер пользователя: {record.user_name}удалён!')

    def update_timer(self, id):
        record = self.__data_base.select.one_record(id)
        #Проверяем существование записи
        if record is None:
            # Если в ДБ нет записи по данному id, то проверяем этот таймер на существование
            print('Записи не существует, удаляем таймер!')
            if self.__scheduler.get_job(str(id)) is not None:
                print(self.__scheduler.get_job(str(id)))
                self.__scheduler.remove_job(str(id))
                print('Таймер удалён!')
        else:
            if record.timer_status == True:
                # Если Статус таймера "ВКЛЮЧЕН", то проверяем наличие такого таймера по id
                print(self.__scheduler.get_job(str(record.id)))
                if self.__scheduler.get_job(str(record.id)) is not None:
                    # Если таймер существует, то проверяем совподает время с временем из БД
                    if record.reminder_time is not None:
                        time = datetime.datetime.strptime(record.reminder_time, '%H:%M')
                    else:
                        time = datetime.time(12,00)
                    triggers = CronTrigger(hour=time.hour, minute=time.minute)
                    if self.__scheduler.get_job(str(record.id)).trigger != triggers:
                        # Если время не совпало, изменяем время таймера
                        #self.__scheduler.reschedule_job(str(record[0]), trigger='cron', hour=time.hour, minute=time.minute)
                        self.__scheduler.remove_job(str(record.id))
                        self.__create_timer(record.id)
                        print('Обновили таймер!')
                    # Если время совпало, то ничего не делаем
                else:
                    # Если таймер не существует, то создаем таймер по БД
                    self.__create_timer(record.id)
            else:
                # Если Статус таймера "ВЫКЛЛЮЧЕН", то проверяем наличие такого таймера по id
                if self.__scheduler.get_job(str(record.id)) is not None:
                    print(self.__scheduler.get_job(str(record.id)))
                    # Если таймер существует, то удаляем таймер
                    self.__scheduler.remove_job(str(record.id))
                    print('Таймер удален!')
                # Если таймера не существует, то ничего не делаем