from flask import Blueprint, jsonify, request, make_response, render_template
from flask import current_app as app
from flask_jwt_extended import get_jwt, jwt_required
from flask_cors import cross_origin
from werkzeug.utils import secure_filename
from werkzeug.datastructures import ImmutableMultiDict
from time import gmtime, strftime, strptime
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
role_group_admin_lokasi = ["12"]
role_group_admin_brand = ["13"]
role_group_admin = ["11", "12", "13"]
role_group_customer = ["21"]
role_group_all = ["11", "12", "13", "21"]

#now = datetime.datetime.now()

dapur = Blueprint('dapur', __name__, static_folder = '../../upload/dapur', static_url_path="/media")

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

def insert_payment(jsonData):
	url = app.config['BISAAIPAYMENT_BASE_URL'] + "transaksi/insert_transaksi_sprint"
	headers = {
	  'X-API-KEY': app.config['BISAAIPAYMENT_KEY'],
	  'Content-Type': 'application/json'
	}
	response = requests.request("POST", url, headers=headers, data = jsonData, verify=False)
	data = response.text.encode('utf8')
	return json.loads(data)

def desc_metode_pembayaran(service_code):
	metode_pembayaran = ""
	service_code = str(service_code)
	if service_code in ["9999", "9998"]:
		if service_code == "9999":
			metode_pembayaran = Markup("Transfer Manual <b>BNI</b> <br>Nomor Rekening : <b>1315441125</b> Atas Nama <b>PT BISA ARTIFISIAL INDONESIA</b>")
		elif service_code == "9998":
			metode_pembayaran = Markup("Transfer Manual <b>BCA</b> <br>Nomor Rekening : <b>0866131541</b> Atas Nama <b>PT BISA ARTIFISIAL INDONESIA</b>")
	else:
		url = app.config['BISAAIPAYMENT_BASE_URL'] + "transaksi/get_merchant_metode_pembayaran?service_code=%s" % (service_code, )
		payload = {}
		headers = {
			'X-API-KEY': app.config['BISAAIPAYMENT_KEY'],
			'Content-Type': 'application/json'
		}
		response = requests.request("GET", url, headers=headers, data = payload, verify=False)
		data = json.loads(response.text.encode('utf8'))
		if data["status_code"] == 200:
			if len(data["data"]) != 0:
				metode_pembayaran = Markup("<b>"+data["data"][0]["metode"]+"</b>")

	return metode_pembayaran

def get_code_wallet():
	url = app.config['BISAAIPAYMENT_BASE_URL'] + "transaksi/get_merchant_metode_pembayaran?tipe=1"
	headers = {
	  'X-API-KEY': app.config['BISAAIPAYMENT_KEY'],
	  'Content-Type': 'application/json'
	}
	response = requests.request("GET", url, headers=headers, verify=False)
	data = json.loads(response.text.encode('utf8'))
	list_code_wallet = []

	for x in data["data"]:
		list_code_wallet.append(x["service_code"])

	return list_code_wallet

#endregion ================================= FUNGSI-FUNGSI AREA ===============================================================


#region ================================= DAPUR AREA ==========================================================================

