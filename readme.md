# Streamserv Network Music Player

## Introduction



## Dependencies

* Python3
* eyeD3
* python-magic-bin (windows)
* aioquic

aioquic requires openssl, see instructions [here](https://github.com/aiortc/aioquic)

### To Install:
    pip install eyeD3
    pip install python-magic-bin
    pip install aioquic

### Create TLS cert

    openssl req -new -newkey rsa:4096 -nodes -keyout private_key.txt -out csr.txt -subj "/C=CA/ST=Somwhere/L=SomeOtherPlace/O=starshine-bcit/CN=streamserv"

    openssl x509 -req-sha256 -days 365 -in csr.txt -signkey private_key.txt  -out certificate.txt

You should now have your own self-signed certificate and key, place them in ./cert

## Server Invocation

### help
    py streamserv.py help

### create database
    py streamserv.py db create your/path/here
        Note: path must be absolute, only works with MP3 files

### db stats
    py streamserv.py db stats

### listen verbosely with defaults
    py streamserv.py serv -v
    
    Note: requires a cert and key as outlined aboce