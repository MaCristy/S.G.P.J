
-- ============================================================
-- MIGRAÇÃO: SISTEMA DE NOTIFICAÇÕES DO S.G.P.J.
-- Finalidade: armazenar notificações individuais dos usuários.
-- ============================================================

CREATE TABLE notificacoes (
    id_notificacao INT AUTO_INCREMENT PRIMARY KEY,

    -- Usuário que receberá a notificação.
    id_usuario_destinatario INT NOT NULL,

    -- Usuário responsável pelo acontecimento, quando aplicável.
    id_usuario_origem INT NULL,

    -- Caso jurídico relacionado, quando aplicável.
    id_caso INT NULL,

    -- Classificação da notificação.
    tipo VARCHAR(50) NOT NULL,

    -- Título e conteúdo apresentados ao usuário.
    titulo VARCHAR(150) NOT NULL,
    mensagem TEXT NOT NULL,

    -- Destino para navegação dentro do sistema, quando aplicável.
    link VARCHAR(255) NULL,

    -- Controle de leitura.
    lida BOOLEAN NOT NULL DEFAULT FALSE,
    data_leitura DATETIME NULL,

    -- Data e hora de criação.
    data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_notificacoes_destinatario
        FOREIGN KEY (id_usuario_destinatario)
        REFERENCES usuarios (id_usuario)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_notificacoes_origem
        FOREIGN KEY (id_usuario_origem)
        REFERENCES usuarios (id_usuario)
        ON DELETE SET NULL ON UPDATE CASCADE,

    CONSTRAINT fk_notificacoes_caso
        FOREIGN KEY (id_caso)
        REFERENCES casos_juridicos (id_caso)
        ON DELETE SET NULL ON UPDATE CASCADE

) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci;

-- Índice para listar notificações de cada usuário.
CREATE INDEX idx_notificacoes_usuario_data
ON notificacoes (id_usuario_destinatario, data_criacao);

-- Índice para localizar notificações não lidas.
CREATE INDEX idx_notificacoes_usuario_leitura
ON notificacoes (id_usuario_destinatario, lida);
