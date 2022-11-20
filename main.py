from flask import Flask
from flask_restful import Api, Resource, request
from ring_doorbell import Ring, Auth
from oauthlib.oauth2 import MissingTokenError
from flask_cors import CORS

app = Flask (__name__)
api = Api(app)
CORS(app)


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

    auth = Auth("PorchPals/1.0", None)
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
    return {"data": videoUrl}, 200

class HelloWorld(Resource):
  def get(self):
    return {"data": "Hello World!"}, 200

api.add_resource(Code,"/code")
api.add_resource(Video,"/video")
api.add_resource(HelloWorld, "/")

if __name__ == "__main__":
  app.run(debug=True)