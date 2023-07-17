# -*- coding: utf-8 -*-

from flask import Flask, request, render_template
import requests
import mysql.connector
app = Flask(__name__)

@app.route('/myaccount', methods=['GET'])
def handle_wechat_redirect():
    # 获取 URL 中的 code 参数
    code = request.args.get('code')
    if not code:
        return 'Missing code parameter', 400

    # 使用 code 获取 access_token 和 openid
    url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
    params = {
        'appid': 'wxa31121df217466fd',
        'secret': '23f9655e97542d4230a1ac9eea819ee7',
        'code': code,
        'grant_type': 'authorization_code'
    }
    response = requests.get(url, params=params)
    response_json = response.json()

    # 从响应中获取 access_token 和 openid
    access_token = response_json.get('access_token')
    openid = response_json.get('openid')

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
    usage_records = get_usage_records(openid)
    # 使用 render_template 函数来渲染 user_account.html 模板
    return render_template('myaccount.html',nickname=nickname,headimgurl=headimgurl,records=usage_records)
def get_usage_records(openid):
    # 连接到数据库
    cnx = mysql.connector.connect(user='root', password='mysql@123',
                                  host='127.0.0.1',
                                  database='myaccount')

    cursor = cnx.cursor()

    # 创建查询语句
    query = ("SELECT usage_time, type, model, token_length "
             "FROM usage_records "
             "WHERE openid = %s")

    # 执行查询
    cursor.execute(query, (openid,))

    # 获取查询结果
    records = []
    for (usage_time, usage_type, model, token_length) in cursor:
        record = {
            'usage_time': usage_time,
            'type': usage_type,
            'model': model,
            'token_length': token_length
        }
        records.append(record)

    # 关闭游标和连接
    cursor.close()
    cnx.close()

    return records
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)    
