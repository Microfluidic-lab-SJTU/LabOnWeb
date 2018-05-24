import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import Sequence
from sqlalchemy.orm import sessionmaker
from util import process_config

config=process_config('config.cfg')
#db_path='sqlite:////home/stevexiaofei/project/flask-video-streaming-master/data.sqlite'
engine = create_engine(config['databasepath'])
Base = declarative_base()
Session = sessionmaker(bind=engine)

class User(Base):
	__tablename__='users'
	id=Column(Integer,Sequence('user_id_seq'),primary_key=True)
	name=Column(String(50))
	password=Column(String(12))
	
	def __repr__(self):
		return "<User(name='%s',password='%s')>"%(self.name,self.password)
		
Base.metadata.create_all(engine)

def register_new_user(user_profile):
	session=Session()
	user=User(name=user_profile['name'],password=user_profile['password'])
	session.add(user)
	session.commit()
	
def register_many_user(user_profile_list):
	session=Session()
	for it in user_profile_list:
		user=User(name=it['name'],password=it['password'])
		session.add(user)
	session.commit()
def query(user_profile):
	'''
		todo: 
			return value:
				0: both name and password match with regisered ones
				1: password error
				2: name have not be registered
	'''
	session=Session()
	return_item=session.query(User).filter(User.name == user_profile['name']).first()
	if return_item:
		if return_item.password==user_profile['password']:
			return 0
		else:
			return 1
	else:
		return 2
def delete(name):
	session=Session()
	session.delete(session.query(User).filter(User.name==name).first())
	session.commit()
