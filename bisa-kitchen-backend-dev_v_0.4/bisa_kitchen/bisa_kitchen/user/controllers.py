from flask import Blueprint, jsonify, request, make_response, render_template
from flask import current_app as app
from flask_jwt_extended import get_jwt, jwt_required
from flask_cors import cross_origin
from werkzeug.utils import secure_filename
from werkzeug.datastructures import ImmutableMultiDict
from time import gmtime, strftime
import hashlib
import datetime
import requests
import cv2
import os
import numpy as np
import base64
import random
import json
import warnings
import string
import jwt

from . models import Data

#11 superadmin, 21 Customer
role_group_super_admin = ["11"]
role_group_admin_lokasi = ["12"]
role_group_admin_brand = ["13"]
role_group_admin = ["11", "12", "13"]
role_group_customer = ["21"]
role_group_all = ["11", "12", "13", "21"]

#now = datetime.datetime.now()

user = Blueprint('user', __name__, static_folder = '../../upload/foto_user', static_url_path="/media")

#region ================================= FUNGSI-FUNGSI AREA ==========================================================================

def tambahLogs(logs):
	f = open(app.config['LOGS'] + "/" + secure_filename(strftime("%Y-%m-%d"))+ ".txt", "a")
	f.write(logs)
	f.close()

def save(encoded_data, filename):
	arr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
	img = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
	return cv2.imwrite(filename, img)

def permission_failed():
    return make_response(jsonify({'error': 'Permission Failed','status_code':403}), 403)

def request_failed():
    return make_response(jsonify({'error': 'Request Failed','status_code':403}), 403)

def defined_error(description, error="Defined Error", status_code=499):
	return make_response(jsonify({'description':description,'error': error,'status_code':status_code}), status_code)

def parameter_error(description, error= "Parameter Error", status_code=400):
	if app.config['PRODUCT_ENVIRONMENT'] == "DEV":
		return make_response(jsonify({'description':description,'error': error,'status_code':status_code}), status_code)
	else:
		return make_response(jsonify({'description':"Terjadi Kesalahan Sistem",'error': error,'status_code':status_code}), status_code)

def bad_request(description):
	if app.config['PRODUCT_ENVIRONMENT'] == "DEV":
		return make_response(jsonify({'description':description,'error': 'Bad Request','status_code':400}), 400) #Development
	else:
		return make_response(jsonify({'description':"Terjadi Kesalahan Sistem",'error': 'Bad Request','status_code':400}), 400) #Production

def randomString(stringLength):
	"""Generate a random string of fixed length """
	letters = string.ascii_lowercase
	return ''.join(random.choice(letters) for i in range(stringLength))

def random_string_number_only(stringLength):
	letters = string.digits
	return ''.join(random.choice(letters) for i in range(stringLength))

#endregion ================================= FUNGSI-FUNGSI AREA ===============================================================


#region ================================= MY PROFILE AREA ==========================================================================

@user.route('/get_my_profile', methods=['GET', 'OPTIONS'])
@jwt_required()
@cross_origin()
def get_my_profile():
	try:
		ROUTE_NAME = str(request.path)

		id_user = str(get_jwt()["id_user"])
		role = str(get_jwt()["role"])

		if role not in role_group_all:
			return permission_failed()

		dt = Data()

		query = """ SELECT a.* FROM user a WHERE id_user = %s AND is_delete = 0 """
		values = (id_user, )

		rowCount = dt.row_count(query, values)
		hasil = dt.get_data(query, values)
		hasil = {'data': hasil , 'status_code': 200, 'row_count': rowCount}
		########## INSERT LOG ##############
		imd = ImmutableMultiDict(request.args)
		imd = imd.to_dict()
		param_logs = "[" + str(imd) + "]"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		####################################
		return make_response(jsonify(hasil),200)
	except Exception as e:
		return bad_request(str(e))

