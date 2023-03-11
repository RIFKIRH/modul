import os
config_path = os.path.abspath(os.path.join(__file__,"../.."))

import sys
sys.path.append(config_path)

import config as CFG
import requests
import datetime
import mysql.connector
import json
from jinja2 import Template
import random
import json

mydb = mysql.connector.connect(
    host = CFG.DB_HOST,
    user = CFG.DB_USER,
    passwd = CFG.DB_PASSWORD,
    database = CFG.DB_NAME
)
cursor = mydb.cursor()

CRON_ERROR_LOG_FOLDER_PATH = CFG.CRON_ERROR_LOG_FOLDER_PATH

BISAAIPAYMENT_BASE_URL 	= CFG.BISAAIPAYMENT_BASE_URL
BISAAIPAYMENT_KEY 		= CFG.BISAAIPAYMENT_KEY

def tambahLogsErrorCrontab(logs):
	# Create directory if not exists
	if os.path.exists(CRON_ERROR_LOG_FOLDER_PATH) == False:
		os.makedirs(CRON_ERROR_LOG_FOLDER_PATH)

	# Write Logss
	f = open(CRON_ERROR_LOG_FOLDER_PATH + "ERROR_" + datetime.datetime.now().strftime("%Y-%m-%d")+ ".txt", "a")
	f.write(logs)
	f.close()

def cek_pembayaran_customer_dapur():
	FUNCTION_NAME = "cek_pembayaran_customer_dapur"
	try:
		query = """ SELECT a.id_customer_dapur, a.nomor_invoice, a.total_harga_pembayaran, b.nama_harga, c.nama_dapur, d.email
					FROM dpr_customer_dapur a
					LEFT JOIN dpr_harga b ON a.id_dpr_harga=b.id_dpr_harga
					LEFT JOIN dpr_dapur c ON b.id_dapur=c.id_dapur
					LEFT JOIN customer d ON a.id_customer=d.id_customer
					WHERE a.is_delete!=1 AND a.status_pemesanan = 1 AND a.service_code IS NOT NULL """
		values = ()

		cursor.execute(query, values)
		result = cursor.fetchall()

		for x in result:
			now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

			# id_transaksi				= x[0]
			id_customer_dapur		 	= x[0]
			nomor_invoice				= x[1]
			total_transaksi				= x[2]
			name_produk					= str(x[4]) + str(x[3])
			email 						= x[5]


			print (FUNCTION_NAME, id_customer_dapur, nomor_invoice, total_transaksi)

			url = BISAAIPAYMENT_BASE_URL+"/transaksi/get_transaksi_status?transaction_no=%s&payment_status=00" % (nomor_invoice)
			payload = {}
			headers = {
				'X-API-KEY': BISAAIPAYMENT_KEY
			}

			response = requests.request("GET", url, headers=headers, data = payload)
			status_code = response.status_code

			if str(status_code) == '200':
				qq 				= "UPDATE dpr_customer_dapur a SET a.waktu_melakukan_pembayaran = %s, a.status_pemesanan=2, a.is_delete=0 WHERE a.id_customer_dapur = %s"
				vv 				= (now, id_customer_dapur)
				cursor.execute(qq,vv)
				mydb.commit()
	except Exception as e:
		logs_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		logs = logs_timestamp + "-- "+FUNCTION_NAME+" -- Error : " + str(e)
		tambahLogsErrorCrontab(logs)


def cek_expired_customer_dapur():
	FUNCTION_NAME = "cek_expired_customer_dapur"
	# Untuk cek apakah transaksi sudah expired atau belum beradasarkan field waktu_akhir_pembayaran
	try:
		now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

		query = "SELECT a.id_customer_dapur FROM dpr_customer_dapur a WHERE %s > a.waktu_akhir_pembayaran AND a.status_pemesanan = 1"
		values = (now, )

		cursor.execute(query,values)
		result = cursor.fetchall()

		for x in result:
			id_customer_dapur = x[0]
			print (FUNCTION_NAME, id_customer_dapur)

			qq = "UPDATE dpr_customer_dapur SET status_pemesanan=4 WHERE id_customer_dapur = %s"
			vv = (id_customer_dapur, )
			cursor.execute(qq,vv)
			mydb.commit()
	except Exception as e:
		logs_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		logs = logs_timestamp + " -- "+FUNCTION_NAME+" -- Error : " + str(e)
		tambahLogsErrorCrontab(logs)


