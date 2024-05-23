import requests
import fake_useragent
from bs4 import BeautifulSoup
import time
import json
import sys

from datetime import datetime


class WeatherPab():
    '''为在12点之前量身打造的天气获取'''
    def __init__(self):
        self.url = 'http://www.weather.com.cn/weather/101010700.shtml'
        self.ua_fake = fake_useragent.UserAgent().chrome


    def get_data(self):
        try:
            url = self.url
            headers = {
                'User_Agent':self.ua_fake
            }
            r = requests.get(url, headers=headers)
            r.raise_for_status()
            r.encoding = r.apparent_encoding

            return r.text
        except:
            sys.setrecursionlimit(10)

    def parser_data(self):
        result = self.get_data()
        soup = BeautifulSoup(result, 'html.parser')

        # 获得此时时间
        hour = datetime.now().hour
        if hour >= 0 and hour <= 8:
            choice = 0
            text = "今"
        else:
            choice = 1
            text = "明"

        tomorrow_weather_element = soup.find_all('li', class_='sky')[choice]

        date = tomorrow_weather_element.find('h1').text
        weather = tomorrow_weather_element.find('p', class_='wea').text
        temp = tomorrow_weather_element.find('p', class_='tem').text.strip().replace('\n', ' ')
        wind_direction = [span['title'] for span in tomorrow_weather_element.find_all('span') if 'title' in span.attrs]
        wind_strength = tomorrow_weather_element.find('p', class_='win').i.text

        weather_ret = (date, weather, temp, wind_direction, wind_strength)
        return weather_ret, text

    def analysis_data(self):
        weather_ret, text = self.parser_data()
        date, weather, temp, wind, wind_strength = weather_ret

        # 返回读取的数据,修改成话
        temp_high, temp_low = temp.split('/')
        temp_high = temp_high.rstrip('℃')
        temp_low = temp_low.rstrip('℃')

        date_calender = date.split('（')[0]

        if len(wind) == 2:
            wind_1, wind_2 = wind[0], wind[1]
            text_lines = f'{text}日({date_calender})天气: 最高温 {temp_high}℃，最低温 {temp_low}℃，风向 {wind_1} 转 {wind_2}，风力 {wind_strength}。'
        else:
            text_lines = f'{text}日({date_calender})天气: 最高温 {temp_high}℃，最低温 {temp_low}℃，风向 {wind}，风力 {wind_strength}。'

        temp_high = int(temp_high)
        temp_low = int(temp_low)

        delta_temp = abs(temp_high - temp_low)
        if delta_temp >= 14 and temp_high < 20:
            text_lines += ' 昼夜温差大，请注意早晚适当增加衣物。'
        if temp_low <= 5:
            text_lines += ' 早晨气温较低，请注意增加衣物。'

        return text_lines


if __name__ == '__main__':
    weather = WeatherPab()
    print(weather.parser_data())
    print(weather.analysis_data())
