basic_testing_scenarios:

1. single or multiple standard (wordpress, joomla, magento or other) website 
running on centos 7. 

2. My website "insert domain here" went down for two hours last night. Check
the access logs and determine if there were malicious requests and spamming
requests. Isolate bad IPs from the logs and the URI that were targeting (I.E 
wp-admin.php or xmlrpc.php, etc) Determine if apache hit max_clients during that 
time.

3. My website is sometimes slow. In this situation, the client probably had to 
many requests to to their domain/web app and or has terrible tuning of their
server. (I.E apache can handle 5,000 concurrent connections but php-fpm pool only
accepts 1,000 concurrent connections.) Determine if apache ran out
of connections, poor performance configuration. Did the php-fpm pool run out of 
connections? Did the database run out of available connections? Was their a slow
query?

4. Incorrect permissions in a document root for a domain. Apache/nginx can't
access website content. Another common problem is an php-fpm pool not being able
to access the document root of an website due to mismatched user/group 
ownership between apache/nginx and php-fpm.

...I will add more basic testing scenarios as I think of them. Feel free to add
any test scenario you can think of that would be within scope of the librecon 
project.