def cek_pembayaran_customer_qr():
	FUNCTION_NAME = "cek_pembayaran_customer_qr"
	try:
		query = """ SELECT a.id_order_customer_qr, a.nomor_invoice, a.total_harga_pembayaran
					FROM pos_order_customer_qr a
					WHERE a.is_delete!=1 AND a.status_pemesanan = 1 AND a.service_code IS NOT NULL AND a.service_code != 9000"""
		values = ()

		cursor.execute(query, values)
		result = cursor.fetchall()

		for x in result:
			now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

			# id_transaksi				= x[0]
			id_order_customer_qr		= x[0]
			nomor_invoice				= x[1]
			total_transaksi				= x[2]


			print (FUNCTION_NAME, id_order_customer_qr, nomor_invoice, total_transaksi)

			url = BISAAIPAYMENT_BASE_URL+"/transaksi/get_transaksi_status?transaction_no=%s&payment_status=00" % (nomor_invoice)
			payload = {}
			headers = {
				'X-API-KEY': BISAAIPAYMENT_KEY
			}

			response = requests.request("GET", url, headers=headers, data = payload)
			status_code = response.status_code

			if str(status_code) == '200':
				qq 				= "UPDATE pos_order_customer_qr a SET a.waktu_melakukan_pembayaran = %s, a.status_pemesanan=2, a.is_delete=0 WHERE a.id_order_customer_qr = %s"
				vv 				= (now, id_order_customer_qr)
				cursor.execute(qq,vv)
				mydb.commit()
	except Exception as e:
		logs_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		logs = logs_timestamp + "-- "+FUNCTION_NAME+" -- Error : " + str(e)
		tambahLogsErrorCrontab(logs)

def cek_expired_customer_qr():
	FUNCTION_NAME = "cek_expired_customer_qr"
	# Untuk cek apakah transaksi sudah expired atau belum beradasarkan field waktu_akhir_pembayaran
	try:
		now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

		query = "SELECT a.id_order_customer_qr FROM pos_order_customer_qr a WHERE %s > a.waktu_akhir_pembayaran AND a.status_pemesanan = 1"
		values = (now, )

		cursor.execute(query,values)
		result = cursor.fetchall()

		for x in result:
			id_order_customer_qr = x[0]
			print (FUNCTION_NAME, id_order_customer_qr)

			qq = "UPDATE pos_order_customer_qr SET status_pemesanan=3 WHERE id_order_customer_qr = %s"
			vv = (id_order_customer_qr, )
			cursor.execute(qq,vv)
			mydb.commit()
	except Exception as e:
		logs_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		logs = logs_timestamp + " -- "+FUNCTION_NAME+" -- Error : " + str(e)
		tambahLogsErrorCrontab(logs)

def cek_pembayaran_customer_kiosk():
	FUNCTION_NAME = "cek_pembayaran_customer_kiosk"
	try:
		query = """ SELECT a.id_order_customer_kiosk, a.nomor_invoice, a.total_harga_pembayaran
					FROM pos_order_customer_kiosk a
					WHERE a.is_delete!=1 AND a.status_pemesanan = 1 AND a.service_code IS NOT NULL AND a.service_code != 9000"""
		values = ()

		cursor.execute(query, values)
		result = cursor.fetchall()

		for x in result:
			now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

			# id_transaksi				= x[0]
			id_order_customer_kiosk		= x[0]
			nomor_invoice				= x[1]
			total_transaksi				= x[2]


			print (FUNCTION_NAME, id_order_customer_kiosk, nomor_invoice, total_transaksi)

			url = BISAAIPAYMENT_BASE_URL+"/transaksi/get_transaksi_status?transaction_no=%s&payment_status=00" % (nomor_invoice)
			payload = {}
			headers = {
				'X-API-KEY': BISAAIPAYMENT_KEY
			}

			response = requests.request("GET", url, headers=headers, data = payload)
			status_code = response.status_code

			if str(status_code) == '200':
				qq 				= "UPDATE pos_order_customer_kiosk a SET a.waktu_melakukan_pembayaran = %s, a.status_pemesanan=2, a.is_delete=0 WHERE a.id_order_customer_kiosk = %s"
				vv 				= (now, id_order_customer_kiosk)
				cursor.execute(qq,vv)
				mydb.commit()
	except Exception as e:
		logs_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		logs = logs_timestamp + "-- "+FUNCTION_NAME+" -- Error : " + str(e)
		tambahLogsErrorCrontab(logs)


def cek_expired_customer_kiosk():
	FUNCTION_NAME = "cek_expired_customer_kiosk"
	# Untuk cek apakah transaksi sudah expired atau belum beradasarkan field waktu_akhir_pembayaran
	try:
		now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

		query = "SELECT a.id_order_customer_kiosk FROM pos_order_customer_kiosk a WHERE %s > a.waktu_akhir_pembayaran AND a.status_pemesanan = 1"
		values = (now, )

		cursor.execute(query,values)
		result = cursor.fetchall()

		for x in result:
			id_order_customer_kiosk = x[0]
			print (FUNCTION_NAME, id_order_customer_kiosk)

			qq = "UPDATE pos_order_customer_kiosk SET status_pemesanan=3 WHERE id_order_customer_kiosk = %s"
			vv = (id_order_customer_kiosk, )
			cursor.execute(qq,vv)
			mydb.commit()
	except Exception as e:
		logs_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		logs = logs_timestamp + " -- "+FUNCTION_NAME+" -- Error : " + str(e)
		tambahLogsErrorCrontab(logs)


# >>>>>>>>>>>>>>>>> FUNCTION CALLER <<<<<<<<<<<<<<<<<<<<<
cek_pembayaran_customer_dapur()
cek_expired_customer_dapur()
cek_pembayaran_customer_qr()
cek_expired_customer_qr()
cek_pembayaran_customer_kiosk()
cek_expired_customer_kiosk()