import email
from flask import Blueprint, jsonify, request, make_response, render_template
from flask import current_app as app
from flask_jwt_extended import get_jwt, jwt_required
from flask_cors import cross_origin
from werkzeug.utils import secure_filename
from werkzeug.datastructures import ImmutableMultiDict
from time import gmtime, strftime, strptime
from markupsafe import Markup
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
import qrcode

from . models import Data

#11 superadmin, 21 Customer
role_group_super_admin = ["11"]
role_group_admin_lokasi = ["12"]
role_group_admin_brand = ["13"]
role_group_admin = ["11", "12", "13"]
role_group_customer = ["21"]
role_group_all = ["11", "12", "13", "21"]

#now = datetime.datetime.now()

pos = Blueprint('pos', __name__, static_folder = '../../upload/pos', static_url_path="/media")

#sandbox variabel
url_sandbox_gojek = 'https://api.sandbox.gobiz.co.id'
url_sanbox_gojek_login = ' https://integration-goauth.gojekapi.com/oauth2/token'
id_brand_gojek_petogogan = 10
beverages_brand = ['tandus','kava']

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

def defined_error(description, error="Defined Error", status_code=499, hidden_description=""):
	return make_response(jsonify({'description':description,'error': error,'status_code':status_code,'hidden_description':hidden_description}), status_code)

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

def login_gobiz(id_brand):
	dt = Data()
	query_temp = "SELECT a.* FROM pos_brand a WHERE a.is_delete!=1 AND a.id_brand = %s"
	values_temp = (id_brand, )
	data_temp = dt.get_data(query_temp, values_temp)

	if len(data_temp) == 0:
		return defined_error("Gagal, Data Brand tidak ditemukan")

	data_temp = data_temp[0]
	
	client_id = "DY8cfa12BrS7E1Oa"
	client_secret = 'jyrPO0tGXI5tTVlLKuRb9CKNnnJmjuKu'

	client_id = data_temp['client_id']
	client_secret = data_temp['client_secret']

	body_params = {'client_id':client_id,
				'client_secret':client_secret,
				'grant_type':'client_credentials',
				'scope':'gofood:catalog:write gofood:catalog:read gofood:order:write gofood:order:read gofood:outlet:write promo:food_promo:read promo:food_promo:write'}	
	head= {'Content-Type': 'application/x-www-form-urlencoded'}
	hasil = requests.post(url_sanbox_gojek_login, body_params, head)
	hasil = hasil.json()
	access_token = hasil['access_token']

	return access_token

#endregion ================================= FUNGSI-FUNGSI AREA ===============================================================


#region ================================= BRAND AREA ==========================================================================
@pos.route('/get_brand', methods=['GET', 'OPTIONS'])
@jwt_required()
@cross_origin()
def get_brand():
	try:
		ROUTE_NAME = str(request.path)

		now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

		role 	= str(get_jwt()["role"])

		if role not in (role_group_super_admin +role_group_admin_lokasi):
			return permission_failed()

		id_admin = str(get_jwt()["id_admin"])
		id_user = id_admin

		dt = Data()
		# parameter khusus (mode)
		mode = request.args.get("mode")
		if (mode == None or mode == ""):
			mode = "1"
		else:
			mode = str(mode)

		if mode == "1": # Normal
			query = """ SELECT b.id_lokasi, a.*
						FROM pos_brand a
						LEFT JOIN lokasi b ON a.id_lokasi=b.id_lokasi
						WHERE a.is_delete!=1 """
			values = ()
		else:
			return parameter_error("Invalid mode Parameter")

		limit = request.args.get("limit")
		page = request.args.get("page")
		id_brand = request.args.get("id_brand")
		id_lokasi = request.args.get("id_lokasi")
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

		if (page == None):
			page = 1

		if id_brand:
			query += " AND a.id_brand = %s "
			values += (id_brand, )

		if role in role_group_admin_lokasi:
			id_lokasi = str(get_jwt()["id_lokasi"])
		
		if id_lokasi:
			query += " AND a.id_lokasi = %s "
			values += (id_lokasi, )

		if search:
			if role in role_group_super_admin:
				query += """ AND CONCAT_WS("|", a.nama_brand) LIKE %s """
				values += ("%"+search+"%", )
			else:
				query += """ AND CONCAT_WS("|", a.nama_brand) LIKE %s """
				values += ("%"+search+"%", )

		if order_by:
			if order_by == "id_asc":
				query += " ORDER BY a.id_brand ASC "
			elif order_by == "id_desc":
				query += " ORDER BY a.id_brand DESC "

			else:
				query += " ORDER BY a.id_brand DESC "
		else:
			query += " ORDER BY a.id_brand DESC "

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


@pos.route('/insert_brand', methods=['POST', 'OPTIONS'])
@jwt_required()
@cross_origin()
def insert_brand():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	role = str(get_jwt()["role"])

	if role not in (role_group_super_admin+role_group_admin_lokasi):
		return permission_failed()

	id_admin = str(get_jwt()["id_admin"])
	id_user = id_admin

	try:
		dt = Data()
		data = request.json

		# Check mandatory data
		if "nama_brand" not in data:
			return parameter_error("Missing nama_brand in Request Body")
		nama_brand 				= data["nama_brand"]

		#Perbedaan Super admin dan Admin Lokasi
		if role in role_group_admin_lokasi:
			id_lokasi = str(get_jwt()["id_lokasi"])
		else:
			if "id_lokasi" not in data:
				return parameter_error("Missing id_lokasi in Request Body")
			id_lokasi 				= data["id_lokasi"]
		
		# cek apakah data lokasi ada
		query_temp = "SELECT a.id_lokasi FROM lokasi a WHERE a.is_delete != 1 AND a.id_lokasi = %s"
		values_temp = (id_lokasi, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data lokasi tidak ditemukan")

		# Cek data opsional
		if "deskripsi_brand" in data:
			deskripsi_brand = data["deskripsi_brand"]
		else:
			deskripsi_brand = None

		if "foto_brand" in data:
			filename_photo = secure_filename(strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_brand.png")
			save(data["foto_brand"], os.path.join(app.config['UPLOAD_FOLDER_FOTO_BRAND'], filename_photo))

			foto_brand = filename_photo
		else:
			foto_brand = None

		# Insert ke tabel db
		query = "INSERT INTO pos_brand (id_lokasi, nama_brand, deskripsi_brand, foto_brand) VALUES (%s, %s, %s, %s)"
		values = (id_lokasi, nama_brand, deskripsi_brand, foto_brand,)
		id_brand = dt.insert_data_last_row(query, values)

		hasil = "Berhasil menambahkan brand"
		hasil_data = {
			"id_brand" : id_brand
		}
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil, 'data' : hasil_data} ), 200)
	except Exception as e:
		return bad_request(str(e))


@pos.route('/update_brand', methods=['PUT', 'OPTIONS'])
@jwt_required()
@cross_origin()
def update_brand():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	role = str(get_jwt()["role"])

	if role not in (role_group_super_admin + role_group_admin_lokasi):
		return permission_failed()

	id_admin = str(get_jwt()["id_admin"])
	id_user = id_admin

	try:
		dt = Data()
		data = request.json

		if "id_brand" not in data:
			return parameter_error("Missing id_brand in Request Body")

		id_brand = data["id_brand"]

		# Cek apakah data brand ada
		query_temp = "SELECT a.id_brand FROM pos_brand a WHERE a.is_delete != 1 AND a.id_brand = %s"
		values_temp = (id_brand, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data Brand tidak ditemukan")

		query = """ UPDATE pos_brand SET id_brand=id_brand """
		values = ()

		#check apakah brandnya sesuai lokasinya
		#agar admin lokasi tidak bisa update brand dari lokasi lain
		#semisal admin petogogan tidak bisa update brand di pasirsalam
		if role in role_group_admin_lokasi:
			id_lokasi = str(get_jwt()["id_lokasi"])
			query_temp = """ SELECT a.*
							FROM pos_brand a
							WHERE a.is_delete != 1 AND a.id_brand = %s AND a.id_lokasi = %s
						"""
			values_temp = (id_brand, id_lokasi, )
			data_temp = dt.get_data(query_temp, values_temp)
			if len(data_temp) == 0:
				return defined_error("Gagal, Data brand tidak ditemukan atau tidak aktif atau bukan berada di lokasi anda")
				

		if role in role_group_super_admin and "id_lokasi" in data:
			id_lokasi = data["id_lokasi"]
			query += """ ,id_lokasi = %s """
			values += (id_lokasi, )
		
		if "nama_brand" in data:
			nama_brand = data["nama_brand"]
			query += """ ,nama_brand = %s """
			values += (nama_brand, )

		if "deskripsi_brand" in data:
			deskripsi_brand = data["deskripsi_brand"]
			query += """ ,deskripsi_brand = %s """
			values += (deskripsi_brand, )

		if "foto_brand" in data:
			filename_photo = secure_filename(strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_brand.png")
			save(data["foto_brand"], os.path.join(app.config['UPLOAD_FOLDER_FOTO_BRAND'], filename_photo))

			foto_brand = filename_photo

			query += """ ,foto_brand = %s """
			values += (foto_brand, )

		if "is_delete" in data:
			is_delete = data["is_delete"]
			# validasi data is_delete
			if str(is_delete) not in ["1"]:
				return parameter_error("Invalid is_delete Parameter")
			query += """ ,is_delete = %s """
			values += (is_delete, )

		query += """ WHERE id_brand = %s """
		values += (id_brand, )
		dt.insert_data(query, values)

		hasil = "Berhasil mengubah data brand"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))

@pos.route('/delete_brand', methods=['PUT', 'OPTIONS'])
@jwt_required()
@cross_origin()
def delete_brand():
	#Pada dasarnya API delete sama dengan API update, akan tetapi parameter yang dibutuhkan lebih di spesifikkan
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	role = str(get_jwt()["role"])

	if role not in (role_group_super_admin + role_group_admin_lokasi):
		return permission_failed()

	id_admin = str(get_jwt()["id_admin"])
	id_user = id_admin

	try:
		dt = Data()
		data = request.json

		if "id_brand" not in data:
			return parameter_error("Missing id_brand in Request Body")

		id_brand = data["id_brand"]

		# Cek apakah data brand ada
		query_temp = "SELECT a.id_brand FROM pos_brand a WHERE a.is_delete != 1 AND a.id_brand = %s"
		values_temp = (id_brand, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data Brand tidak ditemukan")

		query = """ UPDATE pos_brand SET id_brand=id_brand """
		values = ()

		#check apakah brandnya sesuai lokasinya
		#agar admin lokasi tidak bisa update brand dari lokasi lain
		#semisal admin petogogan tidak bisa update brand di pasirsalam
		if role in role_group_admin_lokasi:
			id_lokasi = str(get_jwt()["id_lokasi"])
			query_temp = """ SELECT a.*
							FROM pos_brand a
							WHERE a.is_delete != 1 AND a.id_brand = %s AND a.id_lokasi = %s
						"""
			values_temp = (id_brand, id_lokasi, )
			data_temp = dt.get_data(query_temp, values_temp)
			if len(data_temp) == 0:
				return defined_error("Gagal, Data brand tidak ditemukan atau tidak aktif atau bukan berada di lokasi anda")
		
		if "is_delete" in data:
			is_delete = data["is_delete"]
			# validasi data is_delete
			if str(is_delete) not in ["1"]:
				return parameter_error("Invalid is_delete Parameter")
			query += """ ,is_delete = %s """
			values += (is_delete, )

		query += """ WHERE id_brand = %s """
		values += (id_brand, )
		dt.insert_data(query, values)

		hasil = "Berhasil menghapus data brand"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))

#endregion ================================= BRAND AREA ==========================================================================


#region ================================= PRODUK AREA ==========================================================================

@pos.route('/get_produk', methods=['GET', 'OPTIONS'])
@jwt_required()
@cross_origin() 
def get_produk():
	try:
		ROUTE_NAME = str(request.path)

		role = str(get_jwt()["role"])

		dt = Data()

		query = """ SELECT a.*
					FROM pos_produk a
					INNER JOIN pos_brand b
					ON a.id_brand = b.id_brand
					WHERE a.is_delete != 1 """
		values = ()

		page = request.args.get("page")
		id_produk = request.args.get("id_produk")
		search = request.args.get("search")
		order_by = request.args.get("order_by")

		if role in role_group_admin_brand:
			id_brand = str(get_jwt()["id_brand"])
		else:
		 	id_brand = request.args.get("id_brand")

		if role in role_group_admin_lokasi:
			id_lokasi = str(get_jwt()["id_lokasi"])
		else:
		 	id_lokasi = request.args.get("id_lokasi")

		if (page == None):
			page = 1
		if id_produk:
			query += " AND a.id_produk = %s "
			values += (id_produk, )
		if id_brand:
			query += " AND a.id_brand = %s "
			values += (id_brand, )
		if id_lokasi:
			query += " AND b.id_lokasi = %s "
			values += (id_lokasi, )
		if search:
			query += """ AND CONCAT_WS("|", a.nama_produk) LIKE %s """
			values += ("%"+search+"%", )

		if order_by:
			if order_by == "id_asc":
				query += " ORDER BY a.id_produk ASC "
			elif order_by == "id_desc":
				query += " ORDER BY a.id_produk DESC "

			elif order_by == "nama_asc":
				query += " ORDER BY a.nama_produk ASC "
			elif order_by == "nama_desc":
				query += " ORDER BY a.nama_produk DESC "

			else:
				query += " ORDER BY a.nama_produk ASC "
		else:
			query += " ORDER BY a.nama_produk ASC "

		rowCount = dt.row_count(query, values)
		hasil = dt.get_data(query, values)
		hasil = {'data': hasil , 'status_code': 200, 'page': 1, 'offset': 'None', 'row_count': rowCount}

		# hasil = dt.get_data_lim(query, values, page)
		# hasil = {'data': hasil , 'status_code': 200, 'page': page, 'offset': '10', 'row_count': rowCount}

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

