import os
from flask import Flask, request, abort, jsonify, redirect, url_for
from flask_sqlalchemy import sqlalchemy
from sqlalchemy import func
from flask_cors import CORS
import random
import sys 
from flask_moment import Moment


from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  app = Flask(__name__)
  moment = Moment(app)
  setup_db(app)
  CORS(app)



  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers',
                          'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods',
                          'GET,PUT,POST,DELETE,OPTIONS')
      return response

  
  @app.route('/')
  def index():
      return redirect(url_for('getCategories'))

  @app.route('/categories', methods=['GET'])
  def getCategories():
      try:
          categories = Category.query.order_by(Category.id).all()
      except: 
          abort(422)
      if len(categories) == 0:
          abort(404)
      return jsonify({
          'success': True,
          'categories': [category.format() for category in categories]
      })

  def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

  @app.route('/questions')
  def get_questions():
      try:
          selection = Question.query.order_by(Question.id).all()
          current_questions = paginate_questions(request, selection)
          categories = Category.query.order_by(Category.id).all()
      except Exception:
          abort(422)
      if len(current_questions) == 0 or len(categories) == 0:
          abort(404)
      return jsonify({
          'success': True,
          'questions': current_questions,
          'totalQuestions': len(Question.query.all()),
          'currentCategory': None,
          'categories': [category.format() for category in categories]
      })

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def deleteQuestion(question_id):
      question = Question.query.get(question_id)
      if question is None:
          abort(404)
      try: 
          question.delete()
      except:
          abort(500)

      return jsonify({
          'success': True,
          'question': question_id,
      })

  @app.route('/questions', methods=['POST'])
  def createQuestion():
      questionData = request.get_json()
      try: 
          question = Question(
              question=questionData['question'],
              answer=questionData['answer'],
              catagory=questionData['catagory'],
              difficulty=questionData['difficulty'],
          )
          question.insert()
      except:
          abort(500)
      

      return jsonify({
          'success': True,
          'question': question.format(),
      })



  @app.route('/questions/search', methods=['POST'])
  def search_question():
      search_term = request.get_json()['searchTerm']
      try:
          search_results = Question.query.filter(
              Question.question.ilike(f'%{search_term}%')).all()
      except Exception:
          abort(500)
      return jsonify({
          'success': True,
          'questions': [question.format() for question in search_results],
          'totalQuestions': len(search_results),
          'currentCategory': None,
      }) 


  @app.route('/categories/<int:category_id>/questions')
  def questions_category(category_id):
      category_id = str(category_id)
      questions = Question.query.order_by(Question.id).filter(
          Question.category == category_id).all()
      categories = Category.query.order_by(Category.id).all()

      return jsonify({
          'success': True,
          'questions': [question.format() for question in questions],
          'totalQuestions': len(Question.query.filter(Question.category == category_id).all()),
          'currentCategory': category_id,
          'categories': [category.format() for category in categories]
      })

  @app.route('/play', methods=['POST'])
  def play():
      previous_questions = request.get_json()['previous_questions']
      quiz_category_id = request.get_json()['quiz_category'].get('id')

      max_id = db.session.query(func.max(Category.id)).scalar()
      min_id = db.session.query(func.min(Category.id)).scalar()
      if quiz_category_id > max_id or quiz_category_id < min_id and quiz_category_id != 0:
          abort(404)
      quiz_category_id = str(quiz_category_id)
      try:
          if(quiz_category_id == '0'):
              question = Question.query.filter(~ Question.id.in_(
                  previous_questions)).order_by(func.random()).first()
          else:
              question = Question.query.filter(Question.category == quiz_category_id).filter(
                  ~Question.id.in_(previous_questions)).order_by(func.random()).first()

          if question is not None:
              question = question.format()

      except Exception:
          abort(500)

      return jsonify({
          'success': True,
          'question': question
      })

  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False,
          "error": 404,
          "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False,
          "error": 400,
          "message": "bad request"
      }), 400
  
  return app

    