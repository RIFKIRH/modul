-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 11, 2022 at 03:34 AM
-- Server version: 10.4.13-MariaDB
-- PHP Version: 7.4.7

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `bisa_kitchen_dev`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `id_admin` int(11) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `nama_admin` varchar(255) NOT NULL,
  `status` tinyint(4) NOT NULL COMMENT '1 Aktif, 2 Diblokir',
  `is_delete` tinyint(4) NOT NULL DEFAULT 0 COMMENT '1 Dihapus, !=1 Tidak Dihapus'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `customer`
--

CREATE TABLE `customer` (
  `id_customer` int(11) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `nama_customer` varchar(255) NOT NULL,
  `nama_brand` varchar(255) DEFAULT NULL,
  `nomor_customer` int(20) DEFAULT NULL,
  `alamat_customer` varchar(255) DEFAULT NULL,
  `waktu_daftar` datetime DEFAULT NULL,
  `waktu_terakhir_login` datetime DEFAULT NULL,
  `status` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1 Aktif, 2 Blokir',
  `is_delete` tinyint(4) NOT NULL DEFAULT 0 COMMENT '1 Dihapus, !=1 Tidak Dihapus'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `customer_brosur`
--

CREATE TABLE `customer_brosur` (
  `id_customer_brosur` int(11) NOT NULL,
  `nama_customer_brosur` varchar(255) NOT NULL,
  `email_customer_brosur` varchar(255) NOT NULL,
  `no_customer_brosur` int(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `dpr_customer_dapur`
--

CREATE TABLE `dpr_customer_dapur` (
  `id_customer_dapur` int(11) NOT NULL,
  `id_customer` int(11) NOT NULL,
  `id_dpr_harga` int(11) NOT NULL,
  `kuantitas_pembelian` tinyint(4) NOT NULL DEFAULT 1,
  `waktu_pembayaran` datetime NOT NULL,
  `status_pembayaran` tinyint(4) NOT NULL DEFAULT 1 COMMENT '0 pending, 1 sukses, 2 dibatalkan',
  `waktu_mulai_pemesanan` datetime NOT NULL,
  `waktu_akhir_pemesanan` datetime NOT NULL,
  `status_pemesanan` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1 Aktif, 2 Dibatalkan',
  `barcode` varchar(255) DEFAULT NULL,
  `is_delete` tinyint(4) NOT NULL DEFAULT 0 COMMENT '1 Dihapus, !=1 Tidak Dihapus'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `dpr_dapur`
--

CREATE TABLE `dpr_dapur` (
  `id_dapur` int(11) NOT NULL,
  `id_lokasi` int(11) NOT NULL,
  `id_tingkat` int(11) NOT NULL,
  `nama_dapur` varchar(255) NOT NULL,
  `deskripsi_dapur` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `dpr_dapur_galeri`
--

CREATE TABLE `dpr_dapur_galeri` (
  `id_dapur_galeri` int(11) NOT NULL,
  `id_dapur` int(11) NOT NULL,
  `nama_dapur_galeri` varchar(255) NOT NULL,
  `deskripsi_dapur_galeri` text NOT NULL,
  `file_dapur_galeri` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `dpr_harga`
--

CREATE TABLE `dpr_harga` (
  `id_dpr_harga` int(11) NOT NULL,
  `id_dapur` int(11) NOT NULL,
  `tipe_sewa` tinyint(4) NOT NULL DEFAULT 0 COMMENT '0 kontrak 6 bulan, 1 kontrak 12 bulan, 2 daily rent, 3 hourly rent',
  `harga` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `dpr_lokasi`
--

CREATE TABLE `dpr_lokasi` (
  `id_lokasi` int(11) NOT NULL,
  `id_kota` int(11) NOT NULL,
  `nama_lokasi` varchar(255) NOT NULL,
  `alamat_lokasi` varchar(255) NOT NULL,
  `gmaps_lokasi` varchar(255) NOT NULL,
  `deskripsi_lokasi` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `dpr_lokasi_galeri`
--

CREATE TABLE `dpr_lokasi_galeri` (
  `id_lokasi_galeri` int(11) NOT NULL,
  `id_lokasi` int(11) NOT NULL,
  `nama_lokasi_galeri` varchar(255) NOT NULL,
  `deskripsi_lokasi_galeri` text NOT NULL,
  `file_lokasi_galeri` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `dpr_tingkat`
--

CREATE TABLE `dpr_tingkat` (
  `id_tingkat` int(11) NOT NULL,
  `nama_tingkat` varchar(255) NOT NULL,
  `deskripsi_tingkat` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `kota`
--

CREATE TABLE `kota` (
  `id_kota` int(11) NOT NULL,
  `id_provinsi` int(11) NOT NULL,
  `nama_kota` varchar(255) NOT NULL,
  `nama_provinsi` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `provinsi`
--

CREATE TABLE `provinsi` (
  `id_provinsi` int(11) NOT NULL,
  `nama_provinsi` int(11) NOT NULL,
  `is_delete` tinyint(4) NOT NULL DEFAULT 0 COMMENT '1 Dihapus, !=1 Tidak dihapus'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `utnsl_customer_utensil`
--

CREATE TABLE `utnsl_customer_utensil` (
  `id_customer_utensil` int(11) NOT NULL,
  `id_customer_dapur` int(11) NOT NULL,
  `waktu_insert` int(11) NOT NULL,
  `status` tinyint(4) NOT NULL COMMENT '1: Aktif, 2: Dibatalkan'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `utnsl_customer_utensil_detail`
--

CREATE TABLE `utnsl_customer_utensil_detail` (
  `id_customer_utensil_detail` int(11) NOT NULL,
  `id_customer_utensil` int(11) NOT NULL,
  `id_utensil` int(11) NOT NULL,
  `jumlah` int(11) NOT NULL,
  `total_harga` int(11) NOT NULL,
  `status_barang` tinyint(4) NOT NULL COMMENT '1: Barang belum didapur, 2 : Barang sudah didapur, 3: Barang sudah dikembalikan',
  `waktu_mulai_sewa` datetime NOT NULL,
  `waktu_akhir_sewa` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `utnsl_kategori`
--

CREATE TABLE `utnsl_kategori` (
  `id_kategori` int(11) NOT NULL,
  `nama_kategori` varchar(255) NOT NULL,
  `deskripsi_kategori` text NOT NULL,
  `is_delete` tinyint(4) NOT NULL DEFAULT 0 COMMENT '1 Dihapus, !=1 Tidak dihapus'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `utnsl_utensil`
--

CREATE TABLE `utnsl_utensil` (
  `id_utensil` int(11) NOT NULL,
  `id_kategori` int(11) NOT NULL,
  `id_lokasi` int(11) NOT NULL,
  `nama_utensil` varchar(255) NOT NULL,
  `deskripsi_utensil` text NOT NULL,
  `jumlah` int(11) NOT NULL,
  `harga_sewa` int(11) NOT NULL COMMENT 'Harga sewa perjam',
  `foto_utensil_1` varchar(255) DEFAULT NULL,
  `foto_utensil_2` varchar(255) DEFAULT NULL,
  `foto_utensil_3` varchar(255) DEFAULT NULL,
  `is_delete` tinyint(4) NOT NULL DEFAULT 0 COMMENT '1 Dihapus, !=1 Tidak diihapus'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id_admin`);

--
-- Indexes for table `customer`
--
ALTER TABLE `customer`
  ADD PRIMARY KEY (`id_customer`);

--
-- Indexes for table `customer_brosur`
--
ALTER TABLE `customer_brosur`
  ADD PRIMARY KEY (`id_customer_brosur`);

--
-- Indexes for table `dpr_customer_dapur`
--
ALTER TABLE `dpr_customer_dapur`
  ADD PRIMARY KEY (`id_customer_dapur`),
  ADD KEY `id_customer` (`id_customer`),
  ADD KEY `id_dapur` (`id_dpr_harga`);

--
-- Indexes for table `dpr_dapur`
--
ALTER TABLE `dpr_dapur`
  ADD PRIMARY KEY (`id_dapur`),
  ADD KEY `id_lokasi` (`id_lokasi`),
  ADD KEY `id_tingkat` (`id_tingkat`);

--
-- Indexes for table `dpr_dapur_galeri`
--
ALTER TABLE `dpr_dapur_galeri`
  ADD PRIMARY KEY (`id_dapur_galeri`),
  ADD KEY `id_dapur` (`id_dapur`);

--
-- Indexes for table `dpr_harga`
--
ALTER TABLE `dpr_harga`
  ADD PRIMARY KEY (`id_dpr_harga`),
  ADD KEY `id_dapur` (`id_dapur`);

--
-- Indexes for table `dpr_lokasi`
--
ALTER TABLE `dpr_lokasi`
  ADD PRIMARY KEY (`id_lokasi`),
  ADD KEY `id_kota` (`id_kota`);

--
-- Indexes for table `dpr_lokasi_galeri`
--
ALTER TABLE `dpr_lokasi_galeri`
  ADD PRIMARY KEY (`id_lokasi_galeri`),
  ADD KEY `id_lokasi` (`id_lokasi`);

--
-- Indexes for table `dpr_tingkat`
--
ALTER TABLE `dpr_tingkat`
  ADD PRIMARY KEY (`id_tingkat`);

--
-- Indexes for table `kota`
--
ALTER TABLE `kota`
  ADD PRIMARY KEY (`id_kota`),
  ADD KEY `id_provinsi` (`id_provinsi`);

--
-- Indexes for table `provinsi`
--
ALTER TABLE `provinsi`
  ADD PRIMARY KEY (`id_provinsi`);

--
-- Indexes for table `utnsl_customer_utensil`
--
ALTER TABLE `utnsl_customer_utensil`
  ADD PRIMARY KEY (`id_customer_utensil`),
  ADD KEY `id_customer_dapur` (`id_customer_dapur`);

--
-- Indexes for table `utnsl_customer_utensil_detail`
--
ALTER TABLE `utnsl_customer_utensil_detail`
  ADD PRIMARY KEY (`id_customer_utensil_detail`),
  ADD KEY `id_customer_utensil` (`id_customer_utensil`);

--
-- Indexes for table `utnsl_kategori`
--
ALTER TABLE `utnsl_kategori`
  ADD PRIMARY KEY (`id_kategori`);

--
-- Indexes for table `utnsl_utensil`
--
ALTER TABLE `utnsl_utensil`
  ADD PRIMARY KEY (`id_utensil`),
  ADD KEY `id_kategori` (`id_kategori`),
  ADD KEY `id_lokasi` (`id_lokasi`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `id_admin` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `customer`
--
ALTER TABLE `customer`
  MODIFY `id_customer` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `customer_brosur`
--
ALTER TABLE `customer_brosur`
  MODIFY `id_customer_brosur` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `dpr_customer_dapur`
--
ALTER TABLE `dpr_customer_dapur`
  MODIFY `id_customer_dapur` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `dpr_dapur`
--
ALTER TABLE `dpr_dapur`
  MODIFY `id_dapur` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `dpr_dapur_galeri`
--
ALTER TABLE `dpr_dapur_galeri`
  MODIFY `id_dapur_galeri` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `dpr_harga`
--
ALTER TABLE `dpr_harga`
  MODIFY `id_dpr_harga` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `dpr_lokasi`
--
ALTER TABLE `dpr_lokasi`
  MODIFY `id_lokasi` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `dpr_lokasi_galeri`
--
ALTER TABLE `dpr_lokasi_galeri`
  MODIFY `id_lokasi_galeri` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `dpr_tingkat`
--
ALTER TABLE `dpr_tingkat`
  MODIFY `id_tingkat` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `kota`
--
ALTER TABLE `kota`
  MODIFY `id_kota` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `provinsi`
--
ALTER TABLE `provinsi`
  MODIFY `id_provinsi` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `utnsl_customer_utensil`
--
ALTER TABLE `utnsl_customer_utensil`
  MODIFY `id_customer_utensil` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `utnsl_customer_utensil_detail`
--
ALTER TABLE `utnsl_customer_utensil_detail`
  MODIFY `id_customer_utensil_detail` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `utnsl_kategori`
--
ALTER TABLE `utnsl_kategori`
  MODIFY `id_kategori` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `utnsl_utensil`
--
ALTER TABLE `utnsl_utensil`
  MODIFY `id_utensil` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `dpr_customer_dapur`
--
ALTER TABLE `dpr_customer_dapur`
  ADD CONSTRAINT `dpr_customer_dapur_ibfk_1` FOREIGN KEY (`id_customer`) REFERENCES `customer` (`id_customer`),
  ADD CONSTRAINT `dpr_customer_dapur_ibfk_2` FOREIGN KEY (`id_dpr_harga`) REFERENCES `dpr_harga` (`id_dpr_harga`);

--
-- Constraints for table `dpr_dapur`
--
ALTER TABLE `dpr_dapur`
  ADD CONSTRAINT `dpr_dapur_ibfk_1` FOREIGN KEY (`id_lokasi`) REFERENCES `dpr_lokasi` (`id_lokasi`),
  ADD CONSTRAINT `dpr_dapur_ibfk_2` FOREIGN KEY (`id_tingkat`) REFERENCES `dpr_tingkat` (`id_tingkat`);

--
-- Constraints for table `dpr_dapur_galeri`
--
ALTER TABLE `dpr_dapur_galeri`
  ADD CONSTRAINT `dpr_dapur_galeri_ibfk_1` FOREIGN KEY (`id_dapur`) REFERENCES `dpr_dapur` (`id_dapur`);

--
-- Constraints for table `dpr_harga`
--
ALTER TABLE `dpr_harga`
  ADD CONSTRAINT `dpr_harga_ibfk_1` FOREIGN KEY (`id_dapur`) REFERENCES `dpr_dapur` (`id_dapur`);

--
-- Constraints for table `dpr_lokasi`
--
ALTER TABLE `dpr_lokasi`
  ADD CONSTRAINT `dpr_lokasi_ibfk_1` FOREIGN KEY (`id_kota`) REFERENCES `kota` (`id_kota`);

--
-- Constraints for table `dpr_lokasi_galeri`
--
ALTER TABLE `dpr_lokasi_galeri`
  ADD CONSTRAINT `dpr_lokasi_galeri_ibfk_1` FOREIGN KEY (`id_lokasi`) REFERENCES `dpr_lokasi` (`id_lokasi`);

--
-- Constraints for table `kota`
--
ALTER TABLE `kota`
  ADD CONSTRAINT `kota_ibfk_1` FOREIGN KEY (`id_provinsi`) REFERENCES `provinsi` (`id_provinsi`);

--
-- Constraints for table `utnsl_customer_utensil`
--
ALTER TABLE `utnsl_customer_utensil`
  ADD CONSTRAINT `utnsl_customer_utensil_ibfk_1` FOREIGN KEY (`id_customer_dapur`) REFERENCES `dpr_customer_dapur` (`id_customer_dapur`);

--
-- Constraints for table `utnsl_customer_utensil_detail`
--
ALTER TABLE `utnsl_customer_utensil_detail`
  ADD CONSTRAINT `utnsl_customer_utensil_detail_ibfk_1` FOREIGN KEY (`id_customer_utensil`) REFERENCES `utnsl_customer_utensil` (`id_customer_utensil`);

--
-- Constraints for table `utnsl_utensil`
--
ALTER TABLE `utnsl_utensil`
  ADD CONSTRAINT `utnsl_utensil_ibfk_1` FOREIGN KEY (`id_kategori`) REFERENCES `utnsl_kategori` (`id_kategori`),
  ADD CONSTRAINT `utnsl_utensil_ibfk_2` FOREIGN KEY (`id_lokasi`) REFERENCES `dpr_lokasi` (`id_lokasi`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
