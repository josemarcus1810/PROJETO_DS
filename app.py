from flask import Flask, render_template, request, redirect, url_for
from conexao import conectar

app = Flask(__name__)


# ==================================================
# FUNÇÃO AUXILIAR: REGISTRAR MOVIMENTAÇÕES
# ==================================================

def registrar_movimentacao(
    cursor,
    tipo,
    descricao,
    produto_id=None,
    lote_id=None
):
    cursor.execute(
        """
        INSERT INTO movimentacoes
            (
                produto_id,
                lote_id,
                tipo_movimentacao,
                descricao,
                usuario_responsavel
            )
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            produto_id,
            lote_id,
            tipo,
            descricao,
            "Sistema"
        )
    )


# ==================================================
# INÍCIO E LOGIN
# ==================================================

@app.route("/")
@app.route("/index.html")
def inicio():
    return render_template("index.html")


@app.route("/login.html")
def login():
    return render_template("login.html")


# ==================================================
# PRODUTOS: LISTAR E CADASTRAR
# ==================================================

@app.route("/produtos.html", methods=["GET", "POST"])
def produtos():
    banco = None
    cursor = None

    try:
        banco = conectar()
        cursor = banco.cursor(dictionary=True)

        if request.method == "POST":
            nome = request.form.get("nome", "").strip()
            tipo = request.form.get("tipo", "")
            validade = request.form.get("validade") or None

            try:
                quantidade = int(
                    request.form.get("quantidade", "")
                )
            except ValueError:
                return "Quantidade inválida.", 400

            prefixos = {
                "papelaria": "PAP",
                "limpeza": "LIM",
                "informatica": "INF",
                "outros": "OUT"
            }

            if (
                not nome
                or tipo not in prefixos
                or quantidade < 1
            ):
                return "Preencha os campos corretamente.", 400

            prefixo = prefixos[tipo]

            cursor.execute(
                """
                SELECT codigo
                FROM produtos
                WHERE codigo LIKE %s
                """,
                (prefixo + "_%",)
            )

            codigos = cursor.fetchall()
            numeros = []

            for item in codigos:
                try:
                    numeros.append(
                        int(item["codigo"].split("_")[1])
                    )
                except (IndexError, ValueError):
                    pass

            codigo = f"{prefixo}_{max(numeros, default=0) + 1:02d}"

            cursor.execute(
                """
                INSERT INTO produtos
                    (
                        codigo,
                        nome,
                        tipo,
                        data_validade,
                        quantidade
                    )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    codigo,
                    nome,
                    tipo,
                    validade,
                    quantidade
                )
            )

            produto_id = cursor.lastrowid

            registrar_movimentacao(
                cursor,
                "Inclusão",
                f"Produto {codigo} - {nome} cadastrado",
                produto_id=produto_id
            )

            banco.commit()

            return redirect(url_for("produtos"))

        cursor.execute(
            "SELECT * FROM produtos ORDER BY id DESC"
        )

        lista_produtos = cursor.fetchall()

        return render_template(
            "produtos.html",
            produtos=lista_produtos
        )

    except Exception as erro:
        if banco:
            banco.rollback()

        print("Erro na página de produtos:", erro)
        return "Erro ao processar produtos. Confira o terminal.", 500

    finally:
        if cursor:
            cursor.close()
        if banco:
            banco.close()


# ==================================================
# PRODUTOS: EDITAR
# ==================================================

