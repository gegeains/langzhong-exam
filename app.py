from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3
import time
import pandas as pd
import os

app = Flask(__name__)
# 修复500报错：会话密钥
app.secret_key = "exam2025_admin_889966"
DB_NAME = "ai_study.db"

# 初始化数据库
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # 用户表
    c.execute('''CREATE TABLE IF NOT EXISTS user
    (id INTEGER PRIMARY KEY AUTOINCREMENT,phone TEXT,grade TEXT,weak_sub TEXT,createtime TEXT)''')
    # 题目表
    c.execute('''CREATE TABLE IF NOT EXISTS question
    (id INTEGER PRIMARY KEY AUTOINCREMENT,subject TEXT,grade TEXT,q_type TEXT,knowledge TEXT,q_content TEXT,answer TEXT)''')
    # 作答记录表
    c.execute('''CREATE TABLE IF NOT EXISTS report
    (id INTEGER PRIMARY KEY AUTOINCREMENT,phone TEXT,score INT,wrong_know TEXT,suggest TEXT,createtime TEXT)''')
    conn.commit()
    conn.close()

# 六年级题库
six_grade = [
("数学","六年级","判断题","折扣百分数","一件商品八五折=原价×85%","对"),
("数学","六年级","填空题","圆柱体积","r=2cm h=10cm π=3.14，体积=____","125.6"),
("数学","六年级","选择题","分数应用题","360人3/5公办，公办人数A216 B150 C30","A"),
("数学","六年级","判断题","盈亏应用题","每班35剩20，每班45缺15，共7个班。","对"),
("数学","六年级","填空题","百分数","12的25%是多少","3"),
("数学","六年级","选择题","长方体体积","长5宽4高3体积A60 B120 C20","A"),
("语文","六年级","填空题","古诗文默写","独在异乡为异客，____，每逢佳节倍思亲","每逢佳节倍思亲"),
("语文","六年级","选择题","成语填空","()辕()辙 A南北 B东西 C前后","A"),
]

# 首页做题页面
@app.route('/',methods=["GET","POST"])
def index():
    init_db()
    if request.method == "POST":
        phone = request.form.get("phone")
        grade = request.form.get("grade")
        weak_sub = request.form.get("weak_sub")
        ex_list = six_grade
        wrong_str = ""
        score = 0
        wrong_know = []
        for q in ex_list:
            user_ans = request.form.get(q[0]+q[2]+q[4],"")
            if user_ans == q[5]:
                score += 10
            else:
                wrong_str += q[3]+"、"
                wrong_know.append(q[3])
        suggest = "薄弱知识点："+wrong_str.strip("、")
        now_time = time.strftime("%Y-%m-%d %H:%M:%S")
        # 入库用户
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("insert into user(phone,grade,weak_sub,createtime) values (?,?,?,?)",(phone,grade,weak_sub,now_time))
        cur.execute("insert into report(phone,score,wrong_know,suggest,createtime) values (?,?,?,?,?)",(phone,score,str(wrong_know),suggest,now_time))
        conn.commit()
        conn.close()
        return render_template_string('''
        <h3>测评完成</h3>
        <p>得分：{{score}}分</p>
        <p>{{suggest}}</p>
        <a href="/">返回首页</a>
        ''',score=score,suggest=suggest)

    html = '''
    <h2>小升初学科测评</h2>
    <form method="post">
    家长手机号：<input name="phone" required><br><br>
    就读年级：
    <select name="grade">
    <option value="六年级">六年级</option>
    <option value="初三">初三</option>
    </select><br><br>
    薄弱学科：<input name="weak_sub" placeholder="数学/语文" required><hr>
    '''
    for item in six_grade:
        sub,tg,ttype,know,qcont,ans = item
        html += f"<p>{qcont}</p>"
        html += f'<input name="{sub}{ttype}{qcont}" placeholder="填写答案"><br>'
    html += '''<button type="submit">提交测评</button></form>'''
    return html

# 导出全部家长Excel
@app.route('/export')
def export_customer():
    conn = sqlite3.connect(DB_NAME)
    sql = '''
    SELECT u.phone,u.grade,u.weak_sub,r.score,r.wrong_know,r.suggest
    FROM user u LEFT JOIN report r ON u.phone=r.phone
    WHERE u.grade IN ("六年级","初三") AND u.weak_sub != ""
    '''
    df = pd.read_sql(sql,conn)
    save_name = "AI测评_意向家长名单.xlsx"
    df.to_excel(save_name,index=False)
    conn.close()
    return f'导出成功，共{len(df)}位意向家长，文件：{save_name}'

# =========管理员后台【手机号登录：账号填家长手机号，固定密码：131452wjc】========
@app.route('/admin',methods=["GET","POST"])
def admin_login():
    if session.get("admin_ok"):
        return admin_home()
    if request.method=="POST":
        phone = request.form["phone"]
        pwd = request.form["password"]
        # 登录规则：任意手机号+固定密码131452wjc即可进后台
        if len(phone)>=11 and pwd=="131452wjc":
            session["admin_ok"]=True
            return redirect(url_for("admin_home"))
        return '''
        <form method="post">
        <h3>登录失败：手机号或密码错误</h3>
        管理员手机号：<input name="phone" placeholder="填写手机号"><br>
        登录密码：<input type="password" name="password"><br>
        <button>登录后台</button>
        </form>
        '''
    # 登录页：手机+密码
    return '''
    <form method="post">
    <h3>测评数据后台登录</h3>
    管理员手机号：<input name="phone" placeholder="输入11位手机号"><br><br>
    登录密码：<input type="password" name="password" placeholder="固定密码131452wjc"><br><br>
    <button type="submit">进入数据后台</button>
    </form>
    '''

@app.route("/admin/home")
def admin_home():
    if not session.get("admin_ok"):
        return redirect(url_for("admin_login"))
    return '''
    <h3>意向家长数据管理中心</h3>
    <p><a href="/export">👉一键下载全部Excel家长名单</a></p>
    <p><a href="/admin/logout">退出登录</a></p>
    '''

@app.route("/admin/logout")
def logout():
    session.pop("admin_ok",None)
    return redirect(url_for("admin_login"))

if __name__ == '__main__':
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port,debug=False)
