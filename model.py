class Record():
    def __init__(self, record):
        self.id = record[0]
        self.user_name = record[1]
        self.name_soldier = record[2]
        self.date = record[3]
        self.delta_date = record[4]
        self.timer_status = record[5]
        self.reminder_time = record[6]
        list = record[7].split('\n')
        for l in list:
            if l.split(' = ')[0] == 'notification':
                if l.split(' = ')[1] == 'True':
                    status = True
                else:
                    status = False
                self.notification_status = status
            if l.split(' = ')[0] == 'holidays':
                if l.split(' = ')[1] == 'True':
                    status = True
                else:
                    status = False
                self.holidays_status = status

class Holiday():
    def __init__(self, record):
        self.date = record[0]
        self.time_congratulations = record[1]
        self.name_holiday = record[3]