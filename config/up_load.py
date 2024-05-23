from flask import Flask, request, jsonify, Blueprint

app = Flask(__name__)

SCHEDULE_FILE_PATH = 'D:\\pythonProject\\CXSJHOMEWORK\\docs\\Schedule\\Schedule_my'

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/submit', methods=['POST'])
def submit_data():
    # 从POST请求中获取参数
    new_data = request.json.get('data')

    # 检查是否有缺少的参数
    if new_data is None:
        return jsonify({'error': 'Missing data parameter'}), 400

    try:
        # 读取现有数据
        try:
            with open(SCHEDULE_FILE_PATH, 'r', encoding='utf-8') as f:
                current_data = f.read()
        except FileNotFoundError:
            current_data = ""

        # 将新数据添加到现有数据
        updated_data = current_data + new_data

        # 将更新后的数据写入文件
        with open(SCHEDULE_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(updated_data)
    except Exception as e:
        return jsonify({'error': f'Failed to write data: {str(e)}'}), 500

    # 返回成功响应
    return jsonify({'message': 'Data successfully received and updated', 'data': new_data}), 200

@upload_bp.route('/schedule', methods=['GET'])
def get_schedule():
    try:
        # 从文件中读取课表数据
        with open(SCHEDULE_FILE_PATH, 'r', encoding='utf-8') as f:
            schedule_data = f.read()
    except FileNotFoundError:
        return jsonify({'error': 'Schedule file not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to read data: {str(e)}'}), 500

    # 返回课表数据
    return jsonify({'data': schedule_data}), 200

# 注册蓝图
app.register_blueprint(upload_bp, url_prefix='/upload')

if __name__ == '__main__':
    app.run(debug=True)