@user.route('/update_my_profile', methods=['PUT', 'OPTIONS'])
@jwt_required()
@cross_origin()
def update_my_profile():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.now()
	id_user 		= str(get_jwt()["id_user"])
	role 			= str(get_jwt()["role"])

	if role not in role_group_all:
		return permission_failed()

	try:
		dt = Data()
		data = request.json


		query_temp = " SELECT id_user FROM user WHERE id_user = %s AND is_delete != 1 "
		values_temp = (id_user, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, data tidak ditemukan")

		query = """ UPDATE user SET id_user = id_user """
		values = ()

		if "password" in data:
			password = data["password"]

			if "old_password" not in data:
				return parameter_error("Missing old_password in Request Body")

			old_password = data["old_password"]
			old_pass_enc = hashlib.md5(old_password.encode('utf-8')).hexdigest()
			# check if old password is correct
			query_temp = "SELECT id_user, password FROM user WHERE id_user = %s AND password = %s LIMIT 1"
			values_temp = (id_user, old_pass_enc)
			if len(dt.get_data(query_temp, values_temp)) == 0:
				return defined_error("Password lama tidak sesuai")

			# Convert password to MD5
			pass_ency = hashlib.md5(password.encode('utf-8')).hexdigest()
			query += """ ,password = %s, waktu_terakhir_ganti_password = %s """
			values += (pass_ency, now, )

		if "nama" in data:
			nama = data["nama"]
			query += """ ,nama = %s """
			values += (nama, )

		if "tanggal_lahir" in data:
			tanggal_lahir = data["tanggal_lahir"]
			query += """ ,tanggal_lahir = %s """
			values += (tanggal_lahir, )

		if "jenis_kelamin" in data:
			jenis_kelamin = data["jenis_kelamin"].upper()
			# validasi data jenis kelamin
			if str(jenis_kelamin) not in ["LK", "PR"]:
				return parameter_error("Invalid jenis_kelamin Parameter")
			query += """ ,jenis_kelamin = %s """
			values += (jenis_kelamin, )

		if "nomor_telepon" in data:
			nomor_telepon = data["nomor_telepon"]
			query += """ ,nomor_telepon = %s """
			values += (nomor_telepon, )

		if "alamat" in data:
			alamat = data["alamat"]
			query += """ ,alamat = %s """
			values += (alamat, )

		if "foto_user" in data:
			filename_photo = secure_filename(strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_user.png")
			save(data["foto_user"], os.path.join(app.config['UPLOAD_FOLDER_FOTO_USER'], filename_photo))

			query += """ ,foto_user = %s """
			values += (filename_photo, )

		query += """ WHERE id_user = %s """
		values += (id_user, )
		dt.insert_data(query, values)

		hasil = "Success Update My Profile"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))

#endregion ================================= MY PROFILE AREA ==========================================================================


#region ================================= CUSTOMER AREA ==========================================================================

@user.route('/insert_customer', methods=['POST', 'OPTIONS'])
@cross_origin()
def insert_customer():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	try:
		dt = Data()
		data = request.json
		print(data)

		# Check mandatory data
		if "email" not in data:
			return parameter_error("Missing email in Request Body")
		if "password" not in data:
			return parameter_error("Missing password in Request Body")
		if "nama_customer" not in data:
			return parameter_error("Missing nama_customer in Request Body")

		email = data["email"]
		password = data["password"]
		nama_customer = data["nama_customer"]

		# check if username already used or not
		query_temp = "SELECT id_customer FROM customer WHERE email = %s AND is_delete != 1"
		values_temp = (email, )
		if len(dt.get_data(query_temp, values_temp)) != 0:
			return defined_error("Email Already Registered")

		# Convert password to MD5
		pass_ency = hashlib.md5(password.encode('utf-8')).hexdigest()

		# Check optional data
		if "nomor_customer" in data:
			nomor_customer = data["nomor_customer"]
		else:
			nomor_customer 	= None

		if "alamat_customer" in data:
			alamat_customer = data["alamat_customer"]
		else:
			alamat_customer	= None

		# waktu_daftar = strftime("%Y-%m-%d %H:%M:%S")
		waktu_daftar = now

		# Insert to table customer
		query = "INSERT into customer (email, password, nama_customer, nomor_customer, alamat_customer, waktu_daftar) VALUES (%s, %s, %s, %s, %s, %s)"
		values = (email, pass_ency, nama_customer, nomor_customer, alamat_customer, waktu_daftar)
		id_customer = dt.insert_data_last_row(query, values)

		hasil = "Insert Customer Success"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_customer = "+str(id_customer)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_customer = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))

#endregion ================================= CUSTOMER AREA ==========================================================================


#region ================================= ADMIN AREA ==========================================================================

@user.route('/insert_admin', methods=['POST', 'OPTIONS'])
@cross_origin()
def insert_admin():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.now()
	try:
		dt = Data()
		data = request.json
		print(data)

		# Check mandatory data
		if "email" not in data:
			return parameter_error("Missing email in Request Body")
		if "password" not in data:
			return parameter_error("Missing password in Request Body")
		if "nama_admin" not in data:
			return parameter_error("Missing nama_admin in Request Body")

		email = data["email"]
		password = data["password"]
		nama_admin = data["nama_admin"]

		# check if username already used or not
		query_temp = "SELECT id_admin FROM admin WHERE email = %s AND is_delete != 1"
		values_temp = (email, )
		if len(dt.get_data(query_temp, values_temp)) != 0:
			return defined_error("Email Already Registered")

		# Convert password to MD5
		pass_ency = hashlib.md5(password.encode('utf-8')).hexdigest()

		# Check optional data
		# Default variables for optional data
		status 	= 1

		# Insert to table admin
		query = "INSERT into admin (email, password, nama_admin, status) VALUES (%s, %s, %s, %s)"
		values = (email, pass_ency, nama_admin, status)
		id_admin = dt.insert_data_last_row(query, values)

		hasil = "Insert admin Success"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_admin = "+str(id_admin)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_admin = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))

