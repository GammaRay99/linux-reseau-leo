# TP2 : Gestion de service

# Sommaire

- [TP2 : Gestion de service](#tp2--gestion-de-service)
- [Sommaire](#sommaire)
- [0. Prérequis](#0-prérequis)
  - [Checklist](#checklist)
- [I. Un premier serveur web](#i-un-premier-serveur-web)
  - [1. Installation](#1-installation)
  - [2. Avancer vers la maîtrise du service](#2-avancer-vers-la-maîtrise-du-service)
- [II. Une stack web plus avancée](#ii-une-stack-web-plus-avancée)
  - [1. Intro blabla](#1-intro-blabla)
  - [2. Setup](#2-setup)
    - [A. Base de données](#a-base-de-données)
    - [B. Serveur Web et NextCloud](#b-serveur-web-et-nextcloud)
    - [C. Finaliser l'installation de NextCloud](#c-finaliser-linstallation-de-nextcloud)

# 0. Prérequis

## Checklist

# I. Un premier serveur web

## 1. Installation

🖥️ **VM web.tp2.linux**

| Machine         | IP            | Service     |
|-----------------|---------------|-------------|
| `web.tp2.linux` | `10.102.1.11` | Serveur Web |

🌞 **Installer le serveur Apache**

```
[user@web ~]$ sudo dnf install httpd
  [...]
```


🌞 **Démarrer le service Apache**


```
[user@web ~]$ sudo systemctl start httpd.service
[user@web ~]$ sudo systemctl status httpd.service
● httpd.service - The Apache HTTP Server
     Loaded: loaded (/usr/lib/systemd/system/httpd.service; disabled; vendor preset: disabled)
     Active: active (running) since Tue 2022-11-15 10:05:11 CET; 9s ago
       Docs: man:httpd.service(8)
   Main PID: 1287 (httpd)
     Status: "Started, listening on: port 80"
      Tasks: 213 (limit: 5907)
     Memory: 23.2M
        CPU: 104ms
     CGroup: /system.slice/httpd.service
```

```
[user@web ~]$ sudo systemctl enable httpd.service
Created symlink /etc/systemd/system/multi-user.target.wants/httpd.service → /usr/lib/systemd/system/httpd.service.
```
```
[user@web ~]$ sudo firewall-cmd --zone=public --add-port=80/tcp
success
```
```
[user@web ~]$ sudo ss -lntp | grep httpd
LISTEN 0    511   *:80   *:*  users:(("httpd",pid=1291,fd=4),("httpd",pid=1290,fd=4),("httpd",pid=1289,fd=4),("httpd",pid=1287,fd=4))
```

🌞 **TEST**

```
[user@web ~]$ sudo systemctl status httpd
● httpd.service - The Apache HTTP Server
     Loaded: loaded (/usr/lib/systemd/system/httpd.service; enabled; vendor preset: disabled)
     Active: active (running) since Tue 2022-11-15 10:09:30 CET; 1min 6s ago
```
```
[user@web ~]$ systemctl list-unit-files | grep enabled | grep httpd
httpd.service                              enabled         disabled
```
```
[user@web ~]$ curl localhost
<!doctype html>
  [...]
```

## 2. Avancer vers la maîtrise du service

🌞 **Le service Apache...**

```
[Unit]
Description=The Apache HTTP Server
Wants=httpd-init.service
After=network.target remote-fs.target nss-lookup.target httpd-init.service
Documentation=man:httpd.service(8)

[Service]
Type=notify
Environment=LANG=C

ExecStart=/usr/sbin/httpd $OPTIONS -DFOREGROUND
ExecReload=/usr/sbin/httpd $OPTIONS -k graceful
# Send SIGWINCH for graceful stop
KillSignal=SIGWINCH
KillMode=mixed
PrivateTmp=true
OOMPolicy=continue

[Install]
WantedBy=multi-user.target
```

🌞 **Déterminer sous quel utilisateur tourne le processus Apache**

```
71 User apache
```

```
[user@web ~]$ ps -ef | grep httpd
root         686       1  0 10:09 ?        00:00:00 /usr/sbin/httpd -DFOREGROUND
apache       715     686  0 10:09 ?        00:00:00 /usr/sbin/httpd -DFOREGROUND
apache       718     686  0 10:09 ?        00:00:00 /usr/sbin/httpd -DFOREGROUND
apache       719     686  0 10:09 ?        00:00:00 /usr/sbin/httpd -DFOREGROUND
apache       720     686  0 10:09 ?        00:00:00 /usr/sbin/httpd -DFOREGROUND
user        1318    1058  0 10:30 pts/0    00:00:00 grep --color=auto httpd
```

```
[user@web ~]$ ls -al /usr/share/testpage/
total 12
drwxr-xr-x.  2 root root   24 Nov 15 10:01 .
drwxr-xr-x. 82 root root 4096 Nov 15 10:01 ..
-rw-r--r--.  1 root root 7620 Jul  6 04:37 index.html
```

🌞 **Changer l'utilisateur utilisé par Apache**

```
[user@web ~]$ cat /etc/passwd | grep apache
apache:x:48:48:Apache:/usr/share/httpd:/sbin/nologin
[user@web ~]$ sudo useradd johnny -d /usr/share/httpd -s /sbin/nologin
[user@web ~]$ cat /etc/passwd | grep johnny
johnny:x:1001:1001::/usr/share/httpd:/sbin/nologin
```
```
[user@web ~]$ ps -ef  | grep httpd
root        1399       1  0 10:39 ?        00:00:00 /usr/sbin/httpd -DFOREGROUND
johnny      1400    1399  0 10:39 ?        00:00:00 /usr/sbin/httpd -DFOREGROUND
johnny      1401    1399  0 10:39 ?        00:00:00 /usr/sbin/httpd -DFOREGROUND
johnny      1402    1399  0 10:39 ?        00:00:00 /usr/sbin/httpd -DFOREGROUND
johnny      1403    1399  0 10:39 ?        00:00:00 /usr/sbin/httpd -DFOREGROUND
```

🌞 **Faites en sorte que Apache tourne sur un autre port**

```
[user@web ~]$ sudo firewall-cmd --zone=public --add-port=8080/tcp
success
[user@web ~]$ sudo firewall-cmd --remove-port=80/tcp
success
[user@web ~]$ sudo firewall-cmd --list-all | grep port
  ports: 8080/tcp
  forward-ports: 
  source-ports: 

[user@web ~]$ sudo firewall-cmd --runtime-to-permanent
success
```

```
[user@web ~]$ sudo ss -lntp | grep httpd
LISTEN 0   511   *:8080 *:*  users:(("httpd",pid=1685,fd=4),("httpd",pid=1684,fd=4),("httpd",pid=1683,fd=4),("httpd",pid=1680,fd=4))
```

```
[user@web ~]$ curl localhost:8080
<!doctype html>
  [...]
```

📁 [**Fichier `/etc/httpd/conf/httpd.conf`**](./data/httpd.conf)

# II. Une stack web plus avancée

Done

## 1. Intro blabla

**Le serveur web `web.tp2.linux` sera le serveur qui accueillera les clients.** C'est sur son IP que les clients devront aller pour visiter le site web.  

**Le service de base de données `db.tp2.linux` sera uniquement accessible depuis `web.tp2.linux`.** Les clients ne pourront pas y accéder. Le serveur de base de données stocke les infos nécessaires au serveur web, pour le bon fonctionnement du site web.

---

Bon le but de ce TP est juste de s'exercer à faire tourner des services, un serveur + sa base de données, c'est un peu le cas d'école. J'ai pas envie d'aller deep dans la conf de l'un ou de l'autre avec vous pour le moment, on va se contenter d'une conf minimale.

Je vais pas vous demander de coder une application, et cette fois on se contentera pas d'un simple `index.html` tout moche et on va se mettre dans la peau de l'admin qui se retrouve avec une application à faire tourner. **On va faire tourner un [NextCloud](https://nextcloud.com/).**

En plus c'est utile comme truc : c'est un p'tit serveur pour héberger ses fichiers via une WebUI, style Google Drive. Mais on l'héberge nous-mêmes :)

---

## 2. Setup

🖥️ **VM db.tp2.linux**


| Machines        | IP            | Service                 |
|-----------------|---------------|-------------------------|
| `web.tp2.linux` | `10.102.1.11` | Serveur Web             |
| `db.tp2.linux`  | `10.102.1.12` | Serveur Base de Données |

### A. Base de données

🌞 **Install de MariaDB sur `db.tp2.linux`**

```
[user@db ~]$ dnf install mariadb-server
  [...]
  Complete!
```
```
[user@db ~]$ sudo systemctl enable mariadb
Created symlink /etc/systemd/system/mysql.service → /usr/lib/systemd/system/mariadb.service.
Created symlink /etc/systemd/system/mysqld.service → /usr/lib/systemd/system/mariadb.service.
Created symlink /etc/systemd/system/multi-user.target.wants/mariadb.service → /usr/lib/systemd/system/mariadb.service.
[user@db ~]$ sudo systemctl start mariadb
[user@db ~]$ sudo mysql_secure_installation
  [...]
All done!  If you've completed all of the above steps, your MariaDB
installation should now be secure.

Thanks for using MariaDB!
```
```
[user@db ~]$ sudo ss -lntp | grep maria
LISTEN 0      80                 *:3306            *:*    users:(("mariadbd",pid=3224,fd=19))
[user@db ~]$ sudo firewall-cmd --zone=public --add-port=3306/tcp
success
```

🌞 **Préparation de la base pour NextCloud**

```
[user@db ~]$ sudo mysql -u root -p
Enter password: 
  [...]
MariaDB [(none)]>
```

  - exécutez les commandes SQL suivantes :

```
MariaDB [(none)]> CREATE USER 'nextcloud'@'10.102.1.11' IDENTIFIED BY 'pewpewpew';
Query OK, 0 rows affected (0.007 sec)

MariaDB [(none)]> CREATE DATABASE IF NOT EXISTS nextcloud CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
Query OK, 1 row affected (0.000 sec)

MariaDB [(none)]> GRANT ALL PRIVILEGES ON nextcloud.* TO 'nextcloud'@'10.102.1.11';
Query OK, 0 rows affected (0.006 sec)

MariaDB [(none)]> FLUSH PRIVILEGES;
Query OK, 0 rows affected (0.000 sec)
```


🌞 **Exploration de la base de données**

```
[user@web ~]$ mysql -u nextcloud -h 10.102.1.12 -p
Enter password: 
  [...]
mysql> 
```

```
mysql> SHOW DATABASES;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| nextcloud          |
+--------------------+
2 rows in set (0.00 sec)

mysql> USE nextcloud
Database changed
mysql> SHOW TABLES;
Empty set (0.00 sec)
```

🌞 **Trouver une commande SQL qui permet de lister tous les utilisateurs de la base de données**

```
MariaDB [(none)]> SELECT * FROM mysql.user;
  [...]
```

### B. Serveur Web et NextCloud

⚠️⚠️⚠️ **N'OUBLIEZ PAS de réinitialiser votre conf Apache avant de continuer. En particulier, remettez le port et le user par défaut.**

🌞 **Install de PHP**

```bash
# On ajoute le dépôt CRB
$ sudo dnf config-manager --set-enabled crb
# On ajoute le dépôt REMI
$ sudo dnf install dnf-utils http://rpms.remirepo.net/enterprise/remi-release-9.rpm -y

# On liste les versions de PHP dispos, au passage on va pouvoir accepter les clés du dépôt REMI
$ dnf module list php

# On active le dépôt REMI pour récupérer une version spécifique de PHP, celle recommandée par la doc de NextCloud
$ sudo dnf module enable php:remi-8.1 -y

# Eeeet enfin, on installe la bonne version de PHP : 8.1
$ sudo dnf install -y php81-php
```

Done

🌞 **Install de tous les modules PHP nécessaires pour NextCloud**

```bash
# eeeeet euuuh boom. Là non plus j'ai pas pondu ça, c'est la doc :
$ sudo dnf install -y libxml2 openssl php81-php php81-php-ctype php81-php-curl php81-php-gd php81-php-iconv php81-php-json php81-php-libxml php81-php-mbstring php81-php-openssl php81-php-posix php81-php-session php81-php-xml php81-php-zip php81-php-zlib php81-php-pdo php81-php-mysqlnd php81-php-intl php81-php-bcmath php81-php-gmp
```

Done aussi

🌞 **Récupérer NextCloud**

```
[user@web tp2_nextcloud]$ ls
nextcloud  nextcloud-25.0.0rc3.zip

[user@web tp2_nextcloud]$ sudo mv nextcloud/* ./
[user@web tp2_nextcloud]$ ls index.html 
index.html
```

```
[user@web tp2_nextcloud]$ ls -all
total 132
drwxr-xr-x. 14 apache apache  4096 Nov 15 11:34 .
drwxr-xr-x.  5 root   root      54 Nov 15 11:31 ..
drwxr-xr-x. 47 apache apache  4096 Oct  6 14:47 3rdparty
drwxr-xr-x. 50 apache apache  4096 Oct  6 14:44 apps
    [...]
drwxr-xr-x.  3 apache apache    35 Oct  6 14:42 themes
drwxr-xr-x.  2 apache apache    43 Oct  6 14:44 updater
-rw-r--r--.  1 apache apache   387 Oct  6 14:47 version.php
```

🌞 **Adapter la configuration d'Apache**


```
# Supplemental configuration
#
# Load config files in the "/etc/httpd/conf.d" directory, if any.
IncludeOptional conf.d/*.conf
```

```
[user@web conf.d]$ cat nextcloud_custom.conf 
<VirtualHost *:80>
  DocumentRoot /var/www/tp2_nextcloud/ # on indique le chemin de notre webroot
  ServerName  web.tp2.linux # on précise le nom que saisissent les clients pour accéder au service
  <Directory /var/www/tp2_nextcloud/> # on définit des règles d'accès sur notre webroot
    Require all granted
    AllowOverride All
    Options FollowSymLinks MultiViews
    <IfModule mod_dav.c>
      Dav off
    </IfModule>
  </Directory>
</VirtualHost>
```

🌞 **Redémarrer le service Apache** pour qu'il prenne en compte le nouveau fichier de conf


```
[user@web conf.d]$ sudo systemctl restart httpd
Job for httpd.service failed because the control process exited with error code.
See "systemctl status httpd.service" and "journalctl -xeu httpd.service" for details.
```

Log:
```
Nov 15 11:42:11 web.tp2.b2 systemd[1]: Starting The Apache HTTP Server...
Nov 15 11:42:11 web.tp2.b2 httpd[4970]: AH00526: Syntax error on line 2 of /etc/httpd/conf.d/nextcloud_custom.conf:
Nov 15 11:42:11 web.tp2.b2 httpd[4970]: DocumentRoot takes one argument, Root directory of the document tree
Nov 15 11:42:11 web.tp2.b2 systemd[1]: httpd.service: Main process exited, code=exited, status=1/FAILURE
Nov 15 11:42:11 web.tp2.b2 systemd[1]: httpd.service: Failed with result 'exit-code'.
Nov 15 11:42:11 web.tp2.b2 systemd[1]: Failed to start The Apache HTTP Server.
```

Après des test, il semble que les commentaires (#) sont interprétés. On les supprime et on relance

```
[user@web conf.d]$ sudo systemctl restart httpd
[user@web conf.d]$ systemctl status httpd.service
● httpd.service - The Apache HTTP Server
     Loaded: loaded (/usr/lib/systemd/system/httpd.service; enabled; vendor preset: disabled)
    Drop-In: /usr/lib/systemd/system/httpd.service.d
             └─php81-php-fpm.conf
     Active: active (running) since Tue 2022-11-15 11:49:15 CET; 1s ago
```

### C. Finaliser l'installation de NextCloud

➜ **Sur votre PC**

```
 ╭─gammray@manjaro in ~ took 28s
 ╰─λ cat /etc/hosts
# Host addresses
127.0.0.1  localhost
127.0.1.1  manjaro
::1        localhost ip6-localhost ip6-loopback
ff02::1    ip6-allnodes
ff02::2    ip6-allrouters
192.168.121.1 ctfd.marshack.fr
192.168.120.1 game1.marshack.fr
192.168.120.2 game2.marshack.fr
192.168.121.1 portailvms.marshack.fr
192.168.122.2 vnc.marshack.fr
10.102.1.11   web.tp2.linux
```

```
 ╭─gammray@manjaro in ~ took 3ms
 ╰─λ curl http://web.tp2.linux
<!DOCTYPE html>
<html>
<head>
  <script> window.location.href="index.php"; </script>
  <meta http-equiv="refresh" content="0; URL=index.php">
</head>
</html>
```

- on va vous demander un utilisateur et un mot de passe pour créer un compte admin
  - ne saisissez rien pour le moment
- cliquez sur "Storage & Database" juste en dessous
  - choisissez "MySQL/MariaDB"
  - saisissez les informations pour que NextCloud puisse se connecter avec votre base
- saisissez l'identifiant et le mot de passe admin que vous voulez, et validez l'installation

🌴 **C'est chez vous ici**, baladez vous un peu sur l'interface de NextCloud, faites le tour du propriétaire :)
C'est cool chez moi

🌞 **Exploration de la base de données**

```
[user@web config]$ mysql -u nextcloud -h 10.102.1.12 -p -D nextcloud
Enter password: 
  [...]
mysql> 
```

```
mysql> show tables;
+-----------------------------+
| Tables_in_nextcloud         |
+-----------------------------+
| oc_accounts                 |
  [...]
| oc_whats_new                |
+-----------------------------+
95 rows in set (0.00 sec)

mysql> 
```

```
mysql> select table_schema as database_name,
    ->     count(*) as tables
    -> from information_schema.tables
    -> where table_type = 'BASE TABLE'
    ->       and table_schema not in ('information_schema', 'sys',
    ->                                'performance_schema', 'mysql')
    -> group by table_schema
    -> order by table_schema;
+---------------+--------+
| database_name | tables |
+---------------+--------+
| nextcloud     |     95 |
+---------------+--------+
1 row in set (0.00 sec)
```

![](https://media.tenor.com/3PCreHGZ3rcAAAAd/done-well.gif)