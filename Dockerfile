# Use the official Apache image from Docker Hub
FROM httpd:2.4

# Install certbot for SSL certificates
RUN apt-get update && \
    apt-get install -y certbot python3-certbot-apache && \
    apt-get clean

# Copy custom Virtual Host file
COPY ./my_vhost.conf /usr/local/apache2/conf/extra/my_vhost.conf

# Enable the Virtual Host and SSL module
RUN echo "Include /usr/local/apache2/conf/extra/my_vhost.conf" >> /usr/local/apache2/conf/httpd.conf && \
    sed -i 's/^#\(LoadModule .*mod_ssl.so\)/\1/' /usr/local/apache2/conf/httpd.conf

EXPOSE 443
