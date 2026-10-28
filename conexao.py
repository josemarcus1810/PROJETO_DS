import os

import mysql.connector


def conectar():
    """
    Abre uma conexão com o MySQL.

    Os valores abaixo são os mesmos que o projeto já usava. Se precisar
    mudar algo (porta, senha...), edite aqui ou defina as variáveis de
    ambiente DB_HOST, DB_PORT, DB_USER, DB_PASSWORD e DB_NAME.
    """
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", "3307")),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", "root"),
        database=os.environ.get("DB_NAME", "almoxarifado"),
        charset="utf8mb4",
    )
