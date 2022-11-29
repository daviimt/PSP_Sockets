import socket, re
import pwinput
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
opcion = ""
log = False
aciertos = 0

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

def validEmail(correo):
    expresion_regular = r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
    return re.match(expresion_regular, correo)

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

# Nombre para mostrar como nick
nick = input("Introduce tu nick: ")
s.send(nick.encode())
print("Esperando que se conecten jugadores. Esto puede tardar varios minutos...")
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
ganador = puntos[0].split(' ')

if(ganador[0] == nick):
    print('Has ganado!!')
else:
    print('Has perdido...')

print('RANKING:')
for punt in puntos:
    print(punt)

print('Fin de la partida.')