#endregion ================================= ADMIN AREA ==========================================================================

#region ================================= ADMIN Lokasi AREA ==========================================================================
@user.route('/insert_admin_lokasi', methods=['POST', 'OPTIONS'])
@jwt_required()
@cross_origin()
def insert_admin_lokasi():
	ROUTE_NAME = str(request.path)

	id_admin = str(get_jwt()["id_admin"])
	role = str(get_jwt()["role"])

	if role not in role_group_super_admin:
		return permission_failed()
	now = datetime.datetime.now()
	try:
		dt = Data()
		data = request.json
		print(data)

		# Check mandatory data
		if "id_lokasi" not in data:
			return parameter_error("Missing id_lokasi in Request Body")
		if "password" not in data:
			return parameter_error("Missing password in Request Body")
		if "nama_admin_lokasi" not in data:
			return parameter_error("Missing nama_admin_lokasi in Request Body")
		if "email" not in data:
			return parameter_error("Missing email in Request Body")

		email = data["email"]
		password = data["password"]
		nama_admin_lokasi = data["nama_admin_lokasi"]
		id_lokasi = data["id_lokasi"]


		# check if username already used or not
		query_temp = "SELECT id_admin_lokasi FROM admin_lokasi WHERE email = %s AND is_delete != 1"
		values_temp = (email, )
		if len(dt.get_data(query_temp, values_temp)) != 0:
			return defined_error("Email Already Registered")

		# Convert password to MD5
		pass_ency = hashlib.md5(password.encode('utf-8')).hexdigest()

		# Check optional data
		# Default variables for optional data
		status 	= 1

		# Insert to table admin
		query = "INSERT into admin_lokasi (email, password, nama_admin_lokasi, status,id_lokasi) VALUES (%s, %s, %s, %s,%s)"
		values = (email, pass_ency, nama_admin_lokasi, status,id_lokasi)
		id_admin = dt.insert_data_last_row(query, values)

		hasil = "Insert admin lokasi Success"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_admin = "+str(id_admin)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_admin = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))

@user.route('/get_profile_admin_lokasi', methods=['GET', 'OPTIONS'])
@jwt_required()
@cross_origin()
def get_profile_admin_lokasi():
	try:
		ROUTE_NAME = str(request.path)

		id_admin = str(get_jwt()["id_admin"])
		role = str(get_jwt()["role"])

		if role not in role_group_admin_lokasi:
			return permission_failed()

		dt = Data()

		query = """ SELECT * FROM admin_lokasi a WHERE id_admin_lokasi = %s AND is_delete = 0 """
		values = (id_admin, )

		rowCount = dt.row_count(query, values)
		hasil = dt.get_data(query, values)
		hasil = {'data': hasil , 'status_code': 200, 'row_count': rowCount}
		########## INSERT LOG ##############
		imd = ImmutableMultiDict(request.args)
		imd = imd.to_dict()
		param_logs = "[" + str(imd) + "]"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_admin)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		####################################
		return make_response(jsonify(hasil),200)
	except Exception as e:
		return bad_request(str(e))

@user.route('/update_profile_admin_lokasi', methods=['POST', 'OPTIONS'])
@jwt_required()
@cross_origin()
def update_profile_admin_lokasi():
	try:
		ROUTE_NAME = str(request.path)

		id_admin = str(get_jwt()["id_admin"])
		role = str(get_jwt()["role"])

		if role not in role_group_admin_lokasi:
			return permission_failed()

		dt = Data()
		data = request.json

		if "nama_admin_lokasi" not in data:
			return parameter_error("Missing email in Request Body")

		nama_admin_lokasi = data["nama_admin_lokasi"]

		query = "UPDATE admin_lokasi SET nama_admin_lokasi =%s WHERE `admin_lokasi`. `id_admin_lokasi` =%s"
		values = (nama_admin_lokasi, id_admin)
		hasil = dt.insert_data(query, values)
		pesan = "Data telah di ubah"
		########## INSERT LOG ##############
		imd = ImmutableMultiDict(request.args)
		imd = imd.to_dict()
		param_logs = "[" + str(imd) + "]"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_admin = "+str(id_admin)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_admin = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': pesan} ), 200)
	except Exception as e:
		return bad_request(str(e))


#endregion ================================= ADMIN Lokasi AREA ==========================================================================

