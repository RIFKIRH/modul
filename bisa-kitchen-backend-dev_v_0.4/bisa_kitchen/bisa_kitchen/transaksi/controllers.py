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

transaksi = Blueprint('transaksi', __name__, static_folder = '../../upload/transaksi', static_url_path="/media")

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


#region ================================= DAPUR AREA ==========================================================================

@transaksi.route('/get_metode_pembayaran', methods=['GET', 'OPTIONS'])
@jwt_required()
@cross_origin()
def get_metode_pembayaran():
	try:
		ROUTE_NAME = str(request.path)

		role = str(get_jwt()["role"])

		if role in role_group_super_admin:
			id_admin = str(get_jwt()["id_admin"])
			id_user = id_admin
		if role in role_group_customer:
			id_customer = str(get_jwt()["id_customer"])
			id_user = id_customer

		dt = Data()

		query = """ SELECT a.*
					FROM metode_pembayaran a
					WHERE a.is_delete!=1 """
		values = ()

		id_metode_pembayaran = request.args.get("id_metode_pembayaran")
		service_code = request.args.get("service_code")
		search = request.args.get("search")
		order_by = request.args.get("order_by")

		if id_metode_pembayaran:
			query += " AND a.id_metode_pembayaran = %s "
			values += (id_metode_pembayaran, )
		if service_code:
			query += " AND a.service_code = %s "
			values += (service_code, )
		if search:
			query += """ AND CONCAT_WS("|", a.nama_metode_pembayaran) LIKE %s """
			values += ("%"+search+"%", )

		if order_by:
			if order_by == "nama_asc":
				query += " ORDER BY a.nama_metode_pembayaran ASC "
			elif order_by == "nama_desc":
				query += " ORDER BY a.nama_metode_pembayaran DESC "
			else:
				query += " ORDER BY a.nama_metode_pembayaran ASC "
		else:
			query += " ORDER BY a.nama_metode_pembayaran ASC "

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

@transaksi.route('/insert_metode_pembayaran', methods=['POST', 'OPTIONS'])
@jwt_required()
@cross_origin()
def insert_metode_pembayaran():
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
		if "nama_metode_pembayaran" not in data:
			return parameter_error("Missing nama_metode_pembayaran in Request Body")
		if "service_code" not in data:
			return parameter_error("Missing service_code in Request Body")

		nama_metode_pembayaran 			= data["nama_metode_pembayaran"]
		service_code 					= data["service_code"]

		# Cek data opsional

		if "deskripsi_metode_pembayaran" in data:
			deskripsi_metode_pembayaran = data["deskripsi_metode_pembayaran"]
		else:
			deskripsi_metode_pembayaran = None

		if "logo_metode_pembayaran" in data:
			filename_photo = secure_filename(strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_logo_metode_pembayaran.png")
			save(data["logo_metode_pembayaran"], os.path.join(app.config['UPLOAD_FOLDER_LOGO_METODE_PEMBAYARAN'], filename_photo))

			logo_metode_pembayaran = filename_photo
		else:
			logo_metode_pembayaran = None

		# Insert ke tabel db
		query = "INSERT INTO metode_pembayaran (nama_metode_pembayaran, deskripsi_metode_pembayaran, service_code, logo_metode_pembayaran) VALUES (%s, %s, %s, %s)"
		values = (nama_metode_pembayaran, deskripsi_metode_pembayaran, service_code, logo_metode_pembayaran)
		id_metode_pembayaran = dt.insert_data_last_row(query, values)

		hasil = "Berhasil menambahkan metode pembayaran"
		hasil_data = {
			"id_metode_pembayaran" : id_metode_pembayaran
		}
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)
		return make_response(jsonify({'status_code':200, 'description': hasil, 'data' : hasil_data} ), 200)
	except Exception as e:
		return bad_request(str(e))

#endregion ================================= DAPUR AREA ==========================================================================

#region ================================= POS AREA ==========================================================================

@transaksi.route('/get_metode_pembayaran_qr_kiosk', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_metode_pembayaran_qr_kiosk():
	try:
		ROUTE_NAME = str(request.path)

		dt = Data()

		query = """ SELECT a.*
					FROM metode_pembayaran a
					WHERE a.is_delete!=1 """
		values = ()

		id_metode_pembayaran = request.args.get("id_metode_pembayaran")
		service_code = request.args.get("service_code")
		search = request.args.get("search")
		order_by = request.args.get("order_by")

		if id_metode_pembayaran:
			query += " AND a.id_metode_pembayaran = %s "
			values += (id_metode_pembayaran, )
		if service_code:
			query += " AND a.service_code = %s "
			values += (service_code, )
		if search:
			query += """ AND CONCAT_WS("|", a.nama_metode_pembayaran) LIKE %s """
			values += ("%"+search+"%", )

		if order_by:
			if order_by == "nama_asc":
				query += " ORDER BY a.nama_metode_pembayaran ASC "
			elif order_by == "nama_desc":
				query += " ORDER BY a.nama_metode_pembayaran DESC "
			else:
				query += " ORDER BY a.nama_metode_pembayaran ASC "
		else:
			query += " ORDER BY a.nama_metode_pembayaran ASC "

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

#endregion ================================= POS AREA ==========================================================================
