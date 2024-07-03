import copy

import networkx as nx

from database.DAO import DAO


class Model:
    def __init__(self):
        self._allAirports = DAO.getAllAirports()  # lista di tutti gli oggetti aeroporto
        self._idMap = {}
        for a in self._allAirports:
            self._idMap[a.ID] = a

        self._grafo = nx.Graph()  # grafo semplice, non orientato

        self._bestPath = []
        self._bestObjFun = 0

    def getCamminoOttimo(self, v0, v1, t):  # funzione esterna accessibile dall'esterno

        self._bestPath = []  # mettendoli anche dentro il metodo mi assicuro che
        self._bestObjFun = 0  # ogni volta che cerco un cammino riparto da 0

        parziale = [v0]  # cerco un cammino che fra v0 e v1, quindi v0 c'è sicuro

        self._ricorsione(parziale, v1, t)  # v1 è il target

        return self._bestPath, self._bestObjFun  # restituisco anche il peso massimo

    def _ricorsione(self, parziale, target, t):

        # Verificare che parziale sia una possibile soluzione
            # se questa è vera, verificare se parziale è meglio di best
            # in caso esco, se non sono uscita vuol dire che parziale è ancora più corta del numero massimo di archi

        if len(parziale) == t+1:  # perché parziale appende i nodi, invece t sono gli archi
            if self.getObjFun(parziale) > self._bestObjFun and parziale[-1] == target:
                self._bestObjFun = self.getObjFun(parziale)
                self._bestPath = copy.deepcopy(parziale)
            return
            # io voglio uscire comunque se la lunghezza è t+1 perché non
            # voglio verificare parziali più lunghi del mio limite


        """
        questa è la soluzione per avere delle soluzioni lunghe ESATTAMENTE t, se invece volessi delle soluzioni 
        lunghe AL MASSIMO t farei così, salvando sempre le soluzioni ammissibili anche se non sono lunghe t
        
        if len(parziale) == t+1: 
            return
        if self.getObjFun(parziale) > self._bestObjFun and parziale[-1] == target:
            self._bestObjFun = self.getObjFun(parziale)
            self._bestPath = copy.deepcopy(parziale)
        
        nel secondo if non ho bisogno della return perché sto controllando delle soluzioni potenzialmente più corte di t
        quindi non ha senso interrompere quell'esplorazione
        con il secondo if sto assumendo di poter salvare una soluzione parziale più corta di t, ma poi continuo
        a esplorare, e sto anche assumendo che posso ritornarci, che posso passare dal target e poi ritornarci, 
        quindi posso avere dei cicli
        così esco se la lunghezza = t+1 oppure se l'ultimo elemento della lista è il target
        """


        # se non sono uscita posso ancora aggiungere nodi
            # prendo i vicini e provo ad aggiungere
            # ricorsione
        for n in self._grafo.neighbors(parziale[-1]):  # sull'ultimo che ho aggiunto, ciclo sui vicini e li appendo
            # qui solitamente ci metto i vincoli tipo non posso mettere lo stesso nodo più volte,
            # o non posso mai passare attraverso lo stesso arco più volte
            # ad esempio
            if n not in parziale:
                parziale.append(n)
                self._ricorsione(parziale, target, t)
                parziale.pop()

    def getObjFun(self, listOfNodes):  # arriva una lista di nodi in cui sa che c'è un arco tra di loro
        # uso questa funzione per verificare se ha senso salvare una soluzione

        objVal = 0

        for i in range(0, len(listOfNodes)-1):  # ciclo sui nodi e prendo gli archi
            objVal += self._grafo[listOfNodes[i]][listOfNodes[i+1]]["weight"]
            # quando i vale 0 prendo l'arco fra 0 e 1, quando i vale 1 prendo l'arco da 1 a 2 e così via,
            # per questo metto -1 perché altrimenti poi andrei a prendere un arco che non esiste

        return objVal

    def buildGraph(self, nMin):  # nMin viene dall'esterno quindi sarà un input della funzione
        self._nodi = DAO.getAllNodes(nMin, self._idMap)
        self._grafo.add_nodes_from(self._nodi)
        self._addEdgesV2()

    def _addEdgesV1(self):
        allConnessioni = DAO.getAllEdgesV1(self._idMap)  # queste connessioni hanno delle ripetizioni
        for c in allConnessioni:
            v0 = c.V0
            v1 = c.V1
            peso = c.n
            if v0 in self._grafo and v1 in self._grafo:  # vuol dire che i nodi ci sono quindi posso aggiungere l'arco
                if self._grafo.has_edge(v0, v1):  # controllo se esiste già l'arco, se sì modifico solo il peso
                    self._grafo[v0][v1]["weight"] += peso
                else:  # se l'arco non esiste lo aggiungo con il peso che ho
                    self._grafo.add_edge(v0, v1, weight=peso)

    def _addEdgesV2(self):
        allConnessioni = DAO.getAllEdgesV2(self._idMap)
        for c in allConnessioni:
            if c.V0 in self._grafo and c.V1 in self._grafo:  # se i nodi ci sono allora aggiungo l'arco
                self._grafo.add_edge(c.V0, c.V1, weight=c.N)

    def getSortedVicini(self, v0):
        vicini = self._grafo.neighbors(v0)  # vicini non ordinati
        viciniTuple = []  # lista di tuple
        for v in vicini:
            viciniTuple.append((v, self._grafo[v0][v]["weight"]))  # metto il vicino e il suo peso,
            # quindi un oggetto e un numero
        viciniTuple.sort(key=lambda x: x[1], reverse=True)  # x[1] ovvero ordino per il secondo campo della tupla
        return viciniTuple

    def esistePercorso(self, v0, v1):  # vuole capire se v0 e v1 sono connessi

        connessa = nx.node_connected_component(self._grafo, v0)
        # metodo che mi restiuisce la componente connessa che contiene v0

        if v1 in connessa:
            return True

        return False

    def trovaCamminoD(self, v0, v1):

        return nx.dijkstra_path(self._grafo, v0, v1)  # questo mi restituisce una lista di nodi
        # questo mi dà il cammino ottimo, ovvero quello che minimizza il peso degli archi

    def trovaCamminoBFS(self, v0, v1):  # BFS garantisce il cammino con il minor numero di archi
        # sviluppa in ampiezza

        # costruisco l'albero di visita: ne ho due: BFS e DFS
        tree = nx.bfs_tree(self._grafo, v0)  # questo metodo mi restituisce un grafo orientato
        if v1 in tree:
            print(f"{v1} è presente nell'albero di visita BFS")

        # recupero il cammino in maniera iterativa
        path = [v1]  # v1 perché parto dalla fine

        while path[-1] != v0:  # finché l'ultimo elemento non è v0
            # prendo i predecessori dell'ultimo elemento che ho messo in path
            path.append(list(tree.predecessors(path[-1]))[0])
            # predecessors mi restituisce un iteratore, quindi lo metto in una lista
            # prendo il primo elemento perché l'albero ha per costruzione
            # sempre un solo predecessore per come è costruito l'albero

        path.reverse()

        return path

    def trovaCamminoDFS(self, v0, v1):  # cammino più lungo
        # sviluppa in profondità

        tree = nx.dfs_tree(self._grafo, v0)
        if v1 in tree:
            print(f"{v1} è presente nell'albero di visita DFS")

        path = [v1]

        while path[-1] != v0:
            path.append(list(tree.predecessors(path[-1]))[0])

        path.reverse()

        return path

    def printGraphDetails(self):
        print(f"Num nodi: {len(self._grafo.nodes)}")
        print(f"Num archi: {len(self._grafo.edges)}")

    def getNumNodi(self):
        return len(self._grafo.nodes)

    def getNumArchi(self):
        return len(self._grafo.edges)

    def getAllNodes(self):
        return self._nodi
