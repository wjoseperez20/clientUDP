# clientUDP

Cliente que permite la comunicacion con el server host en la VPN UCAB. Este codigo es para uso en la práctica 3 de curso de Sistemas Distribuidos.

# Dependencias

 - [PyYAML](https://pyyaml.org/)

## En distribuciones Debian

```
# apt-get install python-yaml
```

## Con el uso de pip

```
# pip install pyyaml
```

# Uso

Clonar el repositorio

```
$ git clone https://github.com/wjoseperez20/clientUDP.git
$ cd clientTCP
```

Es necesario generar el archivo `client_parameters.yaml`. El archivo
[`client_parameters.sample.yaml`](https://github.com/wjoseperez20/clientUDP/blob/master/client_parameters.sample.yaml)
contiene un ejemplo del contenido.

```
$ cp client_parameters.sample.yaml client_parameters.yaml
```

Ejecución:

```
$ ./client_conect.py
```