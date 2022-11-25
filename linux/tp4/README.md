# TP4 : Conteneurs


# Sommaire

- [TP4 : Conteneurs](#tp4--conteneurs)
- [Sommaire](#sommaire)
- [0. Prérequis](#0-prérequis)
  - [Checklist](#checklist)
- [I. Docker](#i-docker)
  - [1. Install](#1-install)
  - [2. Vérifier l'install](#2-vérifier-linstall)
  - [3. Lancement de conteneurs](#3-lancement-de-conteneurs)
- [II. Images](#ii-images)
- [III. `docker-compose`](#iii-docker-compose)
  - [1. Intro](#1-intro)
  - [2. Make your own meow](#2-make-your-own-meow)

# 0. Prérequis

## Checklist

# I. Docker

🖥️ Machine **docker1.tp4.linux**

## 1. Install

🌞 **Installer Docker sur la machine**


```
[user@localhost ~]$ sudo dnf install docker^C
[user@localhost ~]$ sudo dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo
[user@localhost ~]$ sudo dnf install docker-ce docker-ce-cli containerd.io
  [...]
Complete!
[user@localhost ~]$ sudo usermod -aG docker $(whoami)
[user@localhost ~]$ logout
Connection to 10.104.1.2 closed.
  [...]
[user@localhost ~]$ groups
user wheel docker
[user@localhost ~]$ sudo systemctl enable docker
Created symlink /etc/systemd/system/multi-user.target.wants/docker.service → /usr/lib/systemd/system/docker.service.
```

## 2. Vérifier l'install

## 3. Lancement de conteneurs

🌞 **Utiliser la commande `docker run`**

```
[user@localhost docker_conf]$ docker run --name web -v /srv/docker_conf/default.conf:/etc/nginx/conf.d/default.conf -v /srv/docker_conf/index.html:/usr/share/nginx/html/index.html -m 4g -c 2 -p 8080:90 nginx
```

```
 ╭─gammray@manjaro in repo: linux-reseau-leo/linux/tp4 on  main [?] took 48ms
 ╰─λ ─ curl http://10.104.1.2:8080/
  salut oué
```

# II. Images

🌞 **Construire votre propre image**

📁 [**`Dockerfile`**](./files/Dockerfile)

## Exemple de Dockerfile et utilisation

# III. `docker-compose`

## 1. Intro

## 2. Make your own meow

🌞 **Conteneurisez votre application**

```
[user@docker last_step]$ cat Dockerfile | grep clone
RUN git -C /srv/server clone https://github.com/GammaRay99/web_server.git

[user@docker last_step]$ ls
docker-compose.yml  Dockerfile

[user@docker last_step]$ docker build . -t server
  [...]
Successfully tagged server:latest

[user@docker last_step]$ docker compose up
[+] Running 1/0
 ⠿ Container last_step-web_server-1  Created                                                                                                                                             0.0s
Attaching to last_step-web_server-1

 ╭─gammray@manjaro in repo: linux-reseau-leo/linux/tp4 on  main [?] 
 ╰─λ curl http://10.104.1.2/
1 counters   
```

📁 📁 [`app/Dockerfile`](./app/Dockerfile) et [`app/docker-compose.yml`](./app/docker-compose.yml). Je veux un sous-dossier `app/` sur votre dépôt git avec ces deux fichiers dedans :)
