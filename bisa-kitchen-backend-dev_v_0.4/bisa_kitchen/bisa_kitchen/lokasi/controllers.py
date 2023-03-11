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

lokasi = Blueprint('lokasi', __name__, static_folder = '../../upload/lokasi', static_url_path="/media")

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


#region ================================= LOKASI KITCHEN AREA ==========================================================================

@lokasi.route('/get_lokasi_kitchen', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_lokasi_kitchen():
	try:
		ROUTE_NAME = str(request.path)

		dt = Data()

		query = """ SELECT a.*, b.id_provinsi, b.nama_kota, c.nama_provinsi
					FROM lokasi a
					LEFT JOIN kota b ON a.id_kota=b.id_kota
					LEFT JOIN provinsi c ON b.id_provinsi=c.id_provinsi
					WHERE a.is_delete != 1 """
		values = ()

		page = request.args.get("page")
		id_lokasi = request.args.get("id_lokasi")
		id_kota = request.args.get("id_kota")
		id_provinsi = request.args.get("id_provinsi")
		search = request.args.get("search")
		order_by = request.args.get("order_by")

		if (page == None):
			page = 1
		if id_lokasi:
			query += " AND a.id_lokasi = %s "
			values += (id_lokasi, )
		if id_kota:
			query += " AND a.id_kota = %s "
			values += (id_kota, )
		if id_provinsi:
			query += " AND c.id_provinsi = %s "
			values += (id_provinsi, )
		if search:
			query += """ AND CONCAT_WS("|", a.nama_lokasi) LIKE %s """
			values += ("%"+search+"%", )

		if order_by:
			if order_by == "id_asc":
				query += " ORDER BY a.id_lokasi ASC "
			elif order_by == "id_desc":
				query += " ORDER BY a.id_lokasi DESC "
			else:
				query += " ORDER BY a.id_lokasi DESC "
		else:
			query += " ORDER BY a.id_lokasi DESC "

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

@lokasi.route('/insert_lokasi_kitchen', methods=['POST', 'OPTIONS'])
@jwt_required()
@cross_origin()
def insert_lokasi_kitchen():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	role = str(get_jwt()["role"])

	if role not in role_group_super_admin:
		return permission_failed()

	if role in role_group_super_admin:
		id_admin = str(get_jwt()["id_admin"])
		id_user = id_admin
	if role in role_group_customer:
		id_customer = str(get_jwt()["id_customer"])
		id_user = id_customer

	try:
		dt = Data()
		data = request.json

		# Check mandatory data
		if "id_kota" not in data:
			return parameter_error("Missing id_kota in Request Body")
		if "nama_lokasi" not in data:
			return parameter_error("Missing nama_lokasi in Request Body")
		if "deskripsi_lokasi" not in data:
			return parameter_error("Missing deskripsi_lokasi in Request Body")
		if "alamat_lokasi" not in data:
			return parameter_error("Missing alamat_lokasi in Request Body")


		id_kota 			= data["id_kota"]
		nama_lokasi 		= data["nama_lokasi"]
		deskripsi_lokasi 	= data["deskripsi_lokasi"]
		alamat_lokasi 		= data["alamat_lokasi"]

		# cek apakah data kota ada
		query_temp = "SELECT id_kota FROM kota WHERE is_delete!=1 AND id_kota = %s"
		values_temp = (id_kota, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data Kota tidak ditemukan")

		# Cek data-data opsional

		if "gmaps_lokasi" in data:
			gmaps_lokasi = data["gmaps_lokasi"]
		else:
			gmaps_lokasi = None

		# Insert ke tabel db
		query = "INSERT INTO lokasi (id_kota, nama_lokasi, deskripsi_lokasi, alamat_lokasi, gmaps_lokasi) VALUES (%s, %s, %s, %s, %s)"
		values = (id_kota, nama_lokasi, deskripsi_lokasi, alamat_lokasi, gmaps_lokasi)
		id_lokasi = dt.insert_data_last_row(query, values)

		hasil = "Berhasil menambahkan lokasi kitchen"
		hasil_data = {
			"id_lokasi" : id_lokasi
		}
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil, 'data' : hasil_data} ), 200)
	except Exception as e:
		return bad_request(str(e))

@lokasi.route('/update_lokasi_kitchen', methods=['PUT', 'OPTIONS'])
@jwt_required()
@cross_origin()
def update_lokasi_kitchen():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	role = str(get_jwt()["role"])

	if role not in role_group_super_admin:
		return permission_failed()

	if role in role_group_super_admin:
		id_admin = str(get_jwt()["id_admin"])
		id_user = id_admin
	if role in role_group_customer:
		id_customer = str(get_jwt()["id_customer"])
		id_user = id_customer

	try:
		dt = Data()
		data = request.json

		if "id_lokasi" not in data:
			return parameter_error("Missing id_lokasi in Request Body")

		id_lokasi = data["id_lokasi"]

		# Cek apakah data lokasi ada
		query_temp = "SELECT a.id_lokasi FROM lokasi a WHERE a.is_delete != 1 AND a.id_lokasi = %s"
		values_temp = (id_lokasi, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data lokasi tidak ditemukan")

		query = """ UPDATE lokasi SET id_lokasi=id_lokasi """
		values = ()

		if "id_kota" in data:
			id_kota = data["id_kota"]

			# cek apakah data kota ada
			query_temp = "SELECT id_kota FROM kota WHERE is_delete!=1 AND id_kota = %s"
			values_temp = (id_kota, )
			data_temp = dt.get_data(query_temp, values_temp)
			if len(data_temp) == 0:
				return defined_error("Gagal, Data Kota tidak ditemukan")

			query += """ ,id_kota = %s """
			values += (id_kota, )

		if "nama_lokasi" in data:
			nama_lokasi = data["nama_lokasi"]
			query += """ ,nama_lokasi = %s """
			values += (nama_lokasi, )

		if "deskripsi_lokasi" in data:
			deskripsi_lokasi = data["deskripsi_lokasi"]
			query += """ ,deskripsi_lokasi = %s """
			values += (deskripsi_lokasi, )

		if "alamat_lokasi" in data:
			alamat_lokasi = data["alamat_lokasi"]
			query += """ ,alamat_lokasi = %s """
			values += (alamat_lokasi, )

		if "gmaps_lokasi" in data:
			gmaps_lokasi = data["gmaps_lokasi"]
			query += """ ,gmaps_lokasi = %s """
			values += (gmaps_lokasi, )

		if "is_delete" in data:
			is_delete = data["is_delete"]
			# validasi data is_delete
			if str(is_delete) not in ["1"]:
				return parameter_error("Invalid is_delete Parameter")
			query += """ ,is_delete = %s """
			values += (is_delete, )

		query += """ WHERE id_lokasi = %s """
		values += (id_lokasi, )
		dt.insert_data(query, values)

		hasil = "Berhasil mengubah data lokasi kitchen"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))

