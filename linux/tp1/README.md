# TP1 : (re)Familiaration avec un système GNU/Linux

## Sommaire

- [TP1 : (re)Familiaration avec un système GNU/Linux](#tp1--refamiliaration-avec-un-système-gnulinux)
  - [Sommaire](#sommaire)
  - [0. Préparation de la machine](#0-préparation-de-la-machine)
  - [I. Utilisateurs](#i-utilisateurs)
    - [1. Création et configuration](#1-création-et-configuration)
    - [2. SSH](#2-ssh)
  - [II. Partitionnement](#ii-partitionnement)
    - [1. Préparation de la VM](#1-préparation-de-la-vm)
    - [2. Partitionnement](#2-partitionnement)
  - [III. Gestion de services](#iii-gestion-de-services)
  - [1. Interaction avec un service existant](#1-interaction-avec-un-service-existant)
  - [2. Création de service](#2-création-de-service)
    - [A. Unité simpliste](#a-unité-simpliste)
    - [B. Modification de l'unité](#b-modification-de-lunité)

## 0. Préparation de la machine

🌞 **Setup de deux machines Rocky Linux configurées de façon basique.**

- **un accès internet (via la carte NAT)**
```
[user@node1 ~]$ ping 8.8.8.8
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=63 time=22.8 ms
^C
--- 8.8.8.8 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 22.831/22.831/22.831/0.000 ms
```

```
[user@node2 ~]$ ping 8.8.8.8
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=63 time=22.8 ms
^C
--- 8.8.8.8 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 22.758/22.758/22.758/0.000 ms
```

- **un accès à un réseau local** (les deux machines peuvent se `ping`) (via la carte Host-Only)
```
[user@node1 ~]$ ping 10.101.1.11
PING 10.101.1.11 (10.101.1.11) 56(84) bytes of data.
64 bytes from 10.101.1.11: icmp_seq=1 ttl=64 time=0.034 ms
^C
--- 10.101.1.11 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.034/0.034/0.034/0.000 ms
```

```
[user@node2 ~]$ ping 10.101.1.12
PING 10.101.1.12 (10.101.1.12) 56(84) bytes of data.
64 bytes from 10.101.1.12: icmp_seq=1 ttl=64 time=0.335 ms
^C
--- 10.101.1.12 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2031ms
rtt min/avg/max/mdev = 0.108/0.184/0.335/0.106 ms
```
- **vous n'utilisez QUE `ssh` pour administrer les machines**
```
 ╭─gammray@manjaro in ~ took 3ms
 ╰─λ ssh john
    user@10.101.1.11's password: 
    Last login: Mon Nov 14 12:42:17 2022 from 10.101.1.1
 [user@node1 ~]$ 
```
- **les machines doivent avoir un nom**

```
[user@node1 ~]$ hostname
node1.tp1.b2
```

```
[user@node2 ~]$ hostname
node2.tp1.b2
```

- **utiliser `1.1.1.1` comme serveur DNS**

```
[user@node1 ~]$ dig ynov.com
  [...]
;; QUESTION SECTION:
;ynov.com.      IN  A

;; ANSWER SECTION:
ynov.com.   300 IN  A 104.26.10.233
ynov.com.   300 IN  A 172.67.74.226
ynov.com.   300 IN  A 104.26.11.233

;; Query time: 17 msec
;; SERVER: 1.1.1.1#53(1.1.1.1)
;; WHEN: Mon Nov 14 15:35:05 CET 2022
;; MSG SIZE  rcvd: 85
```
Réponse: `ynov.com.   300 IN  A 104.26.10.233`  
DNS: `;; SERVER: 1.1.1.1#53(1.1.1.1)`

- **les machines doivent pouvoir se joindre par leurs noms respectifs**
```
[user@node1 ~]$ ping node2 -c 1
PING node2 (10.101.1.12) 56(84) bytes of data.
64 bytes from node2 (10.101.1.12): icmp_seq=1 ttl=64 time=0.999 ms

--- node2 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
```

```
[user@node2 ~]$ ping node1 -c 1
PING node1 (10.101.1.11) 56(84) bytes of data.
64 bytes from node1 (10.101.1.11): icmp_seq=1 ttl=64 time=1.21 ms

--- node1 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms

```

- **le pare-feu est configuré pour bloquer toutes les connexions exceptées celles qui sont nécessaires**

```
[user@node1 ~]$ sudo firewall-cmd --list-all
public (active)
  target: default
  icmp-block-inversion: no
  interfaces: enp0s3 enp0s8
  sources: 
  services: cockpit dhcpv6-client ssh
  ports: 
  protocols: 
  forward: yes
  masquerade: no
  forward-ports: 
  source-ports: 
  icmp-blocks: 
  rich rules: 
[user@node1 ~]$ sudo firewall-cmd --zone=public --remove-service=cockpit
success
[user@node1 ~]$ sudo firewall-cmd --zone=public --remove-service=dhcpv6-client
success
[user@node1 ~]$ ping node2 -c 1
PING node2 (10.101.1.12) 56(84) bytes of data.
64 bytes from node2 (10.101.1.12): icmp_seq=1 ttl=64 time=0.440 ms

--- node2 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.440/0.440/0.440/0.000 ms
[user@node1 ~]$ sudo firewall-cmd --zone=public --list-all | grep services
  services: ssh
[user@node1 ~]$ sudo firewall-cmd --runtime-to-permanent
success
```

Same process pour node2

```
[user@node2 ~]$ sudo firewall-cmd --zone=public --list-all | grep services
  services: ssh
```

| Name               | IP            |
|--------------------|---------------|
| 🖥️ `node1.tp1.b2` | `10.101.1.11` |
| 🖥️ `node2.tp1.b2` | `10.101.1.12` |
| Votre hôte         | `10.101.1.1`  |

## I. Utilisateurs
### 1. Création et configuration

*toutes les commandes sont effectués en double sur les deux machines*

🌞 **Ajouter un utilisateur à la machine**, qui sera dédié à son administration

```
[user@node1 ~]$ sudo useradd john -d /home/john_the_admin -s /bin/bash
[user@node1 ~]$ sudo passwd john
```
```
[john@node1 ~]$ cat /etc/passwd | grep john
john:x:1001:1001::/home/john_the_admin:/bin/bash
```

(`bob` pour la deuxième machine)

🌞 **Créer un nouveau groupe `admins`** qui contiendra les utilisateurs de la machine ayant accès aux droits de `root` *via* la commande `sudo`.

```
[user@node1 ~]$ sudo groupadd admins
```
```
[user@node1 ~]$ sudo cat /etc/sudoers | grep admins
%admins ALL=(ALL)       ALL
```
🌞 **Ajouter votre utilisateur à ce groupe `admins`**

```
[user@node1 ~]$ usermod -aG admins john
```

```
[john@node1 ~]$ sudo -l
[sudo] password for john: 
Matching Defaults entries for john on node1:
    !visiblepw, always_set_home, match_group_by_gid, always_query_group_plugin, env_reset, env_keep="COLORS DISPLAY HOSTNAME HISTSIZE
    KDEDIR LS_COLORS", env_keep+="MAIL PS1 PS2 QTDIR USERNAME LANG LC_ADDRESS LC_CTYPE", env_keep+="LC_COLLATE LC_IDENTIFICATION
    LC_MEASUREMENT LC_MESSAGES", env_keep+="LC_MONETARY LC_NAME LC_NUMERIC LC_PAPER LC_TELEPHONE", env_keep+="LC_TIME LC_ALL LANGUAGE
    LINGUAS _XKB_CHARSET XAUTHORITY", secure_path=/sbin\:/bin\:/usr/sbin\:/usr/bin

User john may run the following commands on node1:
    (ALL) ALL
```

### 2. SSH

🌞 **Pour cela...**

```
 ╭─gammray@manjaro in ~/.ssh 
 ╰─λ ls
.rw-r--r--  459 gammray 14 nov.  13:00 config
.rw------- 2,6k gammray 16 févr. 16:13 id_rsa
.rw-r--r--  569 gammray 16 févr. 16:13 id_rsa.pub
.rw-------  10k gammray 14 nov.  13:00 known_hosts
.rw------- 8,6k gammray 30 sept. 11:42 known_hosts.old
```

🌞 **Assurez vous que la connexion SSH est fonctionnelle**, sans avoir besoin de mot de passe.

```
 ╭─gammray@manjaro in ~/.ssh took 13ms
 ╰─λ ─ ssh-copy-id -i ./id_rsa john@10.101.1.11
/usr/bin/ssh-copy-id: INFO: Source of key(s) to be installed: "./id_rsa.pub"
/usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s), to filter out any that are already installed
/usr/bin/ssh-copy-id: INFO: 1 key(s) remain to be installed -- if you are prompted now it is to install the new keys
john@10.101.1.11's password: 

Number of key(s) added: 1

Now try logging into the machine, with:   "ssh 'john@10.101.1.11'"
and check to make sure that only the key(s) you wanted were added.


 ╭─gammray@manjaro in ~/.ssh took 5s
 ╰─λ ssh john@10.101.1.11
Last login: Mon Nov 14 16:23:10 2022
[john@node1 ~]$ 
```

## II. Partitionnement

### 1. Préparation de la VM

⚠️ **Uniquement sur `node1.tp1.b2`.**

```
[john@node1 ~]$ lsblk
NAME        MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
sda           8:0    0    8G  0 disk 
├─sda1        8:1    0    1G  0 part /boot
└─sda2        8:2    0    7G  0 part 
  ├─rl-root 253:0    0  6.2G  0 lvm  /
  └─rl-swap 253:1    0  820M  0 lvm  [SWAP]
sdb           8:16   0    3G  0 disk 
sdc           8:32   0    3G  0 disk
```

### 2. Partitionnement

⚠️ **Uniquement sur `node1.tp1.b2`.**

🌞 **Utilisez LVM** pour...

```
[john@node1 ~]$ sudo pvcreate /dev/sdb
  Physical volume "/dev/sdb" successfully created.
[john@node1 ~]$ sudo pvcreate /dev/sdc
  Physical volume "/dev/sdc" successfully created.
```
```
[john@node1 ~]$ sudo vgcreate compote /dev/sdb
  Volume group "compote" successfully created
[john@node1 ~]$ sudo vgextend compote /dev/sdc
  Volume group "compote" successfully extended
```

```
[john@node1 ~]$ sudo lvcreate -L 1G compote -n part1
  Logical volume "part1" created.
[john@node1 ~]$ sudo lvcreate -L 1G compote -n part2
  Logical volume "part2" created.
[john@node1 ~]$ sudo lvcreate -L 1G compote -n part3
  Logical volume "part3" created.
[john@node1 ~]$ sudo lvs
  Devices file sys_wwid t10.ATA_____VBOX_HARDDISK___________________________VB158ae404-fe8e2c9e_ PVID Qzkn59GMcn27xUGNlHmmPwixhvgHUBSk last seen on /dev/sda2 not found.
  LV    VG      Attr       LSize Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert
  part1 compote -wi-a----- 1.00g                                                    
  part2 compote -wi-a----- 1.00g                                                    
  part3 compote -wi-a----- 1.00g 
```

```
[john@node1 ~]$ sudo mkfs -t ext4 /dev/compote/part1
  [...]
Allocating group tables: done                            
Writing inode tables: done                            
Creating journal (8192 blocks): done
Writing superblocks and filesystem accounting information: done

[john@node1 ~]$ sudo mkfs -t ext4 /dev/compote/part2
  [...]
Allocating group tables: done                            
Writing inode tables: done                            
Creating journal (8192 blocks): done
Writing superblocks and filesystem accounting information: done

[john@node1 ~]$ sudo mkfs -t ext4 /dev/compote/part3
  [...]
Allocating group tables: done                            
Writing inode tables: done                            
Creating journal (8192 blocks): done
Writing superblocks and filesystem accounting information: done
```

```
[john@node1 ~]$ sudo mkdir /mnt/part1
[john@node1 ~]$ sudo mkdir /mnt/part2
[john@node1 ~]$ sudo mkdir /mnt/part3
[john@node1 ~]$ sudo mount /dev/compote/part1 /mnt/part1
[john@node1 ~]$ sudo mount /dev/compote/part2 /mnt/part2
[john@node1 ~]$ sudo mount -o noexec /dev/compote/part3 /mnt/part3
```

🌞 **Grâce au fichier `/etc/fstab`**, faites en sorte que cette partition soit montée automatiquement au démarrage du système.

```
[john@node1 ~]$ cat /etc/fstab | grep part
UUID=ba050126-1272-43ec-9790-a8949a2f2c0e /mnt/part1 ext4 defaults 0 0
UUID=19456ffa-4f6e-42b9-9f0a-90958cd02d31 /mnt/part2 ext4 defaults 0 0
UUID=bcaec546-796d-41f0-8471-2bade319084d /mnt/part3 ext4 noexec 0 0 
```


## III. Gestion de services

**Référez-vous au mémo pour voir les autres commandes `systemctl` usuelles.**

## 1. Interaction avec un service existant

⚠️ **Uniquement sur `node1.tp1.b2`.**

🌞 **Assurez-vous que...**

```
john@node1 ~]$ sudo systemctl status firewalld
● firewalld.service - firewalld - dynamic firewall daemon
     Loaded: loaded (/usr/lib/systemd/system/firewalld.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2022-11-14 17:21:42 CET; 10min ago
       Docs: man:firewalld(1)
   Main PID: 788 (firewalld)
      Tasks: 2 (limit: 5907)
     Memory: 41.7M
        CPU: 418ms
     CGroup: /system.slice/firewalld.service
             └─788 /usr/bin/python3 -s /usr/sbin/firewalld --nofork --nopid
```

```
[john@node1 ~]$ systemctl list-unit-files | grep enabled | grep firewalld
firewalld.service                          enabled         enabled
```

## 2. Création de service

### A. Unité simpliste

⚠️ **Uniquement sur `node1.tp1.b2`.**

🌞 **Créer un fichier qui définit une unité de service** 

```
[john@node1 ~]$ cat /etc/systemd/system/web.service 
[Unit]
Description=Very simple web service

[Service]
ExecStart=/usr/bin/python3 -m http.server 8888

[Install]
WantedBy=multi-user.target
```

```
[john@node1 ~]$ sudo systemctl daemon-reload
```

```
[john@node1 ~]$ sudo systemctl start web
[john@node1 ~]$ sudo systemctl status web
● web.service - Very simple web service
     Loaded: loaded (/etc/systemd/system/web.service; disabled; vendor preset: disabled)
     Active: active (running) since Mon 2022-11-14 17:37:22 CET; 1s ago
   Main PID: 1051 (python3)
      Tasks: 1 (limit: 5907)
     Memory: 9.2M
        CPU: 53ms
     CGroup: /system.slice/web.service
             └─1051 /usr/bin/python3 -m http.server 8888
```

🌞 **Une fois le service démarré, assurez-vous que pouvez accéder au serveur web**


```
 ╭─gammray@manjaro in repo: linux-reseau-leo/linux on  main [x?] took 5ms
 ╰─λ curl http://10.101.1.11:8888
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Directory listing for /</title>
</head>
<body>
<h1>Directory listing for /</h1>
<hr>
<ul>
<li><a href="afs/">afs/</a></li>
<li><a href="bin/">bin@</a></li>
<li><a href="boot/">boot/</a></li>
<li><a href="dev/">dev/</a></li>
<li><a href="etc/">etc/</a></li>
<li><a href="home/">home/</a></li>
<li><a href="lib/">lib@</a></li>
<li><a href="lib64/">lib64@</a></li>
<li><a href="media/">media/</a></li>
<li><a href="mnt/">mnt/</a></li>
<li><a href="opt/">opt/</a></li>
<li><a href="proc/">proc/</a></li>
<li><a href="root/">root/</a></li>
<li><a href="run/">run/</a></li>
<li><a href="sbin/">sbin@</a></li>
<li><a href="srv/">srv/</a></li>
<li><a href="sys/">sys/</a></li>
<li><a href="tmp/">tmp/</a></li>
<li><a href="usr/">usr/</a></li>
<li><a href="var/">var/</a></li>
</ul>
<hr>
</body>
</html>
```

### B. Modification de l'unité

🌞 **Préparez l'environnement pour exécuter le mini serveur web Python**

```
[web@node1 moew]$ ls -all
total 4
drwxr-xr-x. 2 web  web  24 Nov 14 17:42 .
drwxr-xr-x. 3 root root 18 Nov 14 17:41 ..
-rw-rw-r--. 1 web  web  14 Nov 14 17:42 index.html
```

🌞 **Modifiez l'unité de service `web.service` créée précédemment en ajoutant les clauses**

```
[john@node1 moew]$ cat /etc/systemd/system/web.service 
[Unit]
Description=Very simple web service

[Service]
User=web
WorkingDirectory=/var/www/moew
ExecStart=/usr/bin/python3 -m http.server 8888

[Install]
WantedBy=multi-user.target
```

```
[john@node1 moew]$ sudo systemctl daemon-reload
[john@node1 moew]$ sudo systemctl restart web.service
[john@node1 moew]$ sudo systemctl status web.service
● web.service - Very simple web service
     Loaded: loaded (/etc/systemd/system/web.service; disabled; vendor preset: disabled)
     Active: active (running) since Mon 2022-11-14 17:44:25 CET; 5s ago
   Main PID: 1191 (python3)
      Tasks: 1 (limit: 5907)
     Memory: 9.0M
        CPU: 50ms
     CGroup: /system.slice/web.service
             └─1191 /usr/bin/python3 -m http.server 8888
```

🌞 **Vérifiez le bon fonctionnement avec une commande `curl`**

```
 ╭─gammray@manjaro in repo: linux-reseau-leo/linux on  main [x?] took 5ms
 ╰─λ curl http://10.101.1.11:8888
<h1>MOEW</h1>
```