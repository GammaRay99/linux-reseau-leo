# TP4 : TCP, UDP et services réseau

Dans ce TP on va explorer un peu les protocoles TCP et UDP. On va aussi mettre en place des services qui font appel à ces protocoles.

# 0. Prérequis
# I. First steps

Faites-vous un petit top 5 des applications que vous utilisez sur votre PC souvent, des applications qui utilisent le réseau : un site que vous visitez souvent, un jeu en ligne, Spotify, j'sais po moi, n'importe.

**Discord:**

SRC : 10.33.18.180:57570
DST : 162.159.135.234:443
PROTOCOL : TCP

[pcap](./pcap/discord.pcapng)

```
$ ss -ntp
ESTAB   0    0    10.33.18.180:57570    162.159.135.234:443   users:(("Discord",pid=2274,fd=39))                                       
```

**Firefox:**

SRC : 10.33.18.180:43114
DST : 104.16.249.249:443
PROTOCOL : TCP

[pcap](./pcap/firefox.pcapng)

```
$ sudo ss -npt
[...]   
ESTAB  0  0    10.33.18.180:43114    104.16.249.249:443    users:(("python",pid=15030,fd=126),("firefox",pid=14771,fd=126))
[...]
```

**NetCat:**

SRC : 127.0.0.1:12345   (je l'ai fait en local mais avec l'ip ynov ça aurait été les 2 mêmes aussi)
DST : 127.0.0.1:57392
PROTOCOL : TCP

[pcap](./pcap/netcat.pcapng)

```
$  sudo ss -ntp
ESTAB 0   0   127.0.0.1:12345    127.0.0.1:57392  users:(("nc",pid=16522,fd=4)) 
```

**packet manager (pacman):**

SRC : 10.33.18.180:56442 & 10.33.18.180:50026
DST : 104.236.0.104:443 & 172.67.185.210:443
PROTOCOL : TCP

[pcap](./pcap/pacman.pcapng)

```
$ sudo ss -npt
ESTAB    0    0     10.33.18.180:56442    104.236.0.104:443     users:(("pacman",pid=17054,fd=9))
ESTAB    0    0     10.33.18.180:50026    172.67.185.210:443    users:(("pacman",pid=17054,fd=8))
```

**Youtube:**

SRC : 10.33.18.180:48412
DST : 173.194.0.137:443
PROTOCOL : UDP

[pcap](./pcap/youtube.com)

```
$ sudo ss -npt
[...]  
ESTAB  0    0    10.33.18.180:48412     173.194.0.137:443     users:(("firefox",pid=18173,fd=231))
```

# II. Mise en place

## 1. SSH

Connectez-vous en SSH à votre VM.

🌞 **Examinez le trafic dans Wireshark**

- donnez un sens aux infos devant vos yeux, capturez un peu de trafic, et coupez la capture, sélectionnez une trame random et regardez dedans, vous laissez pas brainfuck par Wireshark n_n

- **déterminez si SSH utilise TCP ou UDP**
  - pareil réfléchissez-y deux minutes, logique qu'on utilise pas UDP non ?
   ``TCP (TLS) pour chiffrer la communication + pour al fiabilité``
- **repérez le *3-Way Handshake* à l'établissement de la connexion**
  - c'est le `SYN` `SYNACK` `ACK`
- **repérez le FIN FINACK à la fin d'une connexion**
- entre le *3-way handshake* et l'échange `FIN`, c'est juste une bouillie de caca chiffré, dans un tunnel TCP

🌞 **Demandez aux OS**

Depuis ma machine:

```
$ sudo ss -npt  
ESTAB    0     0     10.3.1.1:50892     10.3.1.11:22       users:(("ssh",pid=19647,fd=3))
```

Depuis la VM:

```
[john@localhost ~]$ sudo ss -npt 
ESTAB    0    0      10.3.1.11:22       10.3.1.1:50892     users:(("sshd",pid=884,fd=4),("sshd",pid=871,fd=4))
```

🦈 **Je veux une capture clean avec le 3-way handshake, un peu de trafic au milieu et une fin de connexion**

[cadeau le pcap](./pcap.ssh.pcapng)

## 2. NFS

Allumez une deuxième VM Linux pour cette partie.

Vous allez installer un serveur NFS. Un serveur NFS c'est juste un programme qui écoute sur un port (comme toujours en fait, oèoèoè) et qui propose aux clients d'accéder à des dossiers à travers le réseau.

Une de vos VMs portera donc le serveur NFS, et l'autre utilisera un dossier à travers le réseau.

🌞 **Mettez en place un petit serveur NFS sur l'une des deux VMs**

C'est bon :)

🌞 **Wireshark it !**

[le pcap](./pcap/needforspeed.pcap)

le port est 2049

🌞 **Demandez aux OS**

```
[john@localhost salut]$ sudo ss -npt
ESTAB  0       0         10.3.1.11:752    192.168.64.2:2049
```

🦈 **Et vous me remettez une capture de trafic NFS** la plus complète possible. J'ai pas dit que je voulais le plus de trames possible, mais juste, ce qu'il faut pour avoir un max d'infos sur le trafic

## 3. DNS

🌞 Utilisez une commande pour effectuer une requête DNS depuis une des VMs

- capturez le trafic avec un `tcpdump`
- déterminez le port et l'IP du serveur DNS auquel vous vous connectez

