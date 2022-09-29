# TP2 : Ethernet, IP, et ARP

Dans ce TP on va approfondir trois protocoles, qu'on a survolé jusqu'alors :

- **IPv4** *(Internet Protocol Version 4)* : gestion des adresses IP
  - on va aussi parler d'ICMP, de DHCP, bref de tous les potes d'IP quoi !
- **Ethernet** : gestion des adresses MAC
- **ARP** *(Address Resolution Protocol)* : permet de trouver l'adresse MAC de quelqu'un sur notre réseau dont on connaît l'adresse IP


# Sommaire

- [TP2 : Ethernet, IP, et ARP](#tp2--ethernet-ip-et-arp)
- [Sommaire](#sommaire)
- [0. Prérequis](#0-prérequis)
- [I. Setup IP](#i-setup-ip)
- [II. ARP my bro](#ii-arp-my-bro)
- [II.5 Interlude hackerzz](#ii5-interlude-hackerzz)
- [III. DHCP you too my brooo](#iii-dhcp-you-too-my-brooo)
- [IV. Avant-goût TCP et UDP](#iv-avant-goût-tcp-et-udp)

# 0. Prérequis

# I. Setup IP

Le lab, il vous faut deux machine : 

- les deux machines doivent être connectées physiquement
- vous devez choisir vous-mêmes les IPs à attribuer sur les interfaces réseau, les contraintes :
  - IPs privées (évidemment n_n)
  - dans un réseau qui peut contenir au moins 38 adresses IP (il faut donc choisir un masque adapté)
  - oui c'est random, on s'exerce c'est tout, p'tit jog en se levant
  - le masque choisi doit être le plus grand possible (le plus proche de 32 possible) afin que le réseau soit le plus petit possible

🌞 **Mettez en place une configuration réseau fonctionnelle entre les deux machines**
PC 1:
```
$ ip a 
  [...]
  inet 10.42.0.1/26 brd 10.42.0.63
  [...]
```
PC 2:
```
$ ifconfig
  [...]
  inet 10.42.0.2 netmask 0xffffffc0 broadcast 10.42.0.63
  [...]  
```

Le masque : ``255.255.255.192``
L'adresse réseau : ``10.42.0.0/26``
L'adresse de broadcast : ``10.42.0.63/26``

```
$ cat /etc/systemd/network/wlp0s20f3.network
[Match]
Name=wlp0s20f3

[Network]
Address=10.42.0.1/26
Gateway=10.42.0.1
DNS=8.8.8.8
```

🌞 **Prouvez que la connexion est fonctionnelle entre les deux machines**

```
$ ping 10.42.0.2
PING 10.42.0.2 (10.42.0.2) 56(84) bytes of data.
64 bytes from 10.42.0.2: icmp_seq=1 ttl=64 time=0.578 ms
64 bytes from 10.42.0.2: icmp_seq=2 ttl=64 time=0.749 ms
```

🌞 **Wireshark it**

Le premier paquet ICMP est de type 8, un "Echo Request", le deuxième est de type 0, un "Echo reply"

🦈 **PCAP qui contient les paquets ICMP qui vous ont permis d'identifier les types ICMP**

[pcap icmp ici](./pcap/icmp.pcapng)

# II. ARP my bro

ARP permet, pour rappel, de résoudre la situation suivante :

- pour communiquer avec quelqu'un dans un LAN, il **FAUT** connaître son adresse MAC
- on admet un PC1 et un PC2 dans le même LAN :
  - PC1 veut joindre PC2
  - PC1 et PC2 ont une IP correctement définie
  - PC1 a besoin de connaître la MAC de PC2 pour lui envoyer des messages
  - **dans cette situation, PC1 va utilise le protocole ARP pour connaître la MAC de PC2**
  - une fois que PC1 connaît la mac de PC2, il l'enregistre dans sa **table ARP**

🌞 **Check the ARP table**

```
$ arp -n
Address                  HWtype  HWaddress           Flags Mask            Iface
10.42.0.2                ether   a0:ce:c8:ee:d4:14   C                     enp8s0
10.33.19.254             ether   00:c0:e7:e0:04:4e   C                     wlp0s20f3
```
La MAC de mon binome : ``a0:ce:c8:ee:d4:14``
La MAC de la gateway : ``00:c0:e7:e0:04:4e``

🌞 **Manipuler la table ARP**

```
$ sudo ip n flush all
$ arp -n
$ 
$
```
```
$ sudo ip n flush all ; ping 10.42.0.2 -c 1 ; arp -n
PING 10.42.0.2 (10.42.0.2) 56(84) bytes of data.
64 bytes from 10.42.0.2: icmp_seq=1 ttl=64 time=0.860 ms

--- 10.42.0.2 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.860/0.860/0.860/0.000 ms
Address                  HWtype  HWaddress           Flags Mask            Iface
10.42.0.2                ether   a0:ce:c8:ee:d4:14   C                     enp8s0
```

J'ai mit les 3 commandes à la suite, car en le faisant à la main, le routeur Ynov réapparaissait dans la table.

> Les échanges ARP sont effectuées automatiquement par votre machine lorsqu'elle essaie de joindre une machine sur le même LAN qu'elle. Si la MAC du destinataire n'est pas déjà dans la table ARP, alors un échange ARP sera déclenché.

🌞 **Wireshark it**

Dans le terminal:
```
$ sudo ip n flush all ; ping 10.42.0.2
```

-Trame 1:

    - Adresse source : 08:97:98:d4:fb:50  (PC 1)
    - Adresse dest   : ff:ff:ff:ff:ff:ff  (BROADCAST)

-Trame 2:

    -Adresse source : a0:ce:c8:ee:d4:14  (PC 2)
    -Adresse dest   : 08:97:98:d4:fb:50  (PC 1)

🦈 **PCAP qui contient les trames ARP**

[le pcap du arp](./pcap/arp.pcapng)

> L'échange ARP est constitué de deux trames : un ARP broadcast et un ARP reply.

# II.5 Interlude hackerzz

![](./images/hackerz.png)

# III. DHCP you too my brooo


*DHCP* pour *Dynamic Host Configuration Protocol* est notre p'tit pote qui nous file des IP quand on arrive dans un réseau, parce que c'est chiant de le faire à la main :)

Quand on arrive dans un réseau, notre PC contacte un serveur DHCP, et récupère généralement 3 infos :

- **1.** une IP à utiliser
- **2.** l'adresse IP de la passerelle du réseau
- **3.** l'adresse d'un serveur DNS joignable depuis ce réseau

L'échange DHCP consiste en 4 trames : DORA, que je vous laisse google vous-mêmes : D

🌞 **Wireshark it**

-Trame 1:

    - Adresse source : 44:af:28:c4:66:70  (ME)
    - Adresse dest   : ff:ff:ff:ff:ff:ff  (BROADCAST)

-Trame 2:

    -Adresse source : 00:c0:e7:e0:04:4e  (DHCP SERVER)
    -Adresse dest   : 44:af:28:c4:66:70  (ME)

-Trame 3:

    -Adresse source : 44:af:28:c4:66:70  (ME)
    -Adresse dest   : 00:c0:e7:e0:04:4e  (DHCP SERVER)

-Trame 4:

    -Adresse source : 00:c0:e7:e0:04:4e  (DHCP SERVER)
    -Adresse dest   : 44:af:28:c4:66:70  (ME) 

**1** L'ip proposée se trouve dans les données de la trame 2. Dans wireshark : ``Dynamic Host Configuration Protocol (Offer) > Your (client) IP address = 10.33.18.180``

**2** L'ip de la passerelle se trouve aussi dans la trame 2. Dans wireshark : ``Dynamic Host Configuration Protocol (Offer) > Option : (3) Router > Router = 10.33.19.254``

**3** L'ip d'un serveur DNS aussi dans la trame 2. Dans wireshark : ``Dynamic Host Configuration Protocol (Offer) > Option : (6) Domain Name Server > Domaine Name Server = 8.8.8.8``


🦈 **PCAP qui contient l'échange DORA**

[le pcap dhcp](./pcap/dhcp.pcapng)


> **Soucis** : l'échange DHCP ne se produit qu'à la première connexion. **Pour forcer un échange DHCP**, ça dépend de votre OS. Sur **GNU/Linux**, avec `dhclient` ça se fait bien. Sur **Windows**, le plus simple reste de définir une IP statique pourrie sur la carte réseau, se déconnecter du réseau, remettre en DHCP, se reconnecter au réseau. Sur **MacOS**, je connais peu mais Internet dit qu'c'est po si compliqué, appelez moi si besoin.

# IV. Avant-goût TCP et UDP

TCP et UDP ce sont les deux protocoles qui utilisent des ports. Si on veut accéder à un service, sur un serveur, comme un site web :

- il faut pouvoir joindre en terme d'IP le correspondant
  - on teste que ça fonctionne avec un `ping` généralement
- il faut que le serveur fasse tourner un programme qu'on appelle "service" ou "serveur"
  - le service "écoute" sur un port TCP ou UDP : il attend la connexion d'un client
- le client **connaît par avance** le port TCP ou UDP sur lequel le service écoute
- en utilisant l'IP et le port, il peut se connecter au service en utilisant un moyen adapté :
  - un navigateur web pour un site web
  - un `ncat` pour se connecter à un autre `ncat`
  - et plein d'autres, **de façon générale on parle d'un client, et d'un serveur**

---

🌞 **Wireshark it**

En regardant la vidéo : ``catJAM DANCING FOR 10 HOURS``, on voit sur wireshark des paquets provenant de mon IP vers l'ip ``77.136.192.86`` et vers le port ``443``

🦈 **PCAP qui contient un extrait de l'échange qui vous a permis d'identifier les infos**

[catJam pcap](./pcap/catjam.pcapng)


![](https://c.tenor.com/82Rr2PPBCtIAAAAd/cat-jam-cat.gif)