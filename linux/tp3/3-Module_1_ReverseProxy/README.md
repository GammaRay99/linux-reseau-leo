# Module 1 : Reverse Proxy


## Sommaire

- [Module 1 : Reverse Proxy](#module-1--reverse-proxy)
  - [Sommaire](#sommaire)
- [I. Intro](#i-intro)
- [II. Setup](#ii-setup)
- [III. HTTPS](#iii-https)

# I. Intro

# II. Setup

🖥️ **VM `proxy.tp3.linux`**

**N'oubliez pas de dérouler la [📝**checklist**📝](../../2/README.md#checklist).**

➜ **On utilisera NGINX comme reverse proxy**

```
[user@localhost ~]$ sudo dnf install nginx
  [...]
Complete!
```

```
[user@localhost ~]$ sudo systemctl enable nginx
Created symlink /etc/systemd/system/multi-user.target.wants/nginx.service → /usr/lib/systemd/system/nginx.service.
[user@localhost ~]$ sudo systemctl start nginx
[user@localhost ~]$ sudo systemctl status nginx
● nginx.service - The nginx HTTP and reverse proxy server
     Loaded: loaded (/usr/lib/systemd/system/nginx.service; enabled; vendor preset: disabled)
     Active: active (running) since Fri 2022-11-18 09:49:17 CET; 5s ago
```

```
[user@localhost ~]$ sudo ss -lntp | grep ng
LISTEN 0      511          0.0.0.0:80        0.0.0.0:*    users:(("nginx",pid=1068,fd=6),("nginx",pid=1067,fd=6))
LISTEN 0      511             [::]:80           [::]:*    users:(("nginx",pid=1068,fd=7),("nginx",pid=1067,fd=7))
```

```
[user@localhost ~]$ sudo firewall-cmd --zone=public --add-port=80/tcp
success
[user@localhost ~]$ sudo firewall-cmd --list-all
public (active)
  target: default
  icmp-block-inversion: no
  interfaces: enp0s3 enp0s8
  sources: 
  services: ssh
  ports: 80/tcp
```

```
[user@localhost ~]$ ps -ef | grep nginx
root        1067       1  0 09:49 ?        00:00:00 nginx: master process /usr/sbin/nginx
nginx       1068    1067  0 09:49 ?        00:00:00 nginx: worker process
```
User nginx

```
 ╭─gammray@manjaro in repo: linux-reseau-leo/linux/tp3/3-Module_1_ReverseProxy on  main [?] 
 ╰─λ curl http://10.102.1.13
  <!doctype html>
  [...]
```

➜ **Configurer NGINX**


```
[user@localhost nginx]$ cat nginx.conf 
  [...]
    # Load modular configuration files from the /etc/nginx/conf.d directory.
    # See http://nginx.org/en/docs/ngx_core_module.html#include
    # for more information.
    include /etc/nginx/conf.d/*.conf;
```

➜ **Modifier votre fichier `hosts` de VOTRE PC**

```
 ╭─gammray@manjaro in repo: linux-reseau-leo/linux/tp3/3-Module_1_ReverseProxy on  main [?] took 17s
 ╰─λ cat /etc/hosts
10.102.1.13   web.tp2.linux
```

```
 ╭─gammray@manjaro in repo: linux-reseau-leo/linux/tp3/3-Module_1_ReverseProxy on  main [?] took 981ms
 ╰─λ curl web.tp2.linux
<!DOCTYPE html>
  [...]
```

✨ **Bonus** : rendre le serveur `web.tp2.linux` injoignable sauf depuis l'IP du reverse proxy. En effet, les clients ne doivent pas joindre en direct le serveur web : notre reverse proxy est là pour servir de serveur frontal. Une fois que c'est en place :
```
 ╭─gammray@manjaro in repo: linux-reseau-leo/linux/tp3/3-Module_1_ReverseProxy on  main [?] took 719ms
 ╰─λ ping 10.102.1.11
PING 10.102.1.11 (10.102.1.11) 56(84) bytes of data.
From 10.102.1.11 icmp_seq=1 Destination Port Unreachable
^C
--- 10.102.1.11 ping statistics ---
1 packets transmitted, 0 received, +1 errors, 100% packet loss, time 0ms


 ╭─gammray@manjaro in repo: linux-reseau-leo/linux/tp3/3-Module_1_ReverseProxy on  main [?] took 227ms
[🔴] ─ ping 10.102.1.13
PING 10.102.1.13 (10.102.1.13) 56(84) bytes of data.
64 bytes from 10.102.1.13: icmp_seq=1 ttl=64 time=0.316 ms
^C
--- 10.102.1.13 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.316/0.316/0.316/0.000 ms
```

# III. HTTPS

```
 ╭─gammray@manjaro in repo: linux-reseau-leo/linux/tp3/3-Module_1_ReverseProxy on  main [?] took 17ms
[🔴] ─ curl --insecure https://web.tp2.linux
<!DOCTYPE html>
<html>
<head>
  <script> window.location.href="index.php"; </script>
  <meta http-equiv="refresh" content="0; URL=index.php">
</head>
</html>
```