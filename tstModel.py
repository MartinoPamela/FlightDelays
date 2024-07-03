from datetime import datetime

import networkx as nx

from model.model import Model

mymodel = Model()
mymodel.buildGraph(5)
mymodel.printGraphDetails()

v0 = mymodel.getAllNodes()[0]  # ne prendo uno a caso, cioè il primo che mi restituisce

connessa = list(nx.node_connected_component(mymodel._grafo, v0))  # così prendo la connessa di v0 e
# sono sicura che un cammino ci sia

v1 = connessa[10]  # 10 è un numero a caso, sto prendendo un nodo da connessa

pathD = mymodel.trovaCamminoD(v0, v1)
pathBFS = mymodel.trovaCamminoBFS(v0, v1)
pathDFS = mymodel.trovaCamminoDFS(v0, v1)

print("Metodo di Dijkstra")
print(*pathD, sep=" \n")
print("---------------------")
print("Metodo albero Breadth first")
print(*pathBFS, sep=" \n")
print("---------------------")
print("Metodo albero Depth first")
print(*pathDFS, sep=" \n")

tic = datetime.now()
bestPath, bestScore = mymodel.getCamminoOttimo(v0, v1, 4)
print("---------------------")
print(f"Cammino ottimo fra {v0} e {v1} ha peso = {bestScore}. \n Trovato in {datetime.now() - tic} secondi ")
print(*bestPath, sep=" \n")  # * fa l'unpack di una lista e stampa ogni singolo elemento,
# e poi gli dico fra un print e l'altro metti un \n, quindi vai a capo
