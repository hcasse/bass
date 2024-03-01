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

