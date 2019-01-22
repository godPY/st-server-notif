import valve.source.a2s
import numpy as np

def server(ip,port):
     with valve.source.a2s.ServerQuerier(address=(ip,port), timeout=7) as server:
        return server.info()

def player(ip,port):
    with valve.source.a2s.ServerQuerier(address=(ip, port), timeout=7) as server:
        return server.players()