@pos.route('/insert_produk', methods=['POST', 'OPTIONS'])
@jwt_required()
@cross_origin()
def insert_produk():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	role = str(get_jwt()["role"])

	if role not in role_group_admin:
		return permission_failed()

	id_admin = str(get_jwt()["id_admin"])
	id_user = id_admin

	try:
		dt = Data()
		data = request.json

		# Check mandatory data
		if role in role_group_admin_brand:
			id_brand = str(get_jwt()["id_brand"])
		else:
			if "id_brand" not in data:
				return parameter_error("Missing id_brand in Request Body")
			id_brand = data["id_brand"]

		# cek apakah data brand ada dan aktif
		query_temp = "SELECT a.id_brand FROM pos_brand a WHERE a.is_delete != 1 AND a.id_brand = %s"
		values_temp = (id_brand, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data Brand tidak ditemukan atau tidak aktif")

		# cek apakah admin lokasi benar memasukkan brand pada lokasinya
		if role in role_group_admin_lokasi:
			id_lokasi = str(get_jwt()["id_lokasi"])
			query_temp = "SELECT a.id_brand FROM pos_brand a WHERE a.is_delete != 1 AND a.id_brand = %s AND a.id_lokasi= %s"
			values_temp = (id_brand, id_lokasi, )
			data_temp = dt.get_data(query_temp, values_temp)
			if len(data_temp) == 0:
				return defined_error("Gagal, Data Brand tidak ditemukan atau tidak aktif atau bukan berada di lokasi anda")

		if "nama_produk" not in data:
			return parameter_error("Missing nama_produk in Request Body")
		if "deskripsi_produk" not in data:
			return parameter_error("Missing deskripsi_produk in Request Body")
		if "harga" not in data:
			return parameter_error("Missing harga in Request Body")
		if "pajak" not in data:
			return parameter_error("Missing pajak in Request Body")

		nama_produk 				= data["nama_produk"]
		deskripsi_produk			= data["deskripsi_produk"]
		harga		 				= data["harga"]
		pajak		 				= data["pajak"]


		# Cek data opsional
		if "foto_produk" in data:
			filename_photo = secure_filename(strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_produk.png")
			save(data["foto_produk"], os.path.join(app.config['UPLOAD_FOLDER_FOTO_PRODUK'], filename_photo))

			foto_produk = filename_photo
		else:
			foto_produk = None

		# Insert ke tabel db
		query = "INSERT INTO pos_produk (id_brand, nama_produk, deskripsi_produk, harga, pajak, foto_produk) VALUES (%s, %s, %s, %s, %s, %s)"
		values = (id_brand, nama_produk, deskripsi_produk, harga, pajak, foto_produk)
		id_produk = dt.insert_data_last_row(query, values)

		hasil = "Berhasil menambahkan produk"
		hasil_data = {
			"id_produk" : id_produk
		}
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil, 'data' : hasil_data} ), 200)
	except Exception as e:
		return bad_request(str(e))

@pos.route('/update_produk', methods=['PUT', 'OPTIONS'])
@jwt_required()
@cross_origin()
def update_produk():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	role = str(get_jwt()["role"])

	if role not in role_group_admin:
		return permission_failed()

	id_admin = str(get_jwt()["id_admin"])
	id_user = id_admin

	try:
		dt = Data()
		data = request.json

		# Check mandatory data
		if "id_produk" not in data:
			return parameter_error("Missing id_produk in Request Body")
		
		id_produk = data["id_produk"]

		# Cek apakah data produk ada
		query_temp = "SELECT a.id_produk FROM pos_produk a WHERE a.is_delete != 1 AND a.id_produk = %s"
		values_temp = (id_produk, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data Produk tidak ditemukan")

		query = """ UPDATE pos_produk SET id_produk=id_produk """
		values = ()

		#check apakah produknya sesuai brandnya
		#agar admin brand tidak bisa update produk dari brand lain
		if role in role_group_admin_brand:
			id_brand = str(get_jwt()["id_brand"])
			query_temp = "SELECT a.id_produk FROM pos_produk a WHERE a.is_delete != 1 AND a.id_produk = %s AND a.id_brand = %s"
			values_temp = (id_produk, id_brand, )
			data_temp = dt.get_data(query_temp, values_temp)
			if len(data_temp) == 0:
				return defined_error("Gagal, Data produk tidak ditemukan atau tidak aktif atau bukan produk anda")

		#check apakah produknya sesuai lokasinya
		#agar admin lokasi tidak bisa update produk dari lokasi lain
		#semisal admin petogogan tidak bisa update produk di pasirsalam
		if role in role_group_admin_lokasi:
			id_lokasi = str(get_jwt()["id_lokasi"])
			query_temp = """ SELECT a.id_produk, b.id_lokasi
							FROM pos_produk a
							LEFT JOIN pos_brand b ON a.id_brand=b.id_brand
							WHERE a.is_delete != 1 AND a.id_produk = %s AND b.id_lokasi = %s
						"""
			values_temp = (id_produk, id_lokasi, )
			data_temp = dt.get_data(query_temp, values_temp)
			if len(data_temp) == 0:
				return defined_error("Gagal, Data produk tidak ditemukan atau tidak aktif atau bukan berada di lokasi anda")

		
		if "id_brand" in data and role not in role_group_admin_brand:
			id_brand = data["id_brand"]

			# cek apakah data kota ada
			if role in role_group_admin_lokasi:
				id_lokasi = str(get_jwt()["id_lokasi"])
				query_temp = "SELECT a.id_brand FROM pos_brand a WHERE a.is_delete != 1 AND a.id_brand = %s AND a.id_lokasi = %s"
				values_temp = (id_brand, id_lokasi, )
				data_temp = dt.get_data(query_temp, values_temp)
				if len(data_temp) == 0:
					return defined_error("Gagal, Data brand tidak ditemukan atau bukan berada di lokasi anda")
			elif role in role_group_super_admin:
				query_temp = "SELECT a.id_brand FROM pos_brand a WHERE a.is_delete != 1 AND a.id_brand = %s"
				values_temp = (id_brand, )
				data_temp = dt.get_data(query_temp, values_temp)
				if len(data_temp) == 0:
					return defined_error("Gagal, Data brand tidak ditemukan")

			query += """ ,id_brand = %s """
			values += (id_brand, )

		if "nama_produk" in data:
			nama_produk = data["nama_produk"]
			query += """ ,nama_produk = %s """
			values += (nama_produk, )

		if "deskripsi_produk" in data:
			deskripsi_produk = data["deskripsi_produk"]
			query += """ ,deskripsi_produk = %s """
			values += (deskripsi_produk, )

		if "harga" in data:
			harga = data["harga"]
			query += """ ,harga = %s """
			values += (harga, )
		
		if "pajak" in data:
			pajak = data["pajak"]
			query += """ ,pajak = %s """
			values += (pajak, )

		if "foto_produk" in data:
			filename_photo = secure_filename(strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_produk.png")
			save(data["foto_produk"], os.path.join(app.config['UPLOAD_FOLDER_FOTO_PRODUK'], filename_photo))

			foto_produk= filename_photo

			query += """ ,foto_produk = %s """
			values += (foto_produk, )

		if "is_delete" in data:
			is_delete = data["is_delete"]
			# validasi data is_delete
			if str(is_delete) not in ["1"]:
				return parameter_error("Invalid is_delete Parameter")
			query += """ ,is_delete = %s """
			values += (is_delete, )

		query += """ WHERE id_produk = %s """
		values += (id_produk, )
		dt.insert_data(query, values)

		hasil = "Berhasil mengubah data produk"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))

@pos.route('/delete_produk', methods=['PUT', 'OPTIONS'])
@jwt_required()
@cross_origin()
def delete_produk():
	#Pada dasarnya API delete sama dengan API update, akan tetapi parameter yang dibutuhkan lebih di spesifikkan
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	role = str(get_jwt()["role"])

	if role not in role_group_admin:
		return permission_failed()

	id_admin = str(get_jwt()["id_admin"])
	id_user = id_admin

	try:
		dt = Data()
		data = request.json

		# Check mandatory data
		if "id_produk" not in data:
			return parameter_error("Missing id_produk in Request Body")
		
		id_produk = data["id_produk"]

		# Cek apakah data produk ada
		query_temp = "SELECT a.id_produk FROM pos_produk a WHERE a.is_delete != 1 AND a.id_produk = %s"
		values_temp = (id_produk, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data Produk tidak ditemukan")

		query = """ UPDATE pos_produk SET id_produk=id_produk """
		values = ()

		#check apakah produknya sesuai brandnya
		#agar admin brand tidak bisa update produk dari brand lain
		if role in role_group_admin_brand:
			id_brand = str(get_jwt()["id_brand"])
			query_temp = "SELECT a.id_produk FROM pos_produk a WHERE a.is_delete != 1 AND a.id_produk = %s AND a.id_brand = %s"
			values_temp = (id_produk, id_brand, )
			data_temp = dt.get_data(query_temp, values_temp)
			if len(data_temp) == 0:
				return defined_error("Gagal, Data produk tidak ditemukan atau tidak aktif atau bukan produk anda")

		#check apakah produknya sesuai lokasinya
		#agar admin lokasi tidak bisa update produk dari lokasi lain
		#semisal admin petogogan tidak bisa update produk di pasirsalam
		if role in role_group_admin_lokasi:
			id_lokasi = str(get_jwt()["id_lokasi"])
			query_temp = """ SELECT a.id_produk, b.id_lokasi
							FROM pos_produk a
							LEFT JOIN pos_brand b ON a.id_brand=b.id_brand
							WHERE a.is_delete != 1 AND a.id_produk = %s AND b.id_lokasi = %s
						"""
			values_temp = (id_produk, id_lokasi, )
			data_temp = dt.get_data(query_temp, values_temp)
			if len(data_temp) == 0:
				return defined_error("Gagal, Data produk tidak ditemukan atau tidak aktif atau bukan berada di lokasi anda")

		if "is_delete" in data:
			is_delete = data["is_delete"]
			# validasi data is_delete
			if str(is_delete) not in ["1"]:
				return parameter_error("Invalid is_delete Parameter")
			query += """ ,is_delete = %s """
			values += (is_delete, )

		query += """ WHERE id_produk = %s """
		values += (id_produk, )
		dt.insert_data(query, values)

		hasil = "Berhasil menghapus data produk"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))

#endregion ================================= PRODUK AREA ==========================================================================


#region ================================= ORDER DAN ORDER DETAIL AREA ==========================================================================

@pos.route('/get_order', methods=['GET', 'OPTIONS'])
@jwt_required()
@cross_origin()
def get_order():
	try:
		ROUTE_NAME = str(request.path)

		role = str(get_jwt()["role"])

		if role not in role_group_admin:
			return permission_failed()

		dt = Data()

		query = """ SELECT a.*, b.*
					FROM pos_order a
					LEFT JOIN pos_metode_pembayaran b ON a.id_metode_pembayaran_pos=b.id_metode_pembayaran_pos
					WHERE a.is_delete !=1  """
		values = ()

		page = request.args.get("page")
		id_order = request.args.get("id_order")
		status_order = request.args.get("status_order")
		search = request.args.get("search")
		order_by = request.args.get("order_by")

		if role in role_group_admin_brand:
			id_brand = str(get_jwt()["id_brand"])
		else:
			id_brand = request.args.get("id_brand")

		if (page == None):
			page = 1
		if id_order:
			query += " AND a.id_order = %s "
			values += (id_order, )
		if id_brand:
			query += " AND a.id_brand = %s "
			values += (id_brand, )
		if status_order:
			query += " AND a.status_order = %s "
			values += (status_order, )
		if search:
			query += """ AND CONCAT_WS("|", a.nomor_order) LIKE %s """
			values += ("%"+search+"%", )

		if order_by:
			if order_by == "id_asc":
				query += " ORDER BY a.id_order ASC "
			elif order_by == "id_desc":
				query += " ORDER BY a.id_order DESC "
			else:
				query += " ORDER BY a.id_order DESC "
		else:
			query += " ORDER BY a.id_order DESC "

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

