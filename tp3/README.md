# TP3 : On va router des trucs

Au menu de ce TP, on va revoir un peu ARP et IP histoire de **se mettre en jambes dans un environnement avec des VMs**.

Puis on mettra en place **un routage simple, pour permettre à deux LANs de communiquer**.

## Sommaire

- [TP3 : On va router des trucs](#tp3--on-va-router-des-trucs)
  - [Sommaire](#sommaire)
  - [0. Prérequis](#0-prérequis)
  - [I. ARP](#i-arp)
    - [1. Echange ARP](#1-echange-arp)
    - [2. Analyse de trames](#2-analyse-de-trames)
  - [II. Routage](#ii-routage)
    - [1. Mise en place du routage](#1-mise-en-place-du-routage)
    - [2. Analyse de trames](#2-analyse-de-trames-1)
    - [3. Accès internet](#3-accès-internet)
  - [III. DHCP](#iii-dhcp)
    - [1. Mise en place du serveur DHCP](#1-mise-en-place-du-serveur-dhcp)
    - [2. Analyse de trames](#2-analyse-de-trames-2)

## 0. Prérequis

## I. ARP

Première partie simple, on va avoir besoin de 2 VMs.

| Machine  | `10.3.1.0/24` |
|----------|---------------|
| `john`   | `10.3.1.11`   |
| `marcel` | `10.3.1.12`   |

```schema
   john               marcel
  ┌─────┐             ┌─────┐
  │     │    ┌───┐    │     │
  │     ├────┤ho1├────┤     │
  └─────┘    └───┘    └─────┘
```

> Référez-vous au [mémo Réseau Rocky](../../cours/memo/rocky_network.md) pour connaître les commandes nécessaire à la réalisation de cette partie.

### 1. Echange ARP

🌞**Générer des requêtes ARP**

```
[marcel@localhost ~]$ ip n 
10.3.1.1 dev enp0s3 lladdr 0a:00:27:00:00:01 REACHABLE

[marcel@localhost ~]$ ping 10.3.1.11
PING 10.3.1.11 (10.3.1.11) 56(84) bytes of data.
64 bytes from 10.3.1.11: icmp_seq=1 ttl=64 time=1.82 ms
^C
--- 10.3.1.11 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 1.818/1.818/1.818/0.000 ms

[marcel@localhost ~]$ ip n 
10.3.1.11 dev enp0s3 lladdr 08:00:27:72:3a:1d REACHABLE
10.3.1.1 dev enp0s3 lladdr 0a:00:27:00:00:01 REACHABLE
```
```
[john@localhost ~]$ ip n
10.3.1.12 dev enp0s3 lladdr 08:00:27:14:58:8c STALE
10.3.1.1 dev enp0s3 lladdr 0a:00:27:00:00:01 REACHABLE
```
MAC John : ``08:00:27:72:3a:1d``
MAC Marcel : ``08:00:27:14:58:8c``

```
[marcel@localhost ~]$ ip a show enp0s3
2: enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 08:00:27:14:58:8c brd ff:ff:ff:ff:ff:ff
```

### 2. Analyse de trames

🌞**Analyse de trames**

```
[marcel@localhost ~]$ sudo ip n flush all
[marcel@localhost ~]$ sudo tcpdump arp or icmp -n -i enp0s3 -w tp2_arp.pcapng
```

🦈 **Capture réseau [`tp2_arp.pcapng`](./pcap/tp2_arp.pcapng)** qui contient un ARP request et un ARP reply

## II. Routage

Vous aurez besoin de 3 VMs pour cette partie. **Réutilisez les deux VMs précédentes.**

| Machine  | `10.3.1.0/24` | `10.3.2.0/24` |
|----------|---------------|---------------|
| `router` | `10.3.1.254`  | `10.3.2.254`  |
| `john`   | `10.3.1.11`   | no            |
| `marcel` | no            | `10.3.2.12`   |

> Je les appelés `marcel` et `john` PASKON EN A MAR des noms nuls en réseau 🌻

```schema
   john                router              marcel
  ┌─────┐             ┌─────┐             ┌─────┐
  │     │    ┌───┐    │     │    ┌───┐    │     │
  │     ├────┤ho1├────┤     ├────┤ho2├────┤     │
  └─────┘    └───┘    └─────┘    └───┘    └─────┘
```

```
[marcel@localhost ~]$ ping 10.3.1.11
ping: connect: Network is unreachable
```

### 1. Mise en place du routage

🌞**Activer le routage sur le noeud `router`**

```
[router@localhost ~]$ sudo firewall-cmd --get-active-zone
public
  interfaces: enp0s3 enp0s8
[router@localhost ~]$ sudo firewall-cmd --add-masquerade --zone=public
success
[router@localhost ~]$ sudo firewall-cmd --add-masquerade --zone=public --permanent
success
[router@localhost ~]$ 
```

🌞**Ajouter les routes statiques nécessaires pour que `john` et `marcel` puissent se `ping`**

```
marcel@localhost ~]$ sudo ip route add 10.3.1.0/24 via 10.3.2.254 dev enp0s3
[marcel@localhost ~]$ sudo systemctl restart NetworkManager
[marcel@localhost ~]$ ping 10.3.1.11 -c 1
PING 10.3.1.11 (10.3.1.11) 56(84) bytes of data.
64 bytes from 10.3.1.11: icmp_seq=1 ttl=63 time=0.877 ms
```

```
[john@localhost ~]$ sudo ip route add 10.3.2.0/24 via 10.3.1.254 dev enp0s3
[sudo] password for john: 
[john@localhost ~]$ ping 10.3.2.12 -c 1
PING 10.3.2.12 (10.3.2.12) 56(84) bytes of data.
64 bytes from 10.3.2.12: icmp_seq=1 ttl=63 time=0.853 ms
```

### 2. Analyse de trames

🌞**Analyse des échanges ARP**


Déduction :
John -> ARP Request avec MAC dest router et IP dest marcel -> router -> ARP Request avec MAC src router -> Marcel
Marcel -> ARP Reply avec MAC des router et IP dest John -> router -> ARP Reply avec MAC src router -> John

Observation:
```
| ordre | type trame  | IP source  | MAC source                   | IP destination | MAC destination             |
|-------|-------------|------------|------------------------------|----------------|-----------------------------|
| 1     | Requête ARP | x          | `router` `08:00:27:c2:f9:89` | x              | `Broadcast` `FF:FF:FF:FF:FF`|
| 2     | Réponse ARP | x          | `marcel` `08:00:27:f1:c6:e3` | x              | `router` `08:00:27:c2:f9:89`|
| 4     | Ping        | 10.3.2.254 | `router` `08:00:27:c2:f9:89` | 10.3.2.12      | `marcel` `08:00:27:f1:c6:e3`|
| 4     | Pong        | 10.3.2.12  | `marcel` `08:00:27:f1:c6:e3` | 10.3.2.254     | `router` `08:00:27:c2:f9:89`|
```

j'ai pas réussit à formater le tableau :(

🦈 **Capture réseau [`tp2_routage_marcel.pcapng`](./pcp/tp2_routage_marcel.pcapng)**

### 3. Accès internet

🌞**Donnez un accès internet à vos machines**

```
[router@localhost ~]$ ping 8.8.8.8 -c 1
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=63 time=13.6 ms
```
```
[john@localhost ~]$ sudo ip route add default via 10.3.1.254 dev enp0s3
[john@localhost ~]$ ping 8.8.8.8 -c 1
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=61 time=14.4 ms
```

```
[marcel@localhost ~]$ sudo ip route add default via 10.3.2.254 dev enp0s3
[marcel@localhost ~]$ ping 8.8.8.8 -c 1
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=61 time=16.2 ms
```

```
[marcel@localhost ~]$ cat /etc/sysconfig/network-scripts/ifcfg-enp0s3
  [...]
DNS1=8.8.8.8

[marcel@localhost ~]$ dig google.com
  [...]
;; QUESTION SECTION:
;google.com.      IN  A

;; ANSWER SECTION:
google.com.   226 IN  A 142.250.201.174
  [...]

[marcel@localhost ~]$ ping -c 1 google.com
PING google.com (142.250.179.78) 56(84) bytes of data.
64 bytes from par21s19-in-f14.1e100.net (142.250.179.78): icmp_seq=1 ttl=61 time=13.6 ms
```

```
[john@localhost ~]$ ping google.com
PING google.com (142.250.179.78) 56(84) bytes of data.
64 bytes from par21s19-in-f14.1e100.net (142.250.179.78): icmp_seq=1 ttl=61 time=12.9 ms
```

🌞**Analyse de trames**


| ordre | type trame | IP source          | MAC source                | IP destination    | MAC destination          |
|-------|------------|--------------------|---------------------------|-------------------|--------------------------|
| 1     | ping       | `john` `10.3.1.11` | `john` `00:27:72:3a:1d`   | `8.8.8.8`         | `router` `00:27:79:94:9f`|
| 2     | pong       | `8.8.8.8`          | `router` `00:27:79:94:9f` | `john` `10.3.1.11`| `john` `00:27:72:3a:1d`  |

🦈 **Capture réseau [`tp2_routage_internet.pcapng`](./pcap/tp2_routage_internet.pcapng)**

## III. DHCP

On reprend la config précédente, et on ajoutera à la fin de cette partie une 4ème machine pour effectuer des tests.

| Machine  | `10.3.1.0/24`              | `10.3.2.0/24` |
|----------|----------------------------|---------------|
| `router` | `10.3.1.254`               | `10.3.2.254`  |
| `john`   | `10.3.1.11`                | no            |
| `bob`    | oui mais pas d'IP statique | no            |
| `marcel` | no                         | `10.3.2.12`   |

```schema
   john               router              marcel
  ┌─────┐             ┌─────┐             ┌─────┐
  │     │    ┌───┐    │     │    ┌───┐    │     │
  │     ├────┤ho1├────┤     ├────┤ho2├────┤     │
  └─────┘    └─┬─┘    └─────┘    └───┘    └─────┘
   bob         │
  ┌─────┐      │
  │     │      │
  │     ├──────┘
  └─────┘
```

### 1. Mise en place du serveur DHCP

🌞**Sur la machine `john`, vous installerez et configurerez un serveur DHCP** (go Google "rocky linux dhcp server").

```
[john@localhost ~]$ sudo dnf install dhcp-server
  [...]
[john@localhost ~]$ sudo cp /etc/dhcp/dhcpd.conf /etc/dhcp/dhcpd.conf.bak
[john@localhost ~]$ sudo vim /etc/dhcp/dhcpd.conf
  [...]
[john@localhost ~]$ sudo cat /etc/dhcp/dhcpd.conf
  [...]
default-lease-time 900;
max-lease-time 10800;

authoritative;

subnet 10.3.1.0 netmask 255.255.255.0 {
  range 10.3.1.50 10.3.1.250;
  option broadcast-address 10.3.1.255;
}

[john@localhost ~]$ sudo firewall-cmd --permanent --add-port=67/udp
[john@localhost ~]$ sudo systemctl enable --now dhcpd
```

```
[bob@localhost ~]$ sudo dhclient
[bob@localhost ~]$ ip a show enp0s3
2: enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 08:00:27:14:d1:02 brd ff:ff:ff:ff:ff:ff
    inet 10.3.1.50/24 brd 10.3.1.255 scope global dynamic enp0s3
       valid_lft 781sec preferred_lft 781sec
    inet6 fe80::a00:27ff:fe14:d102/64 scope link noprefixroute 
       valid_lft forever preferred_lft forever
```

> Il est possible d'utilise la commande `dhclient` pour forcer à la main, depuis la ligne de commande, la demande d'une IP en DHCP, ou renouveler complètement l'échange DHCP (voir `dhclient -h` puis call me et/ou Google si besoin d'aide).

🌞**Améliorer la configuration du DHCP**

```
[john@localhost ~]$ sudo cat /etc/dhcp/dhcpd.conf
  [...]
default-lease-time 900;
max-lease-time 10800;

authoritative;

subnet 10.3.1.0 netmask 255.255.255.0 {
  range 10.3.1.50 10.3.1.250;
  option broadcast-address 10.3.1.255;

  option routers 10.3.1.254;
  option domain-name-servers 8.8.8.8;
}
```

```
[bob@localhost ~]$ sudo dhclient -r
[bob@localhost ~]$ sudo dhclient
[bob@localhost ~]$ ip a
2: enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 08:00:27:14:d1:02 brd ff:ff:ff:ff:ff:ff
    inet 10.3.1.53/24 brd 10.3.1.255 scope global dynamic enp0s3
       valid_lft 943sec preferred_lft 943sec
    inet6 fe80::a00:27ff:fe14:d102/64 scope link noprefixroute 
       valid_lft forever preferred_lft forever

[bob@localhost ~]$ ping 10.3.1.254
PING 10.3.1.254 (10.3.1.254) 56(84) bytes of data.
64 bytes from 10.3.1.254: icmp_seq=1 ttl=64 time=0.555 ms
  [...]

[bob@localhost ~]$ ip route show
default via 10.3.1.254 dev enp0s3 
10.3.1.0/24 dev enp0s3 proto kernel scope link src 10.3.1.53 

[bob@localhost ~]$ ping 10.3.1.11
PING 10.3.1.11 (10.3.1.11) 56(84) bytes of data.
64 bytes from 10.3.1.11: icmp_seq=1 ttl=64 time=0.702 ms
  [...]

[bob@localhost ~]$ dig goole.com
  [...]
;; QUESTION SECTION:
;goole.com.     IN  A

;; ANSWER SECTION:
goole.com.    3600  IN  A 217.160.0.201
  [...]

[bob@localhost ~]$ ping google.com
PING google.com (142.250.179.110) 56(84) bytes of data.
64 bytes from par21s20-in-f14.1e100.net (142.250.179.110): icmp_seq=1 ttl=61 time=12.3 ms
```

### 2. Analyse de trames

🌞**Analyse de trames**

- lancer une capture à l'aide de `tcpdump` afin de capturer un échange DHCP
- demander une nouvelle IP afin de générer un échange DHCP
- exportez le fichier `.pcapng`

🦈 **Capture réseau [`tp2_dhcp.pcapng`](./pcap/tp2_dhcp.pcapng)**