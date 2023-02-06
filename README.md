# price-tracker

Get prices from the website and save them to the database.

## Quickstart

```zsh
$ cd ~/Documents/GitHub/price-tracker
$ python main.py
```

## MySQL table

item_info

```mysql
CREATE TABLE `item_info` (
  `id` int(2) NOT NULL,
  `item` varchar(40) DEFAULT NULL,
  `url` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `item` (`item`),
  UNIQUE KEY `url` (`url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

price

```mysql
CREATE TABLE `price` (
  `id` int(4) NOT NULL AUTO_INCREMENT,
  `date` varchar(10) DEFAULT NULL,
  `SONY-XR-77A80K` varchar(10) DEFAULT NULL,
  `LG-OLED77C24LA` varchar(10) DEFAULT NULL,
  `Nespresso-SNE500BKS` varchar(10) DEFAULT NULL,
  `Samsung-RS66A8101B1/EF` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```