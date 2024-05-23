from flask import Flask, request, jsonify, Blueprint
import numpy as np
import pandas as pd
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
from src.Read_breakfast import Read_breakfast, Weight_Food
from src.Read_schedule import Read_schedule
from src.weather import WeatherPab
import time
from gevent.pywsgi import WSGIServer

app = Flask(__name__)

command_bp = Blueprint('command', __name__)

class Command():
    def __init__(self):
        self.weather = WeatherPab()
        self.schedule = Read_schedule().parser_data()
        self.model = self.train_model()
        self.menu = [
            ("蒸包 + 瘦肉皮蛋粥 + 豆浆", "slow", 2),
            ("蒸包 + 荷叶粥 + 豆腐脑", "slow", 2),
            ("蒸包 + 豆腐脑 + 地瓜丸子", "quick", 2),
            ("油条 + 瘦肉皮蛋粥 + 煮鸡蛋", "slow", 2),
            ("油条 + 八宝粥 + 茶叶蛋", "quick", 2),
            ("手抓饼 + 瘦肉皮蛋粥 + 豆浆", "quick", 2),
            ("手抓饼 + 荷叶粥 + 豆腐脑", "slow", 2),
            ("手抓饼 + 豆腐脑 + 煮鸡蛋", "quick", 2),
            ("酱香饼 + 瘦肉皮蛋粥 + 豆浆", "slow", 2),
            ("酱香饼 + 荷叶粥 + 煮鸡蛋", "quick", 2),
            ("酱香饼 + 豆腐脑 + 茶叶蛋", "quick", 2),
            ("肉夹馍 + 瘦肉皮蛋粥 + 豆浆", "slow", 2),
            ("肉夹馍 + 荷叶粥 + 煮鸡蛋", "slow", 2),
            ("烧麦 + 瘦肉皮蛋粥 + 豆浆", "quick", 2),
            ("烧麦 + 荷叶粥 + 豆腐脑", "slow", 2),
            ("烧麦 + 豆腐脑 + 地瓜丸子", "quick", 2),
            ("蛋挞 + 荷叶粥 + 茶叶蛋", "quick", 2),
            ("蛋挞 + 瘦肉皮蛋粥 + 豆浆", "quick", 2),
            ("小笼包 + 荷叶粥 + 茶叶蛋", "quick", 1),
            ("小笼包 + 瘦肉皮蛋粥 + 豆腐脑", "slow", 1),
            ("小笼包 + 豆腐脑 + 煮鸡蛋", "quick", 1),
            ("香菇面 + 荷叶粥 + 茶叶蛋", "slow", 1),
            ("香菇面 + 瘦肉皮蛋粥 + 豆浆", "slow", 1),
            ("香菇面 + 豆腐脑 + 煮鸡蛋", "slow", 1),
            ("馄饨 + 荷叶粥 + 茶叶蛋", "slow", 1),
            ("馄饨 + 瘦肉皮蛋粥 + 豆浆", "slow", 1),
            ("馄饨 + 豆腐脑 + 煮鸡蛋", "slow", 1),
            ("煮鸡蛋 + 瘦肉皮蛋粥 + 豆浆", "quick", 1),
        ]

    def get_lowestTemp(self):
        info = self.weather.parser_data()
        lowest = info[0][2].split('/')[1]
        return int(lowest[:-1])  # 返回整数类型的温度

    def lowest_parse(self):
        lowest_temp = self.get_lowestTemp()
        if lowest_temp < -5:
            return 1
        elif lowest_temp < 5:
            return 2
        else:
            return 3


    def Like_change_write_in(self, choice):
        with open('Like.txt', 'a', encoding='utf-8') as f:
            features = self.get_current_features()
            timestamp = datetime.now().isoformat()
            f.write(f"{','.join(map(str, features))},{choice},{timestamp}\n")


    def get_current_features(self):
        lowest_temp = self.get_lowestTemp()
        schedule = 1 if self.schedule == 'early' else 2 if self.schedule == 'medium' else 3 if self.schedule == 'late' else 4
        return [lowest_temp, schedule]


    def get_training_data(self):
        try:
            with open('Like.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                data = [line.strip().split(',') for line in lines if line.strip()]
                df = pd.DataFrame(data, columns=['temp', 'schedule', 'choice', 'timestamp'])
                df = df.astype({'temp': int, 'schedule': int, 'choice': int, 'timestamp': 'datetime64'})
                X = df[['temp', 'schedule']].values
                y = df['choice'].values

                # 计算权重
                current_time = datetime.now()
                df['time_diff'] = (current_time - df['timestamp']).dt.total_seconds()
                max_time_diff = df['time_diff'].max()
                df['weight'] = 1 - (df['time_diff'] / max_time_diff)  # 离当前时间越久，权重越低

                sample_weight = df['weight'].values
                return X, y, sample_weight
        except FileNotFoundError:
            return np.array([]), np.array([]), np.array([])

    def train_model(self):
        X, y, sample_weight = self.get_training_data()
        if len(X) > 0 and len(y) > 0:
            model = RandomForestClassifier(n_estimators=100)
            model.fit(X, y, sample_weight=sample_weight)
            return model
        else:
            return None

    def get_recommendations(self, user_id, rating_matrix, k=3):
        """
        获取推荐项目列表
        user_id: 用户ID
        rating_matrix: 用户-项目评分矩阵
        k: 考虑的最相似用户数量
        """
        # 计算用户之间的余弦相似度
        user_similarity = cosine_similarity(rating_matrix)
        user_similarity_df = pd.DataFrame(user_similarity, index=rating_matrix.index, columns=rating_matrix.index)

        # 获取指定用户的相似度向量
        user_similarities = user_similarity_df.loc[user_id]

        # 获取该用户评分为0的项目
        user_ratings = rating_matrix.loc[user_id]
        unrated_items = user_ratings[user_ratings == 0].index

        # 计算未评分项目的加权评分
        recommendations = {}
        for item in unrated_items:
            # 计算相似用户对该项目的加权评分
            weighted_sum = sum(
                user_similarities[u] * rating_matrix.loc[u, item] for u in rating_matrix.index if u != user_id)
            sim_sum = sum(user_similarities[u] for u in rating_matrix.index if u != user_id)
            predicted_rating = weighted_sum / sim_sum if sim_sum != 0 else 0
            recommendations[item] = predicted_rating

        # 按照预测评分排序，返回评分最高的前k个项目
        recommended_items = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:k]
        return [item for item, rating in recommended_items]


    def predict_choice(self):
        if self.model is not None:
            next_feature = np.array([self.get_current_features()])
            prediction = self.model.predict(next_feature)
            return prediction[0]
        else:
            return random.randint(1, 2)  # 默认随机推荐1号或2号食堂


    def command(self):
        '''推荐菜谱'''
        localtime = time.asctime()

        # 如果 Like.txt 文件不存在或为空，则初始化
        try:
            with open('Like.txt', 'r', encoding='utf-8') as f:
                like_content = f.read()
        except FileNotFoundError:
            like_content = None

        if not like_content:
            with open('Like.txt', 'w', encoding='utf-8') as f:
                f.write("0,0,2,1970-01-01T00:00:00\n")  # 初始化为默认特征和2号食堂

        parse_lowest = self.lowest_parse()

        if self.schedule == 'early':
            menu_choices = [item for item in self.menu if item[1] == "quick"]
        else:
            menu_choices = self.menu

        predicted_choice = self.predict_choice()
        food_choices = [item for item in menu_choices if item[2] == predicted_choice]
        if food_choices:
            food, _, canteen = random.choice(food_choices)
        else:
            # 如果没有匹配的食品选择，随机选择一个
            food, _, canteen = random.choice(menu_choices)

        if parse_lowest == 1:
            recommendation_str = "推荐温暖的早餐，比如热粥或汤"
        elif parse_lowest == 2:
            recommendation_str = "推荐较温暖的早餐，比如煎蛋或面包"
        else:
            recommendation_str = "推荐清凉的早餐，比如水果和酸奶"

        if self.schedule == 'early':
            recommendation_str += "。今天有早课，推荐快速简单的早餐"
        elif self.schedule == 'medium':
            recommendation_str += "。今天上午有中期课，推荐营养均衡的早餐"
        elif self.schedule == 'late':
            recommendation_str += "。上午没课哦，多睡一会，想吃什么吃什么"
        else:
            recommendation_str += "。上午没课哦，多睡一会，想吃什么吃什么"

        recommendation_str += f"。根据您的历史选择，推荐您去{canteen}号食堂，推荐的早餐是：{food}。"

        return recommendation_str

    def recommend_for_canteen(self, canteen):
        '''根据食堂推荐菜谱'''
        if self.schedule == 'early':
            menu_choices = [item for item in self.menu if item[1] == "quick" and item[2] == canteen]
        else:
            menu_choices = [item for item in self.menu if item[2] == canteen]

        if menu_choices:
            food, _, canteen = random.choice(menu_choices)
            recommendation_str = f"推荐的早餐是：{food}。"
        else:
            recommendation_str = "没有找到合适的推荐。"

        return recommendation_str


@command_bp.route('/recommend', methods=['GET'])
def recommend():
    command = Command()
    recommendation = command.command()
    return jsonify({'recommendation': recommendation})


@command_bp.route('/record_choice', methods=['POST'])
def record_choice():
    data = request.json
    choice = data.get('choice')
    recommended_canteen = data.get('recommended_canteen')

    if choice is None or recommended_canteen is None:
        return jsonify({'error': 'Missing choice or recommended_canteen parameter'}), 400

    command = Command()
    command.Like_change_write_in(choice)

    if choice != recommended_canteen:
        alternate_recommendation = command.recommend_for_canteen(choice)
        return jsonify({'message': f'用户选择了{choice}号食堂，记录已更新。', 'alternate_recommendation': alternate_recommendation})
    else:
        return jsonify({'message': f'用户选择了{choice}号食堂，记录已更新。'})


def run():
    pass
