blogZ
======
建立环境
    建立虚拟环境，cd到工程目录执行：
    python -m venv venv
    激活虚拟环境
    source venv/bin/activate   (linux环境)
    .venv\Scripts\activate   (windows环境)
    
    安装依赖包
    pip install -r requirements.txt（不好使）
    pip install flask_migrate flask_bootstrap flask_mail flask_moment flask_wtf flask_script flask_login flask_pagedown bleach markdown

    如果要发送邮件的话需要设置环境变量
    export MAIL_USERNAME xx@xx.com
    export MAIL_PASSWORD xxxx
    export MAIL_SERVER smtp.blogz.com
    export MAIL_PORT 25

======
1 创建数据库
    没有migrations目录的话需要执行
    python manage.py db init
    python manage.py db migrate -m "initial migrate"
    
    创建数据库
    python manage.py db upgrade
    
2 在数据库中添加角色模型（可选）
    ./manage.py shell
    >>>Role.insert_roles()

3 从json中导入现存数据（可选）
    Post.json_to_db()

4 运行命令
    ./manage.py runserver -h 127.0.0.1 -p 5000       (linux环境)
    python manage.py runserver -h 127.0.0.1 -p 5000  (windows环境)

5 创建管理账户
    默认是admin@blogz.com
