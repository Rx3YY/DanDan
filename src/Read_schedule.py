import os
import json
import time
import re
import datetime
from pathlib import Path

# 读取课表，通过你的课表来分析

class Read_schedule():
    def __init__(self):
        self.path = Path('docs/Schedule')

    def get_data(self):
        file_url = []
        for root, dirs, files in os.walk(self.path):
            for file in files:
                file_url.append(os.path.join(root, file))
        return file_url[0]

    def parser_data(self):
        file_url = self.get_data()

        lines_list = []
        with open(f'{file_url}', 'r', encoding='utf8') as f:
            for line in f:
                lines_list.append(line.strip())

        weekday_number = datetime.datetime.today().weekday()

        if weekday_number >= 0 and weekday_number <= 3 or weekday_number == 6:
            '''当天的提醒下一天的'''
            schedule = lines_list[(weekday_number) % 7]

        # 设置三个阈值,对应有早八、早十、上午无科的情景    分别是early  medium  late
        try:
            pattern = r'\d+-\d+'
            matches = re.findall(pattern, schedule)
            matches_with_original = [(int(match.split('-')[0]), match) for match in matches]
            sorted_matches = sorted(matches_with_original, key=lambda x: x[0])

            start_schedule = sorted_matches[0][0]

            # print(start_schedule)
            # print(sorted_matches)

            if start_schedule == 1:
                return 'early'
            elif start_schedule == 3:
                return 'medium'
            else:
                return 'late'
        except:
            return 'late'


if __name__ == '__main__':
    a = Read_schedule()
    print(a.parser_data())