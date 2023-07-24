# -*- coding: utf-8 -*-

from flask import Flask, request, render_template, Blueprint, jsonify, redirect,session
import requests
from db_manager import DatabaseManager
from hupijiao_pay import Hupi
from datetime import datetime
import config
import uuid
import json
import logging

app = Flask(__name__, static_url_path='/static')
api = Blueprint('api', __name__, url_prefix='/api')
app.secret_key = config.session_secret_key  # 请更改为你自己的秘钥
app.logger.setLevel(logging.INFO)  # 设置日志级别为 INFO
handler = logging.StreamHandler()  # 创建一个流处理器
app.logger.addHandler(handler)  # 将流处理器添加到 logger
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # 创建一个日志格式器
handler.setFormatter(formatter)  # 将日志格式器设置为流处理器的格式器
@api.route('/myaccount', methods=['GET'])
def handle_wechat_redirect():
    # 获取 URL 中的 code 参数
    code = request.args.get('code')
    if not code:
        return 'Missing code parameter', 400
    app.secret_key = generate_order_id()
    # 使用 code 获取 access_token 和 openid
    url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
    params = {
        'appid': config.wechatmp_app_id,
        'secret': config.wechatmp_app_secret,
        'code': code,
        'grant_type': 'authorization_code'
    }
    response = requests.get(url, params=params)
    response_json = response.json()

    # 从响应中获取 access_token 和 openid
    access_token = response_json.get('access_token')
    session['openid'] = response_json.get('openid')
    openid = session.get('openid')
    userinfo_url = 'https://api.weixin.qq.com/sns/userinfo'
    params = {
        'access_token': access_token,
        'openid': openid,
        'lang': 'zh_CN'
    }
    try:
        response = requests.get(userinfo_url, params=params)
        response_json = response.json()
        nickname = response_json.get('nickname').encode('latin1').decode('utf-8')
        headimgurl = response_json.get('headimgurl')
    except requests.RequestException as e:
        print(f"Error occurred during request: {e}")
        # Handle the exception as you see fit here.
    except (UnicodeEncodeError, UnicodeDecodeError) as e:
        print(f"Error occurred during encoding/decoding: {e}")
        # Handle the exception as you see fit here.
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Handle the exception as you see fit here.

    if not access_token or not openid:
        return 'Failed to get access_token or openid', 400

    # 在这里，你可以使用获取到的 access_token 和 openid 实现用户的登录
    # 例如，你可以从数据库中获取用户的数据
    usage_records, user_balance = DatabaseManager().get_user_records_balance(openid)
    # 使用 render_template 函数来渲染 user_account.html 模板
    return render_template('myaccount.html', nickname=nickname, headimgurl=headimgurl, records=usage_records,
                           user_balance=user_balance)
def generate_order_id() -> object:
    # Get current date as string in the format YYYYMMDD
    date_str = datetime.now().strftime('%Y%m%d')

    # Generate a random UUID, convert it to a string, and take the first 24 characters
    # UUID is 36 characters long (including hyphens), so this leaves us with 24 characters after removing hyphens
    # This ensures that the total length of the order ID (date + UUID) does not exceed 32 characters
    uuid_str = str(uuid.uuid4()).replace('-', '')[:24]

    # Combine date and UUID to create order ID
    order_id = date_str + uuid_str

    return order_id


@api.route('/pay', methods=['POST'])
def handle_pay():
    # 从请求中获取JSON数据
    data = request.get_json()
    # 通过键来访问字典中的值
    price = data.get('price')
    attach_json = {
        "openid": session.get('openid'),
        "price": data.get('price'),
        "tokens": data.get('tokens')
    }
    attach = json.dumps(attach_json)
    obj = Hupi()
    r = obj.Pay(generate_order_id(), "wechat", price, "隽戈智能",attach)
    response_data = r.json()  # 假设 r 包含了 JSON 数据
    # 提取出跳转URL
    url = response_data.get('url')
    # 返回包含跳转URL的JSON数据
    return jsonify({"url": url}), r.status_code


@api.route('/wechat_pay_notify', methods=['POST'])
def handle_wechat_pay_notify():
    if request.method == 'POST':
        # 获取POST数据
        post_data = request.form
        # 打印所有的参数
        app.logger.info("Received parameters: %s", post_data)

        # 在这里执行你的业务逻辑，例如验证签名，更新订单状态等
        # ...

        # 返回 "success" 字符串
        return "success"
@api.route('/redirect', methods=['GET'])
def handle_redirect():
    # 这里构造你的微信授权URL
    wechat_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxa31121df217466fd&redirect_uri=https://bot.jungeclub.club/api/myaccount&response_type=code&scope=snsapi_userinfo&state=STATE&connect_redirect=1#wechat_redirect'

    # 使用 flask.redirect 函数来重定向到微信授权的URL
    return redirect(wechat_url)


app.register_blueprint(api)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)