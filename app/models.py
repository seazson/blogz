from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach
from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin, current_user
from . import db, login_manager
import json, os
import time
import flask_whooshalchemyplus
from jieba.analyse.analyzer import ChineseAnalyzer

class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16
#定义了数据库中存放的角色和用户
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles(): #类方法，需要手动执行，用于添加角色类型
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT,
                          Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT,
                              Permission.WRITE, Permission.MODERATE,
                              Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name

class Record_json():
    recs =[]
    dirs = []
    dirs_split = []
    dirs_list = []  #每个元素都是一个字典，包含了主级目录及下面的目录列表信息，例如
                    #[{'name': 'linux', 'list': [[2, 'linux', '内存管理', '']]}, 
                    #{'name': 'x86', 'list': [[2, 'x86', '1', ''], [3, 'x86', '1', '1'], [2, 'x86', '2', '']]}]
    jsonfile = os.path.join('app', 'static', 'doc', 'data.json')

    def __init__(self, **kwargs):
        if not os.path.exists(os.path.dirname(self.jsonfile)):
            os.makedirs(os.path.dirname(self.jsonfile))
        if not os.path.exists(self.jsonfile):
            fd = open(self.jsonfile, 'w', encoding='utf-8')
            fd.write('[]')
            fd.close()
            
    def save(self):
        with open(self.jsonfile, 'w', encoding='utf-8') as f:
            json.dump(self.recs, f)

    def load(self):
        with open(self.jsonfile, 'r', encoding='utf-8') as f:
            self.recs = json.load(f)
        #print(self.recs)

    def update(self, post):
        self.load()
        rec = {}
        rec['id'] = post.id
        rec['name'] = post.name
        rec['dir'] = post.dir
        rec['tag'] = post.tag
        rec['url'] = post.url
        rec['auth'] = post.author_id
        rec['hide'] = post.hide
        rec['createtime'] = post.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        rec['updatetime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        for rec_dict in self.recs:
            if rec_dict['id'] == rec['id']:
                self.recs.remove(rec_dict);
        self.recs.append(rec);
        self.save()

    def delete(self, post):
        self.load()
        for rec_dict in self.recs:
            if rec_dict['id'] == post.id:
                self.recs.remove(rec_dict);
        self.save()

    def update_by_url(self, post):#用于从数据库中导出到json文件中
        self.load()
        rec = {}
        rec['id'] = post.id
        rec['name'] = post.name
        rec['dir'] = post.dir
        rec['tag'] = post.tag
        rec['url'] = post.url
        rec['auth'] = post.author_id
        rec['hide'] = post.hide
        rec['createtime'] = post.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        rec['updatetime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        for rec_dict in self.recs:
            if rec_dict['url'] == rec['url']:
                self.recs.remove(rec_dict);
        self.recs.append(rec);
        self.save()
        
    def find_by_id(self, id):
        self.load()
        for rec_dict in self.recs:
            if rec_dict['id'] == id:
                return rec_dict

    def get_dirs(self):
        self.load()
        for rec_dict in self.recs:
            if rec_dict['dir'] not in self.dirs:
                self.dirs.append(rec_dict['dir'])#获取总共有多少种dir类型
        for pathname in self.dirs:
            self.dirs_split.append(pathname.split("/"))
        tdir1=''
        tdir2=''
        tdir3=''
        indir=0
        self.dirs_list=[]
        dir_dict = {'name':'','list':[]}
        for dir_split in sorted(self.dirs_split):#对每个dir进行分解
            slen = len(dir_split)
            if slen > 0:
                if tdir1 != dir_split[0]:
                    print(dir_split[0])
                    tdir1 = dir_split[0]
                    if indir == 1:
                        self.dirs_list.append(dir_dict.copy())
                        dir_dict['name'] = dir_split[0]
                        dir_dict['list'] = []
                    elif indir == 0:
                        dir_dict['name'] = dir_split[0]
                        dir_dict['list'] = []
                        indir = 1
                    
            
            if slen > 1:
                if tdir2 != dir_split[1]:
                    print('_' + dir_split[1])
                    tdir2 = dir_split[1]
                    dir_dict['list'].append([2,tdir1,dir_split[1],''])

            if slen > 2:
                if tdir3 != dir_split[2]:
                    print('__' + dir_split[2])
                    tdir3 = dir_split[2]
                    dir_dict['list'].append([3,tdir1,tdir2,dir_split[2]])
        self.dirs_list.append(dir_dict.copy())
        print(self.dirs_list)#建立起要创建的dir顺序和层级

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['BLOGZ_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = self.gravatar_hash()
        db.session.add(self)
        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def ping(self):#更新最后访问时间
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size=100, default='identicon', rating='g'):
        url = 'https://secure.gravatar.com/avatar'
        hash = self.avatar_hash or self.gravatar_hash()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def userpic(self,size):
        if size == 256:
            return url_for('static', filename='admin.png')
        else :
            return url_for('static', filename='admin.jpg')

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__ = 'posts'
    __searchable__ = ['body','name']
    __analyzer__ = ChineseAnalyzer()

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updatetime = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(128), index=True)
    dir = db.Column(db.String(128), index=True)
    tag = db.Column(db.String(128))
    hide = db.Column(db.Integer)
    url = db.Column(db.String(256))

    def __init__(self, **kwargs):
        super(Post, self).__init__(**kwargs)

    def __repr__(self):
        return '<Post {}>'.format(self.body)
    
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        #target.body_html = bleach.linkify(bleach.clean(
        #    markdown(value, output_format='html'),
        #    tags=allowed_tags, strip=False)) #将用户写入的文档转换成html格式，并且过滤掉不允许的标签
        target.body_html = value

    @staticmethod
    def json_to_db():
        rec_json = Record_json()
        rec_json.load()
        for rec_dict in rec_json.recs:
            post = Post.query.get(rec_dict['id'])#从数据库中查找一个存在的post        
            if not post:
                post = Post()
            else:
                post.id = rec_dict['id']
            post.name = rec_dict['name']
            post.dir = rec_dict['dir']
            post.tag = rec_dict['tag'] 
            post.url = rec_dict['url']
            post.hide = rec_dict['hide']
            post.author_id = rec_dict['auth']
            post.timestamp = datetime.strptime(rec_dict['createtime'], '%Y-%m-%d %H:%M:%S')
            post.timestamp = datetime.strptime(rec_dict['updatetime'], '%Y-%m-%d %H:%M:%S')
            if post.url and os.path.exists(post.url):
                fd = open(post.url, 'r', encoding='utf-8')
                post.body = fd.read()
            db.session.add(post)
            db.session.commit()
        
    @staticmethod
    def db_to_json():
        rec_json = Record_json()
        posts = Post.query.order_by(Post.id).all()
        for post in posts:
            rec_json.update_by_url(post)
            if not os.path.exists(os.path.dirname(post.url)) :
                os.makedirs(os.path.dirname(post.url))
            fh = open(post.url, 'w', encoding='utf-8')
            fh.write(post.body)
            fh.close()
        
db.event.listen(Post.body, 'set', Post.on_changed_body) #在数据库写body字段时触发

