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

daerah = Blueprint('daerah', __name__, static_folder = '../../upload/daerah', static_url_path="/media")

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

#region ================================= PROVINSI ==========================================================================

@daerah.route('/get_provinsi', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_provinsi():
	try:
		ROUTE_NAME = str(request.path)
		
		dt = Data()

		query = """ SELECT *
					FROM provinsi
					WHERE is_delete != 1 """
		values = ()

		page = request.args.get("page")
		id_provinsi = request.args.get("id_provinsi")
		search = request.args.get("search")
		order_by = request.args.get("order_by")

		if (page == None):
			page = 1
		if id_provinsi:
			query += " AND id_provinsi = %s "
			values += (id_provinsi, )
		if search:
			query += """ AND CONCAT_WS("|", nama_provinsi) LIKE %s """
			values += ("%"+search+"%", )

		if order_by:
			if order_by == "id_asc":
				query += " ORDER BY id_provinsi ASC "
			elif order_by == "id_desc":
				query += " ORDER BY id_provinsi DESC "
			else:
				query += " ORDER BY id_provinsi DESC "
		else:
			query += " ORDER BY id_provinsi DESC "

		rowCount = dt.row_count(query, values)
		hasil = dt.get_data_lim(query, values, page)
		hasil = {'data': hasil , 'status_code': 200, 'page': page, 'offset': '10', 'row_count': rowCount}
		########## INSERT LOG ##############
		imd = ImmutableMultiDict(request.args)
		imd = imd.to_dict()
		param_logs = "[" + str(imd) + "]"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+" - param_logs = "+param_logs+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL - param_logs = "+param_logs+"\n"
		tambahLogs(logs)
		####################################
		return make_response(jsonify(hasil),200)
	except Exception as e:
		return bad_request(str(e))

@daerah.route('/insert_provinsi', methods=['POST', 'OPTIONS'])
@jwt_required()
@cross_origin()
def insert_provinsi():
	try:
		ROUTE_NAME = str(request.path)

		now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

		role 	= str(get_jwt()["role"])

		if role not in role_group_super_admin:
			return permission_failed()

		if role in role_group_super_admin:
			id_admin = str(get_jwt()["id_admin"])
			id_user = id_admin

		dt = Data()
		data = request.json

		# Check mandatory data
		if "nama_provinsi" not in data:
			return parameter_error("Missing nama_provinsi in Request Body")

		nama_provinsi 					= data["nama_provinsi"]

		# Insert to table tempat uji kompetensi
		query = "INSERT INTO provinsi (nama_provinsi) VALUES (%s)"
		values = (nama_provinsi, )
		id_provinsi = dt.insert_data_last_row(query, values)

		hasil = "Berhasil menambahkan provinsi"
		hasil_data = {
			"id_provinsi" : id_provinsi
		}
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil, 'data' : hasil_data} ), 200)
	except Exception as e:
		return bad_request(str(e))

@daerah.route('/update_provinsi', methods=['PUT', 'OPTIONS'])
@jwt_required()
@cross_origin()
def update_provinsi():
	try:
		ROUTE_NAME = str(request.path)

		now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

		role 	= str(get_jwt()["role"])

		if role not in role_group_super_admin:
			return permission_failed()

		if role in role_group_super_admin:
			id_admin = str(get_jwt()["id_admin"])
			id_user = id_admin

		dt = Data()
		data = request.json

		if "id_provinsi" not in data:
			return parameter_error("Missing id_provinsi in Request Body")

		id_provinsi = data["id_provinsi"]

		# Cek apakah data skema sertifikasi ada
		query_temp = " SELECT id_provinsi FROM provinsi WHERE is_delete!=1 AND id_provinsi = %s "
		values_temp = (id_provinsi, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, data tidak ditemukan")

		query = """ UPDATE provinsi SET id_provinsi=id_provinsi """
		values = ()
		
		if "nama_provinsi" in data:
			nama_provinsi = data["nama_provinsi"]	
			query += """ ,nama_provinsi = %s """
			values += (nama_provinsi, )
		
		if "is_delete" in data:
			is_delete = data["is_delete"]
			# validasi data is_delete
			if str(is_delete) not in ["1"]:
				return parameter_error("Invalid is_delete Parameter")
			query += """ ,is_delete = %s """
			values += (is_delete, )
		
		query += """ WHERE id_provinsi = %s """
		values += (id_provinsi, )
		dt.insert_data(query, values)

		hasil = "Berhasil mengubah data provinsi"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))

#endregion ================================= PROVINSI ==========================================================================

#region ================================= KOTA ==========================================================================

