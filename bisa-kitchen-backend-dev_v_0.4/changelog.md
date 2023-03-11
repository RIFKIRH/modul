### Changelog `BISA KITCHEN`
<b>Bisa Kitchen Backend Full Changelog</b>


---
#### v 0.4.2 -- 2022/12/20 -- Bagja
###### Change:
* API :
    * API pos/get_order_waiting_for_paid
        * menambahkan parameter kiosk

#### v 0.4.2 -- 2022/12/15 -- Ahmad
###### New:
* API :
    * Add API pos/insert_order_kiosk
    * Add API transaksi/get_metode_pembayaran_qr_kiosk

* Database :
    * add new table pos_order_customer_kiosk

* Crontab :
    * add new function cek_pembayaran_customer_kiosk()
    * add new function cek_expired_customer_kiosk()

* Config di init
    * add app.config['UPLOAD_FOLDER_FOTO_QRSCAN_PEMBAYARAN'] = UPLOAD_FOLDER_PATH+"pos/foto_qrscan_pembayaran/"
    * add app.config['UPLOAD_FOLDER_FOTO_QRSCAN_PEMBAYARAN'], di list folder create

###### Change:
* API :
    * API pos/get_order_for_display_complete
        * Logiz agar menu yang belum dibayar tidak muncul di kds (menu dari kiosk)
    * API pos/insert_produk dan pos/update_produk
        * Menambahkan parameter pajak
    * API pos/insert_order pos/insert_order_customer_qr
        * Menambahkan perhitungan untuk pajak

* Database :
    * Add new field in pos_produk 'pajak'
    * Add new field in metode_pembayaran 'kategori'

#### v 0.4.2 -- 2022/12/15 -- Masayu
###### Change:
* API :
    * API pos/update_order_paid
    
---

#### v 0.4.1 -- 2022/12/04 -- Masayu
###### Change:
* API :
    * API pos/insert_customer_qrcode
    * API pos/get_customer_qrcode/<id_qrcode>
        * Menghilangkan JWT Required untuk customer

* DATABASE 
    * add new table pos_customer_qrcode

#### v 0.4.1 -- 2022/12/04 
###### Change:
* API :
    * API pos/update_order
        * Menambahkan TRY pada logic didalam if "status_order", sebagai respon ke gobiz

#### v 0.4.1 -- 2022/12/04 -- Bagja
###### New:
* API :
    * Add API pos/get_produk_customer_qr
    * Add API pos/get_meja

* Library :
    * import qrcode
    
###### Change:
* Init:
    * Penambahan directory untuk qr code 

#### v 0.4.1 -- 2022/12/04 -- Ahmad
###### New:
* API :
    * Add API pos/get_produk_customer_qr
    * Add API pos/get_brand_customer_qr
    * Add API pos/update_order_paid
    * Add API pos/get_order_waiting_for_paid
    * Add API pos/insert_order_customer_qr

* Database :
    * add new table pos_order_customer_qr

* Crontab :
    * add new function cek_pembayaran_customer_qr()
    * add new function cek_expired_customer_qr()

###### Change:
* API :
    * API pos/get_order_for_display_complete
        * Logiz agar menu yang belum dibayar tidak muncul di kds

---
#### v 0.4.0 -- 2022/11/29 -- All
###### New:
* API :
    * Add API pos/insert_order_gojek
    * Add API pos/delete_display
    * Add API pos/delete_display_brand
    * Add API pos/accept_order_gojek (BELOM READY, KARENA DARI GOBIZ, TIDAK BISA DITESTING)
    * Add API pos/insert_pembayaran_pos
    * Add API pos/update_pembayaran_pos
    * Add API pos/get_pembayaran_pos

* DATABASE 
    * add new table pos_order_gojek
    * add new table pos_order_gojek
    * add new table pos_metode_pembayaran

* Config di init
    * add app.config['UPLOAD_FOLDER_FOTO_PEMBAYARAN'] = UPLOAD_FOLDER_PATH+"pos/foto_pembayaran/"
    * add app.config['UPLOAD_FOLDER_FOTO_PEMBAYARAN'], di list folder create

###### Change:
* API :
    * API pos/update_order
        * Menambahkan logic didalam if "status_order", sebagai respon ke gobiz
    * API pos/insert_order
        * Menambahkan parameter id_metode_pembayaran_pos
    * API pos/get_order
        * Menambahkan parameter dari tabel pos_metode_pembayaran

