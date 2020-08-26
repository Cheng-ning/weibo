import datetime
from math import ceil
from os import abort

from flask import Blueprint, redirect, request, render_template, session

from libs.orm import db
from libs.utils import login_required
from article.models import Article


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
    aid = int(request.args.get('aid'))
    article = Article.query.get(aid)
    return render_template('read.html', article=article)


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
