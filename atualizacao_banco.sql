-- =====================================================================
-- BANCO PARA PUBLICAÇÃO (ONLINE) - Sistema de Almoxarifado  (NÃO DESTRUTIVO)
--
-- Sem DROP: não apaga nada e pode ser executado mais de uma vez.
--
-- PARTE 1 - Tabelas
--   Não usa CREATE DATABASE nem USE de propósito: ela roda no banco que
--   estiver SELECIONADO. Hospedagens costumam criar o banco pelo painel
--   (às vezes com nome como usuario$almoxarifado). Crie o banco pelo
--   painel, selecione-o e execute esta parte. O mesmo vale para um banco
--   de testes (ex.: almoxarifado_teste): selecione-o e execute a Parte 1.
--
-- PARTE 2 - Usuário próprio da aplicação (opcional)
--   Só funciona se você tiver permissão de administrador no MySQL
--   (servidor seu). Em hospedagens que criam usuários pelo painel
--   (como o PythonAnywhere), pule esta parte e crie o usuário no painel.
--
-- Depois de executar, configure o sistema com as variáveis de ambiente:
--   DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME  (lidas pelo conexao.py)
-- =====================================================================

-- =====================================================================
-- PARTE 1 - TABELAS (ordem importa por causa das chaves estrangeiras)
-- =====================================================================

-- 1. PRODUTOS
CREATE TABLE IF NOT EXISTS `produtos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `codigo` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nome` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tipo` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `data_validade` date DEFAULT NULL,
  `quantidade` int NOT NULL DEFAULT '0',
  `situacao` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'disponível',
  `data_inclusao` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. LOTES
CREATE TABLE IF NOT EXISTS `lotes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `produto_id` int NOT NULL,
  `numero_lote` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `quantidade` int NOT NULL DEFAULT '0',
  `data_validade` date DEFAULT NULL,
  `data_inclusao` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `situacao` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'ativo',
  `data_cadastro` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_lotes_numero` (`numero_lote`),
  KEY `produto_id` (`produto_id`),
  CONSTRAINT `lotes_ibfk_1` FOREIGN KEY (`produto_id`) REFERENCES `produtos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. MOVIMENTAÇÕES
CREATE TABLE IF NOT EXISTS `movimentacoes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `produto_id` int DEFAULT NULL,
  `tipo_movimentacao` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descricao` text COLLATE utf8mb4_unicode_ci,
  `responsavel` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `data_movimentacao` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `lote_id` int DEFAULT NULL,
  `usuario_responsavel` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `produto_id` (`produto_id`),
  KEY `idx_movimentacoes_lote` (`lote_id`),
  CONSTRAINT `movimentacoes_ibfk_1` FOREIGN KEY (`produto_id`) REFERENCES `produtos` (`id`),
  CONSTRAINT `fk_movimentacoes_lote` FOREIGN KEY (`lote_id`) REFERENCES `lotes` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. USUÁRIOS (senha guardada só como hash)
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nome` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `senha_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ativo` tinyint(1) NOT NULL DEFAULT '1',
  `motivo_troca` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `senha_alterada_em` datetime NOT NULL,
  `ultimo_acesso` datetime DEFAULT NULL,
  `data_criacao` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_usuarios_usuario` (`usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. PEDIDOS DE COMPRA
CREATE TABLE IF NOT EXISTS `pedidos_compra` (
  `id` int NOT NULL AUTO_INCREMENT,
  `numero` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `produto_id` int DEFAULT NULL,
  `nome_produto` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `produto_novo` tinyint(1) NOT NULL DEFAULT '0',
  `quantidade` int NOT NULL,
  `setor` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `link_produto` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pendente',
  `solicitante` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `data_pedido` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `data_atualizacao` timestamp NULL DEFAULT NULL,
  `atualizado_por` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_pedidos_numero` (`numero`),
  KEY `idx_pedidos_produto` (`produto_id`),
  KEY `idx_pedidos_status` (`status`),
  CONSTRAINT `fk_pedidos_produto` FOREIGN KEY (`produto_id`)
    REFERENCES `produtos` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_pedidos_status`
    CHECK (`status` IN ('pendente', 'aprovado', 'rejeitado'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Conferência: devem aparecer 5 tabelas
SHOW TABLES;

-- =====================================================================
-- PARTE 2 - USUÁRIO DA APLICAÇÃO COM O MÍNIMO DE PERMISSÕES (OPCIONAL)
--
-- Não use o usuário "root" no sistema online. O sistema só lê, insere e
-- atualiza dados (nunca apaga linhas nem altera tabelas), então basta
-- SELECT, INSERT e UPDATE.
--
-- 1) TROQUE o nome do banco e a senha abaixo antes de executar.
-- 2) 'localhost' = o sistema roda no mesmo servidor do MySQL.
--    Se o sistema ficar em OUTRO servidor, troque 'localhost' por '%'
--    (ou, melhor, pelo IP do servidor do sistema).
-- =====================================================================

CREATE USER IF NOT EXISTS 'almox_app'@'localhost'
  IDENTIFIED BY 'TROQUE_ESTA_SENHA_POR_UMA_FORTE';

GRANT SELECT, INSERT, UPDATE ON `almoxarifado`.* TO 'almox_app'@'localhost';

FLUSH PRIVILEGES;

-- Conferência das permissões do usuário
SHOW GRANTS FOR 'almox_app'@'localhost';

-- Mudanças futuras no banco (colunas novas etc.) devem ser feitas por um
-- usuário administrador, com scripts que só ADICIONAM (ALTER TABLE ... ADD),
-- nunca com DROP. Faça backup antes.
