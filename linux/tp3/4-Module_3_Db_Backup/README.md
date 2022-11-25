# Module 3 : Sauvegarde de base de données


## I. Script dump

➜ **Créer un utilisateur DANS LA BASE DE DONNEES**

```
MariaDB [(none)]> CREATE USER "backups"@"localhost" IDENTIFIED BY 'pewpewpew';
Query OK, 0 rows affected (0.006 sec)

MariaDB [(none)]> GRANT ALL PRIVILEGES ON nextcloud.* TO "backups"@"localhost";
Query OK, 0 rows affected (0.014 sec)

MariaDB [(none)]> FLUSH PRIVILEGES;
Query OK, 0 rows affected (0.001 sec)
```

➜ **Ecrire le script `bash`**

```
[user@db srv]$ cat tp3_db_dump.sh 
#!/bin/bash

user="backups"
password="pewpewpew"
database_name="nextcloud"
curr_date=$(date '+%y%m%d%H%M%S')
file_name=/srv/db_dumps/db_${database_name}_${curr_date}.sql

mysqldump -u $user $database_name --password=$password > $file_name
tar -czf ${file_name}.tar.gz $file_name
rm $file_name
```

## II. Clean it

On va rendre le script un peu plus propre vous voulez bien ?

➜ **Utiliser des variables** déclarées en début de script pour stocker les valeurs suivantes :

```bash
[user@db srv]$ cat tp3_db_dump.sh 
#!/bin/bash

user="backups"
password="pewpewpew"
database_name="nextcloud"
curr_date=$(date '+%y%m%d%H%M%S')
file_name=/srv/db_dumps/db_${database_name}_${curr_date}.sql
ip_host="localhost"

mysqldump -u $user $database_name -h $ip_host --password=$password > $file_name
tar -czf ${file_name}.tar.gz $file_name
rm $file_name
```

```
[user@db srv]$ bash tp3_db_dump.sh 
tar: Removing leading `/' from member names
[user@db srv]$ ls db_dumps/
db_nextcloud_221121122430.sql.tar.gz  db_nextcloud_221121122834.sql.tar.gz
```

➜ **Environnement d'exécution du script**
```
[user@db srv]$ ls -all
total 4
drwxr-xr-x.  3 root     root      44 Nov 21 12:32 .
dr-xr-xr-x. 18 root     root     235 Sep 30 10:26 ..
drwxr-xr-x.  2 db_dumps db_dumps  94 Nov 21 12:28 db_dumps
-rwxr-----.  1 db_dumps db_dumps 408 Nov 21 12:32 tp3_db_dump.sh
[user@db srv]$ sudo -u db_dumps ./tp3_db_dump.sh 
tar: Removing leading `/' from member names
[user@db srv]$ ls db_dumps/
db_nextcloud_221121122430.sql.tar.gz  db_nextcloud_221121122834.sql.tar.gz  db_nextcloud_221121125948.sql.tar.gz
[user@db srv]$
```

✨ **Bonus : Stocker le mot de passe pour se co à la base dans un fichier séparé**

```
[user@db srv]$ ls -all
total 8
drwxr-xr-x.  3 root     root      59 Nov 21 13:07 .
dr-xr-xr-x. 18 root     root     235 Sep 30 10:26 ..
drwxr-xr-x.  2 db_dumps db_dumps   6 Nov 21 13:09 db_dumps
-rw-r-----.  1 db_dumps db_dumps  21 Nov 21 13:07 db_pass
-rwxr--r--.  1 db_dumps db_dumps 407 Nov 21 13:07 tp3_db_dump.sh
[user@db srv]$ sudo -u db_dumps ./tp3_db_dump.sh 
tar: Removing leading `/' from member names
[user@db srv]$ ls db_dumps/
db_nextcloud_221121130922.sql.tar.gz
```

## III. Service et timer

➜ **Créez un *service*** système qui lance le script

- inspirez-vous du *service* créé à la fin du TP1
- la seule différence est que vous devez rajouter `Type=oneshot` dans la section `[Service]` pour indiquer au système que ce service ne tournera pas à l'infini (comme le fait un serveur web par exemple) mais se terminera au bout d'un moment
- vous appelerez le service `db-dump.service`
- assurez-vous qu'il fonctionne en utilisant des commandes `systemctl`

```bash
$ sudo systemctl status db-dump
$ sudo systemctl start db-dump
```

➜ **Créez un *timer*** système qui lance le *service* à intervalles réguliers

- le fichier doit être créé dans le même dossier
- le fichier doit porter le même nom
- l'extension doit être `.timer` au lieu de `.service`
- ainsi votre fichier s'appellera `db-dump.timer`
- la syntaxe est la suivante :

```systemd
[Unit]
Description=Run service X

[Timer]
OnCalendar=*-*-* 4:00:00

[Install]
WantedBy=timers.target
```

> [La doc Arch est cool à ce sujet.](https://wiki.archlinux.org/title/systemd/Timers)

- une fois le fichier créé :

```bash
# demander au système de lire le contenu des dossiers de config
# il découvrira notre nouveau timer
$ sudo systemctl daemon-reload

# on peut désormais interagir avec le timer
$ sudo systemctl start db-dump.timer
$ sudo systemctl enable db-dump.timer
$ sudo systemctl status db-dump.timer

# il apparaîtra quand on demande au système de lister tous les timers
$ sudo systemctl list-timers
```

➜ **Tester la restauration des données** sinon ça sert à rien :)

- livrez-moi la suite de commande que vous utiliseriez pour restaurer les données dans une version antérieure