@app.route("/editar_produto/<int:id>", methods=["GET", "POST"])
def editar_produto(id):
    banco = None
    cursor = None

    try:
        banco = conectar()
        cursor = banco.cursor(dictionary=True)

        if request.method == "POST":
            nome = request.form.get("nome", "").strip()
            tipo = request.form.get("tipo", "")
            validade = request.form.get("validade") or None
            situacao = request.form.get("situacao", "")

            try:
                quantidade = int(
                    request.form.get("quantidade", "")
                )
            except ValueError:
                return "Quantidade inválida.", 400

            tipos_validos = (
                "papelaria",
                "limpeza",
                "informatica",
                "outros"
            )

            situacoes_validas = (
                "disponível",
                "indisponível"
            )

            if (
                not nome
                or tipo not in tipos_validos
                or quantidade < 0
                or situacao not in situacoes_validas
            ):
                return "Preencha os campos corretamente.", 400

            cursor.execute(
                """
                SELECT codigo
                FROM produtos
                WHERE id = %s
                """,
                (id,)
            )

            produto = cursor.fetchone()

            if produto is None:
                return "Produto não encontrado.", 404

            cursor.execute(
                """
                UPDATE produtos
                SET nome = %s,
                    tipo = %s,
                    data_validade = %s,
                    quantidade = %s,
                    situacao = %s
                WHERE id = %s
                """,
                (
                    nome,
                    tipo,
                    validade,
                    quantidade,
                    situacao,
                    id
                )
            )

            registrar_movimentacao(
                cursor,
                "Edição",
                f"Produto {produto['codigo']} - {nome} editado",
                produto_id=id
            )

            banco.commit()

            return redirect(url_for("produtos"))

        cursor.execute(
            "SELECT * FROM produtos WHERE id = %s",
            (id,)
        )

        produto = cursor.fetchone()

        if produto is None:
            return "Produto não encontrado.", 404

        return render_template(
            "editar_produto.html",
            produto=produto
        )

    except Exception as erro:
        if banco:
            banco.rollback()

        print("Erro ao editar produto:", erro)
        return "Erro ao editar produto. Confira o terminal.", 500

    finally:
        if cursor:
            cursor.close()
        if banco:
            banco.close()


# ==================================================
# LOTES: LISTAR
# ==================================================

@app.route("/lotes.html")
def lotes():
    banco = None
    cursor = None

    try:
        banco = conectar()
        cursor = banco.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                l.id,
                l.numero_lote,
                l.quantidade,
                l.data_validade,
                l.situacao,
                l.data_cadastro,
                p.codigo AS codigo_produto,
                p.nome AS nome_produto
            FROM lotes l
            INNER JOIN produtos p ON l.produto_id = p.id
            ORDER BY l.id DESC
            """
        )

        lista_lotes = cursor.fetchall()

        return render_template(
            "lotes.html",
            lotes=lista_lotes
        )

    except Exception as erro:
        print("Erro ao consultar lotes:", erro)
        return "Erro ao carregar lotes. Confira o terminal.", 500

    finally:
        if cursor:
            cursor.close()
        if banco:
            banco.close()


# ==================================================
# LOTES: CADASTRAR
# ==================================================

@app.route("/novo_lote.html", methods=["GET", "POST"])
def novo_lote():
    banco = None
    cursor = None

    try:
        banco = conectar()
        cursor = banco.cursor(dictionary=True)

        if request.method == "POST":
            try:
                produto_id = int(
                    request.form.get("produto_id", "")
                )
                quantidade = int(
                    request.form.get("quantidade", "")
                )
            except ValueError:
                return "Confira o produto e a quantidade.", 400

            validade = request.form.get("validade") or None

            if produto_id < 1 or quantidade < 1:
                return "Informe um produto e uma quantidade válida.", 400

            # Busca qualquer produto cadastrado,
            # mesmo que esteja indisponível.
            cursor.execute(
                """
                SELECT id, codigo, nome
                FROM produtos
                WHERE id = %s
                """,
                (produto_id,)
            )

            produto = cursor.fetchone()

            if produto is None:
                return "Produto não encontrado.", 404

            cursor.execute(
                "SELECT numero_lote FROM lotes"
            )

            lotes_existentes = cursor.fetchall()
            numeros = []

            for lote in lotes_existentes:
                try:
                    numeros.append(
                        int(lote["numero_lote"].split("_")[1])
                    )
                except (IndexError, ValueError):
                    pass

            numero_lote = (
                f"LOTE_{max(numeros, default=0) + 1:02d}"
            )

            cursor.execute(
                """
                INSERT INTO lotes
                    (
                        numero_lote,
                        produto_id,
                        quantidade,
                        data_validade
                    )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    numero_lote,
                    produto_id,
                    quantidade,
                    validade
                )
            )

            lote_id = cursor.lastrowid

            registrar_movimentacao(
                cursor,
                "Novo lote",
                (
                    f"Lote {numero_lote} criado para "
                    f"{produto['codigo']} - {produto['nome']}"
                ),
                produto_id=produto_id,
                lote_id=lote_id
            )

            banco.commit()

            return redirect(url_for("lotes"))

        # Lista TODOS os produtos cadastrados.
        # Não filtra pela situação.
        cursor.execute(
            """
            SELECT id, codigo, nome, situacao
            FROM produtos
            ORDER BY nome
            """
        )

        lista_produtos = cursor.fetchall()

        return render_template(
            "novo_lote.html",
            produtos=lista_produtos
        )

    except Exception as erro:
        if banco:
            banco.rollback()

        print("Erro ao cadastrar lote:", erro)
        return "Erro ao cadastrar lote. Confira o terminal.", 500

    finally:
        if cursor:
            cursor.close()
        if banco:
            banco.close()