@pos.route('/get_order_detail', methods=['GET', 'OPTIONS'])
@jwt_required()
@cross_origin()
def get_order_detail():
	try:
		ROUTE_NAME = str(request.path)

		role = str(get_jwt()["role"])

		if role not in role_group_admin:
			return permission_failed()

		dt = Data()

		query = """ SELECT a.*, b.nomor_order, c.foto_produk
					FROM pos_order_detail a
					LEFT JOIN pos_order b ON a.id_order=b.id_order
					LEFT JOIN pos_produk c ON a.id_produk=c.id_produk
					WHERE a.is_delete!=1 """
		values = ()

		id_order = request.args.get("id_order") # WAJIB

		# validasi parameter id order
		if id_order == None:
			return parameter_error("Missing id_order in Request Parameter")

		# if role in role_group_admin_brand:
		# 	id_brand = str(get_jwt()["id_brand"])
		# else:
		# 	id_brand = request.args.get("id_brand")


		if id_order:
			query += " AND a.id_order = %s "
			values += (id_order, )
		# if id_brand:
		# 	query += " AND b.id_brand = %s "
		# 	values += (id_brand, )

		query += " ORDER BY a.id_order DESC "

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

@pos.route('/insert_order', methods=['POST', 'OPTIONS'])
@jwt_required()
@cross_origin()
def insert_order():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	role = str(get_jwt()["role"])

	if role not in role_group_admin_lokasi:
		return permission_failed()

	id_admin = str(get_jwt()["id_admin"])
	id_lokasi = str(get_jwt()["id_lokasi"])
	id_user = id_admin

	try:
		dt = Data()
		data = request.json

		# Check mandatory data
		if "list_produk" not in data:
			return parameter_error("Missing list_produk in Request Body")
		if "tipe_pembelian" not in data:
			return parameter_error("Missing tipe_pembelian in Request Body")
		if "id_metode_pembayaran_pos" not in data:
			id_metode_pembayaran_pos = None
		else:
			id_metode_pembayaran_pos 	= data["id_metode_pembayaran_pos"]
		
		list_produk 				= data["list_produk"]
		tipe_pembelian 				= data["tipe_pembelian"]
		
		# validasi list order
		if isinstance(list_produk, list) == False:
			return defined_error(description="Format List Order salah", error="Parameter Error", status_code=400, hidden_description="Harap gunakan tipe data array (list) untuk list_produk")

		# cek data produk, perhitungan harga total, dan membuat list insert produk
		total_harga = 0
		list_insert_produk = []
		for x in list_produk:
			if isinstance(x, dict) == False:
				return defined_error(description="Format Produk didalam List Order salah", error="Parameter Error", status_code=400, hidden_description="Harap gunakan format JSON untuk data produk didalam list_produk")

			if "id_produk" not in x:
				return parameter_error("Missing id_produk in list_produk")
			if "jumlah" not in x:
				return parameter_error("Missing jumlah in list_produk")

			id_produk = x["id_produk"]
			jumlah = x["jumlah"]
			
			query_temp = """
							SELECT a.id_produk, a.id_brand, a.nama_produk, a.harga, b.id_lokasi, a.pajak 
							FROM pos_produk a 
							LEFT JOIN pos_brand b ON a.id_brand=b.id_brand 
							WHERE a.is_delete!=1 AND a.id_produk = %s
						"""
			values_temp = (id_produk,)
			data_temp = dt.get_data(query_temp, values_temp)
			print(data_temp)
			if len(data_temp) == 0:
				return defined_error("Gagal, Terdapat data produk yang tidak ditemukan")

			data_temp = data_temp[0]
			db_id_lokasi = data_temp["id_lokasi"]
			db_nama_produk = data_temp["nama_produk"]
			db_harga = data_temp["harga"]
			db_pajak = data_temp["pajak"]

			id_brand = data_temp["id_brand"]
			
			# pengecekan apakah produk yang dibeli berasal dari brand yang sama
			if str(db_id_lokasi) != str(id_lokasi):
				return defined_error("Gagal, Terdapat produk dari lokasi lain. Harap checkout produk dari lokasi yang sama")

			total_harga += db_harga * jumlah * (1 + db_pajak/100)

			json_insert_produk = {
				"id_produk" : id_produk,
				"nama_produk" : db_nama_produk,
				"jumlah" : jumlah,
				"harga_produk_satuan" : db_harga,
				"harga_produk_total" : db_harga * jumlah
			}
			list_insert_produk.append(json_insert_produk)

		# Generate nomor order
		while True:
			nomor_order = str(now.strftime("%Y%m%d") + random_string_number_only(8))
			# cek apakah nomor_order telah digunakan atau belum
			query_temp = "SELECT a.id_order FROM pos_order a WHERE a.nomor_order = %s"
			values_temp = (nomor_order, )
			data_temp = dt.get_data(query_temp, values_temp)

			if len(data_temp) == 0:
				break

		# Insert ke tabel order
		query = "INSERT INTO pos_order (id_brand, id_metode_pembayaran_pos, nomor_order, waktu_order, total_harga, tipe_pembelian) VALUES (%s, %s, %s, %s, %s, %s)"
		values = (id_brand, id_metode_pembayaran_pos, nomor_order, now, total_harga, tipe_pembelian,)
		id_order = dt.insert_data_last_row(query, values)

		# Insert ke tabel order detail
		list_id_order_detail = []
		for x in list_insert_produk:
			query = "INSERT INTO pos_order_detail (id_order, id_produk, nama_produk, jumlah, harga_produk_satuan, harga_produk_total) VALUES (%s, %s, %s, %s, %s, %s)"
			values = (id_order, x["id_produk"], x["nama_produk"], x["jumlah"], x["harga_produk_satuan"], x["harga_produk_total"], )
			id_order_detail = dt.insert_data_last_row(query, values)
			list_id_order_detail.append(id_order_detail)

		hasil = "Berhasil membuat order"
		hasil_data = {
			"id_order" : id_order,
			"total_harga" : int(total_harga),
			"waktu_order" : now,
			"list_id_order_detail" : list_id_order_detail
		}
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil, 'data' : hasil_data} ), 200)
	except Exception as e:
		return bad_request(str(e))


@pos.route('/update_order', methods=['PUT', 'OPTIONS'])
@jwt_required()
@cross_origin()
def update_order():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	role = str(get_jwt()["role"])

	if role not in (role_group_admin_lokasi + role_group_admin_brand):
		return permission_failed()

	id_admin = str(get_jwt()["id_admin"])
	id_user = id_admin

	if role in role_group_admin_lokasi:
		id_lokasi = str(get_jwt()["id_lokasi"])
	if role in role_group_admin_brand:
		id_brand = str(get_jwt()["id_brand"])

	try:
		dt = Data()
		data = request.json

		if "id_order" not in data:
			return parameter_error("Missing id_order in Request Body")

		id_order = data["id_order"]

		# Cek apakah data order ada
		query_temp = "SELECT a.id_order, a.tipe_pembelian, a.id_brand FROM pos_order a WHERE a.is_delete!=1 AND a.id_order = %s"
		values_temp = (id_order, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data Order tidak ditemukan")

		data_temp = data_temp[0]
		tipe_pembelian = str(data_temp['tipe_pembelian'])
		id_brand = data_temp['id_brand']

		query = """ UPDATE pos_order SET id_order=id_order """
		values = ()

		if "status_order" in data:
			status_order = data["status_order"]
			
			# validasi data status order
			if str(status_order) not in ["1","2","3","4","5",]:
				return defined_error("Gagal, Harap berikan data status order dengan benar")
			query += """ ,status_order = %s """
			values += (status_order, )
			try:
				#status order 4 == finish, tipe pembelian 1 == online
				if str(status_order) == '4' and tipe_pembelian == '1':
					#mendapatkan  Akses token gojek
					url_sandbox_gojek = 'https://api.sandbox.gobiz.co.id'
					url_sanbox_gojek_login = 'https://integration-goauth.gojekapi.com/oauth2/token'

					#link untuk prod
					#url_sandbox_gojek = 'https://api.gobiz.co.id/'
					#url_sanbox_gojek_login = 'https://accounts.go-jek.com'
					
					
					body_params = {'client_id':'DY8cfa12BrS7E1Oa',
						'client_secret':'jyrPO0tGXI5tTVlLKuRb9CKNnnJmjuKu',
						'grant_type':'client_credentials',
						'scope':'gofood:catalog:write gofood:catalog:read gofood:order:write gofood:order:read gofood:outlet:write promo:food_promo:read promo:food_promo:write'}
					head= {'Content-Type': 'application/x-www-form-urlencoded'}
					hasil = requests.post(url_sanbox_gojek_login, body_params, head)
					hasil = hasil.json()
					access_token_gobiz = hasil['access_token']

					#mencari parameter outlet id, order_type dan order_id
					query_temp2 = """
								SELECT a.* 
								FROM pos_order_gojek a 
								WHERE a.is_delete!=1 AND a.id_order = %s
								"""
					values_temp2 = (id_order,)
					data_temp2 = dt.get_data(query_temp2, values_temp2)
					if len(data_temp2) == 0:
						return defined_error("Gagal, Terdapat data produk yang tidak ditemukan")

					data_temp2 = data_temp2[0]
					order_id = data_temp2['id_order_gojek_gojek']
					outlet_id = data_temp2['id_outlet']
					order_type = str(data_temp2["tipe_order_gojek"])

					if order_type == '1':
						order_type = 'delivery'
					else:
						order_type = 'pickup'
					
					url_MFR = "/integrations/gofood/outlets/{}/v1/orders/{}/{}/food-prepared".format(outlet_id, order_type, order_id)
					head= {'Content-Type': 'application/json', 'Authorization': "Bearer {}".format(access_token_gobiz)}
					payload = {"country_code" : "ID"}
					hasil = requests.put(url_sandbox_gojek + url_MFR,  data=json.dumps(payload), headers=head)
					print(hasil.json())
					print("Terima kasih telah memesan di GoFood")
				else:
					print("Harap selesaikan pesanan")
			except:
				print("orderan bukan dari gojek")
				
		if "is_delete" in data:
			is_delete = data["is_delete"]
			# validasi data is_delete
			if str(is_delete) not in ["1"]:
				return parameter_error("Invalid is_delete Parameter")
			query += """ ,is_delete = %s """
			values += (is_delete, )

		query += """ WHERE id_order = %s """
		values += (id_order, )
		dt.insert_data(query, values)

		hasil = "Berhasil mengubah data order"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))


#endregion ================================= ORDER DAN ORDER DETAIL AREA ==========================================================================


#region ================================= DISPLAY AREA ==========================================================================

@pos.route('/get_display', methods=['GET', 'OPTIONS'])
@jwt_required()
@cross_origin()
def get_display():
	try:
		ROUTE_NAME = str(request.path)

		now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

		role 	= str(get_jwt()["role"])

		if role not in (role_group_super_admin + role_group_admin_lokasi):
			return permission_failed()

		id_admin = str(get_jwt()["id_admin"])
		id_user = id_admin

		dt = Data()

		# parameter khusus (mode)
		mode = request.args.get("mode")
		if (mode == None or mode == ""):
			mode = "1"
		else:
			mode = str(mode)

		if mode == "1": # Normal
			query = """ SELECT a.*
						FROM pos_display a
						WHERE a.is_delete!=1 """
			values = ()
		else:
			return parameter_error("Invalid mode Parameter")

		limit = request.args.get("limit")
		page = request.args.get("page")
		id_display = request.args.get("id_display")
		search = request.args.get("search")
		order_by = request.args.get("order_by")

		if role in role_group_admin_lokasi:
			id_lokasi = str(get_jwt()["id_lokasi"])
		else:
			id_lokasi = request.args.get("id_lokasi")

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


		if (page == None):
			page = 1

		if id_display:
			query += " AND a.id_display = %s "
			values += (id_display, )

		if id_lokasi:
			query += " AND a.id_lokasi = %s "
			values += (id_lokasi, )

		if search:
			query += """ AND CONCAT_WS("|", a.nama_display) LIKE %s """
			values += (search, )

		if order_by:
			if order_by == "id_asc":
				query += " ORDER BY a.id_display ASC "
			elif order_by == "id_desc":
				query += " ORDER BY a.id_display DESC "

			else:
				query += " ORDER BY a.id_display DESC "
		else:
			query += " ORDER BY a.id_display DESC "

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


@pos.route('/insert_display', methods=['POST', 'OPTIONS'])
@jwt_required()
@cross_origin()
def insert_display():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	role = str(get_jwt()["role"])

	if role not in (role_group_super_admin + role_group_admin_lokasi):
		return permission_failed()

	id_admin = str(get_jwt()["id_admin"])
	id_user = id_admin

	try:
		dt = Data()
		data = request.json

		# Check mandatory data
		if "nama_display" not in data:
			return parameter_error("Missing nama_display in Request Body")
		if "tipe_display" not in data:
			return parameter_error("Missing tipe_display in Request Body")

		nama_display 			= data["nama_display"]
		tipe_display 			= data["tipe_display"]

		# Check mandatory data yang berhubungan sama role
		if role in role_group_admin_lokasi:
			id_lokasi = str(get_jwt()["id_lokasi"])
		else:
			if "id_lokasi" not in data:
				return parameter_error("Missing id_lokasi in Request Body")

			id_lokasi = data["id_lokasi"]

		# Cek data lokasi
		query_temp = "SELECT a.id_lokasi FROM lokasi a WHERE a.is_delete != 1 AND a.id_lokasi = %s"
		values_temp = (id_lokasi, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data lokasi tidak ditemukan")


		# Insert ke tabel db
		query = "INSERT INTO pos_display (id_lokasi, nama_display, tipe_display) VALUES (%s, %s, %s)"
		values = (id_lokasi, nama_display, tipe_display,)
		id_display = dt.insert_data_last_row(query, values)

		hasil = "Berhasil menambahkan display"
		hasil_data = {
			"id_display" : id_display
		}
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil, 'data' : hasil_data} ), 200)
	except Exception as e:
		return bad_request(str(e))


