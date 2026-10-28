"""
Redefine a senha de um usuário que esqueceu a senha ("Esqueci minha senha").

Quem executa precisa ter acesso ao computador/banco do sistema (o
administrador). O script define uma senha temporária e marca o usuário para
trocar a senha no próximo login, com o motivo "Esqueci minha senha".

Uso (no terminal, com o ambiente virtual ativado):
    python redefinir_senha.py
"""

import getpass
from datetime import datetime

import seguranca
from conexao import conectar


def main():
    print("=== Redefinir senha (Esqueci minha senha) ===")

    usuario = input("Nome de usuário: ").strip()

    senha = getpass.getpass("Senha temporária: ")
    erro = seguranca.validar_nova_senha(senha)

    if erro:
        print(erro)
        return

    if senha != getpass.getpass("Confirme a senha temporária: "):
        print("As senhas não conferem.")
        return

    banco = conectar()
    cursor = banco.cursor()

    try:
        cursor.execute(
            """
            UPDATE usuarios
            SET senha_hash = %s,
                senha_alterada_em = %s,
                motivo_troca = %s
            WHERE usuario = %s
            """,
            (
                seguranca.gerar_hash(senha),
                datetime.now(),
                seguranca.MOTIVO_ESQUECI,
                usuario,
            )
        )

        if cursor.rowcount == 0:
            print("Usuário não encontrado.")
            banco.rollback()
            return

        banco.commit()
        print("Senha temporária definida. O usuário deverá trocá-la ao entrar.")

    except Exception as erro_banco:
        banco.rollback()
        print("Erro ao redefinir senha:", erro_banco)

    finally:
        cursor.close()
        banco.close()


if __name__ == "__main__":
    main()
