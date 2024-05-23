import requests

class ReminderClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_recommendation(self):
        try:
            response = requests.get(f"{self.base_url}/recommend")
            if response.status_code == 200:
                return response.json()['recommendation']
            else:
                print(f"Failed to get recommendation: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

    def record_choice(self, choice, recommended_canteen):
        try:
            response = requests.post(f"{self.base_url}/record_choice", json={'choice': choice, 'recommended_canteen': recommended_canteen})
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to log choice: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    client = ReminderClient("http://localhost:8000")

    # 获取推荐
    recommendation = client.get_recommendation()
    if recommendation:
        print(f"推荐: {recommendation}")

    # 假设推荐的是1号食堂，用户选择了2号食堂
    recommended_canteen = 2
    user_choice = 1

    # 记录用户选择
    response = client.record_choice(user_choice, recommended_canteen)
    if response:
        print(response)
