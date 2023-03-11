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

brosur = Blueprint('brosur', __name__, static_folder = '../../upload/brosur', static_url_path="/media")

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

#region ================================= BROSUR ==========================================================================
@brosur.route("/insert_form_brosur", methods=["POST", "OPTIONS"])
@cross_origin()
def insert_form_brosur():
	ROUTE_NAME = str(request.path)
	
	try:
		dt = Data()
		data = request.json

		# Check mandatory data
		if "nama_customer_brosur" not in data:
			return parameter_error("Missing name in Request Body")
		if "email_customer_brosur" not in data:
			return parameter_error("Missing email in Request Body")
		if "no_customer_brosur" not in data:
			return parameter_error("Missing no in Request Body")

		nama_customer_brosur 			= data["nama_customer_brosur"]
		email_customer_brosur 			= data["email_customer_brosur"]
		no_customer_brosur	 			= data["no_customer_brosur"]

		query = "INSERT INTO customer_brosur (nama_customer_brosur, email_customer_brosur, no_customer_brosur) VALUES (%s,%s,%s);"
		values = (nama_customer_brosur, email_customer_brosur, no_customer_brosur,)
		id_customer_brosur = dt.insert_data_last_row(query, values)

		hasil = "Berhasil menambahkan data brosur"
		hasil_data = {
			"id_customer_brosur" : id_customer_brosur,
			"nama_customer_brosur":nama_customer_brosur,
			"email_customer_brosur":email_customer_brosur,
			"no_customer_brosur":no_customer_brosur
		}
		try:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = "+str(id_user)+" - roles = "+str(role)+"\n"
		except Exception as e:
			logs = secure_filename(strftime("%Y-%m-%d %H:%M:%S"))+" - "+ROUTE_NAME+" - id_user = NULL - roles = NULL\n"
		tambahLogs(logs)

		return make_response(jsonify({'status_code':200, 'description': hasil, 'data' : hasil_data} ), 200)
	except Exception as e:
		return bad_request(str(e))

#endregion ================================= BROSUR ==========================================================================