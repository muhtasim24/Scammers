FROM python:3.8

# Set the home directory to /root
ENV HOME /root

# cd into the home directory
WORKDIR /root

# Copy all app files into the image
COPY . .

# Download dependancies
RUN pip3 install -r requirements.txt

EXPOSE 8000

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

CMD /wait && python3 -u app.py