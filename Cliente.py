import socket, re
import pwinput

# Variables globales
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
opcion = ""
log = False
aciertos = 0

# Método para registrar usuarios a través del email y su contraseña
def register():
    global s
    print('Registrar usuario:')
    email = input("Email: ")
    psw = pwinput.pwinput(prompt='Contraseña: ')
    psw2 = pwinput.pwinput(prompt='Repite contraseña: ')
    if(psw == psw2):
        if (validEmail(email)):
            cad = "reg;" + email + ";" + psw
            s.send(cad.encode())
            r = s.recv(1024).decode()
            if (r == "True"):
                print("Usuario registrado correctamente.")
            else:
                print("El correo ya existe.")
        else:
            print("El correo no es válido.")
    else:
        print("Las contraseñas no coinciden.")

# Método para iniciar sesión en cuentas ya registradas escribiendo email y contraseña
def login():
    global log, s
    print('Iniciar sesión: ')
    email = input('Email: ')
    psw = pwinput.pwinput(prompt='Contraseña: ')
    cad = "log;" + email + ";" + psw
    s.send(cad.encode())
    r = s.recv(1024).decode()
    if (r == "True"):
        print("Sesión iniciada con éxito.")
        log = True
    else:
        print("El email o la contraseña no son válidos.")

# Método para declarar un email válido a través de expresiones regulares
def validEmail(correo):
    expresion_regular = r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
    return re.match(expresion_regular, correo)

# Método que definirá la lista de jugadores
def listJug(jug, nom):
    c = "Jugadores: "
    for j in jug:
        if j != nom:
            c = c + j + ","
    print(c)
    
#Conexion | inicio de la app
s.connect(("localhost", 9999))

# Seguirá pidiendo email y contraseña mientras el login o el register sea incorrecto.
while log != True:
    print('Selecciona una opción:')
    opcion = input('1. Registrar usuario.\n2. Iniciar sesión.\n')
    if (opcion == '1'):
        register()
    elif(opcion == '2'):
        login()
    else:
        print('Opción incorrecta')

# Fragmento de código que se encargará de recoger y usar tu nick y te mostrará un mensaje hasta que la partida pueda iniciarse
nick = input("Introduce tu nick: ")
s.send(nick.encode())
print("Esperando que se conecten jugadores. Esto puede tardar varios minutos...")

# Fragmento de código que sen encarga de repartir 5 preguntas al jugador de forma que si este acierta se le suma un punto. Al terminar
# de responder todas sus preguntas, se le comunicará el número de aciertos totales que ha tenido
datos = s.recv(1024).decode()
array = datos.split("$")
jug = array[0].split("&")
listJug(jug, nick)
preguntas = array[1].split("&")
for p in preguntas:
    a = p.split(";")
    preg = a[0].split("*")
    for l in preg:
        print(l)
    resp = input("Respuesta: ")
    if resp == a[1]:
        print("¡Correcto!")
        aciertos = aciertos + 1
    else:
        print("¡Incorrecto!")
print("Has acertado "+ str(aciertos) + "preguntas!")
s.send(str(aciertos).encode())
strPuntos = s.recv(1024).decode()
puntos = strPuntos.split(";")

# Fragmento de código el cual te comunicará si has ganado/perdido, el ranking final de la partida y su finalización
ganador = puntos[0].split(' ')
if(ganador[0] == nick):
    print('Has ganado!!')
else:
    print('Has perdido...')

print('RANKING:')
for punt in puntos:
    print(punt)

print('Fin de la partida.')