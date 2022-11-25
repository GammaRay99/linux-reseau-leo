FROM debian

RUN apt update -y

RUN apt install -y apache2
COPY ./index.html /var/www/html/index.html
COPY ./apache2.conf /etc/apache2/apache2.conf
RUN /usr/sbin/useradd apachelol
RUN /bin/mkdir "/etc/apache2/logs/"
CMD ["/usr/sbin/apache2", "-DFOREGROUND"]
# RUN echo "salut oué" > /var/www/html/index.html
# RUN echo "ServerName localhost" > /etc/apache2/conf-enabled/serverName.conf
