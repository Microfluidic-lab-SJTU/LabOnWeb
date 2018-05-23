#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response,url_for, request, session, json, \
send_from_directory, current_app, g,redirect
from flask.ext.moment import Moment
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlite import *
# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from client import Camera

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
##############################
moment = Moment(app)
app.config['SECRET_KEY'] = 'stevexiaofei@app123456'		

@app.before_request
def preprocess():
	g.username = session.get('username')
	except_list=[url_for('logout'),'/video_feed']
	session['last_base_url']='/' if (request.path in except_list) else url_for('logout')
	
@app.after_request
def postprocess(response):
	return response
@app.route('/mission')
def mission():
	return render_template('mission.html')
	
@app.route('/about')
def about():
	return render_template('about.html')
	
@app.route('/login',methods = [ 'GET', 'POST' ])
def login():
	if request.method == 'POST':
		username = request.values.get('username')
		password = request.values.get('password')
		user_profile={'name':username,'password':password}
		query_return=query(user_profile)
		if query_return==0:
			session['username'] = username
			return json.dumps({
				'success': 'true',
				'msg': 'Login success!'
				})
		elif query_return==1:
			return json.dumps({
				'success': 'false',
				'msg': 'password incorrect please try again!'
				})
		else:
			return json.dumps({
				'success': 'false',
				'msg': "The user does't exit please register first!"
				})
	else:
		return render_template('login.html')

@app.route('/logout', methods = [ 'GET', 'POST' ])
def logout():
	last_base_url=session['last_base_url']
	session.clear()
	return redirect(last_base_url)
@app.route('/controll')
def lab_on_web():
	#print('lab_on_web',session.get('username'))
	if session.get('username',None)==None:
		return render_template('login.html')
	else:
		return render_template('controll.html')

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html' )


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed', methods = [ 'GET', 'POST' ])
def video_feed():
	"""Video streaming route. Put this in the src attribute of an img tag."""
	if request.method == 'GET':
		return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
	else:
		item_idx = int(request.values.get('item_idx'))
		return json.dumps({
				'success': 'true',
				'msg': "respose from remote server\n you select the %d item!"%(item_idx,)
				})


if __name__ == '__main__':
    app.run(host='202.121.181.3',threaded=True)