@dapur.route('/get_dapur', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_dapur():
	try:
		ROUTE_NAME = str(request.path)

		dt = Data()

		query = """ SELECT a.*, b.nama_lokasi, c.nama_tingkat
					FROM dpr_dapur a
					LEFT JOIN lokasi b ON a.id_lokasi=b.id_lokasi
					LEFT JOIN dpr_tingkat c ON a.id_tingkat=c.id_tingkat
					WHERE a.is_delete!=1 """
		values = ()

		page = request.args.get("page")
		id_dapur = request.args.get("id_dapur")
		id_lokasi = request.args.get("id_lokasi")
		id_tingkat = request.args.get("id_tingkat")
		search = request.args.get("search")
		order_by = request.args.get("order_by")

		if (page == None):
			page = 1
		if id_dapur:
			query += " AND a.id_dapur = %s "
			values += (id_dapur, )
		if id_lokasi:
			query += " AND a.id_lokasi = %s "
			values += (id_lokasi, )
		if id_tingkat:
			query += " AND a.id_tingkat = %s "
			values += (id_tingkat, )
		if search:
			query += """ AND CONCAT_WS("|", a.nama_dapur) LIKE %s """
			values += ("%"+search+"%", )

		if order_by:
			if order_by == "id_asc":
				query += " ORDER BY a.id_dapur ASC "
			elif order_by == "id_desc":
				query += " ORDER BY a.id_dapur DESC "
			else:
				query += " ORDER BY a.id_dapur DESC "
		else:
			query += " ORDER BY a.id_dapur DESC "

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

@dapur.route('/insert_dapur', methods=['POST', 'OPTIONS'])
@jwt_required()
@cross_origin()
def insert_dapur():
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
		if "id_tingkat" not in data:
			return parameter_error("Missing id_tingkat in Request Body")
		if "nama_dapur" not in data:
			return parameter_error("Missing nama_dapur in Request Body")
		if "deskripsi_dapur" not in data:
			return parameter_error("Missing deskripsi_dapur in Request Body")


		id_lokasi 				= data["id_lokasi"]
		id_tingkat 				= data["id_tingkat"]
		nama_dapur 				= data["nama_dapur"]
		deskripsi_dapur 		= data["deskripsi_dapur"]

		# cek apakah data lokasi ada
		query_temp = "SELECT a.id_lokasi FROM lokasi a WHERE a.is_delete != 1 AND a.id_lokasi = %s"
		values_temp = (id_lokasi, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data lokasi tidak ditemukan")

		# cek apakah data tingkat ada
		query_temp = "SELECT a.id_tingkat FROM dpr_tingkat a WHERE a.is_delete != 1 AND a.id_tingkat = %s"
		values_temp = (id_tingkat, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data tingkatan dapur tidak ditemukan")

		# Cek data opsional

		if "thumbnail_dapur" in data:
			filename_photo = secure_filename(strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_thumbnail_dapur.png")
			save(data["thumbnail_dapur"], os.path.join(app.config['UPLOAD_FOLDER_FOTO_DAPUR'], filename_photo))

			thumbnail_dapur = filename_photo
		else:
			thumbnail_dapur = None

		# Insert ke tabel db
		query = "INSERT INTO dpr_dapur (id_lokasi, id_tingkat, nama_dapur, deskripsi_dapur, thumbnail_dapur) VALUES (%s, %s, %s, %s, %s)"
		values = (id_lokasi, id_tingkat, nama_dapur, deskripsi_dapur, thumbnail_dapur,)
		id_dapur = dt.insert_data_last_row(query, values)

		hasil = "Berhasil menambahkan dapur"
		hasil_data = {
			"id_dapur" : id_dapur
		}
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil, 'data' : hasil_data} ), 200)
	except Exception as e:
		return bad_request(str(e))

@dapur.route('/update_dapur', methods=['PUT', 'OPTIONS'])
@jwt_required()
@cross_origin()
def update_dapur():
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

		if "id_dapur" not in data:
			return parameter_error("Missing id_dapur in Request Body")

		id_dapur = data["id_dapur"]

		# Cek apakah data lokasi ada
		query_temp = "SELECT a.id_dapur FROM dpr_dapur a WHERE a.is_delete != 1 AND a.id_dapur = %s"
		values_temp = (id_dapur, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data Dapur tidak ditemukan")

		query = """ UPDATE dpr_dapur SET id_dapur=id_dapur """
		values = ()

		if "id_lokasi" in data:
			id_lokasi = data["id_lokasi"]

			# cek apakah data kota ada
			query_temp = "SELECT a.id_lokasi FROM lokasi a WHERE a.is_delete != 1 AND a.id_lokasi = %s"
			values_temp = (id_lokasi, )
			data_temp = dt.get_data(query_temp, values_temp)
			if len(data_temp) == 0:
				return defined_error("Gagal, Data lokasi tidak ditemukan")

			query += """ ,id_lokasi = %s """
			values += (id_lokasi, )

		if "id_tingkat" in data:
			id_tingkat = data["id_tingkat"]

			# Cek apakah data tingkat ada
			query_temp = "SELECT a.id_tingkat FROM dpr_tingkat a WHERE a.is_delete != 1 AND a.id_tingkat = %s"
			values_temp = (id_tingkat, )
			data_temp = dt.get_data(query_temp, values_temp)
			if len(data_temp) == 0:
				return defined_error("Gagal, Data tingkatan dapur tidak ditemukan")

			query += """ ,id_tingkat = %s """
			values += (id_tingkat, )

		if "nama_dapur" in data:
			nama_dapur = data["nama_dapur"]
			query += """ ,nama_dapur = %s """
			values += (nama_dapur, )

		if "deskripsi_dapur" in data:
			deskripsi_dapur = data["deskripsi_dapur"]
			query += """ ,deskripsi_dapur = %s """
			values += (deskripsi_dapur, )

		if "thumbnail_dapur" in data:
			filename_photo = secure_filename(strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_thumbnail_dapur.png")
			save(data["thumbnail_dapur"], os.path.join(app.config['UPLOAD_FOLDER_FOTO_DAPUR'], filename_photo))

			thumbnail_dapur = filename_photo

			query += """ ,thumbnail_dapur = %s """
			values += (thumbnail_dapur, )

		if "is_delete" in data:
			is_delete = data["is_delete"]
			# validasi data is_delete
			if str(is_delete) not in ["1"]:
				return parameter_error("Invalid is_delete Parameter")
			query += """ ,is_delete = %s """
			values += (is_delete, )

		query += """ WHERE id_dapur = %s """
		values += (id_dapur, )
		dt.insert_data(query, values)

		hasil = "Berhasil mengubah data dapur"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))

#endregion ================================= DAPUR AREA ==========================================================================


#region ================================= GALERI DAPUR AREA ==========================================================================

@dapur.route('/get_dapur_galeri', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_dapur_galeri():
	try:
		ROUTE_NAME = str(request.path)

		dt = Data()

		query = """ SELECT a.*, b.nama_dapur
					FROM dpr_dapur_galeri a LEFT JOIN dpr_dapur b ON a.id_dapur=b.id_dapur
					WHERE a.is_delete!=1 """
		values = ()

		id_dapur_galeri = request.args.get("id_dapur_galeri")
		id_dapur = request.args.get("id_dapur")
		search = request.args.get("search")
		order_by = request.args.get("order_by")

		if id_dapur_galeri:
			query += " AND a.id_dapur_galeri = %s "
			values += (id_dapur_galeri, )
		if id_dapur:
			query += " AND a.id_dapur = %s "
			values += (id_dapur, )
		if search:
			query += """ AND CONCAT_WS("|", a.nama_dapur_galeri) LIKE %s """
			values += ("%"+search+"%", )

		if order_by:
			if order_by == "id_asc":
				query += " ORDER BY a.id_dapur_galeri ASC "
			elif order_by == "id_desc":
				query += " ORDER BY a.id_dapur_galeri DESC "
			else:
				query += " ORDER BY a.id_dapur_galeri DESC "
		else:
			query += " ORDER BY a.id_dapur_galeri DESC "

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

@dapur.route('/insert_dapur_galeri', methods=['POST', 'OPTIONS'])
@jwt_required()
@cross_origin()
def insert_dapur_galeri():
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
		if "id_dapur" not in data:
			return parameter_error("Missing id_dapur in Request Body")
		if "nama_dapur_galeri" not in data:
			return parameter_error("Missing nama_dapur_galeri in Request Body")
		if "file_dapur_galeri" not in data:
			return parameter_error("Missing file_dapur_galeri in Request Body")


		id_dapur 				= data["id_dapur"]
		nama_dapur_galeri 		= data["nama_dapur_galeri"]
		file_dapur_galeri 		= data["file_dapur_galeri"]

		# cek apakah data dapur ada
		query_temp = "SELECT a.id_dapur FROM dpr_dapur a WHERE a.is_delete!=1 AND a.id_dapur = %s"
		values_temp = (id_dapur, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data dapur tidak ditemukan")

		# Cek data-data opsional

		if "deskripsi_dapur_galeri" in data:
			deskripsi_dapur_galeri = data["deskripsi_dapur_galeri"]
		else:
			deskripsi_dapur_galeri = None

		# Save file lokasi galeri
		filename_photo = secure_filename(strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_dapur.png")
		save(file_dapur_galeri, os.path.join(app.config['UPLOAD_FOLDER_FOTO_DAPUR'], filename_photo))

		# Insert ke tabel db
		query = "INSERT INTO dpr_dapur_galeri (id_dapur, nama_dapur_galeri, deskripsi_dapur_galeri, file_dapur_galeri) VALUES (%s, %s, %s, %s)"
		values = (id_dapur, nama_dapur_galeri, deskripsi_dapur_galeri, filename_photo, )
		id_dapur_galeri = dt.insert_data_last_row(query, values)

		hasil = "Berhasil menambahkan galeri dapur"
		hasil_data = {
			"id_dapur_galeri" : id_dapur_galeri
		}
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil, 'data' : hasil_data} ), 200)
	except Exception as e:
		return bad_request(str(e))


#endregion ================================= GALERI DAPUR AREA ==========================================================================


#region ================================= HARGA DAPUR AREA ==========================================================================

@dapur.route('/get_harga_dapur', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_harga_dapur():
	try:
		ROUTE_NAME = str(request.path)

		dt = Data()

		query = """ SELECT a.*, b.nama_dapur
					FROM dpr_harga a LEFT JOIN dpr_dapur b ON a.id_dapur=b.id_dapur
					WHERE a.is_delete!=1 """
		values = ()

		page = request.args.get("page")
		id_dpr_harga = request.args.get("id_dpr_harga")
		id_dapur = request.args.get("id_dapur")
		search = request.args.get("search")
		order_by = request.args.get("order_by")

		if (page == None):
			page = 1
		if id_dpr_harga:
			query += " AND a.id_dpr_harga = %s "
			values += (id_dpr_harga, )
		if id_dapur:
			query += " AND a.id_dapur = %s "
			values += (id_dapur, )
		if search:
			query += """ AND CONCAT_WS("|", a.nama_harga) LIKE %s """
			values += ("%"+search+"%", )

		if order_by:
			if order_by == "id_asc":
				query += " ORDER BY a.id_dpr_harga ASC "
			elif order_by == "id_desc":
				query += " ORDER BY a.id_dpr_harga DESC "
			else:
				query += " ORDER BY a.id_dpr_harga DESC "
		else:
			query += " ORDER BY a.id_dpr_harga DESC "

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

@dapur.route('/insert_harga_dapur', methods=['POST', 'OPTIONS'])
@jwt_required()
@cross_origin()
def insert_harga_dapur():
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
		if "id_dapur" not in data:
			return parameter_error("Missing id_dapur in Request Body")
		if "nama_harga" not in data:
			return parameter_error("Missing nama_harga in Request Body")
		if "harga" not in data:
			return parameter_error("Missing harga in Request Body")
		if "jumlah_hari" not in data:
			return parameter_error("Missing jumlah_hari in Request Body")
		if "minimum_sewa" not in data:
			return parameter_error("Missing minimum_sewa in Request Body")


		id_dapur 				= data["id_dapur"]
		nama_harga 				= data["nama_harga"]
		harga 					= data["harga"]
		jumlah_hari 			= data["jumlah_hari"]
		minimum_sewa 			= data["minimum_sewa"]

		# cek apakah data dapur ada
		query_temp = "SELECT a.id_dapur FROM dpr_dapur a WHERE a.is_delete != 1 AND a.id_dapur = %s"
		values_temp = (id_dapur, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data Dapur tidak ditemukan")

		# Cek data opsional

		if "deskripsi_harga" in data:
			deskripsi_harga = data["deskripsi_harga"]
		else:
			deskripsi_harga = None


		# Insert ke tabel db
		query = "INSERT INTO dpr_harga (id_dapur, nama_harga, deskripsi_harga, harga, jumlah_hari, minimum_sewa) VALUES (%s, %s, %s, %s, %s, %s)"
		values = (id_dapur, nama_harga, deskripsi_harga, harga, jumlah_hari, minimum_sewa)
		id_dpr_harga = dt.insert_data_last_row(query, values)

		hasil = "Berhasil menambahkan harga dapur"
		hasil_data = {
			"id_dpr_harga" : id_dpr_harga
		}
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil, 'data' : hasil_data} ), 200)
	except Exception as e:
		return bad_request(str(e))

