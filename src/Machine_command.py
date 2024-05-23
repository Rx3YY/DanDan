import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import OneHotEncoder

# 假设你的数据集格式如下
data = {
    '食物类型': ['辣的', '甜的', '辣的', '咸的', '清淡'],
    '喜好权重': [5, 1, 4, 3, 2]
}
df = pd.DataFrame(data)

# 数据预处理：对食物类型进行独热编码
encoder = OneHotEncoder(sparse=False)
X = encoder.fit_transform(df[['食物类型']])
y = df['喜好权重']

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 创建逻辑回归模型并训练
model = LogisticRegression()
model.fit(X_train, y_train)

# 预测测试集
y_pred = model.predict(X_test)

print(y_pred)
