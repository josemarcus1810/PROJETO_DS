
import mysql.connector

def conectar():
    conexao = mysql.connector.connect(
        host="localhost",
        port=3307,
        user="root",
        password="root",
        database="almoxarifado"
    )

    return conexao