#endregion ================================= LOKASI KITCHEN AREA ==========================================================================


#region ================================= LOKASI GALERI KITCHEN AREA ==========================================================================

@lokasi.route('/get_lokasi_galeri', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_lokasi_galeri():
	try:
		ROUTE_NAME = str(request.path)

		dt = Data()

		query = """ SELECT a.*, b.nama_lokasi
					FROM lokasi_galeri a LEFT JOIN lokasi b ON a.id_lokasi=b.id_lokasi
					WHERE a.is_delete != 1 """
		values = ()

		id_lokasi_galeri = request.args.get("id_lokasi_galeri")
		id_lokasi = request.args.get("id_lokasi")
		search = request.args.get("search")
		order_by = request.args.get("order_by")

		if id_lokasi_galeri:
			query += " AND a.id_lokasi_galeri = %s "
			values += (id_lokasi_galeri, )
		if id_lokasi:
			query += " AND a.id_lokasi = %s "
			values += (id_lokasi, )
		if search:
			query += """ AND CONCAT_WS("|", a.nama_lokasi_galeri) LIKE %s """
			values += ("%"+search+"%", )

		if order_by:
			if order_by == "id_asc":
				query += " ORDER BY a.id_lokasi_galeri ASC "
			elif order_by == "id_desc":
				query += " ORDER BY a.id_lokasi_galeri DESC "
			else:
				query += " ORDER BY a.id_lokasi_galeri DESC "
		else:
			query += " ORDER BY a.id_lokasi_galeri DESC "

		rowCount = dt.row_count(query, values)
		hasil = dt.get_data(query, values)
		hasil = {'data': hasil , 'status_code': 200, 'page': 1, 'offset': 'none', 'row_count': rowCount}
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

@lokasi.route('/insert_lokasi_galeri', methods=['POST', 'OPTIONS'])
@jwt_required()
@cross_origin()
def insert_lokasi_galeri():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	role = str(get_jwt()["role"])

	if role not in role_group_super_admin:
		return permission_failed()

	if role in role_group_super_admin:
		id_admin = str(get_jwt()["id_admin"])
		id_user = id_admin
	if role in role_group_customer:
		id_customer = str(get_jwt()["id_customer"])
		id_user = id_customer

	try:
		dt = Data()
		data = request.json

		# Check mandatory data
		if "id_lokasi" not in data:
			return parameter_error("Missing id_lokasi in Request Body")
		if "nama_lokasi_galeri" not in data:
			return parameter_error("Missing nama_lokasi_galeri in Request Body")
		if "file_lokasi_galeri" not in data:
			return parameter_error("Missing file_lokasi_galeri in Request Body")


		id_lokasi 				= data["id_lokasi"]
		nama_lokasi_galeri 		= data["nama_lokasi_galeri"]
		file_lokasi_galeri 		= data["file_lokasi_galeri"]

		# cek apakah data lokasi ada
		query_temp = "SELECT a.id_lokasi FROM lokasi a WHERE a.is_delete != 1 AND a.id_lokasi = %s"
		values_temp = (id_lokasi, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data lokasi tidak ditemukan")

		# Cek data-data opsional

		if "deskripsi_lokasi_galeri" in data:
			deskripsi_lokasi_galeri = data["deskripsi_lokasi_galeri"]
		else:
			deskripsi_lokasi_galeri = None

		# Save file lokasi galeri
		filename_photo = secure_filename(strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_lokasi_kitchen.png")
		save(file_lokasi_galeri, os.path.join(app.config['UPLOAD_FOLDER_FOTO_LOKASI_KITCHEN'], filename_photo))

		# Insert ke tabel db
		query = "INSERT INTO lokasi_galeri (id_lokasi, nama_lokasi_galeri, deskripsi_lokasi_galeri, file_lokasi_galeri) VALUES (%s, %s, %s, %s)"
		values = (id_lokasi, nama_lokasi_galeri, deskripsi_lokasi_galeri, filename_photo,)
		id_lokasi_galeri = dt.insert_data_last_row(query, values)

		hasil = "Berhasil menambahkan galeri lokasi kitchen"
		hasil_data = {
			"id_lokasi_galeri" : id_lokasi_galeri
		}
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil, 'data' : hasil_data} ), 200)
	except Exception as e:
		return bad_request(str(e))

#endregion ================================= LOKASI GALERI KITCHEN AREA ==========================================================================


