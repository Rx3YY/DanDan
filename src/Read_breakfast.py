import re
import os
import json
from pathlib import Path


class Read_breakfast():
    '''读取菜单并给出相应的组合'''
    def __init__(self):
        self.path = Path('Food')

    def get_data(self):
        file_url = []
        for root, dirs, files in os.walk(self.path):
            for file in files:
                file_url.append(os.path.join(root, file))
        return file_url[0]

    def parser_data(self):
        file_url = self.get_data()
        menus = []
        with open(f'{file_url}', 'r', encoding='utf8') as f:
            for line in f:
                if line != '\n':
                    menus.append(line.strip())
                else:
                    continue

        canteen_regex = r"(.+菜单):"
        food_category_regex = r"(主食|副食|粥类):(.+)"

        # 初始化字典来存储分类后的食物信息
        food_classification = {}
        current_canteen = ""

        for menu in menus:
            # 检测当前行是否为食堂名称
            canteen_match = re.match(canteen_regex, menu)
            if canteen_match:
                current_canteen = canteen_match.group(1)  # 获取食堂名称
                food_classification[current_canteen] = {"主食": [], "副食": [], "粥类": []}  # 初始化该食堂的食物分类
                continue

            # 检测当前行是否包含食物信息，并进行分类
            food_match = re.match(food_category_regex, menu)
            if food_match:
                category, foods = food_match.groups()
                food_list = [food.strip() for food in foods.split('、')]
                food_classification[current_canteen][category].extend(food_list)

        return food_classification


class Weight_Food():
    def __init__(self, food_classification):
        self.food_classification = food_classification

    @staticmethod
    def write_weight(food, calorie, time, price):
        return {
            'food': food,
            'calorie': calorie,
            'time': time,
            'price': price
        }

    def Weight_classify(self):
        weight_list = []
        for canteen, categories in self.food_classification.items():
            for category, foods in categories.items():
                for food in foods:
                    if food == '蒸包':
                        weight_list.append(self.write_weight(food, 5, 3, 1))
                    elif food == '油条':
                        weight_list.append(self.write_weight(food, 4, 3, 1))
                    elif food == '手抓饼':
                        weight_list.append(self.write_weight(food, 4, 4, 3))
                    elif food == '酱香饼':
                        weight_list.append(self.write_weight(food, 3, 3, 2))
                    elif food == '肉夹馍':
                        weight_list.append(self.write_weight(food, 5, 4, 3))
                    elif food == '烧麦':
                        weight_list.append(self.write_weight(food, 3, 5, 1))
                    elif food == '茶叶蛋':
                        weight_list.append(self.write_weight(food, 2, 5, 1))
                    elif food == '地瓜丸子':
                        weight_list.append(self.write_weight(food, 2, 5, 2))
                    elif food == '蛋挞':
                        weight_list.append(self.write_weight(food, 3, 5, 3))
                    elif food == '瘦肉皮蛋粥':
                        weight_list.append(self.write_weight(food, 5, 1, 2))
                    elif food == '荷叶粥':
                        weight_list.append(self.write_weight(food, 4, 1, 2))
                    elif food == '豆浆':
                        weight_list.append(self.write_weight(food, 1, 5, 1))
                    elif food == '豆腐脑':
                        weight_list.append(self.write_weight(food, 3, 1, 2))
                    # 学生食堂一楼的食物权重
                    elif food == '小笼包':
                        weight_list.append(self.write_weight(food, 5, 5, 3))
                    elif food == '香菇面':
                        weight_list.append(self.write_weight(food, 5, 1, 3))
                    elif food == '馄饨':
                        weight_list.append(self.write_weight(food, 5, 1, 4))
                    elif food == '煮鸡蛋':
                        weight_list.append(self.write_weight(food, 2, 5, 1))
                    elif food == '八宝粥':
                        weight_list.append(self.write_weight(food, 4, 4, 1))
        return weight_list
