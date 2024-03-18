import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session
from models import User, db, Question, Category
from datetime import datetime, timedelta
from sqlalchemy import or_
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

import os

#Flaskのインスタンスを生成
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/fukudahideki/Desktop/python_lesson/question_app/question_app.db'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SECRET_KEY'] = os.urandom(24)

# SQLAlchemyオブジェクトにFlaskオブジェクトを登録する
db.init_app(app)

migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

# アプリケーションコンテキストを手動で設定
app.app_context().push()

#ユーザー登録
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return 'Registered successfully'

#ログイン
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        session['username'] = username
        return 'Login successful'
    else:
        return 'Invalid username or password'

#ログアウト
@app.route('/logout')
def logout():
    session.pop('username', None)
    return 'Logged out'

# ホームページ
@app.route('/')
def home():
    categories = Category.query.all()  # カテゴリのリストを取得
    latest_questions = Question.query.order_by(Question.date_posted.desc()).limit(5).all()
    return render_template('index.html', latest_questions=latest_questions, categories=categories)

# しつもんの登録
@app.route('/submit_question', methods=['POST'])
def submit_question():
    if request.method == 'POST':
        question_text = request.form['question']
        answer_text = request.form['answer']
        category_id = request.form['category']  # フォームから選択されたカテゴリIDを取得
        category = Category.query.get(category_id)  # カテゴリIDに対応するカテゴリを取得
        new_question = Question(question_text=question_text, answer_text=answer_text, category_id=category_id, date_posted=datetime.utcnow())
        db.session.add(new_question)
        db.session.commit()
    return redirect(url_for('home'))

# 検索
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_word = request.form['search_word']  # フォームから検索ワードを取得
        # 検索ワードをもとにquestionテーブルのクエリを作成
        query = Question.query.filter(or_(Question.question_text.contains(search_word), Question.answer_text.contains(search_word)))
        # 検索結果を取得
        search_results = query.all()
        return render_template('search_results.html', search_results=search_results)
    else:
        # GETリクエストの場合は、空の検索結果を返す
        return render_template('search_results.html', search_results=[])
        # return redirect(url_for('home'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
