#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'

def configure_app():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

configure_app()
migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class ClearSession(Resource):

    def delete(self):
        session.pop('page_views', None)
        session.pop('user_id', None)
        return '', 204

class ArticleList(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ArticleDetail(Resource):

    def get(self, id):
        if 'page_views' not in session:
            session['page_views'] = 0
        session['page_views'] += 1

        if session['page_views'] <= 3:
            article = Article.query.get(id)
            if article:
                return article.to_dict(), 200
            return {'message': 'Article not found'}, 404

        return {'message': 'Maximum pageview limit reached'}, 401

class UserLogin(Resource):
    
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data.get('username')).first()
        
        if user:
            session['user_id'] = user.id
            return user.to_dict(), 200
        return {'message': 'User not found'}, 404

class UserLogout(Resource):
    
    def delete(self):
        session.pop('user_id', None)
        return {'message': 'No Content'}, 204

class CheckSession(Resource):
    
    def get(self):
        user_id = session.get('user_id')
        
        if user_id:
            user = User.query.get(user_id)
            if user:
                return user.to_dict(), 200
            return {'message': 'User not found'}, 404
        return {}, 401

api.add_resource(ClearSession, '/clear')
api.add_resource(ArticleList, '/articles')
api.add_resource(ArticleDetail, '/articles/<int:id>')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(CheckSession, '/check_session')

if __name__ == '__main__':
    app.run(port=5555, debug=True)

