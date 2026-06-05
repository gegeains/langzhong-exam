from flask import Flask, render_template_string, request
import sqlite3
import time
import pandas as pd
import os

app = Flask(__name__)
DB_NAME = "ai_study.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user
    (id INTEGER PRIMARY KEY AUTOINCREMENT,phone TEXT,grade TEXT,weak_sub TEXT,createtime TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS question
    (id INTEGER PRIMARY KEY AUTOINCREMENT,subject TEXT,grade TEXT,q_type TEXT,knowledge TEXT,q_content TEXT,answer TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS report
    (id INTEGER PRIMARY KEY AUTOINCREMENT,phone TEXT,score INT,wrong_know TEXT,suggest TEXT,createtime TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS exercise
    (id INTEGER PRIMARY KEY AUTOINCREMENT,subject TEXT,grade TEXT,knowledge TEXT,ex_q TEXT,ex_ans TEXT)''')

    six_grade = [
        ("数学","六年级","选择题","行程问题","甲乙400米跑道同向，甲240米/分乙200米/分多久追上？A10 B20 C30","A"),
        ("数学","六年级","判断题","折扣百分数","一件商品八五折=原价×0.85。","对"),
        ("数学","六年级","填空题","圆柱体积","r=2cm h=10cm π=3.14，体积=____","125.6"),
        ("数学","六年级","选择题","分数应用题","360人3/5公办，公办人数A216 B150 C144","A"),
        ("数学","六年级","判断题","盈亏应用题","每班35剩20，每班40缺15，共7个班。","对"),
        ("数学","六年级","填空题","百分数","120的25%是多少","30"),
        ("数学","六年级","选择题","长方体体积","长5宽4高3体积A60 B12 C20","A"),
        ("数学","六年级","判断题","倒数","1的倒数是1，0没有倒数。","对"),
        ("数学","六年级","填空题","比例","3:4=():12","9"),
        ("数学","六年级","选择题","利息","本金1000年利率3%一年利息A30 B300 C3","A"),
        ("语文","六年级","填空题","古诗文默写","独在异乡为异客，________","每逢佳节倍思亲"),
        ("语文","六年级","选择题","成语填空","()辕()辙 A南北 B东西 C前后","A"),
        ("语文","六年级","判断题","病句辨析","全班基本全部到齐是病句。","对"),
        ("语文","六年级","填空题","古诗文","举头望明月，________","低头思故乡"),
        ("语文","六年级","选择题","近义词","突然A忽然B果然C竟然","A"),
        ("语文","六年级","判断题","修辞手法","飞流直下三千尺用了夸张。","对"),
        ("语文","六年级","填空题","成语","千里之行，________","始于足下"),
        ("语文","六年级","选择题","标点","陈述句末尾用A。B！C？","A"),
        ("语文","六年级","判断题","文学常识","《静夜思》作者李白。","对"),
        ("英语","六年级","填空题","一般现在时","I often ____(play) football","play"),
        ("英语","六年级","选择题","名词复数","box复数Aboxs Bboxes Cbox","B"),
        ("英语","六年级","判断题","介词","in+年月份是正确用法。","对"),
        ("英语","六年级","填空题","人称代词","____(我) am a student","I"),
        ("英语","六年级","选择题","疑问词","____is your name?AWhat BHow CWhere","A"),
        ("英语","六年级","判断题","时态","every day搭配一般现在时。","对"),
        ("英语","六年级","填空题","冠词","This is ___ apple","an")
    ]
    nine_grade = [
        ("数学","初三","选择题","一元二次方程","x²-5x+6=0解A2,3 B1,6 C-2,-3","A"),
        ("数学","初三","判断题","二次函数","y=x²-2x-3顶点横坐标是1。","对"),
        ("数学","初三","填空题","利润应用题","进价20售价32，涨1元少卖8，日利润1280定价____","34"),
        ("数学","初三","选择题","勾股定理","直角边3、4斜边A5 B6 C7","A"),
        ("数学","初三","判断题","三角函数","直角三角形sin对边/斜边。","对"),
        ("数学","初三","填空题","因式分解","x²-9=____","(x+3)(x-3)"),
        ("数学","初三","选择题","反比例函数","y=3/x图像在A1、3象限B2、4象限","A"),
        ("数学","初三","判断题","相似三角形","相似三角形对应边成比例。","对"),
        ("数学","初三","填空题","一元一次不等式","2x>6解集____","x>3"),
        ("数学","初三","选择题","概率","骰子掷出奇数概率A1/2 B1/3 C1/6","A"),
        ("语文","初三","填空题","文言文默写","春蚕到死丝方尽，________","蜡炬成灰泪始干"),
        ("语文","初三","选择题","名著常识","及时雨A宋江 B李逵 C武松","A"),
        ("语文","初三","判断题","文言虚词","之可作代词、助词。","对"),
        ("语文","初三","填空题","古诗文","落红不是无情物，________","化作春泥更护花"),
        ("语文","初三","选择题","病句","选出无语病A通过努力成绩提升B大约左右重复","A"),
        ("语文","初三","判断题","文体","议论文三要素：论点论据论证。","对"),
        ("语文","初三","填空题","古诗词","但愿人长久，________","千里共婵娟"),
        ("语文","初三","选择题","词语辨析","矗立形容A建筑B人物C河流","A"),
        ("语文","初三","判断题","作者","《岳阳楼记》范仲淹。","对"),
        ("英语","初三","填空题","被动语态","Many trees ____(plant) every year","are planted"),
        ("英语","初三","判断题","过去完成时","by+过去时间用过完。","对"),
        ("英语","初三","选择题","连词","I like apples ___bananas Aand Bbut Cor","A"),
        ("英语","初三","填空题","非谓语","stop ____(do)休息一下，填to do","to do"),
        ("英语","初三","判断题","时态","since+过去时主句现在完成时。","对"),
        ("英语","初三","选择题","代词","This book is ___(我的)Amine Bmy CI","A"),
        ("英语","初三","填空题","比较级","tall比较级____","taller")
    ]
    all_question = six_grade + nine_grade

    all_exercise = [
        ("数学","六年级","行程问题","两人相距200米同向，快5m/s慢3m/s多久追上？填空","100"),
        ("数学","六年级","折扣百分数","鞋子200元七五折售价？","150"),
        ("数学","六年级","圆柱体积","r=3 h=5 π=3.14体积","141.3"),
        ("语文","六年级","古诗文默写","遥知兄弟登高处，____","遍插茱萸少一人"),
        ("数学","初三","一元二次方程","x²-7x+12=0解","3,4"),
        ("数学","初三","勾股定理","直角边5,12斜边","13"),
        ("语文","初三","文言文默写","落红不是无情物，____","化作春泥更护花")
    ]

    for item in all_question:
        c.execute("INSERT OR IGNORE INTO question(subject,grade,q_type,knowledge,q_content,answer) VALUES (?,?,?,?,?,?)",item)
    for ex in all_exercise:
        c.execute("INSERT OR IGNORE INTO exercise(subject,grade,knowledge,ex_q,ex_ans) VALUES (?,?,?,?,?)",ex)
    conn.commit()
    conn.close()

init_db()

INDEX_HTML = '''
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-size:16px;}
body{padding:15px;background:#f7f8fa;}
.box{background:#fff;padding:20px;border-radius:12px;max-width:600px;margin:0 auto;}
h2{font-size:20px;color:#222;margin-bottom:20px;text-align:center;}
input,select{width:100%;height:44px;margin:8px 0 16px;padding:0 10px;border:1px #ddd solid;border-radius:6px;}
button{width:100%;height:48px;background:#2578f5;color:#fff;border:none;border-radius:6px;font-size:17px;}
</style>
<div class="box">
    <h2>阆中小升初/初升高AI全科测评</h2>
    <form action="/register" method="post">
        <label>家长手机号</label>
        <input type="text" name="phone" required placeholder="请填写手机号">
        <label>在读年级</label>
        <select name="grade">
            <option>六年级</option>
            <option>初三</option>
        </select>
        <label>薄弱科目（语/数/英）</label>
        <input name="weak_sub" placeholder="例如：数学">
        <button type="submit">开始免费测评</button>
    </form>
</div>
'''

TEST_HTML = '''
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-size:16px;}
body{padding:12px;background:#f7f8fa;}
.box{background:#fff;padding:16px;border-radius:12px;max-width:600px;margin:0 auto;}
h3{text-align:center;margin-bottom:18px;font-size:19px;}
.item{margin-bottom:22px;padding-bottom:12px;border-bottom:#eee solid 1px;}
.tip{color:#0984e3;font-size:13px;margin-bottom:6px;}
input{width:100%;height:42px;border:1px #ddd solid;border-radius:6px;padding:0 10px;}
button{width:100%;height:48px;background:#2578f5;color:#fff;border:none;border-radius:6px;font-size:17px;margin-top:10px;}
</style>
<div class="box">
<h3>在线全科测评试卷</h3>
<form action="/submit_paper" method="post">
<input hidden name="phone" value="{{phone}}">
{% for item in q_list %}
<div class="item">
    <div class="tip">{{loop.index}}｜{{item[1]}}｜{{item[3]}}【{{item[4]}}】</div>
    <div>{{item[5]}}</div>
    <input name="ans_{{item[0]}}" placeholder="填写答案">
</div>
{% endfor %}
<button type="submit">提交试卷，生成AI查漏报告</button>
</form>
</div>
'''

REPORT_HTML = '''
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-size:16px;}
body{padding:12px;background:#f7f8fa;}
.box{background:#fff;padding:16px;border-radius:12px;max-width:600px;margin:0 auto;}
h2,h3{text-align:center;margin:12px 0;}
.info{padding:8px 0;border-bottom:#eee solid 1px;}
.ex{margin:10px 0;padding:8px;background:#f6f8ff;border-radius:6px;font-size:15px;}
.suggest{color:#1976d2;padding:10px;background:#eef5ff;border-radius:6px;margin-top:15px;}
</style>
<div class="box">
    <h2>✅ AI智能测评报告</h2>
    <div class="info">手机号：{{phone}}</div>
    <div class="info">本次得分：{{score}}分</div>
    <div class="info">薄弱知识点：{{wrong_know}}</div>
    <hr>
    <h3>📌 AI推荐·查漏补缺练习题</h3>
    {% for item in ex_list %}
    <div class="ex">【{{item[0]}}-{{item[1]}}｜{{item[2]}}】{{item[3]}}<br>参考答案：{{item[4]}}</div>
    {% endfor %}
    <div class="suggest">{{suggest}}</div>
    <p style="margin-top:15px;font-size:14px;color:#666">测评信息已存档，辅导老师后续联系您规划补习</p>
</div>
'''

@app.route('/')
def home():
    return render_template_string(INDEX_HTML)

@app.route('/register',methods=["POST"])
def register():
    phone = request.form["phone"].strip()
    grade = request.form["grade"]
    weak_sub = request.form["weak_sub"]
    create_time = time.strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO user(phone,grade,weak_sub,createtime) VALUES (?,?,?,?)",(phone,grade,weak_sub,create_time))
    q_data = cur.execute("SELECT * FROM question WHERE grade=?",(grade,)).fetchall()
    conn.commit()
    conn.close()
    return render_template_string(TEST_HTML,phone=phone,q_list=q_data)

@app.route('/submit_paper',methods=["POST"])
def submit_paper():
    phone = request.form["phone"]
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    all_q = cur.execute("SELECT id,answer,knowledge FROM question").fetchall()
    score = 0
    wrong_know_set = set()
    per_score = 5
    for qid,std_ans,know in all_q:
        user_ans = request.form.get(f"ans_{qid}","").strip()
        if user_ans == std_ans.strip():
            score += per_score
        else:
            wrong_know_set.add(know)
    wrong_str = ",".join(wrong_know_set) if wrong_know_set else "无薄弱知识点"
    ex_data = []
    if wrong_know_set:
        sql_ex = "SELECT * FROM exercise WHERE knowledge IN ({})".format(','.join(['?']*len(wrong_know_set)))
        ex_data = cur.execute(sql_ex,tuple(wrong_know_set)).fetchall()
    if wrong_know_set:
        suggest = f"AI学习建议：优先完成上方针对性习题，重点巩固【{wrong_str}】薄弱内容，是补习提分关键"
    else:
        suggest = "全科掌握优秀，坚持日常刷题保持水平即可"
    cur.execute('''INSERT INTO report(phone,score,wrong_know,suggest,createtime)
    VALUES (?,?,?,?,?)''',(phone,score,wrong_str,suggest,time.strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    return render_template_string(REPORT_HTML,phone=phone,score=score,wrong_know=wrong_str,suggest=suggest,ex_list=ex_data)

@app.route('/export')
def export_customer():
    conn = sqlite3.connect(DB_NAME)
    sql = '''
    SELECT u.phone,u.grade,u.weak_sub,r.score,r.wrong_know,r.suggest
    FROM user u LEFT JOIN report r ON u.phone=r.phone
    WHERE u.grade IN ("六年级","初三") AND u.weak_sub != ""
    '''
    df = pd.read_sql(sql,conn)
    save_name = "AI测评_高意向家长名单.xlsx"
    df.to_excel(save_name,index=False)
    conn.close()
    return f'导出成功，共{len(df)}位意向家长，文件：{save_name}'
# =========后台admin 账号yangyan 密码131452wjc========
from flask import session,redirect,url_for

@app.route('/admin',methods=["GET","POST"])
def admin_login():
    if session.get("admin_ok"):
        return admin_home()
    if request.method=="POST":
        u = request.form["username"]
        p = request.form["password"]
        if u == "yangyan" and p == "131452wjc":
            session["admin_ok"]=True
            return redirect(url_for("admin_home"))
        return '''
        <form method="post">
        账号错误<br>
        账号:<input name=username><br>
        密码:<input type=password name=password><button>登录</button>
        </form>
        '''
    return '''
    <form method="post">
    <h3>管理员登录</h3>
    账号:<input name="username"><br>
    密码:<input type="password" name="password"><br>
    <button>登录后台</button>
    </form>
    '''

@app.route("/admin/home")
def admin_home():
    if not session.get("admin_ok"):
        return redirect(url_for("admin_login"))
    return '''
    <h3>家长数据后台</h3>
    <a href="/export">点击导出全部家长Excel</a>
    <br><a href="/admin/logout">退出登录</a>
    '''

@app.route("/admin/logout")
def logout():
    session.pop("admin_ok",None)
    return redirect(url_for("admin_login"))
if __name__ == '__main__':
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port,debug=False)
