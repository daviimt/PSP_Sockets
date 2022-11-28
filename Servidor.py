import threading 
import socket
import os
import random
from pathlib import Path
import operator

# Clase Cliente que hereda de Thread.
class Cliente(threading.Thread):
    
    def __init__(self, socket_cliente, datos_cliente) -> None:
        threading.Thread.__init__(self)
        self.socket = socket_cliente
        self.datos = datos_cliente
        self.trivia = list()
        self.nombre = ""
        self.logged = False

    def run(self):
        global semaforo, mutex, numC, contSem, partidaencurso, cad, trivia
        while(self.logged == False):
            datosLogin = self.socket.recv(1024).decode().split(";")
            if (datosLogin[0] == "reg"):
                if(comprobarReg(datosLogin[1], datosLogin[2])):
                    self.socket.send("True".encode())
                else:
                    self.socket.send("False".encode())
            elif (datosLogin[0] == "log"):
                if(comprobarLogin(datosLogin[1], datosLogin[2])):
                    self.socket.send("True".encode())
                    self.logged = True
                else:
                    self.socket.send("False".encode())
            else:
                self.socket.send("False".encode())
        # Nick del cliente para la partida.
        self.nombre = self.socket.recv(1024).decode()
        print("Registrado " + self.nombre)
        semaforo.acquire()
        while partidaencurso:
            pass
        mutex.acquire()
        contSem = contSem - 1
        if (contSem == 0):
            trivia.clear()
            for i in range(5):
                choice = random.choice(preguntas).split("\n")
                while choice[0] in trivia:
                    choice = random.choice(preguntas).split("\n")
                trivia.append(choice[0])
        numC = numC + 1
        jugadores.__setitem__(self.nombre, "0")
        mutex.release()
        while numC != 4:
            pass
        mutex.acquire()
        self.trivia = trivia
        #Aquí se inicia la partida
        j = jugadores.keys()
        jug = "&".join(j)
        preg = str()
        for t in self.trivia:
            preg = preg + t +"&"
        preg = preg[:-1]
        cadena = jug + "$" + preg
        partidaencurso = True
        mutex.release()
        # Aquí se mandan las preguntas y los jugadores contrarios
        self.socket.send(cadena.encode())
        print(self.nombre + " inicia juego.")
        #Aquí termina la partida
        mutex.acquire()
        puntos = self.socket.recv(1024).decode()
        jugadores[self.nombre] = puntos
        # Aquí se reciben los resultados y se vuelcan en un array
        contSem = contSem + 1
        # El último jugador (el que pone el contSem a 4), es el que reinicia las variables,
        # ordena el array de jugadores y muestra la clasificación general en el servidor.
        cad = ""
        dicGen = {}
        jugadoresOrd = list()
        if (contSem == 4):
            jugadoresOrd = sorted(jugadores.items(), key=operator.itemgetter(1), reverse=True)
            if (os.path.isfile('./general.txt') == False):
                myfile = Path('./general.txt')
                myfile.touch(exist_ok=True)
            general = open("./general.txt", "r")
            for l in general:
                p = l.split(";")
                dicGen.__setitem__(p[0], p[1])
            general.close()
            listKeys = dicGen.keys()
            for jugador in enumerate(jugadoresOrd):
                if (jugador[1][0] in listKeys):
                    valor = int(dicGen[jugador[1][0]]) + int(jugadores[jugador[1][0]])
                    dicGen[jugador[1][0]] = valor
                else:
                    dicGen.__setitem__(jugador[1][0], jugadores[jugador[1][0]])
                stri = "{}".format(jugador[1][0]) + " - " + "{}".format(jugadores[jugador[1][0]]) + " puntos"
                cad = cad + str(stri) + ";"
            #dicGen = sorted(dicGen.items(), key= operator.itemgetter(1), reverse=True)
            general = open("./general.txt", "w")
            for k, v in dicGen.items():
                stri = str(k) + ";" + str(v) + ";"
                general.write(str(stri)+"\n")
            general.close()
            mostrarGeneral()
            numC = 0
            partidaencurso = False
        mutex.release()
        # Con este bucle Hacemos esperar a los hilos que ya han terminado para que el array de puntuaciones esté completo.
        while partidaencurso:
            pass
        # Se mandan las puntuaciones a cada jugador y se reinicia el array de jugadores.
        mutex.acquire()
        if cad[len(cad)-1] == ";":
            cad = cad[:-1]
        self.socket.send(cad.encode())
        jugadores.clear()
        jugadoresOrd.clear()
        mutex.release()
        # Finalmente salen del semáforo y se inicia una nueva partida.
        semaforo.release()
        print("Desconectado: " + str(self.datos))

def mostrarGeneral():
    general = open("./general.txt", "r")
    dicPun = {}
    for l in general:
        p = l.split(";")
        dicPun.__setitem__(p[0], p[1])
    general.close()
    punOrd = sorted(dicPun.items(), key=operator.itemgetter(1), reverse=True)
    for j in enumerate(punOrd):
        stri = "Jugador: " + "{}".format(j[1][0]) + " - Puntos:" + "{}".format(dicPun[j[1][0]])
        print(stri)

# Método para hacer un registro de email y contraseña si el email no existe.
def comprobarReg(email, passw):
    global mutex
    mutex.acquire()
    if (os.path.isfile('./usuarios.txt') == False):
        myfile = Path('./usuarios.txt')
        myfile.touch(exist_ok=True)
    fichero = open("./usuarios.txt", "r")
    noExiste = True
    for linea in fichero:
        datos = linea.split(";")
        if (datos[0] == email):
            noExiste = False
    fichero.close()
    if (noExiste):
        fichero = open("./usuarios.txt", "a")
        fichero.write(email + ";" + passw + "\n")
        fichero.close()
    mutex.release()
    return noExiste

# Método para comprobar si el login es correcto.
def comprobarLogin(email, passw):
    global mutex
    fichero = open("./usuarios.txt", "r")
    logCorrect = False
    for linea in fichero:
        datos = linea.split(";")
        if (datos[0] == email and datos[1] == passw+"\n"):
            logCorrect = True
    fichero.close()
    return logCorrect

# Conexión.
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 9999))
server.listen(1)

# Variables necesarias.
jugadores = {}
numC = 0
mutex = threading.Lock()
semaforo = threading.Semaphore(4)
contSem = 4
cad = ""
partidaencurso = False
preguntas = open("./preguntas.txt", "r", encoding="utf8").readlines()
trivia = list()

while True:
    # Se espera a un cliente.
    socket_cliente, datos_cliente = server.accept()
    
    print("Conectado "+str(datos_cliente))
    trivia = list()
    for i in range (5):
        choice = random.choice(preguntas).split("\n")
        while choice[0] in trivia:
            choice = random.choice(preguntas).split("\n")
        trivia.append(choice[0])
    hilo = Cliente(socket_cliente, datos_cliente)
    hilo.start()
