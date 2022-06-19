from .entities.User import User

class ModelUser():

	@classmethod
	def login(self,conn,user):
		try:
			cur = conn.cursor()
			sqlquery =  "select * from usuario where usuario.username = \'" + user.id + "\';"
			cur.execute(sqlquery)
			existente = cur.fetchone()
			if existente != None:
				user = User(existente[0],User.check_password(existente[1],user.password),existente[2])
				return user
			else:
				return None
		except Exception as ex:
			raise Exception(ex)

	@classmethod
	def get_by_id(self,conn,id):
		try:
			cur = conn.cursor()
			sqlquery =  "select * from usuario where usuario.username = \'" + id + "\';"
			cur.execute(sqlquery)
			existente = cur.fetchone()
			if existente != None:
				return User(existente[0],None,existente[2])
			else:
				return None
		except Exception as ex:
			raise Exception(ex)