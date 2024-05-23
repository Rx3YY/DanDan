import time
from datetime import datetime, timedelta
import threading
from flask import Flask, request, jsonify, Blueprint
from gevent.pywsgi import WSGIServer
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import os

from src.weather import WeatherPab
from src.Read_schedule import Read_schedule

timer_bp = Blueprint('time', __name__)

class Logger():
    def __init__(self, log_file_path='time_logging.log'):
        self.log_file_path = log_file_path
        self.ensure_log_file()

    def ensure_log_file(self):
        try:
            with open(self.log_file_path, 'x') as f:
                f.write("reminder_time,choice,timestamp\n")
        except FileExistsError:
            pass

    def log_user_choice(self, reminder_time, choice):
        current_time = datetime.now()
        with open(self.log_file_path, 'a') as file:
            file.write(f"{reminder_time},{choice},{current_time.isoformat()}\n")
        print(f"Logged: {choice} at {reminder_time} on {current_time}")

class Clock():
    def __init__(self):
        self.log_file_path = 'time_logging.log'
        self.config_file_path = 'time_config.txt'
        self.reminder_times = self.load_initial_times()
        self.logger = Logger(self.log_file_path)
        self.current_reminder = None
        self.reminder_lock = threading.Lock()
        self.delay_count = 0  # 延迟次数计数
        self.schedule = Read_schedule().parser_data()  # 获取课表

    def load_initial_times(self):
        default_times = {
            'first_reminder': datetime.strptime('00:00:00', '%H:%M:%S').time(),
            'second_reminder': datetime.strptime('01:00:00', '%H:%M:%S').time()
        }
        try:
            with open(self.config_file_path, 'r') as f:
                times = f.read().strip().split(',')
                if len(times) == 2 and times[0] and times[1]:
                    return {
                        'first_reminder': datetime.strptime(times[0], '%Y-%m-%d %H:%M:%S').time(),
                        'second_reminder': datetime.strptime(times[1], '%Y-%m-%d %H:%M:%S').time()
                    }
                else:
                    print("Config file is empty or malformed. Initializing with default times.")
                    self.save_times(default_times)
                    return default_times
        except (FileNotFoundError, ValueError, IndexError) as e:
            print(f"Error loading initial times: {e}, using default times.")
            self.save_times(default_times)
            return default_times

    def save_times(self, times):
        with open(self.config_file_path, 'w') as f:
            f.write(
                f"{datetime.combine(datetime.now().date(), times['first_reminder']).strftime('%Y-%m-%d %H:%M:%S')},"
                f"{datetime.combine(datetime.now().date(), times['second_reminder']).strftime('%Y-%m-%d %H:%M:%S')}"
            )

    def choose_initial_reminder(self):
        if self.schedule == 'early':
            return self.reminder_times['first_reminder']
        else:
            return self.reminder_times['second_reminder']

    def remind(self, reminder_time):
        print(f"Reminder: It's time to sleep! Current reminder time: {reminder_time}")
        with self.reminder_lock:
            self.current_reminder = reminder_time

    def run_reminder_loop(self):
        initial_reminder = self.choose_initial_reminder()
        while True:
            current_time = datetime.now()
            reminder_datetime = datetime.combine(datetime.now().date(), initial_reminder)
            if abs((reminder_datetime - current_time).total_seconds()) <= 60:
                self.remind(initial_reminder.strftime('%H:%M'))
                time.sleep(60)  # 等待1分钟避免多次提醒
            time.sleep(3)  # 每3秒检查一次

    def adjust_reminder_time(self, reminder_time, adjustment_minutes):
        for key in self.reminder_times.keys():
            if self.reminder_times[key].strftime('%H:%M') == reminder_time:
                adjusted_time = (datetime.combine(datetime.now().date(), self.reminder_times[key]) + timedelta(minutes=adjustment_minutes)).time()
                self.reminder_times[key] = adjusted_time
        self.save_times(self.reminder_times)

    def get_training_data(self):
        if not os.path.exists(self.log_file_path):
            return np.array([]), np.array([])

        try:
            with open(self.log_file_path, 'r') as f:
                lines = f.readlines()[1:]
                data = [line.strip().split(',') for line in lines if line.strip()]
                df = pd.DataFrame(data, columns=['reminder_time', 'choice', 'timestamp'])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['hour'] = df['timestamp'].dt.hour
                df['minute'] = df['timestamp'].dt.minute
                X = df[['hour', 'minute']].values
                y = df['reminder_time'].apply(lambda x: datetime.strptime(x, '%H:%M')).dt.hour + df['reminder_time'].apply(lambda x: datetime.strptime(x, '%H:%M')).dt.minute / 60.0
                return X, y
        except FileNotFoundError:
            return np.array([]), np.array([])

    def fit_time(self):
        X, y = self.get_training_data()
        if len(X) > 0 and len(y) > 0:
            model = RandomForestRegressor(n_estimators=100)
            model.fit(X, y)
            next_feature = np.array([[datetime.now().hour, datetime.now().minute]])
            prediction = model.predict(next_feature)
            adjustment_minutes = int((prediction[0] - int(prediction[0])) * 60)
            for key in self.reminder_times.keys():
                reminder_time = datetime.combine(datetime.now().date(), self.reminder_times[key])
                adjusted_time = reminder_time + timedelta(minutes=adjustment_minutes)
                self.reminder_times[key] = adjusted_time.time()
            self.save_times(self.reminder_times)

clock = Clock()

@timer_bp.route('/remind', methods=['GET'])
def remind():
    with clock.reminder_lock:
        reminder_time = clock.current_reminder
    if reminder_time:
        return jsonify({'reminder': f"Reminder: 该睡觉了！现在是: {reminder_time}。"})
    else:
        return jsonify({'reminder': ""})

@timer_bp.route('/log_choice', methods=['POST'])
def log_choice():
    data = request.get_json()
    reminder_time = data.get('reminder_time')
    choice = data.get('choice')

    if not reminder_time or not choice:
        return jsonify({'error': 'Missing reminder_time or choice parameter'}), 400

    clock.logger.log_user_choice(reminder_time, choice)

    if choice == 'delay':
        clock.adjust_reminder_time(reminder_time, 15)
    elif choice == 'on-time':
        with clock.reminder_lock:
            clock.current_reminder = None  # 用户选择 "on-time" 后不再提醒

    clock.fit_time()
    return jsonify({'message': f"Logged: {choice} at {reminder_time}"})

