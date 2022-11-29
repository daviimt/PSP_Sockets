import threading, socket, os, random, operator
from pathlib import Path

# Variables globales.
jugadores = {}
nClientes = 0
mutex = threading.Lock()
sem = threading.Semaphore(4)
contSem = 4
cad = ""
enCurso = False
preguntas = open("./preguntas.txt", "r", encoding="utf8").readlines()
trivial = list()

# Clase Cliente que hereda de Thread.
class Cliente(threading.Thread):
    
    def __init__(self, socket_cliente, datos_cliente) -> None:
        threading.Thread.__init__(self)
        self.socket = socket_cliente
        self.datos = datos_cliente
        self.trivial = list()
        self.nombre = ""
        self.logged = False

    def run(self):
        global sem, mutex, nClientes, contSem, enCurso, cad, trivial
        while(self.logged == False):
            datosLogin = self.socket.recv(1024).decode().split(";")
            if (datosLogin[0] == "reg"):
                if(validarRegister(datosLogin[1], datosLogin[2])):
                    self.socket.send("True".encode())
                else:
                    self.socket.send("False".encode())
            elif (datosLogin[0] == "log"):
                if(validarLogin(datosLogin[1], datosLogin[2])):
                    self.socket.send("True".encode())
                    self.logged = True
                else:
                    self.socket.send("False".encode())
            else:
                self.socket.send("False".encode())
        
        # Nick del cliente para la partida.
        self.nombre = self.socket.recv(1024).decode()
        print(self.nombre,'ha iniciado sesión')
        sem.acquire()
        while enCurso:
            pass
        mutex.acquire()
        contSem = contSem - 1
        if (contSem == 0):
            trivial.clear()
            for i in range(5):
                choice = random.choice(preguntas).split("\n")
                while choice[0] in trivial:
                    choice = random.choice(preguntas).split("\n")
                trivial.append(choice[0])
        nClientes = nClientes + 1
        jugadores.__setitem__(self.nombre, "0")
        mutex.release()
        while nClientes != 4:
            pass
        mutex.acquire()
        self.trivial = trivial
        
        #Aquí se inicia la partida
        j = jugadores.keys()
        jug = "&".join(j)
        pregunta = str()
        for t in self.trivial:
            pregunta = pregunta + t +"&"
        pregunta = pregunta[:-1]
        cadena = jug + "$" + pregunta
        enCurso = True
        mutex.release()
        
        # Aquí se mandan las preguntas y los jugadores contrarios
        self.socket.send(cadena.encode())
        print(self.nombre ,'comienza la partida')
        
        #Aquí termina la partida
        mutex.acquire()
        puntos = self.socket.recv(1024).decode()
        jugadores[self.nombre] = puntos
        
        # Aquí se reciben los resultados y se vuelcan en un array
        contSem = contSem + 1
        
        # El último jugador (el que pone el contSem a 4), es el que reinicia las variables,
        # ordena el array de jugadores y muestra la clasificación historial en el servidor.
        cad = ""
        dicGen = {}
        jugadoresOrd = list()
        if (contSem == 4):
            jugadoresOrd = sorted(jugadores.items(), key=operator.itemgetter(1), reverse=True)
            if (os.path.isfile('./historial.txt') == False):
                f = Path('./historial.txt')
                f.touch(exist_ok=True)
            historial = open("./historial.txt", "r")
            
            for l in historial:
                p = l.split(";")
                dicGen.__setitem__(p[0], p[1])
            historial.close()
            listKeys = dicGen.keys()
            
            for jugador in enumerate(jugadoresOrd):
                if (jugador[1][0] in listKeys):
                    valor = int(dicGen[jugador[1][0]]) + int(jugadores[jugador[1][0]])
                    dicGen[jugador[1][0]] = valor
                    
                else:
                    dicGen.__setitem__(jugador[1][0], jugadores[jugador[1][0]])
                s = "{}".format(jugador[1][0]) + " - " + "{}".format(jugadores[jugador[1][0]]) + " puntos"
                cad = cad + str(s) + ";"
                
            #dicGen = sorted(dicGen.items(), key= operator.itemgetter(1), reverse=True)
            historial = open("./historial.txt", "w")
            for k, v in dicGen.items():
                s = str(k) + ";" + str(v) + ";"
                historial.write(str(s)+"\n")
            historial.close()
            mostrarhistorial()
            nClientes = 0
            enCurso = False
        mutex.release()
        
        # Con este bucle Hacemos esperar a los hilos que ya han terminado para que el array de puntuaciones esté completo.
        while enCurso:
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
        sem.release()
        print("Desconectado: " + str(self.datos))

def mostrarhistorial():
    historial = open("./historial.txt", "r")
    dicPun = {}
    for l in historial:
        p = l.split(";")
        dicPun.__setitem__(p[0], p[1])
    historial.close()
    punOrd = sorted(dicPun.items(), key=operator.itemgetter(1), reverse=True)
    for j in enumerate(punOrd):
        s = "Jugador: " + "{}".format(j[1][0]) + " - Puntos:" + "{}".format(dicPun[j[1][0]])
        print(s)

# Método para hacer un registro de email y contraseña si el email no existe.
def validarRegister(email, passw):
    global mutex
    mutex.acquire()
    if (os.path.isfile('./usuarios.txt') == False):
        f = Path('./usuarios.txt')
        f.touch(exist_ok=True)
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
def validarLogin(email, passw):
    global mutex
    if(os.path.exists('./usuarios.txt')== False):
        open('./usuarios.txt','w')
    fichero = open("./usuarios.txt", "r")
    logCorrect = False
    for linea in fichero:
        datos = linea.split(";")
        if (datos[0] == email and datos[1] == passw+"\n"):
            logCorrect = True
    fichero.close()
    return logCorrect

if __name__ == "__main__":
    # Conexión.
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(("localhost", 9999))
    servidor.listen(1)

    while True:
        # Se espera a un cliente.
        socket_cliente, datos_cliente = servidor.accept()
        
        print("Conectado "+str(datos_cliente))
        trivial = list()
        for i in range (5):
            choice = random.choice(preguntas).split("\n")
            while choice[0] in trivial:
                choice = random.choice(preguntas).split("\n")
            trivial.append(choice[0])
        hilo = Cliente(socket_cliente, datos_cliente)
        hilo.start()