# ==================================================
# LOTES: EDITAR
# ==================================================

@app.route("/editar_lote/<int:id>", methods=["GET", "POST"])
def editar_lote(id):
    banco = None
    cursor = None

    try:
        banco = conectar()
        cursor = banco.cursor(dictionary=True)

        if request.method == "POST":
            try:
                quantidade = int(
                    request.form.get("quantidade", "")
                )
            except ValueError:
                return "Quantidade inválida.", 400

            validade = request.form.get("validade") or None
            situacao = request.form.get("situacao", "")

            if quantidade < 0:
                return "A quantidade não pode ser negativa.", 400

            if situacao not in ("ativo", "inativo"):
                return "Situação inválida.", 400

            cursor.execute(
                """
                SELECT id, numero_lote, produto_id
                FROM lotes
                WHERE id = %s
                """,
                (id,)
            )

            lote = cursor.fetchone()

            if lote is None:
                return "Lote não encontrado.", 404

            cursor.execute(
                """
                UPDATE lotes
                SET quantidade = %s,
                    data_validade = %s,
                    situacao = %s
                WHERE id = %s
                """,
                (
                    quantidade,
                    validade,
                    situacao,
                    id
                )
            )

            registrar_movimentacao(
                cursor,
                "Edição",
                f"Lote {lote['numero_lote']} editado",
                produto_id=lote["produto_id"],
                lote_id=id
            )

            banco.commit()

            return redirect(url_for("lotes"))

        cursor.execute(
            """
            SELECT
                l.id,
                l.numero_lote,
                l.quantidade,
                l.data_validade,
                l.situacao,
                p.codigo AS codigo_produto,
                p.nome AS nome_produto
            FROM lotes l
            INNER JOIN produtos p ON l.produto_id = p.id
            WHERE l.id = %s
            """,
            (id,)
        )

        lote = cursor.fetchone()

        if lote is None:
            return "Lote não encontrado.", 404

        return render_template(
            "editar_lote.html",
            lote=lote
        )

    except Exception as erro:
        if banco:
            banco.rollback()

        print("Erro ao editar lote:", erro)
        return "Erro ao editar lote. Confira o terminal.", 500

    finally:
        if cursor:
            cursor.close()
        if banco:
            banco.close()


# ==================================================
# PEDIDOS DE COMPRA
# ==================================================

@app.route("/pedidos.html")
def pedidos():
    return render_template("pedidos.html")


@app.route("/visualizar_pedido.html")
def visualizar_pedido():
    return render_template("visualizar_pedido.html")


# ==================================================
# HISTÓRICO DE MOVIMENTAÇÕES
# ==================================================

@app.route("/movimentacoes.html")
def movimentacoes():
    banco = None
    cursor = None

    try:
        banco = conectar()
        cursor = banco.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                m.id,
                m.produto_id,
                m.lote_id,
                m.tipo_movimentacao,
                m.descricao,
                m.usuario_responsavel,
                m.data_movimentacao,
                p.codigo AS codigo_produto,
                p.nome AS nome_produto,
                l.numero_lote
            FROM movimentacoes m
            LEFT JOIN produtos p
                ON m.produto_id = p.id
            LEFT JOIN lotes l
                ON m.lote_id = l.id
            ORDER BY
                m.data_movimentacao DESC,
                m.id DESC
            """
        )

        lista_movimentacoes = cursor.fetchall()

        return render_template(
            "movimentacoes.html",
            movimentacoes=lista_movimentacoes
        )

    except Exception as erro:
        print("Erro ao consultar movimentações:", erro)
        return "Erro ao carregar movimentações. Confira o terminal.", 500

    finally:
        if cursor:
            cursor.close()
        if banco:
            banco.close()


# ==================================================
# USUÁRIO E SENHA
# ==================================================

@app.route("/usuario.html")
def usuario():
    return render_template("usuario.html")


@app.route("/alterar_senha.html")
def alterar_senha():
    return render_template("alterar_senha.html")


# ==================================================
# EXECUTAR O SISTEMA
# ==================================================

if __name__ == "__main__":
    app.run(debug=True)
