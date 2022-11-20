import json
from flask import Flask
from flask_restful import Api, Resource, request
from ring_doorbell import Ring, Auth
from oauthlib.oauth2 import MissingTokenError
from flask_cors import CORS


app = Flask (__name__)
api = Api(app)
CORS(app)

def token_updated(token):
  global freshToken 
  freshToken = json.dumps(token)

class Code(Resource):
  def post(self):
    username = request.form.get('username')
    password = request.form.get('password')
    auth = Auth("PorchPals/1.0", None)
    try:
        auth.fetch_token(username, password)
    except MissingTokenError:
        return {"data": "Code has been sent"}, 201
    except Exception as e:
      return {"data": f'Username, or Password is not valid...Exception is: {e}'}, 401
    return {"data": "Code has been sent"}, 201

  def get(self):
    return "Code Page"

class Video(Resource):
  def post(self):
    username = request.form.get('username')
    password = request.form.get('password')
    code = request.form.get('code') or None
    auth = Auth("PorchPals/1.0", None, token_updated)
    cache = freshToken
    try:
      auth.fetch_token(username, password)
    except MissingTokenError:
      auth.fetch_token(username, password, code)
    except Exception as e:
      return {"data": f'Username, or Password is not valid...Exception is: {e}'}, 401
    ring = Ring(auth)
    ring.update_data()
    devices = ring.devices()
    doorbell = devices['doorbots'][0]
    videoUrl = doorbell.recording_url(doorbell.last_recording_id)
    return {"data": {"videoUrl":videoUrl,"cache":cache}}, 200

class CheckToken(Resource):
  def post(self):
    cache = request.form.get('token')
    print("cache value is: ",cache)
    if cache != "":
      auth = Auth("MyProject/1.0", json.loads(cache), token_updated)
      cache = freshToken
      ring = Ring(auth)
      ring.update_data()
      devices = ring.devices()
      doorbell = devices['doorbots'][0]
      videoUrl = doorbell.recording_url(doorbell.last_recording_id)
      return {"data": {"videoUrl":videoUrl,"cache":cache}}, 200
    else:
      return {"data":"Token not correct"}, 400

class Home(Resource):
  def get(self):
    return "Ring Api Application", 200

api.add_resource(Code,"/code")
api.add_resource(Video,"/video")
api.add_resource(CheckToken, "/token")
api.add_resource(Home, "/")


if __name__ == "__main__":
  app.run(debug=True)