* DATABASE 
    * add new field di pos_produk (id_produk_gojek)
    * add new field di pos_brand (client_id dan client_secret)
    * add new field di pos_order (id_metode_pembayaran_pos)

* JWT
    * JWT expired 30 hari


---
#### v 0.3.2 -- 2022/11/08 -- All
###### New:
* API :
    * Menambahkan CRU Untuk Admin lokasi, Create Admin Lokasi(Permission menggunakan Super Admin), get_profile admin lokasi, Update nama_admin_lokasi
    * Add API pos/delete_produk
    * Add API pos/delete_brand
    * Add API user/change_password/<token>
    * Add API pos/update_dispplay_brand

* Library:
    * Bleprint user (import jwt)

* Variabel
    * Perbaruan list role pada blueprint user dan dapur 

###### Change:
* API :
    * API user/reset_password
        * Mengganti keseluruhan dari API sebelumnya (sebelumnya masih template)
* Templates :
    * reset_password.html
        * Penyesuaian dengan flow yang baru 



#### v 0.3.2 -- 2022/11/7 -- Bagja Lazwardi
###### New:
*API :
    * Menambahkan CRU Untuk Admin lokasi, Create Admin Lokasi(Permission menggunakan Super Admin), get_profile admin lokasi, Update nama_admin_lokasi

#### v 0.3.2 -- 2022/11/07 -- Ahmad
###### New:
* API :
    * Add API pos/delete_produk
    * Add API pos/delete_brand
    * Add API user/change_password/<token>

* Library:
    * Bleprint user (import jwt)

###### Change:
* API :
    * API user/reset_password
        * Mengganti keseluruhan dari API sebelumnya (sebelumnya masih template)
* Templates :
    * reset_password.html
        * Penyesuaian dengan flow yang baru 


#### v 0.3.2 -- 2022/11/07 -- Masayu
* API :
    * Add API pos/update_dispplay_brand

#### v 0.3.1 -- 2022/10/25 -- All
###### New:
* Add Blueprint daerah :
    * Add API daerah/insert_provinsi
    * Add API daerah/update_provinsi
    * Add API daerah/get_provinsi
    * Add API daerah/insert_kota
    * Add API daerah/update_brand
    * Add API daerah/get_brand

###### Change:
* API :
    * Hapus get kota dan provinsi di blueprint lokasi
    * Menambahkan Permision untuk Admin_lokasi di bagian CRU(Create, read, update) Pos Brand
* Change validasi role in API CRU Produk

#### v 0.3.1 -- 2022/10/28 -- Ahmad
###### New:
* Add Blueprint daerah :
    * Add API daerah/insert_provinsi
    * Add API daerah/update_provinsi
    * Add API daerah/get_provinsi
    * Add API daerah/insert_kota
    * Add API daerah/update_brand
    * Add API daerah/get_brand

###### Change:
* API :
    * Hapus get kota dan provinsi di blueprint lokasi

### v 0.3.1 -- 2022/10/29 -- Masayu
* Change validasi role in API CRU Produk


#### v 0.3.1 -- 2022/10/25 -- Bagja Lazwardi
*API :
    * Menambahkan Permision untuk Admin_lokasi di bagian CRU(Create, read, update) Pos Brand

---

### v 0.2

#### v 0.2.2 -- 2022/10/25 -- All
###### New:
* API :
    * Add API login_admin_brand
    * Add API pos/insert_order
    * Add API pos/get_order
    * Add API pos/get_display
    * Add API pos/insert_display
    * Add API pos/update_display
    * Add API pos/get_order_detail
    * Add API pos/get_order_for_display
    * Add API pos/get_order_for_display_complete
    * Add API pos/get_display_brand
    * Add API pos/insert_display_brand

###### Change:
* API :
    * Change API login_admin_lokasi:
        * Menambahkan field id_lokasi pada query
        * Menambahkan Join table dan field nama_lokasi pada query
        * Menambahkan data id_lokasi kedalam token JWT
        * Menambahkan data nama_lokasi kedalam token JWT

    * Change API pos/get_produk :
        * Menambahkan decorator jwt required
        * Menambahkan pengambilan role dari JWT
        * Menambahkan parameter id_brand dan pengecekan role : jika admin brand maka otomatis menggunakan parameter id_brand
        * Menambahkan value nama_asc dan nama_desc pada parameter order_by
        * Mengubah default parameter order_by

    * Change API pos/insert_produk :
        * Mengganti role yang dapat akses API ini
        * Menghapus penerimaan data id_brand (id_brand mengikuti yang disimpan dalam JWT)

    * Change API pos/update_produk :
        * Mengubah validasi role
        * Menambahkan penerimaan data harga