@pos.route('/update_display', methods=['PUT', 'OPTIONS'])
@jwt_required()
@cross_origin()
def update_display():
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

		if "id_display" not in data:
			return parameter_error("Missing id_display in Request Body")

		id_display = data["id_display"]

		# Cek apakah data display ada
		query_temp = "SELECT a.id_display FROM pos_display a WHERE a.is_delete != 1 AND a.id_display = %s"
		values_temp = (id_display, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data Display tidak ditemukan")

		query = """ UPDATE pos_display SET id_display=id_display """
		values = ()


		if "nama_display" in data:
			nama_display = data["nama_display"]
			query += """ ,nama_display = %s """
			values += (nama_display, )

		if "tipe_display" in data:
			tipe_display = data["tipe_display"]
			query += """ ,tipe_display = %s """
			values += (tipe_display, )

		if "is_delete" in data:
			is_delete = data["is_delete"]
			# validasi data is_delete
			if str(is_delete) not in ["1"]:
				return parameter_error("Invalid is_delete Parameter")
			query += """ ,is_delete = %s """
			values += (is_delete, )

		query += """ WHERE id_display = %s """
		values += (id_display, )
		dt.insert_data(query, values)

		hasil = "Berhasil mengubah data display"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))

@pos.route('/delete_display', methods=['PUT', 'OPTIONS'])
@jwt_required()
@cross_origin()
def delete_display():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	role = str(get_jwt()["role"])

	if role not in (role_group_super_admin + role_group_admin_lokasi):
		return permission_failed()

	id_admin = str(get_jwt()["id_admin"])
	id_user = id_admin

	if role in role_group_admin_lokasi:
		id_lokasi = str(get_jwt()["id_lokasi"])
	else:
		id_lokasi = None

	try:
		dt = Data()
		data = request.json

		if "id_display" not in data:
			return parameter_error("Missing id_display in Request Body")

		id_display = data["id_display"]

		# Cek apakah data display ada
		query_temp = "SELECT a.* FROM pos_display a WHERE a.is_delete != 1 AND a.id_display = %s"
		values_temp = (id_display, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data Display tidak ditemukan")
		else:
			data_temp = data_temp[0]
			db_id_lokasi_display = data_temp["id_lokasi"]
			# Jika login sebagai admin lokasi maka cek apakah display milik lokasi tersebut
			if id_lokasi:
				if str(id_lokasi) != str(db_id_lokasi_display):
					return defined_error("Gagal, Data Display bukan milik lokasi anda")


		query = """ UPDATE pos_display SET id_display=id_display """
		values = ()

		if "is_delete" in data:
			is_delete = data["is_delete"]
			# validasi data is_delete
			if str(is_delete) not in ["1"]:
				return parameter_error("Invalid is_delete Parameter")
			query += """ ,is_delete = %s """
			values += (is_delete, )

		query += """ WHERE id_display = %s """
		values += (id_display, )
		dt.insert_data(query, values)

		hasil = "Berhasil menghapus data display"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))


@pos.route('/get_order_for_display', methods=['GET', 'OPTIONS'])
@jwt_required()
@cross_origin()
def get_order_for_display():
	try:
		ROUTE_NAME = str(request.path)

		role = str(get_jwt()["role"])

		if role not in (role_group_super_admin + role_group_admin_lokasi):
			return permission_failed()

		id_admin = str(get_jwt()["id_admin"])
		id_user = id_admin

		dt = Data()

		id_display = request.args.get("id_display")

		if role in role_group_admin_brand:
			id_brand = str(get_jwt()["id_brand"])
		else:
			id_brand = request.args.get("id_brand")

		if id_display == None:
			return parameter_error("Missing id_display in Request Parameter")

		# Cek data display
		query_temp = "SELECT a.id_display, a.id_lokasi, a.tipe_display FROM pos_display a WHERE a.is_delete!=1 AND a.id_display = %s"
		values_temp = (id_display, )
		data_temp = dt.get_data(query_temp, values_temp)

		if len(data_temp) == 0:
			return defined_error("Gagal, Data Display tidak ditemukan")

		data_temp = data_temp[0]

		db_id_lokasi = str(data_temp["id_lokasi"])
		db_tipe_display = str(data_temp["tipe_display"])

		if db_tipe_display != "1":
			# get id brand yang akan ditampilkan ordernya pada display tersebut jika displaynya khusus
			query_temp = "SELECT a.id_brand FROM pos_display_brand a WHERE a.is_delete!=1 AND a.id_display = %s"
			values_temp = (id_display, )
			data_temp = dt.get_data(query_temp, values_temp)

			db_list_id_brand = []
			for x in data_temp:
				db_list_id_brand.append(str(x["id_brand"]))

			string_list_id_brand = ",".join(db_list_id_brand)

			# Get data order
			query = """ SELECT a.*
						FROM pos_order a
						WHERE a.is_delete !=1 AND a.status_order NOT IN (4, 5) AND a.id_brand IN ("""+string_list_id_brand+""") ORDER BY id_order ASC """
			values = ()

		else:
			# Get data order
			query = """ SELECT a.*
						FROM pos_order a
                        LEFT JOIN pos_brand b ON a.id_brand=b.id_brand
						WHERE a.is_delete !=1 AND a.status_order NOT IN (4, 5) AND b.id_lokasi = %s ORDER BY id_order ASC """
			values = (db_id_lokasi, )

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

@pos.route('/get_order_for_display_complete', methods=['GET', 'OPTIONS'])
@jwt_required()
@cross_origin()
def get_order_for_display_complete():
	try:
		ROUTE_NAME = str(request.path)

		role = str(get_jwt()["role"])

		if role not in (role_group_super_admin + role_group_admin_lokasi):
			return permission_failed()

		id_admin = str(get_jwt()["id_admin"])
		id_user = id_admin

		dt = Data()

		id_display = request.args.get("id_display")

		if id_display == None:
			return parameter_error("Missing id_display in Request Parameter")

		# Cek data display
		query_temp = "SELECT a.id_display, a.id_lokasi, a.tipe_display FROM pos_display a WHERE a.is_delete!=1 AND a.id_display = %s"
		values_temp = (id_display, )
		data_temp = dt.get_data(query_temp, values_temp)

		if len(data_temp) == 0:
			return defined_error("Gagal, Data Display tidak ditemukan")

		data_temp = data_temp[0]

		db_id_lokasi = str(data_temp["id_lokasi"])
		db_tipe_display = str(data_temp["tipe_display"])

		# Get id_order yang harus ditampilkan
		if db_tipe_display != "1":
			# get id brand yang akan ditampilkan ordernya pada display tersebut jika displaynya khusus
			query_temp = "SELECT a.id_brand FROM pos_display_brand a WHERE a.is_delete!=1 AND a.id_display = %s"
			values_temp = (id_display, )
			data_temp = dt.get_data(query_temp, values_temp)

			db_list_id_brand = []
			for x in data_temp:
				db_list_id_brand.append(str(x["id_brand"]))

			string_list_id_brand = ",".join(db_list_id_brand)

			# Get data order pos_order_customer_kiosk
			query = """ SELECT a.*
						FROM pos_order a
						LEFT JOIN pos_order_customer_qr b ON a.id_order=b.id_order
						LEFT JOIN pos_order_customer_kiosk c ON a.id_order=c.id_order
						WHERE a.is_delete !=1 AND a.status_order NOT IN (4, 5) AND ((b.status_pemesanan is null OR b.status_pemesanan = 2) AND (c.status_pemesanan is null OR c.status_pemesanan = 2)) AND a.id_brand IN ("""+string_list_id_brand+""") 
						ORDER BY id_order ASC """
			values = ()

		else:
			# Get data order
			query = """ SELECT a.*
						FROM pos_order a
                        LEFT JOIN pos_brand b ON a.id_brand=b.id_brand
						LEFT JOIN pos_order_customer_qr c ON a.id_order=c.id_order
						LEFT JOIN pos_order_customer_kiosk d ON a.id_order=d.id_order
						WHERE a.is_delete !=1 AND a.status_order NOT IN (4, 5) AND ((c.status_pemesanan is null OR c.status_pemesanan = 2) AND (d.status_pemesanan is null OR d.status_pemesanan = 2)) AND b.id_lokasi = %s 
						ORDER BY id_order ASC """
			values = (db_id_lokasi, )

		rowCount_data_order = dt.row_count(query, values)
		data_order = dt.get_data(query, values)

		# Menambahkan data order_detail
		list_order_detail = []
		hasil_data_order = []
		for x in data_order:
			query_order_detail = """ SELECT a.*, b.nomor_order, c.foto_produk
					FROM pos_order_detail a
					LEFT JOIN pos_order b ON a.id_order=b.id_order
					LEFT JOIN pos_produk c ON a.id_produk=c.id_produk
					WHERE a.is_delete!=1 AND a.id_order = %s  """
			values_order_detail = (x["id_order"], )
			data_order_detail = dt.get_data(query_order_detail, values_order_detail)

			temp_data_order = x
			temp_data_order["order_detail"] = data_order_detail

			hasil_data_order.append(temp_data_order)


		hasil = {'data': hasil_data_order , 'status_code': 200, 'page': 1, 'offset': 'none', 'row_count': rowCount_data_order}
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

#endregion ================================= DISPLAY AREA ==========================================================================


#region ================================= DISPLAY BRAND AREA ==========================================================================

@pos.route('/get_display_brand', methods=['GET', 'OPTIONS'])
@jwt_required()
@cross_origin()
def get_display_brand():
	try:
		ROUTE_NAME = str(request.path)

		now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

		role 	= str(get_jwt()["role"])

		if role not in (role_group_super_admin + role_group_admin_lokasi):
			return permission_failed()

		id_admin = str(get_jwt()["id_admin"])
		id_user = id_admin

		dt = Data()

		# parameter khusus (mode)
		mode = request.args.get("mode")
		if (mode == None or mode == ""):
			mode = "1"
		else:
			mode = str(mode)

		if mode == "1": # Normal
			query = """ SELECT a.*, b.nama_display, b.tipe_display, c.nama_brand
						FROM pos_display_brand a
						LEFT JOIN pos_display b on a.id_display=b.id_display
						LEFT JOIN pos_brand c ON a.id_brand=c.id_brand
                        LEFT JOIN lokasi d ON c.id_lokasi= d.id_lokasi
						WHERE a.is_delete!=1 """
			values = ()
		else:
			return parameter_error("Invalid mode Parameter")

		limit = request.args.get("limit")
		page = request.args.get("page")
		id_display = request.args.get("id_display")
		id_brand = request.args.get("id_brand")
		search = request.args.get("search")
		order_by = request.args.get("order_by")

		if role in role_group_admin_lokasi:
			id_lokasi = str(get_jwt()["id_lokasi"])
		else:
			id_lokasi = request.args.get("id_lokasi")

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


		if (page == None):
			page = 1

		if id_display:
			query += " AND a.id_display = %s "
			values += (id_display, )

		if id_brand:
			query += " AND a.id_brand = %s "
			values += (id_brand, )

		if id_lokasi:
			query += " AND d.id_lokasi = %s "
			values += (id_lokasi, )

		if search:
			query += """ AND CONCAT_WS("|", b.nama_display) LIKE %s """
			values += (search, )

		if order_by:
			if order_by == "id_asc":
				query += " ORDER BY a.id_display_brand ASC "
			elif order_by == "id_desc":
				query += " ORDER BY a.id_display_brand DESC "

			else:
				query += " ORDER BY a.id_display_brand DESC "
		else:
			query += " ORDER BY a.id_display_brand DESC "

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