#endregion ================================= HARGA DAPUR AREA ==========================================================================


#region ================================= CUSTOMER DAPUR AREA ==========================================================================

@dapur.route('/get_customer_dapur', methods=['GET', 'OPTIONS'])
@jwt_required()
@cross_origin()
def get_customer_dapur():
	try:
		ROUTE_NAME = str(request.path)

		now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

		role 	= str(get_jwt()["role"])

		if role not in role_group_all:
			return permission_failed()

		if role in role_group_super_admin:
			id_admin = str(get_jwt()["id_admin"])
			id_user = id_admin
		if role in role_group_customer:
			id_customer = str(get_jwt()["id_customer"])
			id_user = id_customer

		dt = Data()

		# parameter khusus (mode)
		mode = request.args.get("mode")
		if (mode == None or mode == ""):
			mode = "1"
		else:
			mode = str(mode)

		if mode == "1": # Normal
			query = """ SELECT a.id_customer_dapur, a.id_customer, a.id_dpr_harga, a.nama_brand_dapur, a.waktu_awal_sewa, a.waktu_akhir_sewa, a.status_pemesanan, b.email, b.nama_customer, d.nama_dapur, d.thumbnail_dapur, e.nama_lokasi
						FROM dpr_customer_dapur a
						LEFT JOIN customer b ON a.id_customer=b.id_customer
						LEFT JOIN dpr_harga c ON a.id_dpr_harga=c.id_dpr_harga
						LEFT JOIN dpr_dapur d ON c.id_dapur=d.id_dapur
						LEFT JOIN lokasi e ON d.id_lokasi=e.id_lokasi
						WHERE a.is_delete!=1 """
			values = ()
		else:
			return parameter_error("Invalid mode Parameter")

		limit = request.args.get("limit")
		page = request.args.get("page")
		id_customer_dapur = request.args.get("id_customer_dapur")
		search = request.args.get("search")
		order_by = request.args.get("order_by")

		# Validasi parameter limit
		if (limit == None or limit == ""):
			limit = 10
		try:
			limit = int(limit)
		except Exception as e:
			return parameter_error ("Invalid limit Parameter")
		# Parameter limit tidak boleh lebih kecil dari 1, kecuali -1 itu unlimited
		if limit != -1 and limit < 1:
			return parameter_error ("Invalid limit Parameter")

		# jika diakses oleh customer hanya menampilkan data milik customer tersebut
		if role in role_group_customer:
			pass
		else:
			id_customer = request.args.get("id_customer")

		if id_customer:
			query += " AND a.status_pemesanan = 2 AND a.id_customer = %s "
			values += (id_customer, )

		if (page == None):
			page = 1
		if id_customer_dapur:
			query += " AND a.id_customer_dapur = %s "
			values += (id_customer_dapur, )

		if search:
			if role in role_group_super_admin:
				query += """ AND CONCAT_WS("|", d.nama_dapur, e.nama_lokasi) LIKE %s """
				values += ("%"+search+"%", )
			else:
				query += """ AND CONCAT_WS("|", d.nama_dapur, e.nama_lokasi) LIKE %s """
				values += ("%"+search+"%", )

		if order_by:
			if order_by == "id_asc":
				query += " ORDER BY a.id_customer_dapur ASC "
			elif order_by == "id_desc":
				query += " ORDER BY a.id_customer_dapur DESC "

			else:
				query += " ORDER BY a.id_customer_dapur DESC "
		else:
			query += " ORDER BY a.id_customer_dapur DESC "

		rowCount = dt.row_count(query, values)
		if str(limit) != "-1":
			hasil = dt.get_data_lim_param(query, values, page, limit)
		else:
			hasil = dt.get_data(query, values)
		hasil = {'data': hasil , 'status_code': 200, 'page': page, 'offset': str(limit), 'row_count': rowCount}
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