* Lainnya :
    * Change pos/controllers.py :
        * Add from markupsafe import Markup
        * Add global variabel role_group_admin_brand
        * Change global variabel role_group_all : menambahkan role admin brand

    * Change init.py (app):
        * Add app config UPLOAD_FOLDER_FOTO_PRODUK

###### DATABASE :
* ADD TABLE admin_brand
* ALTER TABLE `admin_lokasi` ADD `id_lokasi` INT NOT NULL AFTER `id_admin_lokasi`;
* ALTER TABLE `admin_lokasi` ADD FOREIGN KEY (`id_lokasi`) REFERENCES `lokasi`(`id_lokasi`) ON DELETE RESTRICT ON UPDATE RESTRICT;
* ALTER TABLE `pos_order` ADD `id_brand` INT NOT NULL AFTER `id_order`;
* ALTER TABLE `pos_order` ADD FOREIGN KEY (`id_brand`) REFERENCES `pos_brand`(`id_brand`) ON DELETE RESTRICT ON UPDATE RESTRICT;
* ALTER TABLE `pos_order_detail` ADD `nama_produk` VARCHAR(255) NOT NULL AFTER `jumlah`;
* ALTER TABLE `pos_display` ADD `id_lokasi` INT NOT NULL AFTER `id_display`;
* ALTER TABLE `pos_display` ADD FOREIGN KEY (`id_lokasi`) REFERENCES `lokasi`(`id_lokasi`) ON DELETE RESTRICT ON UPDATE RESTRICT;
* ALTER TABLE `pos_display_brand` ADD FOREIGN KEY (`id_display`) REFERENCES `pos_display`(`id_display`) ON DELETE RESTRICT ON UPDATE RESTRICT;
* ALTER TABLE `pos_display_brand` ADD FOREIGN KEY (`id_brand`) REFERENCES `pos_brand`(`id_brand`) ON DELETE RESTRICT ON UPDATE RESTRICT;
* ADD INDEX composite_display_brand di TABLE pos_display_brand

#### v 0.2.1 -- 2022/10/24 -- Raihan
###### New:
* Crontab :
    * Add crontab update_transaksi.py (pengecekan transaksi customer dapur)

###### DATABASE :
* Add TABLE pos_brand
* Add TABLE pos_display
* Add TABLE pos_display_brand
* Add TABLE pos_order
* Add TABLE pos_order_detail
* Add TABLE pos_produk

#### v 0.2.1 -- 2022/10/23 -- Masayu
###### New:

* Merge Blueprint :
    * Merge Utensil & Utensil Kategori

* API :
    * Add API dapur/upload_bukti_transaksi/<id_customer_dapur>
    * Add API pos/get_produk
    * Add API pos/insert_produk
    * Add API pos/update_produk

#### v 0.2.1 -- 2022/10/24 -- Ahmad
###### New:
* Add Blueprint brosur :
    * Add API brosur/insert_form_brosur

* Add Blueprint pos :
    * Add API pos/insert_brand
    * Add API pos/update_brand
    * Add API pos/get_brand

* API :
    * Add API dapur/get_riwayat_transaksi
    * Add API /login_admin_lokasi

###### Change:
* Lainnya :
    * Change init.py (Runner) :
        * Delete API form_brosur

###### Database :
* Mengganti tipe data pada table customer_brosur field no_customer_brosur menjadi varchar


---

### v 0.1

#### v 0.1.1 -- 2022/10/21 -- Raihan
###### New:
* Add Blueprint dapur :
    * Add API dapur/get_dapur
    * Add API dapur/insert_dapur
    * Add API dapur/update_dapur
    * Add API dapur/get_harga_dapur
    * Add API dapur/insert_harga_dapur
    * Add API dapur/get_dapur_galeri
    * Add API dapur/insert_dapur_galeri
    * Add API dapur/get_customer_dapur
    * Add API dapur/insert_customer_dapur

* Add Blueprint transaksi :
    * Add API transaksi/get_metode_pembayaran
    * Add API transaksi/insert_metode_pembayaran

* API :
    * Add API lokasi/get_lokasi_kitchen
    * Add API lokasi/insert_lokasi_kitchen
    * Add API lokasi/update_lokasi_kitchen
    * Add API lokasi/get_lokasi_galeri
    * Add API lokasi/insert_lokasi_galeri

