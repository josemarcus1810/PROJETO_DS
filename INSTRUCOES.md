# Instruções — Sistema de Almoxarifado (versão revisada)

## 1. Antes de tudo: backup

1. Copie a pasta inteira do seu projeto atual para outro lugar (ex.: `PROJETO_DS_backup`).
2. Faça backup do banco: MySQL Workbench → **Server → Data Export** → schema `almoxarifado` → exportar.

> **Nunca importe o `backup_almoxarifado.sql` no banco que você usa hoje.**
> Ele contém `DROP TABLE` e apagaria os dados atuais. Use-o só para restaurar um banco vazio.

## 2. Onde colocar os arquivos

Extraia este ZIP **sobre a pasta do projeto**, aceitando substituir os arquivos. Resultado esperado:

```
PROJETO_DS/
├── app.py                  (substituído)
├── conexao.py              (substituído)
├── seguranca.py            (NOVO)
├── criar_usuario.py        (NOVO)
├── redefinir_senha.py      (NOVO)
├── requirements.txt        (NOVO)
├── atualizacao_banco.sql   (NOVO)
├── INSTRUCOES.md           (NOVO)
├── teste_conexao.py        (igual ao seu)
├── static/style.css        (substituído; mesmas cores, com classes novas)
└── templates/              (substituídos; agora com base.html)
```

As pastas `HTML/` e `css/` **não são usadas pelo Flask** (são cópias antigas, com links quebrados).
Não foram apagadas; mantenha-as ou remova por sua conta.
O Flask só lê `templates/` e `static/`.

## 3. Ambiente virtual e dependências

No terminal, dentro da pasta do projeto (Windows):

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

(Se o `.venv` já existe, apenas ative-o e rode o `pip install`.)

## 4. Conexão com o MySQL

O `conexao.py` mantém os valores que você já usava: `localhost`, porta `3307`, usuário `root`,
senha `root`, banco `almoxarifado`. Se algo for diferente no seu computador, edite os valores
padrão dentro do `conexao.py`. Teste com:

```
python teste_conexao.py
```

## 5. Executar o script SQL (sem perder dados)

O arquivo `atualizacao_banco.sql` só **cria** o que falta (`usuarios`, `pedidos_compra`, um índice e
uma chave estrangeira). Não apaga nem altera nenhum dado. Pode ser executado mais de uma vez.

**Pelo MySQL Workbench:** File → Open SQL Script → escolha `atualizacao_banco.sql` → clique no raio
(Execute). No final, ele lista as colunas das tabelas, para você conferir.

**Pelo terminal:**

```
mysql -u root -p -P 3307 almoxarifado < atualizacao_banco.sql
```

> Importante: o código foi conferido com as colunas do seu `backup_almoxarifado.sql`. O backup
> pode não ser idêntico ao banco instalado no seu computador. Compare a lista final do script
> com as colunas esperadas (estão nos comentários do próprio SQL). Se houver diferença, me avise.

## 6. Criar o primeiro usuário

```
python criar_usuario.py
```

Informe usuário, nome e senha (mínimo 8 caracteres, com pelo menos 1 caractere especial).
A senha é guardada apenas como hash. Execute no terminal comum (não em consoles de IDE que
não escondem a digitação).

## 7. Iniciar o sistema

```
python app.py
```

Abra no navegador: **http://127.0.0.1:5000**

## 8. Como testar cada funcionalidade

| Área | O que fazer | Resultado esperado |
|---|---|---|
| Login | Abra o endereço sem estar logado | Vai para a tela de login |
| Login | Senha errada | "Usuário ou senha inválidos." |
| Login | Usuário e senha corretos | Painel inicial com números reais |
| Produtos | Cadastre um produto "papelaria" | Código `PAP_xx` (continua a sequência), mensagem de sucesso |
| Produtos | Um de cada tipo | `LIM_01`, `INF_01`, `OUT_01` |
| Produtos | Digite ano com 5 dígitos na validade | O campo não deixa; se forçar, o servidor recusa |
| Produtos | Editar quantidade/situação | Salva e aparece em Movimentações |
| Lotes | Novo lote: digite parte do nome ou código | Lista os produtos reais; gera `LOTE_xx` |
| Lotes | Editar lote | Salva e registra a movimentação |
| Movimentações | Abra a página | Dados reais, com código, lote, tipo, descrição, data/hora, usuário |
| Movimentações | Use os filtros | Filtra por nome/código e por tipo |
| Pedidos | "Produto novo? Sim" + link | Cria `PED_xx` pendente |
| Pedidos | "Não" + escolher produto | Cria o pedido ligado ao produto |
| Pedidos | Visualizar → mudar situação | Pendente / Aprovado / Rejeitado salvo |
| Senha | Usuário → Alterar senha | Regras de 8 caracteres + especial aplicadas |
| Sair | Clique em Sair, depois use "Voltar" do navegador | Volta ao login (não mostra páginas internas) |

## 9. Regras de senha e "Esqueci minha senha"

- Senha: mínimo 8 caracteres e pelo menos 1 caractere especial (letras com acento e números não contam).
- **Troca a cada dois meses** = 60 dias. Passado esse prazo, no login o sistema obriga a troca
  (motivo exibido: **Solicitação do sistema**). Até trocar, só é possível acessar "Alterar senha" e "Sair".
- **Esqueci minha senha:** como o projeto não tem e-mail, a tela de login leva a uma página que
  orienta procurar o administrador. Ele executa `python redefinir_senha.py`, define uma senha
  temporária, e no próximo acesso o sistema obriga a troca (motivo: **Esqueci minha senha**).
  Decidi assim por segurança: uma tela que redefinisse a senha só com o nome de usuário permitiria
  que qualquer pessoa trocasse a senha de outra.

## 10. Decisões técnicas adotadas (fáceis de mudar)

- **Validade obrigatória** em produtos e lotes (como já estava no seu `app.py`). Para tornar opcional:
  `VALIDADE_OBRIGATORIA = False` no topo do `app.py`. Anos aceitos: 2000 a 2100 (`ANO_MINIMO`/`ANO_MAXIMO`).
- **Tipo do produto não muda na edição**, porque o código (`PAP_01`) depende do tipo. Antes era possível
  mudar o tipo e o código ficava errado.
- **Lote não altera a quantidade do produto.** Produto e lote têm quantidades independentes
  (o enunciado não define a relação entre elas).
- **Produto indisponível não recebe novos lotes.**
- **Movimentações:** salvar sem alterar nada não gera registro; a descrição lista o que mudou;
  mudar a situação para indisponível/inativo gera o tipo "Inativação" (que já existia no filtro).
  Os registros antigos continuam com o usuário "Sistema".
- **Chave da sessão:** defina a variável de ambiente `SECRET_KEY` em uso real. O valor padrão serve
  apenas para desenvolvimento.

## 11. Limitações conhecidas

- Não há proteção contra CSRF nem bloqueio após várias tentativas de login (fora do escopo simples do projeto).
- A numeração de produtos e lotes (`max + 1`) pode repetir se duas pessoas cadastrarem no mesmo
  instante; o índice único em `lotes.numero_lote` e em `produtos.codigo` impede a duplicação (o segundo
  cadastro dá erro e deve ser refeito). Para uso de uma pessoa, não é problema.
- Erros de banco aparecem como página de erro amigável; o detalhe completo é impresso no terminal onde o Flask roda.
