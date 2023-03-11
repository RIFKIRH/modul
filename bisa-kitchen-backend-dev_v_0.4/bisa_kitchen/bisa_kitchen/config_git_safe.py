import os

#General
PRODUCT_NAME = "Base Structure"
PRODUCT_ENVIRONMENT = "DEV" # DEV/PROD
PORT = 20000

IS_USE_VENV = "YES" # YES/NO
VENV_FOLDER_PATH = os.path.abspath(os.path.join(__file__,"../../../venv_app_name")) +"/" # Just Change value after __file__,

#JWT
JWT_SECRET_KEY = "JWT_SECRET_KEY"
JWT_HEADER_TYPE = "JWT"

#Database
DB_NAME     = ""
DB_USER     = ""
DB_PASSWORD = ""
DB_HOST     = "localhost"

#URL
BACKEND_BASE_URL = "http://localhost:20000/base_struckture_python_flask/"

#EMAIL SERVICE
BISAAI_MAIL_SERVER  = ""
BISAAI_MAIL_SENDER  = ""
BISAAI_MAIL_API_KEY = ""

#BISAAIPAYMENT
BISAAIPAYMENT_BASE_URL  = ""
BISAAIPAYMENT_KEY       = ""

#Folder Path
# 2 variabel dibawah merupakan default logs dan upload (didalam direktori projek)
# 2 variabel dibawah jangan dihapus, jika tidak ingin menggunakan default
# cukup comment 2 variabel dibawah dan buat 2 variabel baru dengan nama yang sama
UPLOAD_FOLDER_PATH  = os.path.abspath(os.path.join(__file__,"../../../upload")) +"/"
LOGS_FOLDER_PATH    = os.path.abspath(os.path.join(__file__,"../../..Testin1/logs"))

#CRONTAB
CRON_FOLDER_PATH            = os.path.abspath(os.path.join(__file__,"../../../crontab")) +"/"
CRON_TEMPLATE_PATH          = os.path.abspath(os.path.join(__file__,"../../../crontab/templates")) +"/"
CRON_ERROR_LOG_FOLDER_PATH  = os.path.abspath(os.path.join(__file__,"../../../crontab/crontab_error_logs")) +"/"
