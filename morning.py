import os
import random
from datetime import date, datetime

import requests
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage

# 当前日期
today = datetime.now()

# 微信公众号 ID
app_id = os.environ["APP_ID"]

# 微信公众号 app_secret
app_secret = os.environ["APP_SECRET"]

# 高德天气接口密钥 key
key = os.environ["KEY"]

# 微信公众号 模板id
template_id = os.environ["TEMPLATE_ID"]

# 用户ID
user_id_1 = os.environ["USER_ID_1"]
# user_id_2 = os.environ["USER_ID_2"]  # 如果只有一个人，删去即可

# 以上环境变量不需要修改，只需要在 github 的 secrets 中添加即可

##################################
# 修改用户信息                     #
##################################

# 用户列表 如果有新增人员，对应添加一个user对象即可

'''
    user_id: 微信公众号的 openid
       name: 昵称
       date: 相识日期
   birthday: 生日
       city: 城市编码，在高德 api 接口文档处查询
'''
user_id_list = [
    {'user_id': user_id_1, "name": '翠花bb', "date": "2019-10-01", "birthday": "09-18",
     'city': '500105'}
    # ,{'user_id': user_id_2, "name": '南无月', "date": "2019-10-01", "birthday": "02-05",
    # 'city': '510116'}
]

##################################
# 以下为主代码，不需要修改           #
##################################

# 随机情话 API
def get_words():
    words = requests.get("https://api.shadiao.pro/chp")
    if words.status_code != 200:
        return get_words()
    result = words.json()['data']['text']
    print(result)
    return result


# 随机文字颜色
def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


# 高德天气信息
def get_weather(city):
    url = "https://restapi.amap.com/v3/weather/weatherInfo?output=JSON&key=" + key + "&city=" + city
    res = requests.get(url).json()
    print(res)
    weather = res["lives"][0]
    return weather['weather'], weather['temperature'], weather['winddirection'], weather['province'] + weather[
        'city']


# 总天数
def get_count(start_date):
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    return delta.days


# 计算生日天数
def get_birthday(birthday):
    print(birthday)
    next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
    if next < datetime.now():
        next = next.replace(year=next.year + 1)
    return (next - today).days


# 发送消息 支持批量用户
def wx_push():
    for user in user_id_list:
        user_id = user.get('user_id')
        name = user.get('name')
        birthday = user.get('birthday')
        start_date = user.get('date')
        city = user.get('city')
        get_count(start_date)
        get_birthday(birthday)
        print(user_id)

        wea, temperature, winddirection, cityName = get_weather(city)

        client = WeChatClient(app_id, app_secret)

        wm = WeChatMessage(client)
        # 获取今天日期
        # Date=today.strftime("%Y-%m-%d")
        data = {
            # "Time": {"value": today.strftime("%Y-%m-%d"), "color": get_random_color()},
            "name": {"value": name, "color": get_random_color()},
            "weather": {"value": wea, "color": get_random_color()},
            "temperature": {"value": temperature + "℃", "color": get_random_color()},
            "cityname": {"value": cityName, "color": get_random_color()},
            "winddirection": {"value": winddirection, "color": get_random_color()},
            "love_days": {"value": get_count(start_date), "color": get_random_color()},
            "birthday_left": {"value": get_birthday(birthday), "color": get_random_color()},
            "words": {"value": get_words(), "color": get_random_color()}
        }
        res = wm.send_template(user_id, template_id, data)
        print(res)


wx_push()
