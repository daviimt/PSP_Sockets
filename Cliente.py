import socket
import re
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
opcion = ""
log = False
aciertos = 0

def register():
    global s
    email = input("Introduce email: ")
    psw = input("Introduce contraseña: ")
    psw2 = input("Repite contraseña: ")
    
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
    print('Inicia sesión: ')
    email = input('Introduce email: ')
    psw = input('Introduce contraseña: ')
    cad = "log;" + email + ";" + psw
    s.send(cad.encode())
    r = s.recv(1024).decode()
    if (r == "True"):
        print("Login correcto.")
        log = True
    else:
        print("El email o la contraseña no son válidos.")

def validEmail(correo):
    expresion_regular = r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
    return re.match(expresion_regular, correo)

def listJug(jug, nom):
    c = "Tus oponentes son: "
    for j in jug:
        if j != nom:
            c = c + j + ","
    print(c)
    
#Conexion | inicio de la app
s.connect(("localhost", 9999))

# Seguirá pidiendo email y contraseña mientras el login o el register sea incorrecto.
while log != True:
    opcion = input("Introduzca cualquier tecla para iniciar sesión, o pulse \'r\' para registrarse en el sistema: ")
    if (opcion == "r"):
        register()
    else:
        login()

# Nombre para mostrar como nick
nick = input("Introduce tu nick para la partida: ")
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
