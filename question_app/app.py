from flask import Flask, render_template, request, redirect, url_for
from models import db, Question
from datetime import datetime
from sqlalchemy import or_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/fukudahideki/Desktop/python_lesson/question_app/question_app.db'
db.init_app(app)

# アプリケーションコンテキストを手動で設定
app.app_context().push()

# ホームページ
@app.route('/')
def home():
    # 最新の5件の質問と回答を取得
    latest_questions = Question.query.order_by(Question.date_posted.desc()).limit(5).all()
    return render_template('index.html', latest_questions=latest_questions)

# しつもんの登録
@app.route('/submit_question', methods=['POST'])
def submit_question():
    if request.method == 'POST':
        question_text = request.form['question']
        answer_text = request.form['answer']
        new_question = Question(question_text=question_text,answer_text=answer_text,date_posted=datetime.utcnow())
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
