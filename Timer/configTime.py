from flask import Flask, request, Blueprint, jsonify
import os

time_blueprint = Blueprint('time_blueprint', __name__)

# 路径到你的时间日志文件
TIME_LOG_PATH = 'Timer/time_config.txt'

@time_blueprint.route('/update_time', methods=['POST'])
def update_time():
    try:
        data = request.json
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if not start_time or not end_time:
            return jsonify({'error': 'Missing time parameters'}), 400

        with open(TIME_LOG_PATH, 'w') as file:
            file.write(f'{start_time},{end_time}\n')

        return jsonify({'message': 'Time log updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
