


all: run-server run-nginx

run-nginx:
	@echo "Running NGINX local server for test."
	-mkdir tmp
	-mkdir var
	-mkdir var/run
	nginx -c nginx.conf -p $(PWD)
	@echo "Error just above can be ignored"

#NGINX_PID = $(shell cat var/run/nginx.pid)
SERVER_PID = $(shell cat server.pid)

shutdown: shutdown-nginx shutdown-server

shutdown-nginx:
	nginx -s quit -c nginx.conf  -p $(PWD)

shutdown-server:
	kill -9 $(SERVER_PID)

run-server:
	@echo "Running server"
	python3 server.py &
