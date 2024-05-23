from flask import Flask
from gevent.pywsgi import WSGIServer

# 从模块中导入蓝图
from config.up_load import upload_bp
from src.command import command_bp
from src.get_weather_app import weather_bp
from Timer.time_class import timer_bp
from Timer.configTime import time_blueprint
from server.server import status_bp

app = Flask(__name__)

# 注册蓝图
app.register_blueprint(upload_bp)
app.register_blueprint(command_bp)
app.register_blueprint(weather_bp)
app.register_blueprint(timer_bp)
app.register_blueprint(time_blueprint)
app.register_blueprint(status_bp)

# 主函数，启动服务
if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 8000), app)
    http_server.serve_forever()
