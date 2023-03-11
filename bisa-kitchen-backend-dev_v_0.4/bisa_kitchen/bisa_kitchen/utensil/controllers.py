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

from . models import Data

#11 superadmin, 21 Customer
role_group_super_admin = ["11"]
role_group_customer = ["21"]
role_group_all = ["11", "21"]

#now = datetime.datetime.now()

utensil = Blueprint('utensil', __name__, static_folder = '../../upload/utensil', static_url_path="/media")

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


#region ================================= UTENSIL AREA ==========================================================================

@utensil.route('/get_utensil', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_utensil():
	try:
		ROUTE_NAME = str(request.path)

		dt = Data()

		query = """ SELECT a.*
					FROM utnsl_utensil a
					WHERE a.is_delete != 1 """
		values = ()

		page = request.args.get("page")
		id_utensil = request.args.get("id_utensil")
		search = request.args.get("search")
		order_by = request.args.get("order_by")

		if (page == None):
			page = 1
		if id_utensil:
			query += """ AND a.id_utensil = %s """
			values += (id_utensil, )
		if search:
			query += """ AND CONCAT_WS("|", a.nama_utensil) LIKE %s """
			values += ("%"+search+"%", )

		if order_by:
			if order_by == "id_asc":
				query += " ORDER BY a.id_utensil ASC "
			elif order_by == "id_desc":
				query += " ORDER BY a.id_utensil DESC "
			else:
				query += " ORDER BY a.id_utensil DESC "
		else:
			query += " ORDER BY a.id_utensil DESC "

		rowCount = dt.row_count(query, values)
		hasil = dt.get_data_lim(query, values, page)
		hasil = {'data': hasil , 'status_code': 200, 'page': page, 'offset': '10', 'row_count': rowCount}
		########## INSERT LOG ##############
		imd = ImmutableMultiDict(request.args)
		imd = imd.to_dict()
		param_logs = "[" + str(imd) + "]"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_customer = "+str(id_customer)+" - roles = "+str(role)+" - param_logs = "+param_logs+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_customer = NULL - roles = NULL - param_logs = "+param_logs+"\n"
		print(logs)
		tambahLogs(logs)
		####################################
		return make_response(jsonify(hasil),200)
	except Exception as e:
		return bad_request(str(e))

@utensil.route('/insert_utensil', methods=['POST', 'OPTIONS'])
@jwt_required()
@cross_origin()
def insert_utensil():

	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	id_admin = str(get_jwt()["id_admin"])
	role = str(get_jwt()["role"])

	if role not in role_group_super_admin:
		return permission_failed()

	try:
		dt = Data()
		data = request.json

		# Check mandatory data
		if "nama_utensil" not in data:
			return parameter_error("Missing nama_utensil in Request Body")
		if "deskripsi_utensil" not in data:
			return parameter_error("Missing deskripsi_utensil in Request Body")
		if "jumlah" not in data:
			return parameter_error("Missing jumlah in Request Body")
		if "harga_sewa" not in data:
			return parameter_error("Missing harga_sewa in Request Body")
		if "id_kategori" not in data:
			return parameter_error("Missing id_kategori in Request Body")
		if "id_lokasi" not in data:
			return parameter_error("Missing id_lokasi in Request Body")



		nama_utensil 					= data["nama_utensil"]
		deskripsi_utensil 				= data["deskripsi_utensil"]
		jumlah 			 				= data["jumlah"]
		harga_sewa		 				= data["harga_sewa"]
		id_kategori		 				= data["id_kategori"]
		id_lokasi		 				= data["id_lokasi"]

		query_temp = "SELECT id_kategori FROM utnsl_kategori WHERE is_delete!=1 AND id_kategori = %s"
		values_temp = (id_kategori, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, kategori tidak ditemukan")

		query_temp = "SELECT id_lokasi FROM lokasi WHERE id_lokasi = %s"
		values_temp = (id_lokasi, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, lokasi tidak ditemukan")

		# Cek data-data opsional

		if "foto_utensil_1" in data:
			filename_photo = secure_filename(now.strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_utensil_1.png")
			save(data["foto_utensil_1"], os.path.join(app.config['UPLOAD_FOLDER_FOTO_UTENSIL'], filename_photo))

			foto_utensil_1 = filename_photo
		else:
			foto_utensil_1 = None

		if "foto_utensil_2" in data:
			filename_photo = secure_filename(now.strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_utensil_2.png")
			save(data["foto_utensil_2"], os.path.join(app.config['UPLOAD_FOLDER_FOTO_UTENSIL'], filename_photo))

			foto_utensil_2 = filename_photo
		else:
			foto_utensil_2 = None

		if "foto_utensil_3" in data:
			filename_photo = secure_filename(now.strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_utensil_3.png")
			save(data["foto_utensil_3"], os.path.join(app.config['UPLOAD_FOLDER_FOTO_UTENSIL'], filename_photo))

			foto_utensil_3 = filename_photo
		else:
			foto_utensil_3 = None

		# Insert to table tempat uji kompetensi
		query = "INSERT INTO utnsl_utensil (nama_utensil, deskripsi_utensil, jumlah, harga_sewa, id_kategori, id_lokasi, foto_utensil_1, foto_utensil_2, foto_utensil_3 ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
		values = (nama_utensil, deskripsi_utensil, jumlah, harga_sewa, id_kategori, id_lokasi, foto_utensil_1, foto_utensil_2, foto_utensil_3)
		id_utensil = dt.insert_data_last_row(query, values)

		hasil = "Berhasil menambahkan utensil"
		hasil_data = {
			"id_utensil" : id_utensil
		}
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_admin = "+str(id_admin)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_admin = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil, 'data' : hasil_data} ), 200)
	except Exception as e:
		return bad_request(str(e))

@utensil.route('/update_utensil', methods=['PUT', 'OPTIONS'])
@jwt_required()
@cross_origin()
def update_utensil():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	id_admin 		= str(get_jwt()["id_admin"])
	role 			= str(get_jwt()["role"])

	if role not in role_group_super_admin:
		return permission_failed()

	try:
		dt = Data()
		data = request.json

		if "id_utensil" not in data:
			return parameter_error("Missing id_utensil in Request Body")

		id_utensil = data["id_utensil"]

		# Cek apakah data utensil ada
		query_temp = " SELECT id_utensil FROM utnsl_utensil WHERE is_delete!=1 AND id_utensil = %s "
		values_temp = (id_utensil, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, data tidak ditemukan")

		query = """ UPDATE utnsl_utensil SET id_utensil=id_utensil """
		values = ()


		if "nama_utensil" in data:
			nama_utensil = data["nama_utensil"]
			query += """ ,nama_utensil = %s """
			values += (nama_utensil, )

		if "deskripsi_utensil" in data:
			deskripsi_utensil = data["deskripsi_utensil"]
			query += """ ,deskripsi_utensil = %s """
			values += (deskripsi_utensil, )

		if "jumlah" in data:
			jumlah = data["jumlah"]
			query += """ ,jumlah = %s """
			values += (jumlah, )

		if "harga_sewa" in data:
			harga_sewa = data["harga_sewa"]
			query += """ ,harga_sewa = %s """
			values += (harga_sewa, )

		if "id_kategori" in data:
			id_kategori = data["id_kategori"]
			query_temp = "SELECT id_kategori FROM utnsl_kategori WHERE is_delete!=1 AND id_kategori = %s"
			values_temp = (id_kategori, )
			data_temp = dt.get_data(query_temp, values_temp)
			if len(data_temp) == 0:
				return defined_error("Gagal, kategori tidak ditemukan")
			query += """ ,id_kategori = %s """
			values += (id_kategori, )

		if "id_lokasi" in data:
			id_lokasi = data["id_lokasi"]
			query_temp = "SELECT id_lokasi FROM lokasi WHERE id_lokasi = %s"
			values_temp = (id_lokasi, )
			data_temp = dt.get_data(query_temp, values_temp)
			if len(data_temp) == 0:
				return defined_error("Gagal, lokasi tidak ditemukan")
			query += """ ,id_lokasi = %s """
			values += (id_lokasi, )

		if "foto_utensil_1" in data:
			filename_photo = secure_filename(now.strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_utensil_1.png")
			save(data["foto_utensil_1"], os.path.join(app.config['UPLOAD_FOLDER_FOTO_UTENSIL'], filename_photo))

			foto_utensil_1 = filename_photo

			query += """ ,foto_utensil_1 = %s """
			values += (foto_utensil_1, )

		if "foto_utensil_2" in data:
			filename_photo = secure_filename(now.strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_utensil_2.png")
			save(data["foto_utensil_2"], os.path.join(app.config['UPLOAD_FOLDER_FOTO_UTENSIL'], filename_photo))

			foto_utensil_2 = filename_photo

			query += """ ,foto_utensil_2 = %s """
			values += (foto_utensil_2, )

		if "foto_utensil_3" in data:
			filename_photo = secure_filename(now.strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_utensil_3.png")
			save(data["foto_utensil_3"], os.path.join(app.config['UPLOAD_FOLDER_FOTO_UTENSIL'], filename_photo))

			foto_utensil_3 = filename_photo

			query += """ ,foto_utensil_3 = %s """
			values += (foto_utensil_3, )

		if "is_delete" in data:
			is_delete = data["is_delete"]
			# validasi data is_delete
			if str(is_delete) not in ["1"]:
				return parameter_error("Invalid is_delete Parameter")
			query += """ ,is_delete = %s """
			values += (is_delete, )

		query += """ WHERE id_utensil = %s """
		values += (id_utensil, )
		dt.insert_data(query, values)

		hasil = "Berhasil mengupdate Utensil"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_admin = "+str(id_admin)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_admin = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))

#endregion ================================= UTENSIL AREA ==========================================================================

#region ================================= UTENSIL KATEGORI AREA ==========================================================================

@utensil.route('/get_utensil_kategori', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_utensil_kategori():
	try:
		ROUTE_NAME = str(request.path)
		
		dt = Data()

		query = """ SELECT *
					FROM utnsl_kategori
					WHERE is_delete != 1 """
		values = ()

		page = request.args.get("page")
		id_kategori = request.args.get("id_kategori")
		search = request.args.get("search")
		is_aktif = request.args.get("is_aktif")
		order_by = request.args.get("order_by")

		if (page == None):
			page = 1
		if id_kategori:
			query += " AND id_kategori = %s "
			values += (id_kategori, )
		if search:
			query += """ AND CONCAT_WS("|", nama_kategori) LIKE %s """
			values += ("%"+search+"%", )
		if is_aktif:
			query += " AND is_aktif = %s "
			values += (is_aktif, )

		if order_by:
			if order_by == "id_asc":
				query += " ORDER BY id_kategori ASC "
			elif order_by == "id_desc":
				query += " ORDER BY id_kategori DESC "
			else:
				query += " ORDER BY id_kategori DESC "
		else:
			query += " ORDER BY id_kategori DESC "

		rowCount = dt.row_count(query, values)
		hasil = dt.get_data_lim(query, values, page)
		hasil = {'data': hasil , 'status_code': 200, 'page': page, 'offset': '10', 'row_count': rowCount}
		########## INSERT LOG ##############
		imd = ImmutableMultiDict(request.args)
		imd = imd.to_dict()
		param_logs = "[" + str(imd) + "]"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_customer = "+str(id_customer)+" - roles = "+str(role)+" - param_logs = "+param_logs+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_customer = NULL - roles = NULL - param_logs = "+param_logs+"\n"
		print(logs)
		tambahLogs(logs)
		####################################
		return make_response(jsonify(hasil),200)
	except Exception as e:
		return bad_request(str(e))

@utensil.route('/insert_utensil_kategori', methods=['POST', 'OPTIONS'])
@jwt_required()
@cross_origin()
def insert_utensil_kategori():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	id_admin = str(get_jwt()["id_admin"])
	role = str(get_jwt()["role"])

	if role not in role_group_super_admin:
		return permission_failed()

	try:
		dt = Data()
		data = request.json
		
		# Check mandatory data
		if "nama_kategori" not in data:
			return parameter_error("Missing nama_kategori in Request Body")
		if "deskripsi_kategori" not in data:
			return parameter_error("Missing deskripsi_kategori in Request Body")
		
		nama_kategori 					= data["nama_kategori"]
		deskripsi_kategori 				= data["deskripsi_kategori"]

		# Insert to table utensil kategori
		query = "INSERT INTO utnsl_kategori (nama_kategori, deskripsi_kategori) VALUES (%s,%s)"
		values = (nama_kategori, deskripsi_kategori)
		id_kategori = dt.insert_data_last_row(query, values)

		hasil = "Berhasil menambahkan utensil kategori"
		hasil_data = {
			"id_kategori" : id_kategori
		}
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_admin = "+str(id_admin)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_admin = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil, 'data' : hasil_data} ), 200)
	except Exception as e:
		return bad_request(str(e))

@utensil.route('/update_utensil_kategori', methods=['PUT', 'OPTIONS'])
@jwt_required()
@cross_origin()
def update_utensil_kategori():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	id_admin 		= str(get_jwt()["id_admin"])
	role 			= str(get_jwt()["role"])

	if role not in role_group_super_admin:
		return permission_failed()
	
	try:
		dt = Data()
		data = request.json

		if "id_kategori" not in data:
			return parameter_error("Missing id_kategori in Request Body")

		id_kategori = data["id_kategori"]

		# Cek apakah data skema sertifikasi ada
		query_temp = " SELECT id_kategori FROM utnsl_kategori WHERE is_delete!=1 AND id_kategori = %s "
		values_temp = (id_kategori, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, data tidak ditemukan")

		query = """ UPDATE utnsl_kategori SET id_kategori=id_kategori """
		values = ()
		
		if "nama_kategori" in data:
			nama_kategori = data["nama_kategori"]	
			query += """ ,nama_kategori = %s """
			values += (nama_kategori, )

		if "deskripsi_kategori" in data:
			deskripsi_kategori = data["deskripsi_kategori"]	
			query += """ ,deskripsi_kategori = %s """
			values += (deskripsi_kategori, )

		if "is_delete" in data:
			is_delete = data["is_delete"]
			# validasi data is_delete
			if str(is_delete) not in ["1"]:
				return parameter_error("Invalid is_delete Parameter")
			query += """ ,is_delete = %s """
			values += (is_delete, )
		
		query += """ WHERE id_kategori = %s """
		values += (id_kategori, )
		dt.insert_data(query, values)

		hasil = "Berhasil mengubah data utensil kategori"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_admin = "+str(id_admin)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_admin = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))

#endregion ================================= utnsl_kategori ==========================================================================