@pos.route('/insert_display_brand', methods=['POST', 'OPTIONS'])
@jwt_required()
@cross_origin()
def insert_display_brand():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	role = str(get_jwt()["role"])

	if role not in (role_group_super_admin + role_group_admin_lokasi):
		return permission_failed()

	id_admin = str(get_jwt()["id_admin"])
	id_user = id_admin

	if role in role_group_admin_lokasi:
		id_lokasi = str(get_jwt()["id_lokasi"])
	else:
		id_lokasi = None

	try:
		dt = Data()
		data = request.json

		# Check mandatory data
		if "id_display" not in data:
			return parameter_error("Missing id_display in Request Body")
		if "id_brand" not in data:
			return parameter_error("Missing id_brand in Request Body")

		id_display 			= data["id_display"]
		id_brand 			= data["id_brand"]

		# Cek apakah data display ada
		query_temp = "SELECT a.id_display, a.id_lokasi FROM pos_display a WHERE a.is_delete != 1 AND a.id_display = %s"
		values_temp = (id_display, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data Display tidak ditemukan")
		else:
			data_temp = data_temp[0]
			db_id_lokasi_display = data_temp["id_lokasi"]
			# Jika login sebagai admin lokasi maka cek apakah display milik lokasi tersebut
			if id_lokasi:
				if str(id_lokasi) != str(db_id_lokasi_display):
					return defined_error("Gagal, Data Display bukan milik lokasi anda")

		# Cek apakah data brand ada
		query_temp = "SELECT a.id_brand, a.id_lokasi FROM pos_brand a WHERE a.is_delete != 1 AND a.id_brand = %s"
		values_temp = (id_brand, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data Brand tidak ditemukan")
		else:
			data_temp = data_temp[0]
			db_id_lokasi_brand = data_temp["id_lokasi"]
			# Jika login sebagai admin lokasi maka cek apakah brand milik lokasi tersebut
			if id_lokasi:
				if str(id_lokasi) != str(db_id_lokasi_brand):
					return defined_error("Gagal, Data Brand bukan milik lokasi anda")

		# Cek apakah brand dan display berada pada lokasi yang sama
		if str(db_id_lokasi_display) != str(db_id_lokasi_brand):
			return defined_error("Gagal, Brand dan Display tidak berada pada lokasi yang sama")

		# Cek apakah brand sudah terhubung ke display atau belum, jika sudah tidak bisa input
		query_temp = "SELECT a.id_display_brand, a.is_delete FROM pos_display_brand a WHERE a.id_display = %s AND a.id_brand = %s"
		values_temp = (id_display, id_brand, )
		data_temp = dt.get_data(query_temp, values_temp)

		# Jika sudah ada data didalam database maka tidak bisa input
		if len(data_temp) != 0:
			data_temp = data_temp[0]

			id_display_brand = data_temp["id_display_brand"]
			db_is_delete = data_temp["is_delete"]

			if str(db_is_delete) == "0":
				return defined_error("Gagal, Brand sudah terhubung dengan display")
			else:
				query = "UPDATE pos_display_brand SET is_delete = 0 WHERE id_display_brand = %s"
				values = (id_display_brand, )
				dt.insert_data(query, values)
		else:
			# Insert ke tabel db
			query = "INSERT INTO pos_display_brand (id_display, id_brand) VALUES (%s, %s)"
			values = (id_display, id_brand,)
			id_display_brand = dt.insert_data_last_row(query, values)

		hasil = "Berhasil menghubungkan display dengan brand"
		hasil_data = {
			"id_display_brand" : id_display_brand
		}
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil, 'data' : hasil_data} ), 200)
	except Exception as e:
		return bad_request(str(e))

@pos.route('/update_display_brand', methods=['PUT', 'OPTIONS'])
@jwt_required()
@cross_origin()
def update_display_brand():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	role = str(get_jwt()["role"])

	if role not in (role_group_super_admin + role_group_admin_lokasi):
		return permission_failed()

	id_admin = str(get_jwt()["id_admin"])
	id_user = id_admin

	if role in role_group_admin_lokasi:
		id_lokasi = str(get_jwt()["id_lokasi"])
	else:
		id_lokasi = None

	try:
		dt = Data()
		data = request.json

		if "id_display" not in data:
			return parameter_error("Missing id_display in Request Body")

		if "id_brand" not in data:
			return parameter_error("Missing id_brand in Request Body")
		
		if "id_display_brand" not in data:
			return parameter_error("Missing id_display_brand in Request Body")

		id_display_brand = data["id_display_brand"]
		id_display = data["id_display"]
		id_brand = data["id_brand"]

		# Cek apakah data display ada
		query_temp = "SELECT a.id_display, a.id_lokasi FROM pos_display a WHERE a.is_delete != 1 AND a.id_display = %s"
		values_temp = (id_display, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data Display tidak ditemukan")
		else:
			data_temp = data_temp[0]
			db_id_lokasi_display = data_temp["id_lokasi"]
			# Jika login sebagai admin lokasi maka cek apakah display milik lokasi tersebut
			if id_lokasi:
				if str(id_lokasi) != str(db_id_lokasi_display):
					return defined_error("Gagal, Data Display bukan milik lokasi anda")

		# Cek apakah data brand ada
		query_temp = "SELECT a.id_brand, a.id_lokasi FROM pos_brand a WHERE a.is_delete != 1 AND a.id_brand = %s"
		values_temp = (id_brand, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data Brand tidak ditemukan")
		else:
			data_temp = data_temp[0]
			db_id_lokasi_brand = data_temp["id_lokasi"]
			# Jika login sebagai admin lokasi maka cek apakah brand milik lokasi tersebut
			if id_lokasi:
				if str(id_lokasi) != str(db_id_lokasi_brand):
					return defined_error("Gagal, Data Brand bukan milik lokasi anda")

		query = """ UPDATE pos_display_brand SET id_display_brand=id_display_brand """
		values = ()
		#check apakah brandnya sesuai lokasinya
		#agar admin lokasi tidak bisa update brand dari lokasi lain
		#semisal admin petogogan tidak bisa update brand di pasirsalam
		if role in role_group_admin_lokasi:
			id_lokasi = str(get_jwt()["id_lokasi"])
			query_temp = """ SELECT a.*
							FROM pos_display_brand a
							WHERE a.is_delete != 1 AND a.id_display = %s AND a.id_brand  =  %s 
						"""
			values_temp = (id_display, id_brand)
			data_temp = dt.get_data(query_temp, values_temp)
			if len(data_temp) == 0:
				return defined_error("Gagal, Data display dan brand tidak ditemukan atau tidak aktif atau bukan berada di lokasi anda")
	

		if role in role_group_super_admin and "id_lokasi" in data:
			id_lokasi = data["id_lokasi"]
			query += """ ,id_lokasi = %s """
			values += (id_lokasi, )

		if "id_display" in data:
			id_display = data["id_display"]
			query_temp = "SELECT id_display FROM pos_display WHERE is_delete!=1 AND id_display = %s"
			values_temp = (id_display, )
			data_temp = dt.get_data(query_temp, values_temp)
			if len(data_temp) == 0:
				return defined_error("Gagal, kategori tidak ditemukan")
			query += """ ,id_display = %s """
			values += (id_display, )

		if "id_brand" in data:
			id_brand = data["id_brand"]
			query_temp = "SELECT id_brand FROM pos_brand WHERE is_delete!=1 AND id_brand = %s"
			values_temp = (id_brand, )
			data_temp = dt.get_data(query_temp, values_temp)
			if len(data_temp) == 0:
				return defined_error("Gagal, kategori tidak ditemukan")
			query += """ ,id_brand = %s """
			values += (id_brand, )

		if "is_delete" in data:
			is_delete = data["is_delete"]
			# validasi data is_delete
			if str(is_delete) not in ["1"]:
				return parameter_error("Invalid is_delete Parameter")
			query += """ ,is_delete = %s """
			values += (is_delete, )

		query += """ WHERE id_display_brand  = %s """
		values += (id_display_brand,)
		dt.insert_data(query, values)

		hasil = "Berhasil mengubah data brand"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))

@pos.route('/delete_display_brand', methods=['PUT', 'OPTIONS'])
@jwt_required()
@cross_origin()
def delete_display_brand():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	role = str(get_jwt()["role"])

	if role not in (role_group_super_admin + role_group_admin_lokasi):
		return permission_failed()

	id_admin = str(get_jwt()["id_admin"])
	id_user = id_admin

	if role in role_group_admin_lokasi:
		id_lokasi = str(get_jwt()["id_lokasi"])
	else:
		id_lokasi = None

	try:
		dt = Data()
		data = request.json
		
		if "id_display_brand" not in data:
			return parameter_error("Missing id_display_brand in Request Body")

		id_display_brand = data["id_display_brand"]

		# Cek apakah data display ada
		query_temp = """ SELECT b.*, a.*
						FROM pos_display_brand a
						LEFT JOIN pos_display b ON a.id_display=b.id_display
						WHERE a.id_display_brand = %s """
						
		values_temp = (id_display_brand, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data Display tidak ditemukan")
		else:
			data_temp = data_temp[0]
			db_id_lokasi_display = data_temp["id_lokasi"]
			# Jika login sebagai admin lokasi maka cek apakah display milik lokasi tersebut
			if id_lokasi:
				if str(id_lokasi) != str(db_id_lokasi_display):
					return defined_error("Gagal, Data Display bukan milik lokasi anda")

		query = """ UPDATE pos_display_brand SET id_display_brand=id_display_brand """
		values = ()
		#check apakah brandnya sesuai lokasinya
		#agar admin lokasi tidak bisa update brand dari lokasi lain
		#semisal admin petogogan tidak bisa update brand di pasirsalam
		if role in role_group_admin_lokasi:
			id_lokasi = str(get_jwt()["id_lokasi"])
			query_temp = """ SELECT b.*, a.*
						FROM pos_display_brand a
						LEFT JOIN pos_display b ON a.id_display=b.id_display
						WHERE a.id_display_brand = %s AND b.id_lokasi = %s """
			values_temp = (id_display_brand, id_lokasi)
			data_temp = dt.get_data(query_temp, values_temp)
			if len(data_temp) == 0:
				return defined_error("Gagal, Data display brand tidak ditemukan atau tidak aktif atau bukan berada di lokasi anda")

		if "is_delete" in data:
			is_delete = data["is_delete"]
			# validasi data is_delete
			if str(is_delete) not in ["1"]:
				return parameter_error("Invalid is_delete Parameter")
			query += """ ,is_delete = %s """
			values += (is_delete, )

		query += """ WHERE id_display_brand  = %s """
		values += (id_display_brand,)
		dt.insert_data(query, values)

		hasil = "Berhasil mengahpus data display brand"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))


#endregion ================================= DISPLAY BRAND AREA ==========================================================================


#region ================================= GOJEK AREA ==========================================================================

@pos.route('/accept_order_gojek', methods=['POST', 'OPTIONS'])
@cross_origin()
def accept_order_gojek():
	#event trigger gofood.order.created
	ROUTE_NAME = str(request.path)
	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
	
	try:
		dt = Data()
		#sepertinya respon webhook dari gobiz berupa json
		data = request.json
		#print(data)

		#akses token gobiz
		#request_gobiz = 
		body_params = {'client_id':'DY8cfa12BrS7E1Oa',
					'client_secret':'jyrPO0tGXI5tTVlLKuRb9CKNnnJmjuKu',
					'grant_type':'client_credentials',
					'scope':'gofood:catalog:write gofood:catalog:read gofood:order:write gofood:order:read gofood:outlet:write promo:food_promo:read promo:food_promo:write'}	
		head= {'Content-Type': 'application/x-www-form-urlencoded'}
		hasil = requests.post(url_sanbox_gojek_login, body_params, head)
		hasil = hasil.json()
		access_token = hasil['access_token']
		print(access_token)
		# Check mandatory data
		if "body" not in data:
			body = data
		else:
			body = data['body']
		
		outlet		= body["outlet"]
		outlet_id	= outlet["id"]

		order_type 	= body["service_type"]
		if order_type == "gofood":
			order_type = "delivery"
		else:
			order_type = "pickup"
			
		order 		= body["order"]
		order_id 	= order["order_number"]

		url_gojek_accept = "/integrations/gofood/outlets/{}/v1/orders/{}/{}/accepted".format(outlet_id, order_type, order_id)
		head= {'Content-Type': 'application/json', 'Authorization': "Bearer {}".format(access_token)}
		hasil = requests.put(url_sandbox_gojek + url_gojek_accept, headers=head)
		print(hasil.json())

		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_admin = "+str(id_admin)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_admin = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil.json(),'body' : body} ), 200)
	except Exception as e:
		return bad_request(str(e))


