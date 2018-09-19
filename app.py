#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response,url_for, request, session, json, \
send_from_directory, current_app, g,redirect,flash,get_flashed_messages
from flask_moment import Moment
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlite import *
from util import process_config
import sys   
reload(sys)   
sys.setdefaultencoding('utf-8')
config=process_config('config.cfg')
# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from base_camera import BaseCamera as  Camera

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
##############################
moment = Moment(app)
app.config['SECRET_KEY'] = 'stevexiaofei@app123456'		
addr1=('10.164.9.18',6666)
addr2=('172.25.110.3',6666)
addr3=('219.228.126.106',6666)
addr_default=('0.0.0.0',6666)
item_list = [addr_default,addr1,addr2,addr3]
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

class down:
	def __init__(self):
		self.imageprocess=os.listdir(os.path.join('static','Download','imageprocess').encode('gbk'))
		self.imageprocess=[ it.encode('gbk') for it in self.imageprocess]
		self.mechinelearning=os.listdir(os.path.join('static','Download','mechinelearning').encode('gbk'))
		self.mechinelearning=[ it.encode('gbk') for it in self.mechinelearning]
		self.programming=os.listdir(os.path.join('static','Download','programming').encode('gbk'))
		self.programming=[ it.encode('gbk') for it in self.programming]
		
		self.others=os.listdir(os.path.join('static','Download','others').encode('gbk'))
		self.others=[ it.encode('gbk') for it in self.others]
	def generator_imageprocess(self):
		for it in self.imageprocess:
			yield os.path.join('static','Download','imageprocess',it).decode('gbk').encode('utf-8').replace(' ','%20'),\
						it.decode('gbk').encode('utf-8').replace(' ','%20'),\
						it.decode('gbk').encode('utf-8')
	def generator_mechinelearning(self):
		for it in self.mechinelearning:
			yield os.path.join('static','Download','mechinelearning',it).decode('gbk').encode('utf-8').replace(' ','%20'),\
						it.decode('gbk').encode('utf-8').replace(' ','%20'),\
						it.decode('gbk').encode('utf-8')
	def generator_others(self):
		for it in self.others:
			yield os.path.join('static','Download','others',it).decode('gbk').encode('utf-8').replace(' ','%20'),\
						it.decode('gbk').encode('utf-8').replace(' ','%20'),\
						it.decode('gbk').encode('utf-8')
	def generator_programming(self):
		for it in self.programming:
			yield os.path.join('static','Download','programming',it).decode('gbk').encode('utf-8').replace(' ','%20'),\
						it.decode('gbk').encode('utf-8').replace(' ','%20'),\
						it.decode('gbk').encode('utf-8')
@app.route('/download')
def download():
	Gene =down()
	#print(files)
	return render_template('download.html',Gene=Gene)
	
@app.route('/about')
def about():
	return render_template('about.html')
@app.route('/project')
def project():
	return render_template('project.html')
	
@app.route('/login',methods = [ 'GET', 'POST' ])
def login():
	if request.method == 'POST':
		username = request.values.get('username')
		password = request.values.get('password')
		user_profile={'name':username,'password':password}
		query_return=query(user_profile)
		if query_return==0:
			session['username'] = username
			session['stream_idx'] = 0
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
		print("Response stream_idx",session['stream_idx'])
		cam = Camera(item_list[session['stream_idx']])
		print('ip: ',item_list[session['stream_idx']] )
		if cam.IsServerLive() is False:
			flash('look like the remote microscope server is closed!')
			session['stream_idx'] = 0
			cam = Camera(item_list[session['stream_idx']])
		return Response(gen(cam),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
	else:
		print('video_feed,else')
		item_idx = int(request.values.get('item_idx'))
		print('the item idx is ',item_idx)
		session['stream_idx'] = item_idx
		return json.dumps({
				'success': 'true',
				'msg': "respose from remote server\n you select the %d item!"%(item_idx,)
				})


if __name__ == '__main__':
    app.run(host=config['ip'],threaded=True)
