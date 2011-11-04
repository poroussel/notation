<VirtualHost *>
	ServerName notation.octets.fr
	ServerAdmin philippe.roussel@octets.fr
	DocumentRoot /home/www/cfai
	LogLevel error
	ErrorLog /var/log/apache2/notation-error.log
	CustomLog /var/log/apache2/notation-access.log combined

    	# Django settings
        WSGIScriptAlias / /home/www/createch/wsgi_handler.py
	WSGIDaemonProcess cfai user=philou group=users processes=1 threads=2
    	WSGIProcessGroup cfai
</VirtualHost>