@dapur.route('/insert_customer_dapur', methods=['POST', 'OPTIONS'])
@jwt_required()
@cross_origin()
def insert_customer_dapur():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	role 	= str(get_jwt()["role"])

	if role not in role_group_customer:
		return permission_failed()

	id_customer = str(get_jwt()["id_customer"])
	id_user = id_customer

	try:
		dt = Data()
		data = request.json

		# Check mandatory data
		if "id_dpr_harga" not in data:
			return parameter_error("Missing id_dpr_harga in Request Body")
		if "nama_brand_dapur" not in data:
			return parameter_error("Missing nama_brand_dapur in Request Body")
		if "waktu_awal_sewa" not in data:
			return parameter_error("Missing waktu_awal_sewa in Request Body")

		id_dpr_harga = data["id_dpr_harga"]
		waktu_awal_sewa = data["waktu_awal_sewa"]
		nama_brand_dapur = data["nama_brand_dapur"]

		# cek apakah data harga dapur ada atau tidak
		query_temp = """ SELECT a.id_dpr_harga, a.id_dapur, a.harga, a.jumlah_hari, minimum_sewa FROM dpr_harga a WHERE a.is_delete!=1 AND a.id_dpr_harga=%s """
		values_temp = (id_dpr_harga, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Sewa Gagal, Data Pricing Plan tidak ditemukan")

		# Sementara di comment terlebih dahulu
		# # cek apakah customer sudah sewa dapur ini tapi belum bayar
		# query_temp = """ SELECT a.id_customer_dapur FROM dpr_customer_dapur a WHERE a.is_delete!=1 AND a.status_pemesanan IN (1) AND a.id_customer = %s AND a.id_dpr_harga = %s """
		# values_temp = (id_customer, id_dpr_harga, )
		# data_temp = dt.get_data(query_temp, values_temp)
		# if len(data_temp) != 0:
		# 	return defined_error("Sewa Gagal, mohon selesaikan transaksi sebelumnya yang anda lakukan pada dapur ini")

		# Ambil data harga
		data_get = data_temp[0]
		db_id_dapur = data_get["id_dapur"]
		harga = data_get["harga"]
		jumlah_hari = data_get["jumlah_hari"]
		minimum_sewa = data_get["minimum_sewa"]

		# validasi waktu awal sewa dan pembuatan waktu akhir sewa berdasarkan jumlah hari dan minimum sewa
		try:
			waktu_awal_sewa_datetime = datetime.datetime.strptime(waktu_awal_sewa, "%Y-%m-%d")
		except Exception as e:
			return defined_error("Mohon gunakan format tanggal yang benar untuk waktu awal penyewaan")

		waktu_akhir_sewa_datetime = waktu_awal_sewa_datetime + datetime.timedelta(days=(jumlah_hari*minimum_sewa)) - datetime.timedelta(seconds=1)

		# Cek apakah ada yang sedang sewa dapur pada waktu sewa yang diberikan
		query_temp = """ SELECT  a.id_customer_dapur
						FROM dpr_customer_dapur a
						LEFT JOIN dpr_harga b ON a.id_dpr_harga=b.id_dpr_harga
						WHERE (a.waktu_awal_sewa >= %s AND a.waktu_awal_sewa <= %s) OR (a.waktu_akhir_sewa >= %s AND a.waktu_akhir_sewa <= %s)
						AND a.status_pemesanan IN (2) AND b.id_dapur = %s """
		values_temp = (waktu_awal_sewa_datetime, waktu_akhir_sewa_datetime, waktu_awal_sewa_datetime, waktu_akhir_sewa_datetime, db_id_dapur, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) != 0:
			return defined_error("Sewa Gagal, Sudah ada yang sewa dapur pada waktu yang diberikan")

		total_harga_pembayaran = harga * minimum_sewa

		# Kalo harganya 0 (gratis)
		if total_harga_pembayaran <= 0 :
			id_kupon = None
			nomor_invoice = "FREE_" + random_string_number_only(8)
			total_harga_pembayaran = 0
			kode_unik = 0
			waktu_awal_pembayaran = now
			waktu_akhir_pembayaran = now
			waktu_melakukan_pembayaran = None
			service_code = None
			redirect_url = None
			redirect_data = None
			nomor_virtual_account = None
			status_pemesanan = 2

		else:
			if "kode_kupon" in data:
				kode_kupon = data["kode_kupon"]

				# Cek apakah data kupon ada dan dapat digunakan pada transaksi ini
				query_temp = """ SELECT a.id_kupon, a.is_for_all, a.is_for_dapur, a.is_for_utensil, a.is_for_bahan, a.is_one_use  FROM kupon a WHERE a.is_delete!=1 AND a.kode_kupon = %s """
				values_temp = (kode_kupon, )
				data_temp = dt.get_data(query_temp, values_temp)
				if len(data_temp) == 0:
					return defined_error("Sewa Gagal, kupon tidak ditemukan")

				data_get = data_temp[0]
				db_id_kupon = int(data_get["id_kupon"])
				db_is_for_all = int(data_get["is_for_all"])
				db_is_for_dapur = int(data_get["is_for_dapur"])
				db_is_for_utensil = int(data_get["is_for_utensil"])
				db_is_for_bahan = int(data_get["is_for_bahan"])
				db_is_one_use = int(data_get["is_one_use"])

				if db_is_for_all != 1:
					if db_is_for_dapur != 1:
						return defined_error("Sewa Gagal, kupon tidak bisa digunakan untuk transaksi ini")

				id_kupon = db_id_kupon
				nomor_invoice = "KUPON_" + random_string_number_only(8)
				kode_unik = 0
				waktu_awal_pembayaran = now
				waktu_akhir_pembayaran = now
				waktu_melakukan_pembayaran = now
				service_code = None
				redirect_url = None
				redirect_data = None
				nomor_virtual_account = None
				status_pemesanan = 2
			else:
				if "kode_unik" not in data:
					return parameter_error("Missing kode_unik in Request Body")
				if "service_code" not in data:
					return parameter_error("Missing service_code in Request Body")

				kode_unik = data["kode_unik"]
				service_code = data["service_code"]

				# validasi kode_unik
				try:
					kode_unik = int(data["kode_unik"])
					if kode_unik < 100 or kode_unik > 999:
						return defined_error("Kode unik invalid")
				except Exception as e:
					return defined_error("Kode unik invalid")

				# service_code validation
				# if service_code not in get_code_wallet():
				# 	return defined_error("Metode Pembayaran Tidak Dapat Digunakan")

				total_harga_pembayaran = total_harga_pembayaran + kode_unik

				# Sprint Transaction
				item_details = "[{\"itemName\":\"Sewa Bisa Kitchen\",\"price\":\"%s\",\"quantity\":\"1\",\"itemURL\":\"https:\/\/bisa.kitchen/\/\"}]" % (total_harga_pembayaran)

				query_temp = "SELECT a.id_customer, a.email, a.nama_customer, a.nomor_customer FROM customer a WHERE a.id_customer = %s"
				values_temp = (id_customer,)
				hasil_data_user = dt.get_data(query_temp, values_temp)

				jsonData = json.dumps({
					"service_code" : service_code,
					"transaction_amount" : total_harga_pembayaran,
					"item_details" : item_details,
					"callback_url" : "https://bisa.kitchen/",
					"customer_name": hasil_data_user[0]["nama_customer"],
					"customer_phone": hasil_data_user[0]["nomor_customer"],
					"customer_email": hasil_data_user[0]["email"],
					"deskripsi" : "Pembayaran Sewa Bisa Kitchen"
				})
				detail = insert_payment(jsonData)
				if (detail["status_code"] != 200):
					return make_response(jsonify({'status_code':400, 'description': detail } ), 400)
				else:
					detail = detail["data"]

				id_kupon = None
				nomor_invoice = detail['transaction_no']
				waktu_awal_pembayaran = detail['transaction_date']
				waktu_akhir_pembayaran = datetime.datetime.strptime(detail['transaction_expire'], "%Y-%m-%d %H:%M:%S")
				waktu_melakukan_pembayaran = None
				status_pemesanan = 1

				if "redirect_url" in detail:
					redirect_url = detail["redirect_url"]
				else:
					redirect_url = None
				if "redirect_data" in detail:
					redirect_data = json.dumps(detail["redirect_data"])
				else:
					redirect_data = None
				if "customer_account" in detail:
					customer_account = detail["customer_account"]
				else:
					nomor_virtual_account = None

		# Insert to table db
		query = "INSERT INTO dpr_customer_dapur (id_customer, id_dpr_harga, id_kupon, nama_brand_dapur, waktu_awal_sewa, waktu_akhir_sewa, nomor_invoice, total_harga_pembayaran, kode_unik, waktu_awal_pembayaran, waktu_akhir_pembayaran, waktu_melakukan_pembayaran, service_code, redirect_url, redirect_data, nomor_virtual_account, status_pemesanan) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
		values = (id_customer, id_dpr_harga, id_kupon, nama_brand_dapur, waktu_awal_sewa_datetime, waktu_akhir_sewa_datetime, nomor_invoice, total_harga_pembayaran, kode_unik, waktu_awal_pembayaran, waktu_akhir_pembayaran, waktu_melakukan_pembayaran, service_code, redirect_url, redirect_data, nomor_virtual_account, status_pemesanan, )
		id_customer_dapur = dt.insert_data_last_row(query, values)

		response_payload ={
			"nomor_invoice" : nomor_invoice,
			"id_customer_dapur" : id_customer_dapur,
			"waktu_awal_pembayaran" : waktu_awal_pembayaran,
			"waktu_akhir_pembayaran" : waktu_akhir_pembayaran,
			"total_harga_pembayaran" : total_harga_pembayaran
		}

		if "detail" in locals():
			if "redirect_data" in detail:
				response_payload["redirect_data"] = detail["redirect_data"]
			if "redirect_url" in detail:
				response_payload["redirect_url"] = detail["redirect_url"]
			if "nomor_virtual_account" in detail:
				response_payload["nomor_virtual_account"] = detail["nomor_virtual_account"]

		hasil = "Sewa Kitchen Berhasil"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)

		return make_response(jsonify({'status_code':200, 'description': hasil, 'data': response_payload} ), 200)
	except Exception as e:
		return bad_request(str(e))