@pos.route('/insert_order_gojek', methods=['POST', 'OPTIONS'])
@cross_origin()
def insert_order_gojek():
	#event trigger gofood.order.merchant_accepted
	ROUTE_NAME = str(request.path)
	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
	
	try:
		dt = Data()
		#sepertinya respon webhook dari gobiz berupa json
		data = request.json
		#print(data)
		# Check mandatory data
		if "body" not in data:
			body = data
		else:
			body = data['body']

		outlet					= body["outlet"]
		outlet_id				= outlet["id"]

		order_type 				= body["service_type"]

		if order_type == 'gofood_pickup':
			tipe_order_gojek = 2
		else:
			tipe_order_gojek = 1 

		order 					= body["order"]
		id_order_gojek 			= order["order_number"]
		order_pin 				= order["pin"]
		list_produk 			= order["order_items"]

		# validasi list order
		if isinstance(list_produk, list) == False:
			return defined_error(description="Format List Order salah", error="Parameter Error", status_code=400, hidden_description="Harap gunakan tipe data array (list) untuk list_produk")

		# cek data produk, perhitungan harga total, dan membuat list insert produk
		total_harga = 0
		list_insert_produk = []
		check_id_brand = 0
		for x in list_produk:
			if isinstance(x, dict) == False:
				return defined_error(description="Format Produk didalam List Order salah", error="Parameter Error", status_code=400, hidden_description="Harap gunakan format JSON untuk data produk didalam list_produk")

			if "id" not in x:
				return parameter_error("Missing id produk gojek in list_produk")
			if "quantity" not in x:
				return parameter_error("Missing jumlah in list_produk")

			id_produk_gojek  	= x["id"]
			jumlah    			= x["quantity"]
			
			query_temp = "SELECT a.id_produk, a.id_brand, a.nama_produk, a.harga, a.id_produk_gojek, b.id_lokasi FROM pos_produk a LEFT JOIN pos_brand b ON a.id_brand=b.id_brand WHERE a.is_delete!=1 AND a.id_produk_gojek = %s"
			values_temp = (id_produk_gojek,)
			data_temp = dt.get_data(query_temp, values_temp)

			if len(data_temp) == 0:
				return defined_error("Gagal, Terdapat data produk yang tidak ditemukan")

			data_temp = data_temp[0]
			db_id_produk = data_temp["id_produk"]
			db_id_lokasi = data_temp["id_lokasi"]
			db_id_brand = data_temp["id_brand"]
			db_nama_produk = data_temp["nama_produk"]
			db_harga = data_temp["harga"]
			
			if check_id_brand == 0:
				db_id_brand_temp = db_id_brand
				check_id_brand = 1

			#check apakah produknya dari brand yang sama
			if str(db_id_brand_temp) != str(db_id_brand):
				return defined_error("Gagal, Produk yang diinput, tidak dari brand yang sama")

			total_harga += db_harga * jumlah

			json_insert_produk = {
				"id_produk_gojek" : id_produk_gojek,
				"id_produk" : db_id_produk,
				"id_brand" : db_id_brand,
				"nama_produk" : db_nama_produk,
				"jumlah" : jumlah,
				"harga_produk_satuan" : db_harga,
				"harga_produk_total" : db_harga * jumlah
			}
			list_insert_produk.append(json_insert_produk)

		# Generate nomor order
		while True:
			nomor_order = str(now.strftime("%Y%m%d") + random_string_number_only(8))
			# cek apakah nomor_order telah digunakan atau belum
			query_temp = "SELECT a.id_order FROM pos_order a WHERE a.nomor_order = %s"
			values_temp = (nomor_order, )
			data_temp = dt.get_data(query_temp, values_temp)

			if len(data_temp) == 0:
				break

		# Insert ke tabel order
		tipe_pembelian = 1 # online
		query = "INSERT INTO pos_order (id_brand, nomor_order, waktu_order, total_harga, tipe_pembelian) VALUES (%s, %s, %s, %s, %s)"
		values = (db_id_brand, nomor_order, now, total_harga, tipe_pembelian,)
		id_order = dt.insert_data_last_row(query, values)

		# Insert ke tabel order gojek
		query = "INSERT INTO pos_order_gojek (id_order, id_order_gojek_gojek, id_outlet, tipe_order_gojek, order_pin) VALUES (%s, %s, %s, %s, %s)"
		values = (id_order, id_order_gojek, outlet_id, tipe_order_gojek, order_pin,)
		id_order_gojek = dt.insert_data_last_row(query, values)

		# Insert ke tabel order detail
		list_id_order_detail = []
		for x in list_insert_produk:
			query = "INSERT INTO pos_order_detail (id_order, id_produk, nama_produk, jumlah, harga_produk_satuan, harga_produk_total) VALUES (%s, %s, %s, %s, %s, %s)"
			values = (id_order, x["id_produk"], x["nama_produk"], x["jumlah"], x["harga_produk_satuan"], x["harga_produk_total"], )
			id_order_detail = dt.insert_data_last_row(query, values)
			list_id_order_detail.append(id_order_detail)

		hasil = "Berhasil membuat order"
		hasil_data = {
			"id_order" : id_order,
			"total_harga" : total_harga,
			"waktu_order" : now,
			"list_id_order_detail" : list_id_order_detail
		}
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil, 'data' : hasil_data} ), 200)
	except Exception as e:
		return bad_request(str(e))
		
#endregion ================================= GOJEK AREA ==========================================================================


#region ================================= METODE PEMBAYARAN AREA ==========================================================================

@pos.route('/insert_pembayaran_pos', methods=['POST', 'OPTIONS'])
@cross_origin()
@jwt_required()
def insert_pembayaran_pos():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	role = str(get_jwt()["role"])

	if role not in (role_group_super_admin + role_group_admin_lokasi):
		return permission_failed()

	id_admin = str(get_jwt()["id_admin"])
	id_user = id_admin

	try:

		dt = Data()
		data = request.json

		#Perbedaan Super admin dan Admin Lokasi
		if role in role_group_admin_lokasi:
			id_lokasi = str(get_jwt()["id_lokasi"])
		else:
			if "id_lokasi" not in data:
				return parameter_error("Missing id_lokasi in Request Body")
			id_lokasi 				= data["id_lokasi"]
		
		# cek apakah data lokasi ada
		query_temp = "SELECT a.id_lokasi FROM lokasi a WHERE a.is_delete != 1 AND a.id_lokasi = %s"
		values_temp = (id_lokasi, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data lokasi tidak ditemukan")

		if "metode_pembayaran" not in data:
			return parameter_error("Missing metode_pembayaran in Request Body")
		if "foto_pembayaran" not in data:
			return parameter_error("Missing foto_pembayaran in Request Body")
		
		metode_pembayaran = data["metode_pembayaran"]

		if "foto_pembayaran" in data:
			filename_photo = secure_filename(strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_pembayaran.png")
			save(data["foto_pembayaran"], os.path.join(app.config['UPLOAD_FOLDER_FOTO_PEMBAYARAN'], filename_photo))

			foto_pembayaran = filename_photo
		else :
			foto_pembayaran = None

		query = "INSERT INTO pos_metode_pembayaran (id_lokasi, metode_pembayaran, foto_pembayaran) VALUES (%s, %s, %s)"
		values = (id_lokasi, metode_pembayaran, foto_pembayaran,)
		id_metode_pembayaran_pos = dt.insert_data_last_row(query, values)

		hasil = "Berhasil menambahkan metode pembayaran pos"
		hasil_data = {
			"id_metode_pembayaran_pos" : id_metode_pembayaran_pos
		}

		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil, 'data' : hasil_data} ), 200)

	except Exception as e:
		return bad_request(str(e))

@pos.route('/update_pembayaran_pos', methods=['PUT', 'OPTIONS'])
@jwt_required()
@cross_origin()
def update_pembayaran_pos():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	role = str(get_jwt()["role"])

	if role not in (role_group_super_admin + role_group_admin_lokasi):
		return permission_failed()

	id_admin = str(get_jwt()["id_admin"])
	id_user = id_admin

	try:
		dt = Data()
		data = request.json

		if "id_metode_pembayaran_pos" not in data:
			return parameter_error("Missing id_metode_pembayaran_pos in Request Body")

		id_metode_pembayaran_pos = data["id_metode_pembayaran_pos"]

		# Cek apakah data metode pembayaran ada
		query_temp = "SELECT a.id_metode_pembayaran_pos FROM pos_metode_pembayaran a WHERE a.is_delete != 1 AND a.id_metode_pembayaran_pos = %s"
		values_temp = (id_metode_pembayaran_pos, )
		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data Pembayaran POS tidak ditemukan")

		query = """ UPDATE pos_metode_pembayaran SET id_metode_pembayaran_pos=id_metode_pembayaran_pos """
		values = ()
				
		if role in role_group_super_admin and "id_lokasi" in data:
			id_lokasi = data["id_lokasi"]
			query += """ ,id_lokasi = %s """
			values += (id_lokasi, )
		
		if "metode_pembayaran" in data:
			metode_pembayaran = data["metode_pembayaran"]
			query += """ ,metode_pembayaran = %s """
			values += (metode_pembayaran, )

		if "foto_pembayaran" in data:
			filename_photo = secure_filename(strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_pembayaran.png")
			save(data["foto_pembayaran"], os.path.join(app.config['UPLOAD_FOLDER_FOTO_PEMBAYARAN'], filename_photo))

			foto_pembayaran = filename_photo

			query += """ ,foto_pembayaran = %s """
			values += (foto_pembayaran, )

		if "is_delete" in data:
			is_delete = data["is_delete"]
			# validasi data is_delete
			if str(is_delete) not in ["1"]:
				return parameter_error("Invalid is_delete Parameter")
			query += """ ,is_delete = %s """
			values += (is_delete, )

		query += """ WHERE id_metode_pembayaran_pos = %s """
		values += (id_metode_pembayaran_pos, )
		dt.insert_data(query, values)

		hasil = "Berhasil mengubah data metode pembayaran pos"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))

@pos.route('/get_pembayaran_pos', methods=['GET', 'OPTIONS'])
@jwt_required()
@cross_origin()
def get_pembayaran_pos():
	try:
		ROUTE_NAME = str(request.path)

		now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

		role 	= str(get_jwt()["role"])
		if role not in (role_group_super_admin +role_group_admin_lokasi):
			return permission_failed()

		id_admin = str(get_jwt()["id_admin"])
		id_user = id_admin

		dt = Data()
		# parameter khusus (mode)
		mode = request.args.get("mode")
		if (mode == None or mode == ""):
			mode = "1"
		else:
			mode = str(mode)

		if mode == "1": # Normal
			query = """ SELECT a.*
						FROM pos_metode_pembayaran a
						WHERE a.is_delete!=1 """
			values = ()
		else:
			return parameter_error("Invalid mode Parameter")

		
		page = request.args.get("page")
		id_lokasi = request.args.get("id_lokasi")
		search = request.args.get("search")
		order_by = request.args.get("order_by")

		if (page == None):
			page = 1

		if role in role_group_admin_lokasi:
			id_lokasi = str(get_jwt()["id_lokasi"])
		
		if id_lokasi:
			query += " AND a.id_lokasi = %s "
			values += (id_lokasi, )

		if search:
			if role in role_group_super_admin:
				query += """ AND CONCAT_WS("|", a.metode_pembayaran) LIKE %s """
				values += ("%"+search+"%", )
			else:
				query += """ AND CONCAT_WS("|", a.metode_pembayaran) LIKE %s """
				values += ("%"+search+"%", )

		if order_by:
			if order_by == "id_asc":
				query += " ORDER BY a.id_metode_pembayaran_pos ASC "
			elif order_by == "id_desc":
				query += " ORDER BY a.id_metode_pembayaran_pos DESC "

			else:
				query += " ORDER BY a.id_metode_pembayaran_pos DESC "
		else:
			query += " ORDER BY a.id_metode_pembayaran_pos DESC "

		rowCount = dt.row_count(query, values)
		hasil = dt.get_data(query, values)
		hasil = {'data': hasil , 'status_code': 200, 'page': page, 'row_count': rowCount}
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

#endregion ================================= METODE PEMBAYARAN AREA ==========================================================================

#region ================================= CUSTOMER QR CODE AREA ==========================================================================

@pos.route('/insert_customer_qrcode', methods=['POST', 'OPTIONS'])
@jwt_required()
@cross_origin()
def insert_customer_qrcode():
	ROUTE_NAME = str(request.path)
	
	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	role = str(get_jwt()["role"])

	if role not in (role_group_super_admin+role_group_admin_lokasi):
		return permission_failed()

	id_admin = str(get_jwt()["id_admin"])
	id_user = id_admin

	try:
		dt = Data()
		data = request.json

		if "nama" not in data:
			return parameter_error("Missing nama in Request Body")
		if "no_telpon" not in data:
			return parameter_error("Missing no_telpon in Request Body")
		if "email" not in data:
			return parameter_error("Missing email in Request Body")
		if "no_table" not in data:
			return parameter_error("Missing no_table in Request Body")

		nama 		= data['nama']
		no_telpon 	= data['no_telpon']
		email 		= data['email']
		no_table 	= data['no_table']

		if role in role_group_admin_lokasi:
			id_lokasi = str(get_jwt()["id_lokasi"])
		else:
			if "id_lokasi" not in data:
				return parameter_error("Missing id_lokasi in Request Body")
			id_lokasi = data['id_lokasi']
			
		query = "INSERT INTO pos_customer_qrcode (id_lokasi,nama, no_telpon, email, no_table) VALUES (%s, %s, %s, %s, %s)"
		values = (id_lokasi ,nama, no_telpon, email, no_table)
		id_qrcode = dt.insert_data_last_row(query, values)

		##update qr code
		#link yang digenerate berasal dari frontend
		obj_qr = qrcode.QRCode()
		obj_qr.add_data("http://bisa.kitchen/menu/{}".format(id_qrcode))
		obj_qr.make(fit = True)
		qr_img = obj_qr.make_image(fill_color = "black", back_color = "white") 

		# saving the QR code image
		filename_photo = secure_filename(strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_qrsan.png")
		filename_photo_dir = os.path.join(app.config['UPLOAD_FOLDER_FOTO_QRSCAN']) + filename_photo
		qr_img.save(filename_photo_dir)
		
		query = """ UPDATE pos_customer_qrcode SET id_qrcode=id_qrcode, qrcode = %s WHERE id_qrcode = %s"""
		values = (filename_photo, id_qrcode, )
		dt.insert_data(query, values)
		
		hasil = {
			"id_qrcode":id_qrcode,
			"qr_code":filename_photo
		}
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)

		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))