@daerah.route('/get_kota', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_tempat_uji_kompetensi():
	try:
		ROUTE_NAME = str(request.path)
		
		dt = Data()

		query = """ SELECT a.*, b.nama_provinsi
					FROM kota a
					LEFT JOIN provinsi b ON a.id_provinsi=b.id_provinsi
					WHERE a.is_delete != 1 """
		values = ()

		page = request.args.get("page")
		id_kota = request.args.get("id_kota")
		id_provinsi = request.args.get("id_provinsi")
		search = request.args.get("search")
		order_by = request.args.get("order_by")

		if (page == None):
			page = 1
		if id_kota:
			query += " AND a.id_kota = %s "
			values += (id_kota, )
		if id_provinsi:
			query += " AND b.id_provinsi = %s "
			values += (id_provinsi, )
		if search:
			query += """ AND CONCAT_WS("|", a.nama_kota) LIKE %s """
			values += ("%"+search+"%", )

		if order_by:
			if order_by == "id_asc":
				query += " ORDER BY a.id_kota ASC "
			elif order_by == "id_desc":
				query += " ORDER BY a.id_kota DESC "
			else:
				query += " ORDER BY a.id_kota DESC "
		else:
			query += " ORDER BY a.id_kota DESC "

		rowCount = dt.row_count(query, values)
		hasil = dt.get_data_lim(query, values, page)
		hasil = {'data': hasil , 'status_code': 200, 'page': page, 'offset': '10', 'row_count': rowCount}
		########## INSERT LOG ##############
		imd = ImmutableMultiDict(request.args)
		imd = imd.to_dict()
		param_logs = "[" + str(imd) + "]"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+" - param_logs = "+param_logs+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL - param_logs = "+param_logs+"\n"
		tambahLogs(logs)
		####################################
		return make_response(jsonify(hasil),200)
	except Exception as e:
		return bad_request(str(e))

@daerah.route('/insert_kota', methods=['POST', 'OPTIONS'])
@jwt_required()
@cross_origin()
def insert_kota():
	try:
		ROUTE_NAME = str(request.path)

		now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

		role 	= str(get_jwt()["role"])

		if role not in role_group_super_admin:
			return permission_failed()

		if role in role_group_super_admin:
			id_admin = str(get_jwt()["id_admin"])
			id_user = id_admin

		dt = Data()
		data = request.json

		# Check mandatory data
		if "id_provinsi" not in data:
			return parameter_error("Missing id_provinsi in Request Body")
		if "nama_kota" not in data:
			return parameter_error("Missing nama_kota in Request Body")

		id_provinsi 					= data["id_provinsi"]
		nama_kota 						= data["nama_kota"]

		# cek apakah data kota ada
		query_temp = "SELECT id_provinsi FROM provinsi WHERE is_delete!=1 AND id_provinsi = %s"
		values_temp = (id_provinsi, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data Kota tidak ditemukan")

		# Insert to table tempat uji kompetensi
		query = "INSERT INTO kota (id_provinsi, nama_kota) VALUES (%s,%s)"
		values = (id_provinsi, nama_kota, )
		id_kota = dt.insert_data_last_row(query, values)

		hasil = "Berhasil menambahkan kota"
		hasil_data = {
			"id_kota" : id_kota
		}
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil, 'data' : hasil_data} ), 200)
	except Exception as e:
		return bad_request(str(e))

@daerah.route('/update_kota', methods=['PUT', 'OPTIONS'])
@jwt_required()
@cross_origin()
def update_kota():
	try:
		ROUTE_NAME = str(request.path)

		now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

		role 	= str(get_jwt()["role"])

		if role not in role_group_super_admin:
			return permission_failed()

		if role in role_group_super_admin:
			id_admin = str(get_jwt()["id_admin"])
			id_user = id_admin

		dt = Data()
		data = request.json

		if "id_kota" not in data:
			return parameter_error("Missing id_kota in Request Body")

		id_kota = data["id_kota"]

		# Cek apakah data skema sertifikasi ada
		query_temp = " SELECT id_kota FROM kota WHERE is_delete!=1 AND id_kota = %s "
		values_temp = (id_kota, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, data tidak ditemukan")

		query = """ UPDATE kota SET id_kota=id_kota """
		values = ()
		
		if "id_provinsi" in data:
			id_provinsi = data["id_provinsi"]
			
			# cek apakah data kota ada
			query_temp = "SELECT id_provinsi FROM provinsi WHERE is_delete!=1 AND id_provinsi = %s"
			values_temp = (id_provinsi, )
			data_temp = dt.get_data(query_temp, values_temp)
			if len(data_temp) == 0:
				return defined_error("Gagal, Data Provinsi tidak ditemukan")

			query += """ ,id_provinsi = %s """
			values += (id_provinsi, )

		if "nama_kota" in data:
			nama_kota = data["nama_kota"]	
			query += """ ,nama_kota = %s """
			values += (nama_kota, )
		
		if "is_delete" in data:
			is_delete = data["is_delete"]
			# validasi data is_delete
			if str(is_delete) not in ["1"]:
				return parameter_error("Invalid is_delete Parameter")
			query += """ ,is_delete = %s """
			values += (is_delete, )
		
		query += """ WHERE id_kota = %s """
		values += (id_kota, )
		dt.insert_data(query, values)

		hasil = "Berhasil mengubah data kota"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))

#endregion ================================= KOTA ==========================================================================


