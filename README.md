# BASS

BASS stands for Basic Architecture Simulation Service and provides a server interface built around the GLISS simulator.

## With `Makefile`

To prepare and compile the application:
```sh
$ make setup
```

To run BASS:
```sh
$ make run
```

## Dependencies

  * [Orchid](https://github.com/hcasse/Orchid)
  * [GLISS](https://sourcesup.renater.fr/projects/gliss2)
  * [armv5t](https://sourcesup.renater.fr/projects/gliss2)

## Running

To run the server, type:

```sh
export PYTHONPATH=$PWD
python3 -m bass.server
```


# Configuration file

By default, it is named `config.ini` and is automatically loaded from `$(PWD)`
or passed with the option `--config`.

The following entries are used:

[server]
PORT=_N_			% port for the server

[bass]
DATA_DIR=_path_		% directory for the data
ADMIN=admin			% identifier of the administrator


# File organization

All data files of the server are stored in a directory thereafter named _VAR_.
By default, it's `$(PWD)/data` but this can be controlled with option
`--data-dir` or in the configuration file.

_VAR_/
* `users` -- user directories
* `password.txt` -- password of the users
* `log.txt` -- logs of the server
