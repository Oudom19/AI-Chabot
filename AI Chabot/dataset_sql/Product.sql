-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Mar 21, 2025 at 05:14 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `Product`
--

-- --------------------------------------------------------

--
-- Table structure for table `images`
--

CREATE TABLE `images` (
  `id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `image_url` varchar(500) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `images`
--

INSERT INTO `images` (`id`, `product_id`, `image_url`) VALUES
(1, 1, 'https://pacific.com.ng/wp-content/uploads/2022/09/mbp14-spacegray-gallery5-202110-img3.jpg'),
(2, 1, 'https://macfinder.co.uk/wp-content/uploads/2022/12/img-MacBook-Pro-Retina-14-Inch-21256.jpg'),
(3, 1, 'https://cdsassets.apple.com/live/SZLF0YNV/images/sp/111902_mbp14-silver2.png'),
(4, 2, 'https://www.alphastore.com.kw/wp-content/uploads/2023/06/Artboard-9.png'),
(5, 2, 'https://www.ione.com.kh/wp-content/uploads/2024/04/1.jpg'),
(6, 2, 'https://shop.theclub.com.hk/media/catalog/product/cache/325fd8d4f7eaef1af70e0a1582ef0e80/4/0/4021581_1.jpg'),
(7, 3, 'https://ssl-product-images.www8-hp.com/digmedialib/prodimg/lowres/c05476924.png'),
(8, 3, 'https://laptopmedia.com/wp-content/uploads/2017/11/81EtAEnTD4L._SL1500_.jpg'),
(9, 3, 'https://id-media.apjonlinecdn.com/catalog/product/cache/b3b166914d87ce343d4dc5ec5117b502/3/W/3WT00PA-5_T1678887487.png'),
(10, 4, 'https://pacific.com.ng/wp-content/uploads/2022/09/mbp14-spacegray-gallery5-202110-img3.jpg'),
(11, 4, 'https://macfinder.co.uk/wp-content/uploads/2022/12/img-MacBook-Pro-Retina-14-Inch-21256.jpg'),
(12, 4, 'https://cdsassets.apple.com/live/SZLF0YNV/images/sp/111902_mbp14-silver2.png'),
(13, 5, 'https://pacific.com.ng/wp-content/uploads/2022/09/mbp14-spacegray-gallery5-202110-img3.jpg'),
(14, 5, 'https://macfinder.co.uk/wp-content/uploads/2022/12/img-MacBook-Pro-Retina-14-Inch-21256.jpg'),
(15, 5, 'https://cdsassets.apple.com/live/SZLF0YNV/images/sp/111902_mbp14-silver2.png'),
(16, 6, 'https://m.media-amazon.com/images/I/61pi8NonKjL._AC_UF1000,1000_QL80_.jpg'),
(17, 6, 'https://rootitsupport.com/userfiles/a314-36p-4(1).png'),
(18, 6, 'https://www.bhphotovideo.com/cdn-cgi/image/fit=scale-down,width=500,quality=95/https://www.bhphotovideo.com/images/images500x500/acer_a314_36p_35uu_14_aspire_3_notebook_1726526121_1852752.jpg'),
(19, 7, 'https://pacific.com.ng/wp-content/uploads/2022/09/mbp14-spacegray-gallery5-202110-img3.jpg'),
(20, 7, 'https://macfinder.co.uk/wp-content/uploads/2022/12/img-MacBook-Pro-Retina-14-Inch-21256.jpg'),
(21, 7, 'https://cdsassets.apple.com/live/SZLF0YNV/images/sp/111902_mbp14-silver2.png'),
(22, 8, 'https://www.alphastore.com.kw/wp-content/uploads/2023/06/Artboard-9.png'),
(23, 8, 'https://www.ione.com.kh/wp-content/uploads/2024/04/1.jpg'),
(24, 8, 'https://shop.theclub.com.hk/media/catalog/product/cache/325fd8d4f7eaef1af70e0a1582ef0e80/4/0/4021581_1.jpg'),
(25, 10, 'https://cdn.uc.assets.prezly.com/18412f1b-f8f0-4428-9f4e-4f34a0443a9d/Swift-3-SF314-71-05.png'),
(26, 10, 'https://pacific.com.kh/khm/wp-content/uploads/2021/12/63725866t11.jpg'),
(27, 10, 'https://5.imimg.com/data5/SELLER/Default/2021/3/LR/YI/LA/12007059/acer-swift-3-14-inches-sf314-59-laptop-500x500.jpg'),
(28, 11, 'https://ssl-product-images.www8-hp.com/digmedialib/prodimg/lowres/c05476924.png'),
(29, 11, 'https://laptopmedia.com/wp-content/uploads/2017/11/81EtAEnTD4L._SL1500_.jpg'),
(30, 11, 'https://id-media.apjonlinecdn.com/catalog/product/cache/b3b166914d87ce343d4dc5ec5117b502/3/W/3WT00PA-5_T1678887487.png'),
(31, 12, 'https://ssl-product-images.www8-hp.com/digmedialib/prodimg/lowres/c05476924.png'),
(32, 12, 'https://laptopmedia.com/wp-content/uploads/2017/11/81EtAEnTD4L._SL1500_.jpg'),
(33, 12, 'https://id-media.apjonlinecdn.com/catalog/product/cache/b3b166914d87ce343d4dc5ec5117b502/3/W/3WT00PA-5_T1678887487.png'),
(34, 13, 'https://pacific.com.ng/wp-content/uploads/2022/09/mbp14-spacegray-gallery5-202110-img3.jpg'),
(35, 13, 'https://macfinder.co.uk/wp-content/uploads/2022/12/img-MacBook-Pro-Retina-14-Inch-21256.jpg'),
(36, 13, 'https://cdsassets.apple.com/live/SZLF0YNV/images/sp/111902_mbp14-silver2.png'),
(37, 14, 'https://destinybizz.com/destiny/wp-content/uploads/2019/03/3567.jpg'),
(38, 14, 'https://m.media-amazon.com/images/I/717o+Q-VV5L._AC_UF894,1000_QL80_.jpg'),
(39, 14, 'https://m.media-amazon.com/images/I/61mKmTFntUL._AC_UF894,1000_QL80_.jpg');

-- --------------------------------------------------------

--
-- Table structure for table `manufacturers`
--

CREATE TABLE `manufacturers` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `manufacturers`
--

INSERT INTO `manufacturers` (`id`, `name`) VALUES
(1, 'Acer'),
(2, 'Apple'),
(3, 'Asus'),
(4, 'Chuwi'),
(5, 'Dell'),
(6, 'HP'),
(7, 'Huawei'),
(8, 'Lenovo'),
(9, 'Microsoft'),
(10, 'MSI'),
(11, 'Razer'),
(12, 'Toshiba'),
(13, 'Vero'),
(14, 'Xiaomi');

-- --------------------------------------------------------

--
-- Table structure for table `operating_systems`
--

CREATE TABLE `operating_systems` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `version` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `operating_systems`
--

INSERT INTO `operating_systems` (`id`, `name`, `version`) VALUES
(6, 'Android', ''),
(5, 'Linux', ''),
(4, 'Mac OS', 'X'),
(1, 'macOS', ''),
(2, 'No OS', ''),
(3, 'Windows', '10');

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE `products` (
  `id` int(11) NOT NULL,
  `manufacturer_id` int(11) DEFAULT NULL,
  `model_name` varchar(255) NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `screen_size` varchar(15) DEFAULT NULL,
  `screen` varchar(255) DEFAULT NULL,
  `cpu` varchar(255) DEFAULT NULL,
  `ram` varchar(50) DEFAULT NULL,
  `storage` varchar(255) DEFAULT NULL,
  `gpu` varchar(255) DEFAULT NULL,
  `os_id` int(11) DEFAULT NULL,
  `weight` varchar(20) DEFAULT NULL,
  `price` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `products`
--

INSERT INTO `products` (`id`, `manufacturer_id`, `model_name`, `category`, `screen_size`, `screen`, `cpu`, `ram`, `storage`, `gpu`, `os_id`, `weight`, `price`) VALUES
(1, 2, 'MacBook Pro', 'Ultrabook', '13.3\"', 'IPS Panel Retina Display 2560x1600', 'Intel Core i5 2.3GHz', '8GB', '128GB SSD', 'Intel Iris Plus Graphics 640', 1, '1.37kg', 1339.69),
(2, 2, 'Macbook Air', 'Notebook', '13.3\"', '1440x900', 'Intel Core i5 1.8GHz', '8GB', '128GB Flash Storage', 'Intel HD Graphics 6000', 1, '1.34kg', 998.94),
(3, 6, '250 G6', 'Notebook', '15.6\"', 'Full HD 1920x1080', 'Intel Core i5 7200U 2.5GHz', '8GB', '256GB SSD', 'Intel HD Graphics 620', 2, '1.86kg', 575),
(4, 2, 'MacBook Pro', 'Notebook', '15.4\"', 'IPS Panel Retina Display 2880x1800', 'Intel Core i7 2.7GHz', '16GB', '512GB SSD', 'AMD Radeon Pro 455', 1, '1.83kg', 2837.45),
(5, 2, 'MacBook Pro', 'Ultrabook', '13.3\"', 'IPS Panel Retina Display 2560x1600', 'Intel Core i7 2.7GHz', '8GB', '256GB SSD', 'Intel Iris Plus Graphics 650', 1, '1.37kg', 1803.6),
(6, 1, 'Aspire 3', 'Notebook', '15.6\"', '1366x768', 'AMD A9-Series 9420 3GHz', '4GB', '500GB HDD', 'AMD Radeon R5', 3, '2.1kg', 400),
(7, 2, 'MacBook Pro', 'Ultrabook', '15.4\"', 'IPS Panel Retina Display 2880x1800', 'Intel Core i7 2.2GHz', '16GB', '256GB Flash Storage', 'Intel Iris Pro Graphics', 4, '2.04kg', 2139.97),
(8, 2, 'Macbook Air', 'Ultrabook', '13.3\"', '1440x900', 'Intel Core i5 1.8GHz', '8GB', '256GB Flash Storage', 'Intel HD Graphics 6000', 1, '1.34kg', 1158.7),
(9, 3, 'ZenBook UX430UN', 'Ultrabook', '14.0\"', 'Full HD 1920x1080', 'Intel Core i7 8550U 1.8GHz', '16GB', '512GB SSD', 'Nvidia GeForce MX150', 3, '1.3kg', 1495),
(10, 1, 'Swift 3', 'Ultrabook', '14.0\"', 'IPS Panel Full HD 1920x1080', 'Intel Core i5 8250U 1.6GHz', '8GB', '256GB SSD', 'Intel UHD Graphics 620', 3, '1.6kg', 770),
(11, 6, '250 G6', 'Notebook', '15.6\"', '1366x768', 'Intel Core i5 7200U 2.5GHz', '4GB', '500GB HDD', 'Intel HD Graphics 620', 2, '1.86kg', 393.9),
(12, 6, '250 G6', 'Notebook', '15.6\"', 'Full HD 1920x1080', 'Intel Core i3 6006U 2GHz', '4GB', '500GB HDD', 'Intel HD Graphics 520', 2, '1.86kg', 344.99),
(13, 2, 'MacBook Pro', 'Ultrabook', '15.4\"', 'IPS Panel Retina Display 2880x1800', 'Intel Core i7 2.8GHz', '16GB', '256GB SSD', 'AMD Radeon Pro 555', 1, '1.83kg', 2439.97),
(14, 5, 'Inspiron 3567', 'Notebook', '15.6\"', 'Full HD 1920x1080', 'Intel Core i3 6006U 2GHz', '4GB', '256GB SSD', 'AMD Radeon R5 M430', 3, '2.2kg', 498.9),
(15, 2, 'MacBook 12\"', 'Ultrabook', '12.0\"', 'IPS Panel Retina Display 2304x1440', 'Intel Core M m3 1.2GHz', '8GB', '256GB SSD', 'Intel HD Graphics 615', 1, '0.92kg', 1262.4),
(16, 2, 'MacBook Pro', 'Ultrabook', '13.3\"', 'IPS Panel Retina Display 2560x1600', 'Intel Core i5 2.3GHz', '8GB', '256GB SSD', 'Intel Iris Plus Graphics 640', 1, '1.37kg', 1518.55),
(17, 5, 'Inspiron 3567', 'Notebook', '15.6\"', 'Full HD 1920x1080', 'Intel Core i7 7500U 2.7GHz', '8GB', '256GB SSD', 'AMD Radeon R5 M430', 3, '2.2kg', 745),
(18, 2, 'MacBook Pro', 'Ultrabook', '15.4\"', 'IPS Panel Retina Display 2880x1800', 'Intel Core i7 2.9GHz', '16GB', '512GB SSD', 'AMD Radeon Pro 560', 1, '1.83kg', 2858),
(19, 8, 'IdeaPad 320-15IKB', 'Notebook', '15.6\"', 'Full HD 1920x1080', 'Intel Core i3 7100U 2.4GHz', '8GB', '1TB HDD', 'Nvidia GeForce 940MX', 2, '2.2kg', 499),
(20, 5, 'XPS 13', 'Ultrabook', '13.3\"', 'IPS Panel Full HD / Touchscreen 1920x1080', 'Intel Core i5 8250U 1.6GHz', '8GB', '128GB SSD', 'Intel UHD Graphics 620', 3, '1.22kg', 979),
(21, 3, 'Vivobook E200HA', 'Netbook', '11.6\"', '1366x768', 'Intel Atom x5-Z8350 1.44GHz', '2GB', '32GB Flash Storage', 'Intel HD Graphics 400', 3, '0.98kg', 191.9),
(22, 8, 'Legion Y520-15IKBN', 'Gaming', '15.6\"', 'IPS Panel Full HD 1920x1080', 'Intel Core i5 7300HQ 2.5GHz', '8GB', '128GB SSD + 1TB HDD', 'Nvidia GeForce GTX 1050', 3, '2.5kg', 999),
(23, 6, '255 G6', 'Notebook', '15.6\"', '1366x768', 'AMD E-Series E2-9000e 1.5GHz', '4GB', '500GB HDD', 'AMD Radeon R2', 2, '1.86kg', 258),
(24, 5, 'Inspiron 5379', '2 in 1 Convertible', '13.3\"', 'Full HD / Touchscreen 1920x1080', 'Intel Core i5 8250U 1.6GHz', '8GB', '256GB SSD', 'Intel UHD Graphics 620', 3, '1.62kg', 819),
(25, 6, '15-BS101nv', 'Ultrabook', '15.6\"', 'Full HD 1920x1080', 'Intel Core i7 8550U 1.8GHz', '8GB', '256GB SSD', 'Intel HD Graphics 620', 3, '1.91kg', 659),
(26, 5, 'Inspiron 3567', 'Notebook', '15.6\"', '1366x768', 'Intel Core i3 6006U 2GHz', '4GB', '1TB HDD', 'Intel HD Graphics 520', 3, '2.3kg', 418.64),
(27, 2, 'MacBook Air', 'Ultrabook', '13.3\"', '1440x900', 'Intel Core i5 1.6GHz', '8GB', '128GB Flash Storage', 'Intel HD Graphics 6000', 4, '1.35kg', 1099),
(28, 5, 'Inspiron 5570', 'Notebook', '15.6\"', 'Full HD 1920x1080', 'Intel Core i5 8250U 1.6GHz', '8GB', '256GB SSD', 'AMD Radeon 530', 3, '2.2kg', 800),
(29, 5, 'Latitude 5590', 'Ultrabook', '15.6\"', 'Full HD 1920x1080', 'Intel Core i7 8650U 1.9GHz', '8GB', '256GB SSD + 256GB SSD', 'Intel UHD Graphics 620', 3, '1.88kg', 1298),
(30, 6, 'ProBook 470', 'Notebook', '17.3\"', 'Full HD 1920x1080', 'Intel Core i5 8250U 1.6GHz', '8GB', '1TB HDD', 'Nvidia GeForce 930MX', 3, '2.5kg', 896),
(31, 4, 'LapBook 15.6\"', 'Notebook', '15.6\"', 'Full HD 1920x1080', 'Intel Atom x5-Z8300 1.44GHz', '4GB', '64GB Flash Storage', 'Intel HD Graphics', 3, '1.89kg', 244.99),
(32, 3, 'E402WA-GA010T', 'Notebook', '14.0\"', '1366x768', 'AMD E-Series E2-6110 1.5GHz', '2GB', '32GB Flash Storage', 'AMD Radeon R2', 3, '1.65kg', 199),
(33, 5, '17-ak001nv', 'Notebook', '17.3\"', 'Full HD 1920x1080', 'AMD A6-Series 9220 2.5GHz', '4GB', '500GB HDD', 'AMD Radeon 530', 3, '2.71kg', 439),
(34, 5, 'XPS 13', 'Ultrabook', '13.3\"', 'Touchscreen / Quad HD+ 3200x1800', 'Intel Core i7 8550U 1.8GHz', '16GB', '512GB SSD', 'Intel UHD Graphics 620', 3, '1.2kg', 1869),
(35, 2, 'MacBook Air', 'Ultrabook', '13.3\"', '1440x900', 'Intel Core i5 1.6GHz', '8GB', '256GB Flash Storage', 'Intel HD Graphics 6000', 4, '1.35kg', 998),
(36, 8, 'IdeaPad 120S-14IAP', 'Notebook', '14.0\"', '1366x768', 'Intel Celeron Dual Core N3350 1.1GHz', '4GB', '64GB Flash Storage', 'Intel HD Graphics 500', 3, '1.44kg', 249),
(37, 1, 'Aspire 3', 'Notebook', '15.6\"', '1366x768', 'Intel Core i3 7130U 2.7GHz', '4GB', '1TB HDD', 'Intel HD Graphics 620', 5, '2.1kg', 367),
(38, 5, 'Inspiron 5770', 'Notebook', '17.3\"', 'IPS Panel Full HD 1920x1080', 'Intel Core i5 8250U 1.6GHz', '8GB', '128GB SSD + 1TB HDD', 'AMD Radeon 530', 3, '2.8kg', 979),
(39, 6, '250 G6', 'Notebook', '15.6\"', '1366x768', 'Intel Core i5 7200U 2.5GHz', '4GB', '1TB HDD', 'Intel HD Graphics 620', 5, '1.86kg', 488.69),
(40, 6, 'ProBook 450', 'Notebook', '15.6\"', 'Full HD 1920x1080', 'Intel Core i5 8250U 1.6GHz', '8GB', '256GB SSD', 'Nvidia GeForce 930MX', 3, '2.1kg', 879),
(41, 3, 'X540UA-DM186', 'Notebook', '15.6\"', 'Full HD 1920x1080', 'Intel Core i3 6006U 2GHz', '4GB', '1TB HDD', 'Intel HD Graphics 620', 5, '2kg', 389),
(42, 5, 'Inspiron 7577', 'Gaming', '15.6\"', 'IPS Panel Full HD 1920x1080', 'Intel Core i7 7700HQ 2.8GHz', '16GB', '256GB SSD + 1TB HDD', 'Nvidia GeForce GTX 1060', 3, '2.65kg', 1499),
(43, 3, 'X542UQ-GO005', 'Notebook', '15.6\"', '1366x768', 'Intel Core i5 7200U 2.5GHz', '8GB', '1TB HDD', 'Nvidia GeForce 940MX', 5, '2.3kg', 522.99),
(44, 1, 'Aspire A515-51G', 'Notebook', '15.6\"', 'IPS Panel Full HD 1920x1080', 'Intel Core i5 8250U 1.6GHz', '4GB', '256GB SSD', 'Intel UHD Graphics 620', 3, '2.2kg', 682),
(45, 5, 'Inspiron 7773', '2 in 1 Convertible', '17.3\"', 'Full HD / Touchscreen 1920x1080', 'Intel Core i5 8250U 1.6GHz', '12GB', '1TB HDD', 'Nvidia GeForce 150MX', 3, '2.77kg', 999),
(46, 2, 'MacBook Pro', 'Ultrabook', '13.3\"', 'IPS Panel Retina Display 2560x1600', 'Intel Core i5 2.0GHz', '8GB', '256GB SSD', 'Intel Iris Graphics 540', 1, '1.37kg', 1419),
(47, 8, 'IdeaPad 320-15ISK', 'Notebook', '15.6\"', '1366x768', 'Intel Core i3 6006U 2GHz', '4GB', '128GB SSD', 'Intel HD Graphics 520', 2, '2.2kg', 369),
(48, 3, 'Rog Strix', 'Gaming', '17.3\"', 'Full HD 1920x1080', 'AMD Ryzen 1700 3GHz', '8GB', '256GB SSD + 1TB HDD', 'AMD Radeon RX 580', 3, '3.2kg', 1299),
(49, 5, 'Inspiron 3567', 'Notebook', '15.6\"', 'Full HD 1920x1080', 'Intel Core i5 7200U 2.5GHz', '4GB', '256GB SSD', 'AMD Radeon R5 M430', 3, '2.3kg', 639);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `images`
--
ALTER TABLE `images`
  ADD PRIMARY KEY (`id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indexes for table `manufacturers`
--
ALTER TABLE `manufacturers`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `operating_systems`
--
ALTER TABLE `operating_systems`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`,`version`);

--
-- Indexes for table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`id`),
  ADD KEY `manufacturer_id` (`manufacturer_id`),
  ADD KEY `os_id` (`os_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `images`
--
ALTER TABLE `images`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=40;

--
-- AUTO_INCREMENT for table `manufacturers`
--
ALTER TABLE `manufacturers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6236;

--
-- AUTO_INCREMENT for table `operating_systems`
--
ALTER TABLE `operating_systems`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `products`
--
ALTER TABLE `products`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=50;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `images`
--
ALTER TABLE `images`
  ADD CONSTRAINT `images_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `products`
--
ALTER TABLE `products`
  ADD CONSTRAINT `products_ibfk_1` FOREIGN KEY (`manufacturer_id`) REFERENCES `manufacturers` (`id`),
  ADD CONSTRAINT `products_ibfk_2` FOREIGN KEY (`os_id`) REFERENCES `operating_systems` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
