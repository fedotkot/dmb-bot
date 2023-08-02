import datetime
from telebot import types

class Create():
    def __init__(self, bot, menu_ending, data_base, timer, create_keyboard):
        self.__bot = bot
        self.__menu_ending = menu_ending
        self.__data_base = data_base
        self.__timer = timer
        self.__create_keyboard = create_keyboard

    def create_timer(self, message, new_write):
        self.__bot.send_message(message.chat.id, 'Как зовут вашего солдата:',
                                reply_markup=types.ReplyKeyboardRemove())
        if new_write:
            self.__bot.register_next_step_handler(message, self.create_date_call, True)
        else:
            self.__bot.register_next_step_handler(message, self.__menu_ending, True)
        self.__bot.register_next_step_handler(message, self.__write_name_soldier)

    def __write_name_soldier(self, message):
        self.__data_base.write.name_soldier(message.chat.id, message.text)

    def create_date_call(self, message,new_write):
        markup = self.__create_keyboard('Сегодняшняя дата')
        self.__bot.send_message(message.chat.id,
                         'Напишите дату призыва в формате "ГГГГ-ММ-ДД", '
                         'или нажмите кнопку "Сегодняшняя дата"',
                         reply_markup=markup)
        self.__bot.register_next_step_handler(message, self.__write_date_call, new_write)

    def __write_date_call(self, message, new_write):
        #Если нажали на кнопку "Сегодняшняя датта"
        if message.text == 'Сегодняшняя дата':
            self.__data_base.write.date(message.chat.id, datetime.date.today())
            status = True
        else:
            #Если дату ввели вручную
            try:
                datetime.datetime.strptime(message.text, '%Y-%m-%d')
                #Провереям дату, чтобы на момент сегоднешней даты разница была меньше года
                delta = datetime.date.today() - datetime.datetime.strptime(message.text, '%Y-%m-%d').date()
                if delta.days <= 365:
                    self.__data_base.write.date(message.chat.id, message.text)
                    status = True
                else:
                    print('Слишком старая дата')
                    self.__bot.send_message(message.chat.id, 'Слишком старая дата. Напишите дату снова:')
                    self.__bot.register_next_step_handler(message, self.__write_date_call, new_write)
                    status = False
            except ValueError:
                print('Формат не правильный')
                self.__bot.send_message(message.chat.id, 'Вы ввели дату неправильно, попробуйте ещё раз:')
                self.__bot.register_next_step_handler(message, self.__write_date_call, new_write)
                status = False

        if status:
            #self.__data_base.save_date(message, message.text)
            if new_write:
                self.create_time_timer(message,new_write)
            else:
                self.__menu_ending(message, True)

    def create_time_timer(self, message, new_write):
        markup = self.__create_keyboard('В полдень')
        self.__bot.send_message(message.chat.id,
                         'Напишите время напоминания в формате: "ЧЧ:ММ"'
                         ' или нажмите кнопку: "В полдень" ',
                         reply_markup=markup)
        self.__bot.register_next_step_handler(message, self.__write_time_timer, new_write)

    def __write_time_timer(self, message, new_write):
        if message.text == 'В полдень':
            #text = '12:00'
            self.__data_base.write.time(message.chat.id, '12:00')
            status = True
        else:
            try:
                print(message.text)
                datetime.datetime.strptime(message.text, '%H:%M')
                #text = message.text
                self.__data_base.write.time(message.chat.id, message.text)
                status = True
            except ValueError:
                print('Формат не правильный')
                self.__bot.send_message(message.chat.id, 'Вы ввели время неправильно, попробуйте ещё раз:')
                self.__bot.register_next_step_handler(message, self.__write_time_timer, new_write)
                status = False

        if status:
            #self.__data_base.save_time(message, text)
            if new_write:
                self.create_interval_date(message,new_write)
            else:
                self.__timer.update_timer(message.chat.id)
                self.__menu_ending(message, True)

    def create_interval_date(self, message, new_write):
        markup = self.__create_keyboard('Каждый день',
                                 'Раз в два дня',
                                 'Раз в неделю')
        self.__bot.send_message(message.chat.id,
                         'Как часто напоминать:',
                         reply_markup=markup)
        self.__bot.register_next_step_handler(message, self.__write_interval_date, new_write)

    #Функция созданиия
    def __write_interval_date(self, message,new_write):
        match message.text:
            case 'Каждый день':
                delta = 1
                status = True
            case 'Раз в два дня':
                delta = 2
                status = True
            case 'Раз в неделю':
                delta = 7
                status = True
            case _:
                self.__bot.send_message(message.chat.id,
                                 'Такого варианта нет. Попробуйте ещё раз:'
                                )
                self.__bot.register_next_step_handler(message, self.__write_interval_date, new_write)
                status = False
        if status:
            self.__data_base.write.delta_date(message.chat.id, delta)
            if new_write:
                self.__data_base.write.timer_status(message.chat.id, True)
                self.__timer.update_timer(message.chat.id)
                self.__bot.send_message(message.chat.id, 'Готово! Поздравляю, вы создали  таймер')
                self.__menu_ending(message, False)
            else:
                self.__menu_ending(message, True)