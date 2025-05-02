#!env python3

# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import time

hostName = "localhost"
serverPort = 4444

class MyServer(BaseHTTPRequestHandler):

	def do_GET(self):

		print("DEBUG: client address =", self.client_address)
		print("DEBUG: server =", self.server)
		print("DEBUG: requestline =", self.requestline)
		print("DEBUG: command =", self.command)
		print("DEBUG: path =", self.path)
		print("DEBUG: request_version =", self.request_version)
		print("DEBUG: headers =", self.headers)

		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
		self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
		self.wfile.write(bytes("<body>", "utf-8"))
		self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
		self.wfile.write(bytes("</body></html>", "utf-8"))

if __name__ == "__main__":
	with open("server.pid", "w") as out:
		out.write(str(os.getpid()))
	webServer = HTTPServer((hostName, serverPort), MyServer)
	print("Server started http://%s:%s" % (hostName, serverPort))
	webServer.serve_forever()
	webServer.server_close()
	print("Server stopped.")
