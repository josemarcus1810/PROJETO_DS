
from conexao import conectar

try:
    banco = conectar()

    if banco.is_connected():
        print("Conexão com o MySQL realizada com sucesso!")

    banco.close()

except Exception as erro:
    print("Erro ao conectar com o MySQL:")
    print(erro)