###### Change:
* API :
    * Change API /: Mengganti respon menjadi Home Backend Bisa Kitchen
    * Change API user/insert_customer :
        * Menghapus penerimaan data nama_brand
        * Mengubah query, menyesuaikan dengan struktur table yang sudah diubah
        * Mengubah kode cek data opsional
        * Mengubah pengambilan waktu pada variabel now
    * Change API utnsl_utensil/get_utnsl_utensil :
        * Menghapus kode penerimaan parameter yang tidak digunakan
        * Menambahkan alias pada query
        * Menambahkan parameter id_utensil
    * Change API utnsl_utensil/insert_utnsl_utensil :
        * Mengganti nama table db ketika pengecekan data lokasi
    * Change API utnsl_utensil/update_utnsl_utensil :
        * Mengganti nama table db ketika pengecekan data lokasi
        * Add update foto_utensil_1, foto_utensil_2, dan foto_utensil_3

* Lainnya :
    * Change config_git_safe.py : Add config untuk PORT
    * Change init.py (Runner) :
        * Add import config as CFG
        * Mengubah port, sekarang mengikuti port yang disimpan dalam config
    * Change init.pt (app) :
        * Menghapus app config UPLOAD_FOLDER_FOTO_TEMPAT_UJI_KOMPETENSI
        * Add app config UPLOAD_FOLDER_FOTO_LOKASI_KITCHEN
        * Import dan Register Blueprint dapur
        * Add app config UPLOAD_FOLDER_FOTO_DAPUR
        * Add app config BISAAI_MAIL_SERVER
        * Add app config BISAAI_MAIL_SENDER
        * Add app config BISAAI_MAIL_API_KEY
        * Add app config BISAAIPAYMENT_BASE_URL
        * Add app config BISAAIPAYMENT_KEY
    * Change lokasi/controllers.py : Menghapus API-API contoh dari base structure (API tempat uji kompetensi)
    * Change utnsl_utensil/controllers.py : Mengganti isi dari parameter static_folder

###### Database :
* Mengganti nama table dpr_lokasi menjadi lokasi
* Mengganti nama table dpr_lokasi_galeri menjadi lokasi_galeri
* ALTER TABLE `dpr_harga` DROP COLUMN `tipe_sewa`;
* ALTER TABLE `dpr_harga` ADD `nama_harga` VARCHAR(255) NOT NULL AFTER `harga`;
* ALTER TABLE `dpr_harga` ADD `deskripsi_harga` TEXT NULL AFTER `nama_harga`;
* ALTER TABLE `dpr_harga` ADD `jumlah_hari` INT NOT NULL AFTER `deskripsi_harga`;
* ALTER TABLE `dpr_harga` ADD `minimum_hari_sewa` INT NOT NULL AFTER `jumlah_hari`;
* ALTER TABLE `dpr_harga` CHANGE `harga` `harga` INT(11) NOT NULL AFTER `deskripsi_harga`;
* ALTER TABLE `dpr_harga` ADD `is_delete` TINYINT NOT NULL DEFAULT '0' COMMENT '1 Dihapus, !=1 Tidak dihapus' AFTER `minimum_sewa`;
* ALTER TABLE `dpr_dapur` ADD `is_delete` TINYINT NOT NULL DEFAULT '0' COMMENT '1 Dihapus, !=1 Tidak dihapus' AFTER `deskripsi_dapur`;
* ALTER TABLE `dpr_tingkat` ADD `is_delete` TINYINT NOT NULL DEFAULT '0' COMMENT '1 Dihapus, !=1 TIdak dihapus' AFTER `deskripsi_tingkat`;
* ALTER TABLE `dpr_dapur` ADD `thumbnail_dapur` TEXT NULL AFTER `deskripsi_dapur`;
* ADD TABLE kupon
* ADD TABLE metode_pembayaran
* ALTER TABLE `customer` CHANGE `waktu_daftar` `waktu_daftar` DATETIME NULL DEFAULT CURRENT_TIMESTAMP;
* ALTER TABLE `dpr_dapur_galeri` ADD `is_delete` TINYINT NOT NULL DEFAULT '0' COMMENT '1 Dihapus, !=1 Tidak dihapus' AFTER `file_dapur_galeri`;
* Perubahan struktur table dpr_customer_dapur (perubahan yang dilakukan cukup banyak jadi drop table nya, kemudian import)
* ALTER TABLE `customer` DROP `nama_brand`;

---

#### v 0.0.1 -- 2021/12/29
###### New:
* Struktur Dasar

###### Change:
* Perubahan API fitur login
* Perubahan fitur form brosur
* Penambahan API utnsl_kategori

---
