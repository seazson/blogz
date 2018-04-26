from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, g
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, SearchForm
from .. import db
from ..models import Permission, Role, User, Post, Record_json
from ..decorators import admin_required
from datetime import datetime
import os,random
from flask_whooshalchemyplus import index_all

@main.before_request
def before_request():
  g.user = current_user
  g.search_form = SearchForm()

@main.route('/', methods=['GET', 'POST'])#路由
def index():#视图函数
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)#page指明要显示的页
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOGZ_POSTS_PER_PAGE'],
        error_out=False)#根据页来获取页里面的内容
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                           pagination=pagination)#使用模板


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOGZ_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)

#编辑文章
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if id == 0:
        post = Post(body='', author=current_user._get_current_object())#临时分配一个post，还未到数据库中
    else:
        post = Post.query.get_or_404(id)#从数据库中查找一个存在的post
    if current_user != post.author and \
            not current_user.can(Permission.ADMIN):
        abort(403)
    if post.id:
        id=post.id
    form = PostForm()
    rec_json = Record_json()
    rec_json.get_dirs()
    #按下提交按钮的操作
    if form.validate_on_submit():
        urlold = post.url
        post.name = form.name.data
        post.dir = form.dir1.data
        if form.dir2.data != '':
            post.dir +=  '/' + form.dir2.data
        if form.dir3.data != '':
            post.dir +=  '/' + form.dir3.data
        print(post.dir)
        post.tag = form.tag.data
        post.url = current_app.config['DOC_DIR'] +'/'+ post.dir + '/' + post.name + '.html'
        post.hide = 1
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated.')
        #更新json文件
        rec_json.update(post)
        #创建文件
        dirname = os.path.join(current_app.config['DOC_DIR'], form.dir1.data,\
                               form.dir2.data, form.dir3.data)
        if not os.path.exists(dirname) :
            os.makedirs(dirname)
        fh = open(post.url, 'w')
        fh.write(post.body_html)
        fh.close()
        #更改了目录或者文件名
        if urlold != post.url:
            print('dir change')
            if urlold and os.path.exists(urlold):
                os.remove(urlold) #python已经能够自动识别windows和linux路径
                work_path = os.path.dirname(urlold)#如果文件夹为空，删除文件夹
                if not os.listdir(work_path):
                     os.rmdir(work_path)
        return redirect(url_for('.post', id=post.id))
    #如果之前创建过则加载已有信息
    if post.id:
        form.name.data = post.name
        form.tag.data = post.tag
        form.body.data = post.body
        dirsplit = post.dir.split('/')
        slen = len(dirsplit)
        if slen > 0:
            form.dir1.data = dirsplit[0]
        if slen > 1:
            form.dir2.data = dirsplit[1]
        if slen > 2:
            form.dir3.data = dirsplit[2]
    return render_template('edit_post.html', id=id,form=form, dirs=sorted(rec_json.dirs),dirs_list=rec_json.dirs_list)

#删除文章
@main.route('/delete_post/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_post(id):
    rec_json = Record_json()
    rec_json.get_dirs()
    post = Post.query.get_or_404(id)#从数据库中查找一个存在的post
    if current_user != post.author and \
        not current_user.can(Permission.ADMIN):
        abort(403)
    urlold = post.url
    db.session.delete(post)
    db.session.commit()
    rec_json.delete(post)
    if urlold and os.path.exists(urlold):
        os.remove(urlold)
        work_path = os.path.dirname(urlold)
        if not os.listdir(work_path):
             os.rmdir(work_path)
    return render_template('delete_post.html', post=post, dirs=sorted(rec_json.dirs),dirs_list=rec_json.dirs_list)


#显示单个文章
@main.route('/post/<int:id>')
def post(id):
    rec_json = Record_json()
    rec_json.get_dirs()
    post = Post.query.get_or_404(id)
    return render_template('post.html', posts=[post], showpost=1,dir='post',dirs_list=rec_json.dirs_list)

#显示分类文章
@main.route('/dir/<path:dirpath>', methods=['GET', 'POST'])
def dir(dirpath):
    rec_json = Record_json()
    rec_json.get_dirs()
    page = request.args.get('page', 1, type=int)#page指明要显示的页
    print(dirpath)
    pagination = Post.query.filter(Post.dir.startswith(dirpath)).order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOGZ_POSTS_PER_PAGE'],
        error_out=False)#根据页来获取页里面的内容
    posts = pagination.items
    return render_template('post.html', posts=posts, pagination=pagination, dir='.dir/' + dirpath,dirs_list=rec_json.dirs_list)

#显示所有文章
@main.route('/blog', methods=['GET', 'POST'])
def blog():
    rec_json = Record_json()
    rec_json.get_dirs()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOGZ_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('blog.html', posts=posts, pagination=pagination, dir='.blog',dirs_list=rec_json.dirs_list)

#上传文件接口实现
def gen_rnd_filename():
    filename_prefix = datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))

@main.route('/ckupload/', methods=['POST'])
def ckupload():
    """CKEditor file upload"""
    error = ''
    url = ''
    callback = request.args.get("CKEditorFuncNum")
    if request.method == 'POST' and 'upload' in request.files:
        fileobj = request.files['upload']
        fname, fext = os.path.splitext(fileobj.filename)
        rnd_name = '%s%s' % (gen_rnd_filename(), fext)
        filepath = os.path.join(current_app.config['DOC_DIR'],'upload', rnd_name)
        # 检查路径是否存在，不存在则创建
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except:
                error = 'ERROR_CREATE_DIR'
        elif not os.access(dirname, os.W_OK):
            error = 'ERROR_DIR_NOT_WRITEABLE'
        if not error:
            fileobj.save(filepath)
            url = url_for('static', filename='%s/%s' % ('doc/upload', rnd_name))
    else:
        error = 'post error'
    res = """

<script type="text/javascript">
  window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
</script>

""" % (callback, url, error)
    response = make_response(res)
    response.headers["Content-Type"] = "text/html"
    return response

@main.route('/search', methods=['GET', 'POST'])
def search():
    index_all(current_app) #建立查找索引
    if not g.search_form.validate_on_submit():
        return redirect(url_for('.blog'))
    return redirect(url_for('.search_results', query = g.search_form.search.data))

    
@main.route('/search_results/<query>')
def search_results(query):
    rec_json = Record_json()
    rec_json.get_dirs()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.whoosh_search(query, 50).order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOGZ_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('search_results.html', query = query, posts=posts, pagination=pagination, dir='.blog',dirs_list=rec_json.dirs_list)
