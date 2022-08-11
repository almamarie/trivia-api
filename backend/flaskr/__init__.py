from crypt import methods
import json
import os
from urllib import response
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def formatQuestions(questions):
    return [question.format() for question in questions]


def paginateQuestions(request, allQuestions):
    page = request.args.get("page", 1, type=int)
    # print("page: ", page)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    formatedQuestions = formatQuestions(allQuestions)

    # print("start, end: ", start, end)
    return formatedQuestions[start:end]


# this function is called a lot of times so it is necessary to make it stand alone
def generate_categories():
    all_categories = Category.query.order_by(Category.id).all()
    # print("All Categories: ", all_categories)

    # The number of categories are few so there is no need to paginate them.
    categories = {}
    for category in all_categories:
        categories[category.id] = category.type

    return categories


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/api/": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )

        response.headers.add(
            "Access-Control-Allow-Methods", "GET,POST,DELETE"
        )

        return response

    """
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route("/categories", methods=['GET'])
    def get_all_categories():
        categories = generate_categories()
        # print(categories)
        return jsonify({
            'success': True,
            'categories': categories
        })
    """
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions", methods=["GET"])
    def get_paginated_books():
        allQuestions = Question.query.order_by(Question.category).all()
        currentQuestions = paginateQuestions(request, allQuestions)

        if len(currentQuestions) == 0:
            abort(404)

        categories = generate_categories()

        # print("jiberrish", categories[currentQuestions[0]['category']])
        # print("\n\nCurrent Category: ", categories)
        # generate the current category
        currentCategory = categories[currentQuestions[0]['category']]

        # print(currentCategory)
        return jsonify({
            'success': True,
            'questions': currentQuestions,
            'totalQuestions': len(currentQuestions),
            'categories': categories,
            'currentCategory': currentCategory
        })

    """
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    # get books from a particular id
    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_paginated_books_by_categories(category_id):
        # generate the current category
        currentCategory = Category.query.filter(
            Category.id == category_id).with_entities(Category.type).one_or_none()

        if currentCategory is None:
            abort(404)

        allQuestions = Question.query.filter(
            Question.category == category_id).order_by(Question.category).all()
        currentQuestions = paginateQuestions(request, allQuestions)

        if len(currentQuestions) == 0:
            abort(404)

        # print(currentCategory)
        return jsonify({
            'success': True,
            'questions': currentQuestions,
            'totalQuestions': len(currentQuestions),
            'currentCategory': currentCategory[0]
        })

    """
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            if question is None:
                abort(404)

            question.delete()
            return jsonify({
                'success': True,
                'id': question_id
            })
        except:
            abort(422)
    """

    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.


    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/questions", methods=["POST"])
    def add_new_question():
        body = request.get_json()
        search = body.get("searchTerm", None)
        try:
            if search != None:
                match = Question.query.filter(
                    Question.question.ilike("%{}%".format(search)))

                formatedQuestions = formatQuestions(match)

                categories = generate_categories()

                currentCategory = categories[formatedQuestions[0]['category']]
                return jsonify({
                    'success': True,
                    'questions': formatedQuestions,
                    'totalQuestions': len(formatedQuestions),
                    'currentCategory': currentCategory
                })

            else:
                # chech each field to be sure if it not null and
                # send a 460 error code (looked through the error codes at
                # developer.mozilla.org and chose one that is not used)
                new_question = body.get("question", None)
                if new_question is None:
                    abort(422)

                new_answer = body.get("answer", None)
                if new_answer is None:
                    abort(422)

                new_difficulty = body.get("difficulty", None)
                if new_difficulty is None:
                    abort(422)

                new_category = body.get("category", None)
                if new_category is None:
                    abort(422)

                if Question.query.filter(Question.question == new_question).one_or_none() != None:
                    abort(422)

                newQuestion = Question(
                    question=new_question,
                    answer=new_answer,
                    difficulty=new_difficulty,
                    category=new_category
                )

                newQuestion.insert

                return jsonify({
                    'success': True,
                })

        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=['GET'])
    def get_question_for_quiz():

        body = request.get_json()
        previousQuestions = body.get("previous_questions", None)
        # print("\nprevious questions: ", previousQuestions)
        if previousQuestions is None:
            abort(400)

        quiz_category = body.get("quiz_category", None)
        # print("\Quiz category: ", quiz_category)
        if quiz_category is None:
            abort(400)

        category_id = Category.query.filter(Category.type == quiz_category)
        if category_id is None:
            abort(400)

        nextQuestion = Question.query.filter(
            ~Question.id.in_(previousQuestions)).first()

        # print("next question: ", nextQuestion.format())
        if nextQuestion == None:
            return jsonify({
                'success': False,
                'message': "End of questions"
            })

        return jsonify({
            'success': True,
            'question': nextQuestion.format()
        })
    """
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404,
                    "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422,
                    "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @app.errorhandler(405)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 405,
                    "message": "method not allowed"}),
            405,
        )

# Tried creating new status codes but got errors
    # @app.errorhandler(460)
    # def incomplete_data(error):
    #     return (
    #         jsonify({"success": False, "error": 460,
    #                 "message": "provided incomplete data"}),
    #         460,
    #     )

    # @app.errorhandler(461)
    # def incomplete_data(error):
    #     return (
    #         jsonify({"success": False, "error": 461,
    #                 "message": "Question already in database"}),
    #         461,
    #     )
    return app
