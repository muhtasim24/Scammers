FROM python:3.8

# Set the home directory to /root
ENV HOME /root

# cd into the home directory
WORKDIR /root

# Copy all app files into the image
COPY . .

# Download dependencies
RUN pip3 install -r requirements.txt

# Install Nginx
RUN apt-get update && apt-get install -y nginx

# Remove default Nginx configuration
RUN rm /etc/nginx/sites-enabled/default

# Copy your Nginx configuration file to the image
COPY nginx.conf /etc/nginx/sites-enabled/app.conf

# Expose port 80 for HTTP traffic
EXPOSE 80

# Start Nginx and your application
CMD service nginx start && python3 -u app.py
