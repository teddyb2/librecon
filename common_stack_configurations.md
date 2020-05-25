Common LAMP/LEMP stack configurations:

-common web server
-a basic LAMP or LEMP server that has an (cms) wordpress website that is configured
with an vhost, SSL, php be it fastCGI or php-fpm, varnish caching and an 
database (can be local or remote).

-apache/nginx: create a vhost 80/443 or hybrid (80+443) vhost with basics
such as document root location (/var/www/* or /home/*, etc), location of SSL 
PKI keys, specify error and access log locations. Custom logging is welcomed! 
You can basically put any of these logs anywhere, but nothing insane such as 
putting logs under /boot or /usr/lib. 

-mysql/mariadb: either database is fine. The main object with this would be create
a regular database for wordpress, joomla, magento, etc. Using librecon, I would
check the contents of /root/.my.cnf (it if exists), /etc/my.cnf or /etc/mysql.d for 
general configuration info. In the context of the cms, I would be parsing files
such as wp-config.php for wordpress for site specific database information. 
Database can live locally or remotely, it doesn't matter. The big take away is 
finding the db name, user and slow-log or error log that an website might be using.

-php: A lot of RS clients run webservers that use the built in default php handler
fastCGI. (Apache is executing the php code). In this situation, I would be looking
at php settings in /etc/php.ini or in /etc/httpd/conf.modules.d/ for php configuration
information.

Another common php scenario is utilizing an php-fpm pool to proxy php requests from
apache/nginx for processing. In this situation, I would be searching /etc/php-fpm.conf
and /etc/php-fpm.d/* for individual pool configurations. Within these configurations,
I would be pulling the pool name, the user/group it runs as, performance settings and
ultimately any proxxing directives such as ProxyPassMatch, FileHandler, SetFile
handler. The reason this is important is because it tells me how php requests 
are being proxied from the web server, pool name, and the user/group it is running
as. A common trouble ticket I see is an client has incorrect permissions for an 
php-fpm pool in that the group ownership of the pool doesn't match the group
ownership of the website document root. Additionally, I would be looking for the 
location of the php error or request log specific to the php-fpm pool in question
should it exist.


