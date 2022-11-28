import socket
import re

def correoValido(correo):
    expresion_regular = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
    return re.match(expresion_regular, correo)

def login():
    global log, s
    email = input("Introduce email: ")
    passw = input("Introduce contraseña: ")
    cadena = "log;" + email + ";" + passw
    s.send(cadena.encode())
    r = s.recv(1024).decode()
    if (r == "True"):
        print("Login correcto.")
        log = True
    else:
        print("El email o la contraseña no son válidos.")

def registro():
    global s
    email = input("Introduce email: ")
    passw = input("Introduce contraseña: ")
    passw2 = input("Repite contraseña: ")
    
    if(passw == passw2):
        if (correoValido(email)):
            cadena = "reg;" + email + ";" + passw
            s.send(cadena.encode())
            r = s.recv(1024).decode()
            if (r == "True"):
                print("Usuario registrado con éxito. Para iniciar sesión, haga login.")
            else:
                print("El correo ya existe.")
        else:
            print("El correo no es válido.")
    else:
        print("Las contraseñas no coinciden.")

def mostrarJug(jug, nom):
    c = "Tus oponentes son: "
    for j in jug:
        if j != nom:
            c = c + j + ","
    print(c)
            

#Conexion | inicio de la app
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", 9999))

opcion = ""
log = False
aciertos = 0

# Seguirá pidiendo email y contraseña mientras el login o el registro sea incorrecto.
while log != True:
    opcion = input("Introduzca cualquier tecla para loggearse en el sistema, o pulse \'r\' para registrarse en el sistema: ")
    if (opcion == "r"):
        registro()
    else:
      login()

# Nombre para mostrar como nick
nom_cliente = input("Introduce tu nick para la partida: ")
s.send(nom_cliente.encode())
print("Esperando a que haya partidas disponibles. Esto puede tardar varios minutos...")
datos = s.recv(1024).decode()
arr = datos.split("$")
jug = arr[0].split("&")
mostrarJug(jug, nom_cliente);
preguntas = arr[1].split("&")
for p in preguntas:
    a = p.split(";")
    preg = a[0].split("*")
    for lin in preg:
        print(lin)
    resp = input("Respuesta: ")
    if resp == a[1]:
        print("¡Correcto!")
        aciertos = aciertos + 1
    else:
        print("¡Incorrecto!")
print("Has tenido un total de "+ str(aciertos) + " aciertos.")
s.send(str(aciertos).encode())
cadPuntuaciones = s.recv(1024).decode()
puntuaciones = cadPuntuaciones.split(";")
print("CLASIFICACIÓN FINAL:")
for punt in puntuaciones:
    print(punt)
print("Fin de la partida.")
