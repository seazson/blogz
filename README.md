blogZ
======

建立环境
---
    建立虚拟环境，cd到工程目录执行：<br>
    python -m venv venv<br>
    激活虚拟环境<br>
    source venv/bin/activate   (linux环境)<br>
    .venv\Scripts\activate   (windows环境)<br>
    
    安装依赖包<br>
    pip install -r requirements.txt（不好使）<br>
    pip install flask_migrate flask_bootstrap flask_mail flask_moment flask_wtf flask_script flask_login flask_pagedown bleach markdown Flask-WhooshAlchemyplus jieba<br>

    如果要发送邮件的话需要设置环境变量<br>
    export MAIL_USERNAME xx@xx.com<br>
    export MAIL_PASSWORD xxxx<br>
    export MAIL_SERVER smtp.blogz.com<br>
    export MAIL_PORT 25<br>

使用
---
1 创建数据库
    没有migrations目录的话需要执行<br>
    python manage.py db init<br>
    python manage.py db migrate -m "initial migrate"<br>
    
    创建数据库<br>
    python manage.py db upgrade<br>
    
2 在数据库中添加角色模型（可选）
    ./manage.py shell<br>
    >>>Role.insert_roles()<br>

3 从json中导入现存数据（可选）
    Post.json_to_db()<br>

4 运行命令
    ./manage.py runserver -h 127.0.0.1 -p 5000       (linux环境)<br>
    python manage.py runserver -h 127.0.0.1 -p 5000  (windows环境)<br>

5 创建管理账户
    默认是admin@blogz.com<br>
