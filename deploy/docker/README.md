# How to build the Docker Image

From the top-level directory:
```sh
$ sudo -s
$ docker image pull ubuntu:latest
$ docker build -t bass .
```

## Helpful

List images:
```sh
$ sudo docker images
```

Run container with bash:
```sh
$ sudo docker container run -it ubuntu:latest bash
```

To list containers:
```sh
$ sudo docker ps
$ sudo docker ps -a
```
