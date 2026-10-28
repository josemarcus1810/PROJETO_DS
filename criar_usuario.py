"""
Cria um usuário do sistema (execute uma vez para criar o primeiro acesso).

Uso (no terminal, com o ambiente virtual ativado):
    python criar_usuario.py

A senha é pedida no terminal e guardada apenas como hash.
Antes, execute o arquivo atualizacao_banco.sql para criar a tabela usuarios.
"""

import getpass
import re
from datetime import datetime

import seguranca
from conexao import conectar


def main():
    print("=== Criar usuário do Sistema de Almoxarifado ===")

    usuario = input("Nome de usuário (letras, números, . _ -): ").strip()

    if not re.fullmatch(r"[A-Za-z0-9._-]{3,50}", usuario):
        print("Usuário inválido. Use de 3 a 50 caracteres: letras, números, . _ -")
        return

    nome = input("Nome completo: ").strip() or usuario

    senha = getpass.getpass("Senha: ")
    erro = seguranca.validar_nova_senha(senha)

    if erro:
        print(erro)
        return

    if senha != getpass.getpass("Confirme a senha: "):
        print("As senhas não conferem.")
        return

    banco = conectar()
    cursor = banco.cursor()

    try:
        cursor.execute("SELECT id FROM usuarios WHERE usuario = %s", (usuario,))

        if cursor.fetchone():
            print("Esse usuário já existe. Para trocar a senha dele, use redefinir_senha.py")
            return

        cursor.execute(
            """
            INSERT INTO usuarios (usuario, nome, senha_hash, senha_alterada_em)
            VALUES (%s, %s, %s, %s)
            """,
            (usuario, nome, seguranca.gerar_hash(senha), datetime.now())
        )
        banco.commit()
        print(f"Usuário '{usuario}' criado com sucesso.")

    except Exception as erro_banco:
        banco.rollback()
        print("Erro ao criar usuário:", erro_banco)

    finally:
        cursor.close()
        banco.close()


if __name__ == "__main__":
    main()