@pos.route('/get_customer_qrcode/<id_qrcode>/', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_customer_qrcode(id_qrcode):
    try:
        ROUTE_NAME = str(request.path)

        now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

        dt = Data()

        query = """ SELECT b.id_lokasi, a.*
                    FROM pos_customer_qrcode a
                    LEFT JOIN lokasi b ON a.id_lokasi=b.id_lokasi
                """
        values = ()

        if id_qrcode:
            query += " WHERE a.id_qrcode = %s "
            values += (id_qrcode, )

        rowCount = dt.row_count(query, values)
        hasil = dt.get_data(query, values)
        hasil = {'data': hasil , 'status_code': 200, 'page': 1, 'offset': 'None', 'row_count': rowCount}
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

@pos.route('/insert_order_customer_qr', methods=['POST', 'OPTIONS'])
@cross_origin()
def insert_order_customer_qr():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	try:
		dt = Data()
		data = request.json

		# Check mandatory data
		if "list_produk" not in data:
			return parameter_error("Missing list_produk in Request Body")
		if "tipe_pembelian" not in data:
			return parameter_error("Missing tipe_pembelian in Request Body")
		if "id_qrcode" not in data:
			return parameter_error("Missing id_qrcode in Request Body")
		if "service_code" not in data:
			return parameter_error("Missing service_code in Request Body")
		
		list_produk 				= data["list_produk"]
		tipe_pembelian 				= data["tipe_pembelian"]
		id_qrcode    				= data["id_qrcode"]
		service_code 				= data["service_code"]
		
		# validasi list order
		if isinstance(list_produk, list) == False:
			return defined_error(description="Format List Order salah", error="Parameter Error", status_code=400, hidden_description="Harap gunakan tipe data array (list) untuk list_produk")

		# cek data produk, perhitungan harga total, dan membuat list insert produk
		total_harga = 0
		list_insert_produk = []
		for x in list_produk:
			if isinstance(x, dict) == False:
				return defined_error(description="Format Produk didalam List Order salah", error="Parameter Error", status_code=400, hidden_description="Harap gunakan format JSON untuk data produk didalam list_produk")
			if "id_produk" not in x:
				return parameter_error("Missing id_produk in list_produk")
			if "jumlah" not in x:
				return parameter_error("Missing jumlah in list_produk")

			id_produk = x["id_produk"]
			jumlah = x["jumlah"]
			
			query_temp = """
							SELECT a.id_produk, a.id_brand, a.nama_produk, a.harga, b.id_lokasi, a.pajak 
							FROM pos_produk a 
							LEFT JOIN pos_brand b ON a.id_brand=b.id_brand 
							WHERE a.is_delete!=1 AND a.id_produk = %s
						"""
			values_temp = (id_produk,)
			data_temp = dt.get_data(query_temp, values_temp)
			print(data_temp)
			if len(data_temp) == 0:
				return defined_error("Gagal, Terdapat data produk yang tidak ditemukan")

			data_temp = data_temp[0]
			db_id_lokasi = data_temp["id_lokasi"]
			db_nama_produk = data_temp["nama_produk"]
			db_harga = data_temp["harga"]
			db_pajak = data_temp["pajak"]

			id_brand = data_temp["id_brand"]
			
			# pengecekan apakah produk yang dibeli berasal dari brand yang sama
			#if str(db_id_lokasi) != str(id_lokasi):
			#	return defined_error("Gagal, Terdapat produk dari lokasi lain. Harap checkout produk dari lokasi yang sama")

			total_harga += db_harga * jumlah * (1 + db_pajak/100)

			json_insert_produk = {
				"id_produk" : id_produk,
				"nama_produk" : db_nama_produk,
				"jumlah" : jumlah,
				"harga_produk_satuan" : db_harga,
				"harga_produk_total" : db_harga * jumlah
			}
			list_insert_produk.append(json_insert_produk)

		# Generate nomor order
		while True:
			nomor_order = str(now.strftime("%Y%m%d") + random_string_number_only(8))
			# cek apakah nomor_order telah digunakan atau belum
			query_temp = "SELECT a.id_order FROM pos_order a WHERE a.nomor_order = %s"
			values_temp = (nomor_order, )
			data_temp = dt.get_data(query_temp, values_temp)

			if len(data_temp) == 0:
				break

		# Insert ke tabel order
		query = "INSERT INTO pos_order (id_brand, nomor_order, waktu_order, total_harga, tipe_pembelian) VALUES (%s, %s, %s, %s, %s)"
		values = (id_brand, nomor_order, now, total_harga, tipe_pembelian,)
		id_order = dt.insert_data_last_row(query, values)

		# Insert ke tabel order detail
		list_id_order_detail = []
		for x in list_insert_produk:
			query = "INSERT INTO pos_order_detail (id_order, id_produk, nama_produk, jumlah, harga_produk_satuan, harga_produk_total) VALUES (%s, %s, %s, %s, %s, %s)"
			values = (id_order, x["id_produk"], x["nama_produk"], x["jumlah"], x["harga_produk_satuan"], x["harga_produk_total"], )
			id_order_detail = dt.insert_data_last_row(query, values)
			list_id_order_detail.append(id_order_detail)

		if str(service_code) == str(9000):
			kode_unik = None
			nomor_invoice = None
			waktu_awal_pembayaran = now
			waktu_akhir_pembayaran = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
			waktu_melakukan_pembayaran = None
			redirect_url = None
			redirect_data = None
			nomor_virtual_account = None

		else:
			if "kode_unik" not in data:
				return parameter_error("Missing kode_unik in Request Body")

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

			total_harga = total_harga + kode_unik

			# Sprint Transaction
			item_details = "[{\"itemName\":\"Pembayaran Makanan Bisa Kitchen\",\"price\":\"%s\",\"quantity\":\"1\",\"itemURL\":\"https:\/\/bisa.kitchen/\/\"}]" % (total_harga)

			#nanti diubah jangan lupa, nunggu table dari yang lain
			query_temp = "SELECT a.id_qrcode, a.email, a.nama, a.no_telpon FROM pos_customer_qrcode a WHERE a.id_qrcode = %s"
			values_temp = (id_qrcode,)
			hasil_data_user = dt.get_data(query_temp, values_temp)

			jsonData = json.dumps({
				"service_code" : service_code,
				"transaction_amount" : total_harga,
				"item_details" : item_details,
				"callback_url" : "https://bisa.kitchen/",
				"customer_name": hasil_data_user[0]["nama"],
				"customer_phone": hasil_data_user[0]["no_telpon"],
				"customer_email": hasil_data_user[0]["email"],
				"deskripsi" : "Pembayaran Produk Bisa Kitchen"
			})
			detail = insert_payment(jsonData)
			if (detail["status_code"] != 200):
				return make_response(jsonify({'status_code':400, 'description': detail } ), 400)
			else:
				detail = detail["data"]

			nomor_invoice = detail['transaction_no']
			waktu_awal_pembayaran = detail['transaction_date']
			waktu_akhir_pembayaran = datetime.datetime.strptime(detail['transaction_expire'], "%Y-%m-%d %H:%M:%S")
			waktu_melakukan_pembayaran = None

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

		# Insert ke tabel pos_order_customer_qr
		query = "INSERT INTO pos_order_customer_qr (id_order, id_qrcode, nomor_invoice, total_harga_pembayaran, kode_unik, waktu_awal_pembayaran, waktu_akhir_pembayaran, waktu_melakukan_pembayaran, service_code, redirect_url, redirect_data, nomor_virtual_account) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
		values = (id_order, id_qrcode, nomor_invoice, total_harga, kode_unik, waktu_awal_pembayaran, waktu_akhir_pembayaran, waktu_melakukan_pembayaran, service_code, redirect_url, redirect_data, nomor_virtual_account,)
		id_order_customer_qr  = dt.insert_data_last_row(query, values)

		response_payload ={
			"nomor_invoice" : nomor_invoice,
			"id_qrcode" : id_qrcode,
			"id_order_customer_qr ": id_order_customer_qr,
			"waktu_awal_pembayaran" : waktu_awal_pembayaran,
			"waktu_akhir_pembayaran" : waktu_akhir_pembayaran,
			"total_harga_pembayaran" : int(total_harga)
		}

		if "detail" in locals():
			if "redirect_data" in detail:
				response_payload["redirect_data"] = detail["redirect_data"]
			if "redirect_url" in detail:
				response_payload["redirect_url"] = detail["redirect_url"]
			if "nomor_virtual_account" in detail:
				response_payload["nomor_virtual_account"] = detail["nomor_virtual_account"]

		hasil = "Order Makanan Bisa Kitchen Via QR Berhasil"

		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)

		return make_response(jsonify({'status_code':200, 'description': hasil, 'data': response_payload} ), 200)
	except Exception as e:
		return bad_request(str(e))

@pos.route('/get_order_waiting_for_paid', methods=['GET', 'OPTIONS'])
@jwt_required()
@cross_origin()
def get_order_waiting_for_paid():
	try:
		ROUTE_NAME = str(request.path)

		role = str(get_jwt()["role"])

		if role not in (role_group_super_admin + role_group_admin_lokasi):
			return permission_failed()

		id_admin = str(get_jwt()["id_admin"])
		id_user = id_admin

		dt = Data()
		hasil_akhir = []
		rowCount = 0
		
		for x in range (2):
			if x:
				query = """ SELECT a.*, b.status_pemesanan, b.total_harga_pembayaran, b.id_order_customer_qr, c.nama, c.no_table, c.id_lokasi
						FROM pos_order a
						LEFT JOIN pos_order_customer_qr b ON a.id_order =b.id_order 
						LEFT JOIN pos_customer_qrcode c ON c.id_qrcode=b.id_qrcode
						WHERE a.is_delete !=1 AND b.status_pemesanan = 1 """
			else:
				query = """ SELECT a.*, b.status_pemesanan, b.total_harga_pembayaran, b.id_order_customer_kiosk, c.id_lokasi
						FROM pos_order a
						LEFT JOIN pos_order_customer_kiosk b ON a.id_order =b.id_order 
						LEFT JOIN pos_brand c ON c.id_brand=a.id_brand
						WHERE a.is_delete !=1 AND b.status_pemesanan = 1 """
			
			values = ()

			page = request.args.get("page")
			id_order = request.args.get("id_order")
			search = request.args.get("search")
			order_by = request.args.get("order_by")

			if role in role_group_admin_lokasi:
				id_lokasi = str(get_jwt()["id_lokasi"])
			else:
				id_lokasi = request.args.get("id_lokasi")

			if (page == None):
				page = 1
			if id_order:
				query += " AND a.id_order = %s "
				values += (id_order, )
			if id_lokasi:
				query += " AND c.id_lokasi = %s "
				values += (id_lokasi, )
			if search:
				query += """ AND CONCAT_WS("|", a.nomor_order) LIKE %s """
				values += ("%"+search+"%", )

			if order_by:
				if order_by == "id_asc":
					query += " ORDER BY a.id_order ASC "
				elif order_by == "id_desc":
					query += " ORDER BY a.id_order DESC "
				else:
					query += " ORDER BY a.id_order DESC "
			else:
				query += " ORDER BY a.id_order DESC "

			rowCount += dt.row_count(query, values)
			hasil = dt.get_data_lim(query, values, page)
			for x in hasil:
				hasil_akhir.append(x)
			'''
			if x:
				for x in hasil:
					x['id_order_customer'] = x.pop('id_order_customer_qr')
					hasil_akhir.append(x)
			else:
				for x in hasil:
					x['id_order_customer'] = x.pop('id_order_customer_kiosk')
					hasil_akhir.append(x)
			'''
		#print(hasil_akhir)
		
		hasil = {'data': hasil_akhir , 'status_code': 200, 'page': page, 'offset': '10', 'row_count': rowCount}
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

@pos.route('/update_order_paid', methods=['PUT', 'OPTIONS'])
@jwt_required()
@cross_origin()
def update_order_paid():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	role = str(get_jwt()["role"])

	if role not in (role_group_super_admin + role_group_admin_lokasi):
		return permission_failed()

	id_admin = str(get_jwt()["id_admin"])
	id_user = id_admin
	dt = Data()
	data = request.json

	if role in role_group_admin_lokasi:
		id_lokasi = str(get_jwt()["id_lokasi"])

	try:
		if "order_type" not in data:
			return parameter_error("Missing order_type in Request Body")

		if "id_order_customer" not in data:
			return parameter_error("Missing id_order_customer in Request Body")
		
		order_type = data["order_type"]
		if order_type:
			if role in role_group_super_admin:
				if "id_lokasi" in data:
					id_lokasi = data["id_lokasi"]
				else:
					return parameter_error("Missing id_lokasi in Request Body")	
		
		id_order_customer = data["id_order_customer"]

		# Cek apakah data order ada
		if order_type:
			query_temp = """SELECT a.id_order_customer_qr, a.status_pemesanan, b.id_lokasi 
						FROM pos_order_customer_qr a 
						LEFT JOIN pos_customer_qrcode b ON a.id_qrcode=b.id_qrcode
						WHERE a.is_delete!=1 AND a.id_order_customer_qr = %s AND b.id_lokasi = %s"""
			values_temp = (id_order_customer, id_lokasi, )
		else: 
			query_temp = """SELECT id_order_customer_kiosk, status_pemesanan
						FROM pos_order_customer_kiosk  
						WHERE is_delete!=1 AND id_order_customer_kiosk = %s"""
			values_temp = (id_order_customer, )

		data_temp = dt.get_data(query_temp, values_temp)
		if len(data_temp) == 0:
			return defined_error("Gagal, Data Order tidak ditemukan")

		data_temp = data_temp[0]

		if order_type:
			query = """ UPDATE pos_order_customer_qr SET id_order_customer_qr=id_order_customer_qr """
		else: 
			query = """ UPDATE pos_order_customer_kiosk SET id_order_customer_kiosk=id_order_customer_kiosk """
			
		values = ()

		if "status_pemesanan" in data:
			status_pemesanan = data["status_pemesanan"]
			# validasi data is_delete
			query += """ ,status_pemesanan = %s """
			values += (status_pemesanan, )
		else:
			return defined_error("Gagal, Status Pemesanan tidak ada")

		if order_type:
			query += """ WHERE id_order_customer_qr = %s """
		else:
			query += """ WHERE id_order_customer_kiosk = %s """

		values += (id_order_customer, )

		dt.insert_data(query, values)

		hasil = "Berhasil mengubah data order"
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil} ), 200)
	except Exception as e:
		return bad_request(str(e))
	