@dapur.route('/upload_bukti_transaksi/<id_customer_dapur>', methods=['POST', 'OPTIONS'])
@jwt_required()
@cross_origin()
def upload_bukti_transaksi(id_customer_dapur):
	data = request.files
	dt = Data()

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
	if "foto_bukti_bayar" in data:
		filename_photo = secure_filename(now.strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_bukti_bayar.png")
		data["foto_bukti_bayar"].save(os.path.join(app.config['UPLOAD_FOLDER_FOTO_BUKTI_BAYAR'], filename_photo))
		print(data["foto_bukti_bayar"])
		query_temp = "SELECT foto_bukti_bayar FROM dpr_customer_dapur WHERE is_delete != 1 AND id_customer_dapur = %s"
		values_temp = (id_customer_dapur, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data Customer Dapur tidak ditemukan")

		query = """ UPDATE dpr_customer_dapur SET foto_bukti_bayar = %s WHERE id_customer_dapur = %s """
		values = (filename_photo, id_customer_dapur)
		dt.insert_data(query, values)

		return make_response(jsonify({'status_code':200, 'description': "Bukti Bayar Customer Dapur Berhasil Di Upload "} ), 200)





#endregion ================================= CUSTOMER DAPUR AREA ==========================================================================

#region ================================= RIWAYAT TRANSAKSI ==========================================================================

@dapur.route('/get_riwayat_transaksi', methods=['GET', 'OPTIONS'])
@jwt_required()
@cross_origin()
def get_riwayat_transaksi():
	try:
		ROUTE_NAME = str(request.path)

		now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

		role 	= str(get_jwt()["role"])

		if role not in role_group_all:
			return permission_failed()

		if role in role_group_super_admin:
			id_admin = str(get_jwt()["id_admin"])
			id_user = id_admin
		if role in role_group_customer:
			id_customer = str(get_jwt()["id_customer"])
			id_user = id_customer

		dt = Data()

		# parameter khusus (mode)
		mode = request.args.get("mode")
		if (mode == None or mode == ""):
			mode = "1"
		else:
			mode = str(mode)

		if mode == "1": # Normal
			query = """ SELECT b.id_customer, a.*
						FROM dpr_customer_dapur a
						LEFT JOIN customer b ON a.id_customer=b.id_customer
						WHERE a.is_delete!=1 """
			values = ()
		else:
			return parameter_error("Invalid mode Parameter")

		limit = request.args.get("limit")
		page = request.args.get("page")
		id_customer_dapur = request.args.get("id_customer_dapur")
		search = request.args.get("search")
		order_by = request.args.get("order_by")

		# Validasi parameter limit
		if (limit == None or limit == ""):
			limit = 10
		try:
			limit = int(limit)
		except Exception as e:
			return parameter_error ("Invalid limit Parameter")
		# Parameter limit tidak boleh lebih kecil dari 1, kecuali -1 itu unlimited
		if limit != -1 and limit < 1:
			return parameter_error ("Invalid limit Parameter")

		# jika diakses oleh customer hanya menampilkan data milik customer tersebut
		if role in role_group_customer:
			pass
		else:
			id_customer = request.args.get("id_customer")

		if id_customer:
			query += " AND b.id_customer = %s "
			values += (id_customer, )

		if (page == None):
			page = 1
		if id_customer_dapur:
			query += " AND a.id_customer_dapur = %s "
			values += (id_customer_dapur, )

		if search:
			if role in role_group_super_admin:
				query += """ AND CONCAT_WS("|", a.nama_brand_dapur) LIKE %s """
				values += ("%"+search+"%", )
			else:
				query += """ AND CONCAT_WS("|", a.nama_brand_dapur) LIKE %s """
				values += ("%"+search+"%", )

		if order_by:
			if order_by == "id_asc":
				query += " ORDER BY a.id_customer_dapur ASC "
			elif order_by == "id_desc":
				query += " ORDER BY a.id_customer_dapur DESC "

			else:
				query += " ORDER BY a.id_customer_dapur DESC "
		else:
			query += " ORDER BY a.id_customer_dapur DESC "

		rowCount = dt.row_count(query, values)
		if str(limit) != "-1":
			hasil = dt.get_data_lim_param(query, values, page, limit)
		else:
			hasil = dt.get_data(query, values)
		hasil = {'data': hasil , 'status_code': 200, 'page': page, 'offset': str(limit), 'row_count': rowCount}
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

#endregion ================================= RIWAYAT TRANSAKSI ==========================================================================