#region ================================= USER AREA ==========================================================================

@user.route('/reset_password', methods=['POST', 'OPTIONS'])
@cross_origin()
def reset_password():
	#khusus admin lokasi
	ROUTE_NAME = str(request.path)
	try:
		data = request.json
		if "email" not in data:
			return parameter_error("Missing email in Request Body")
		email = data["email"]

		dt = Data()
		
		list_tabel_user = ['admin_lokasi','admin_brand','admin','customer'] 
		for tabel_user in list_tabel_user:
			# Check if email is exist and active
			query_temp = "SELECT * FROM {} WHERE email = %s AND is_delete != 1 ".format(tabel_user)
			values_temp = ( email,)
			data_email = dt.get_data(query_temp, values_temp)

			if len(data_email) != 0:
				nama 			= "nama_" + tabel_user
				nama 			= data_email[0][nama]
				old_password 	= data_email[0]["password"]
				break
		
		if len(data_email) == 0:
			return defined_error("Email belum terdaftar")
		if str(data_email[0]["status"]) != "1":
			return defined_error("Akun tidak aktif atau terblokir")

		#token = user.get_reset_token()
		token = jwt.encode({'reset_password': email, 'nama': nama, 'password':old_password,
							'exp': datetime.datetime.now() + datetime.timedelta(minutes=5) - datetime.timedelta(hours=7)}, 
							os.getenv('SECRET_KEY', 'random_key'), algorithm='HS256')
						
		# Try send email first then change password in database
		try:
			template = render_template('reset_password.html', nama=nama, token=token)
			url = app.config['BISAAI_MAIL_SERVER']
			payload = json.dumps(
				{
					'pengirim': app.config['BISAAI_MAIL_SENDER'],
					'penerima': email,
					'isi': template,
					'judul': '[Verifikasi Reset Password Bisa Kitchen]'
				})
			files = {}
			headers = {
				'X-API-KEY': app.config['BISAAI_MAIL_API_KEY'],
				'Content-Type': 'application/json'
			}
			response = requests.request('POST', url, headers = headers, data = payload, files = files, allow_redirects=False, verify=False)
			if response.status_code != 200:
				raise Exception()
		except Exception as e:
			return defined_error("Reset Password Gagal")
		
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+" - email = "+email+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL - email = "+email+"\n"
		tambahLogs(logs)

		hasil = 'Silahkan cek email untuk proses verifikasi'
		return make_response(jsonify({'status_code':200 , 'description': hasil, "token_verif" : token} ), 200)
	except Exception as e:
		return bad_request(str(e))

@user.route('/change_password/<token>', methods=['POST', 'OPTIONS'])
@cross_origin()
def change_password(token):
	try:
		#khusus admin lokasi
		ROUTE_NAME = str(request.path)

		email 			= jwt.decode(str(token), os.getenv('SECRET_KEY', 'random_key'), 
									algorithms=['HS256'])['reset_password']
		nama 			= jwt.decode(str(token), os.getenv('SECRET_KEY', 'random_key'), 
									algorithms=['HS256'])['nama']
		old_password 	= jwt.decode(str(token), os.getenv('SECRET_KEY', 'random_key'), 
									algorithms=['HS256'])['password']

		dt = Data()

		#check apakah password yang terkandung di jwt sudah dirubah
		#sehingga link verifikasi tidak dapat digunakan berulang
		list_tabel_user = ['admin_lokasi','admin_brand','admin','customer'] 
		for tabel_user in list_tabel_user:
			# Check if email is exist and active
			query_temp = "SELECT * FROM {} WHERE email = %s AND is_delete != 1 ".format(tabel_user)
			values_temp = ( email,)
			data_email = dt.get_data(query_temp, values_temp)

			if len(data_email) != 0:
				break

		db_password 	= data_email[0]["password"]
		if str(old_password) != str(db_password):
			return defined_error("Gagal, password sudah dirubah beberapa saat yang lalu, silahkan cek email anda")
		
		data = request.json

		# Check mandatory data
		if "new_password" not in data:
			return parameter_error("Missing new_password in Request Body")
		
		new_password 			= data["new_password"]
		
		newpass_encoded = hashlib.md5(new_password.encode('utf-8')).hexdigest()

		# If send email success, change password in database
		query = "UPDATE {} SET password = %s WHERE email = %s".format(tabel_user)
		values = (newpass_encoded, email)
		dt.insert_data(query, values)

		#======================================================================

		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+" - email = "+email+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL - email = "+email+"\n"
		tambahLogs(logs)

		hasil = 'Berhasil Reset Password'
		return make_response(jsonify({'status_code':200 , 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))

	
#endregion ================================= USER AREA ==========================================================================
