import datetime
from math import ceil
from os import abort

from flask import Blueprint, redirect, request, render_template, session

from libs.orm import db
from libs.utils import login_required
from article.models import Article, Comment, Thumb
from user.models import Follow

article_bp = Blueprint('article', __name__, url_prefix='/article')
article_bp.template_folder = './templates'


@article_bp.route('/index')
def index():
    page = int(request.args.get('page', 1))
    per_page = 30
    offset = per_page * (page - 1)
    art_list = Article.query.order_by(Article.updated.desc()).limit(per_page).offset(offset)

    max_page = ceil(Article.query.count() / per_page)

    if page <= 3:
        start, end = 1, 7
    elif page > (max_page - 3) and max_page > 6:
        start, end = max_page - 6, max_page
    else:
        start, end = (page - 3), (page + 3)

    pages = range(start, end + 1)
    return render_template('index.html', art_list=art_list, pages=pages, page=page)


@article_bp.route('/post', methods=('POST', 'GET'))
@login_required
def post_article():
    if request.method == 'POST':
        uid = session['uid']
        content = request.form.get('content', '').strip()
        now = datetime.datetime.now()


        if not content:
            return render_template('post.html', err='微博内容不允许为空')

        article = Article(uid=uid, content=content, created=now, updated=now)
        db.session.add(article)
        db.session.commit()
        return redirect('/article/read?aid=%s' % article.id)
    else:
        return render_template('post.html')


@article_bp.route('/read')
def read():
    """阅读微博"""
    aid = int(request.args.get('aid'))
    article = Article.query.get(aid)
    article.n_thumb = Thumb.query.filter_by(aid=aid).count()


    #获取当前所有微博的评论
    comments = Comment.query.filter_by(aid=aid).order_by(Comment.created.desc())

    #判断自己是否点过赞
    uid = session.get('uid')
    if uid:
        if Thumb.query.filter_by(uid=uid, aid=aid).count():
            is_liked = True
        else:
            is_liked = False
    else:
        is_liked  = False

    return render_template('read.html', article=article, comments=comments, is_liked=is_liked)


@article_bp.route('/edit', methods=("POST", "GET"))
@login_required
def edit_article():
    if request.method == 'POST':
        aid = int(request.form.get('aid', 0))
    else:
        aid = int(request.args.get('aid', 0))
    article = Article.query.get(aid)
    if article.uid != session['uid']:
        abort(403)

    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        now = datetime.datetime.now()

        if not content:
            return render_template('edit.html', article=article, err='微博内容不允许为空')

        article.content = content
        article.updated = now
        db.session.commit()

        return redirect(f'/article/read?aid={aid}')

    else:
        article = Article.query.get(aid)
        return render_template('edit.html', article=article)


@article_bp.route('/delete')
@login_required
def delete_article():
    aid = int(request.args.get('aid'))
    article = Article.query.get(aid)

    if article.uid == session['uid']:
        db.session.delete(article)
        db.session.commit()
        return redirect('/')
    else:
        abort(403)


@article_bp.route('/post_comment', methods=('POST',))
@login_required
def post_comment():
    aid = int(request.form.get('aid', 0))
    content = request.form.get('content', '').strip()
    uid = session['uid']
    created = datetime.datetime.now()

    comment = Comment(uid=uid, aid=aid, content=content, created=created)
    db.session.add(comment)
    db.session.commit()

    return redirect(f'/article/read?aid={aid}')


@article_bp.route('/reply', methods=('POST',))
def reply():
    aid = int(request.form.get('aid'))
    cid = int(request.form.get('cid'))
    content = request.form.get('content')
    now = datetime.datetime.now()

    comment = Comment(uid=session['uid'], aid=aid, cid=cid, content=content, created=now)
    db.session.add(comment)
    db.session.commit()

    return redirect((f'/article/read?aid={aid}'))


@article_bp.route('/delete_comment')
def delete_comment():
    cid = int(request.args.get('cid'))
    comment = Comment.query.get(cid)

    if comment.uid != session['uid']:
        abort(403)

    comment.content = '当前评论已被删除'
    db.session.commit()

    return redirect('/')


@article_bp.route('/set_thumb')
@login_required
def set_thumb():
    aid = int(request.args.get('aid'))
    uid = session['uid']
    thumb = Thumb(aid=aid,uid=uid)

    if not Thumb.query.filter_by(aid=aid,uid=uid).first():
        Article.query.filter_by(id=aid).update({'n_thumb':Article.n_thumb + 1})
        db.session.add(thumb)
    else:
        Article.query.filter_by(id=aid).update({'n_thumb': Article.n_thumb - 1})
        Thumb.query.filter_by(aid=aid, uid=uid).delete()

    db.session.commit()
    return redirect(f'/article/read?aid={aid}')

@article_bp.route('/follow_article')
def follow_article():
    """查看自己关注的人的微博"""
    uid = session['uid']

    # 找到自己关注的人 uid 列表
    follows = Follow.query.filter_by(uid=uid).values('fid')
    fid_list = [fid for (fid,) in follows]

    #找到这些人最近发布的前100条微博
    art_list = Article.query.filter(Article.uid.in_(fid_list)).order_by(Article.created.desc()).limit(100)

    return render_template('follow_article.html', art_list=art_list)