@pos.route('/get_brand_customer_qr', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_brand_customer_qr():
	try:
		ROUTE_NAME = str(request.path)

		now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

		dt = Data()
		# parameter khusus (mode)
		mode = request.args.get("mode")
		if (mode == None or mode == ""):
			mode = "1"
		else:
			mode = str(mode)

		if mode == "1": # Normal
			query = """ SELECT b.id_lokasi, a.*
						FROM pos_brand a
						LEFT JOIN lokasi b ON a.id_lokasi=b.id_lokasi
						WHERE a.is_delete!=1 """
			values = ()
		else:
			return parameter_error("Invalid mode Parameter")

		limit = request.args.get("limit")
		page = request.args.get("page")
		id_lokasi = request.args.get("id_lokasi")
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

		if (page == None):
			page = 1
		
		if id_lokasi:
			query += " AND a.id_lokasi = %s "
			values += (id_lokasi, )

		if search:
			query += """ AND CONCAT_WS("|", a.nama_brand) LIKE %s """
			values += ("%"+search+"%", )

		if order_by:
			if order_by == "id_asc":
				query += " ORDER BY a.id_brand ASC "
			elif order_by == "id_desc":
				query += " ORDER BY a.id_brand DESC "

			else:
				query += " ORDER BY a.id_brand DESC "
		else:
			query += " ORDER BY a.id_brand DESC "

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

@pos.route('/get_produk_customer_qr', methods=['GET', 'OPTIONS'])
@cross_origin() 
def get_produk_customer_qr():
	try:
		ROUTE_NAME = str(request.path)

		dt = Data()

		query = """ SELECT a.*
					FROM pos_produk a
					INNER JOIN pos_brand b
					ON a.id_brand = b.id_brand
					WHERE a.is_delete != 1 """
		values = ()

		page = request.args.get("page")

		search = request.args.get("search")
		order_by = request.args.get("order_by")
		id_brand = request.args.get("id_brand")
		id_lokasi = request.args.get("id_lokasi")

		if (page == None):
			page = 1
		if id_brand:
			query += " AND a.id_brand = %s "
			values += (id_brand, )
		if id_lokasi:
			query += " AND b.id_lokasi = %s "
			values += (id_lokasi, )
		if search:
			query += """ AND CONCAT_WS("|", a.nama_produk) LIKE %s """
			values += ("%"+search+"%", )

		if order_by:
			if order_by == "id_asc":
				query += " ORDER BY a.id_produk ASC "
			elif order_by == "id_desc":
				query += " ORDER BY a.id_produk DESC "

			elif order_by == "nama_asc":
				query += " ORDER BY a.nama_produk ASC "
			elif order_by == "nama_desc":
				query += " ORDER BY a.nama_produk DESC "

			else:
				query += " ORDER BY a.nama_produk ASC "
		else:
			query += " ORDER BY a.nama_produk ASC "

		rowCount = dt.row_count(query, values)
		hasil = dt.get_data(query, values)
		hasil = {'data': hasil , 'status_code': 200, 'page': 1, 'offset': 'None', 'row_count': rowCount}

		# hasil = dt.get_data_lim(query, values, page)
		# hasil = {'data': hasil , 'status_code': 200, 'page': page, 'offset': '10', 'row_count': rowCount}

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





#endregion ================================= CUSTOMER QR CODE AREA ==========================================================================


#region ================================= KIOSK AREA ==========================================================================
@pos.route('/insert_order_kiosk', methods=['POST', 'OPTIONS'])
@cross_origin()
def insert_order_kiosk():
	ROUTE_NAME = str(request.path)

	now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

	try:
		dt = Data()
		data = request.json

		# Check mandatory data
		if "list_produk" not in data:
			return parameter_error("Missing list_produk in Request Body")
		if "tipe_pembelian" not in data:
			return parameter_error("Missing tipe_pembelian in Request Body")
		if "service_code" not in data:
			return parameter_error("Missing service_code in Request Body")
		if "nama" in data:
			nama = data["nama"]
		else:
			nama = "bisa kitchen"
		
		list_produk 				= data["list_produk"]
		tipe_pembelian 				= data["tipe_pembelian"]
		service_code 				= data["service_code"]
		
		# validasi list order
		if isinstance(list_produk, list) == False:
			return defined_error(description="Format List Order salah", error="Parameter Error", status_code=400, hidden_description="Harap gunakan tipe data array (list) untuk list_produk")

		# cek data produk, perhitungan harga total, dan membuat list insert produk
		total_harga = 0
		list_insert_produk = []
		for x in list_produk:
			if isinstance(x, dict) == False:
				return defined_error(description="Format Produk didalam List Order salah", error="Parameter Error", status_code=400, hidden_description="Harap gunakan format JSON untuk data produk didalam list_produk")
			if "id_produk" not in x:
				return parameter_error("Missing id_produk in list_produk")
			if "jumlah" not in x:
				return parameter_error("Missing jumlah in list_produk")

			id_produk = x["id_produk"]
			jumlah = x["jumlah"]
			
			query_temp = """
							SELECT a.id_produk, a.id_brand, a.nama_produk, a.harga, b.id_lokasi, a.pajak 
							FROM pos_produk a 
							LEFT JOIN pos_brand b ON a.id_brand=b.id_brand 
							WHERE a.is_delete!=1 AND a.id_produk = %s
						"""
			values_temp = (id_produk,)
			data_temp = dt.get_data(query_temp, values_temp)
			print(data_temp)
			if len(data_temp) == 0:
				return defined_error("Gagal, Terdapat data produk yang tidak ditemukan")

			data_temp = data_temp[0]
			db_id_lokasi = data_temp["id_lokasi"]
			db_nama_produk = data_temp["nama_produk"]
			db_harga = data_temp["harga"]
			db_pajak = data_temp["pajak"]

			id_brand = data_temp["id_brand"]
			
			# pengecekan apakah produk yang dibeli berasal dari brand yang sama
			#if str(db_id_lokasi) != str(id_lokasi):
			#	return defined_error("Gagal, Terdapat produk dari lokasi lain. Harap checkout produk dari lokasi yang sama")

			total_harga += db_harga * jumlah * (1 + db_pajak/100)

			json_insert_produk = {
				"id_produk" : id_produk,
				"nama_produk" : db_nama_produk,
				"jumlah" : jumlah,
				"harga_produk_satuan" : db_harga,
				"harga_produk_total" : db_harga * jumlah
			}
			list_insert_produk.append(json_insert_produk)

		# Generate nomor order
		while True:
			nomor_order = str(now.strftime("%Y%m%d") + random_string_number_only(8))
			# cek apakah nomor_order telah digunakan atau belum
			query_temp = "SELECT a.id_order FROM pos_order a WHERE a.nomor_order = %s"
			values_temp = (nomor_order, )
			data_temp = dt.get_data(query_temp, values_temp)

			if len(data_temp) == 0:
				break

		# Insert ke tabel order
		query = "INSERT INTO pos_order (id_brand, nomor_order, waktu_order, total_harga, tipe_pembelian) VALUES (%s, %s, %s, %s, %s)"
		values = (id_brand, nomor_order, now, total_harga, tipe_pembelian,)
		id_order = dt.insert_data_last_row(query, values)

		# Insert ke tabel order detail
		list_id_order_detail = []
		for x in list_insert_produk:
			query = "INSERT INTO pos_order_detail (id_order, id_produk, nama_produk, jumlah, harga_produk_satuan, harga_produk_total) VALUES (%s, %s, %s, %s, %s, %s)"
			values = (id_order, x["id_produk"], x["nama_produk"], x["jumlah"], x["harga_produk_satuan"], x["harga_produk_total"], )
			id_order_detail = dt.insert_data_last_row(query, values)
			list_id_order_detail.append(id_order_detail)
		
		if str(service_code) == str(9000):
			kode_unik = None
			nomor_invoice = None
			waktu_awal_pembayaran = now
			waktu_akhir_pembayaran = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
			waktu_melakukan_pembayaran = None
			redirect_url = None
			redirect_data = None
			nomor_virtual_account = None
			filename_photo = None

		else:
			if "kode_unik" not in data:
				return parameter_error("Missing kode_unik in Request Body")

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

			total_harga = total_harga + kode_unik

			# Sprint Transaction
			item_details = "[{\"itemName\":\"Pembayaran Makanan Bisa Kitchen\",\"price\":\"%s\",\"quantity\":\"1\",\"itemURL\":\"https:\/\/bisa.kitchen/\/\"}]" % (total_harga)

			#dummy data
			no_telpon = "081234567890"
			email = "test@gmail.com"

			jsonData = json.dumps({
				"service_code" : service_code,
				"transaction_amount" : total_harga,
				"item_details" : item_details,
				"callback_url" : "https://bisa.kitchen/",
				"customer_name": nama,
				"customer_phone": no_telpon,
				"customer_email": email,
				"deskripsi" : "Pembayaran Produk Bisa Kitchen"
			})
			detail = insert_payment(jsonData)
			if (detail["status_code"] != 200):
				return make_response(jsonify({'status_code':400, 'description': detail } ), 400)
			else:
				detail = detail["data"]

			nomor_invoice = detail['transaction_no']
			waktu_awal_pembayaran = detail['transaction_date']
			waktu_akhir_pembayaran = datetime.datetime.strptime(detail['transaction_expire'], "%Y-%m-%d %H:%M:%S")
			waktu_melakukan_pembayaran = None

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

		# Insert ke tabel pos_order_customer_qr
		query = "INSERT INTO pos_order_customer_kiosk (id_order, nama, nomor_invoice, total_harga_pembayaran, kode_unik, waktu_awal_pembayaran, waktu_akhir_pembayaran, waktu_melakukan_pembayaran, service_code, redirect_url, redirect_data, nomor_virtual_account) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
		values = (id_order, nama, nomor_invoice, total_harga, kode_unik, waktu_awal_pembayaran, waktu_akhir_pembayaran, waktu_melakukan_pembayaran, service_code, redirect_url, redirect_data, nomor_virtual_account,)
		id_order_customer_kiosk  = dt.insert_data_last_row(query, values)

		if redirect_url != None:
			##update qr code
			#link yang digenerate berasal dari frontend
			obj_qr = qrcode.QRCode()
			obj_qr.add_data(redirect_url)
			obj_qr.make(fit = True)
			qr_img = obj_qr.make_image(fill_color = "black", back_color = "white") 

			# saving the QR code image
			filename_photo = secure_filename(strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_qrsan.png")
			filename_photo_dir = os.path.join(app.config['UPLOAD_FOLDER_FOTO_QRSCAN_PEMBAYARAN']) + filename_photo
			qr_img.save(filename_photo_dir)
			
			query = """ UPDATE pos_order_customer_kiosk SET id_order_customer_kiosk=id_order_customer_kiosk, qrcode = %s WHERE id_order_customer_kiosk = %s"""
			values = (filename_photo, id_order_customer_kiosk, )
			dt.insert_data(query, values)

		response_payload ={
			"nomor_invoice" : nomor_invoice,
			"nomor_order":nomor_order,
			"id_order_customer_kiosk ": id_order_customer_kiosk,
			"waktu_awal_pembayaran" : waktu_awal_pembayaran,
			"waktu_akhir_pembayaran" : waktu_akhir_pembayaran,
			"total_harga_pembayaran" : int(total_harga),
			"redirect_data":redirect_data,
			"redirect_url":redirect_url,
			"nomor_virtual_account":nomor_virtual_account,
			"qrcode":filename_photo
		}

		if "detail" in locals():
			if "redirect_data" in detail:
				response_payload["redirect_data"] = detail["redirect_data"]
			if "redirect_url" in detail:
				response_payload["redirect_url"] = detail["redirect_url"]
			if "nomor_virtual_account" in detail:
				response_payload["nomor_virtual_account"] = detail["nomor_virtual_account"]
		
		hasil = "Order Makanan Bisa Kitchen Via QR Berhasil"

		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)

		return make_response(jsonify({'status_code':200, 'description': hasil, 'data': response_payload} ), 200)
	except Exception as e:
		return bad_request(str(e))

#endregion ================================= KIOSK AREA ==========================================================================