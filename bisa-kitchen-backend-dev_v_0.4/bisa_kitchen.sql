-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 30, 2022 at 01:50 PM
-- Server version: 10.4.24-MariaDB
-- PHP Version: 8.1.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `bisa_kicthen_1`
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
  `nama_kota` varchar(255) NOT NULL,
  `nama_provinsi` varchar(255) NOT NULL
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
  ADD PRIMARY KEY (`id_kota`);

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
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
