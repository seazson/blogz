# blogZ

## 建立环境

* 建立虚拟环境，cd到工程目录执行：
```Bash
    python -m venv venv
```

* 激活虚拟环境
```Bash
    source venv/bin/activate   (linux环境)
    .venv\Scripts\activate   (windows环境)
```

* 安装依赖包
```Bash
    pip install -r requirements.txt（不好使）
    pip install flask_migrate flask_bootstrap flask_mail flask_moment flask_wtf flask_script flask_login flask_pagedown bleach markdown Flask-WhooshAlchemyplus jieba
```

* 如果要发送邮件的话需要设置环境变量
```Bash
    export MAIL_USERNAME xx@xx.com
    export MAIL_PASSWORD xxxx
    export MAIL_SERVER smtp.blogz.com
    export MAIL_PORT 25
```

## 使用

### 1 创建数据库
没有migrations目录的话需要执行<br>
```Bash
    python manage.py db init
    python manage.py db migrate -m "initial migrate"
```
创建数据库<br>
```Bash
    python manage.py db upgrade
```
### 2 在数据库中添加角色模型（可选）
```Bash
    ./manage.py shell
    >>>Role.insert_roles()
```
### 3 从json中导入现存数据（可选）
```Bash
    Post.json_to_db()
```
### 4 运行命令
```Bash
    ./manage.py runserver -h 127.0.0.1 -p 5000       (linux环境)
    python manage.py runserver -h 127.0.0.1 -p 5000  (windows环境)
```
### 5 创建管理账户
默认是admin@blogz.com<br>
