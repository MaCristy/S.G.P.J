-- =============================================================================
-- SISTEMA DE GESTÃO DA PRÁTICA JURÍDICA (S.G.P.J.)
-- Migração incremental: solicitações públicas de cadastro
-- Arquivo: Database/migracao_solicitacoes_cadastro.sql
-- Requisito: MySQL 8.0.16 ou superior.
--
-- FINALIDADE:
-- Adicionar a tabela solicitacoes_cadastro a um banco sgpj já existente,
-- sem recriar ou modificar as tabelas e os dados atuais.
--
-- IMPORTANTE:
-- 1. Faça backup do banco antes de executar a migração.
-- 2. As tabelas usuarios, alunos e professores devem existir previamente.
-- 3. CREATE TABLE IF NOT EXISTS evita erro se a tabela já existir, mas não
--    atualiza automaticamente uma tabela existente com estrutura diferente.
-- 4. Execute esta migração uma única vez por ambiente, após conferir o backup.
-- =============================================================================

USE sgpj;

CREATE TABLE IF NOT EXISTS solicitacoes_cadastro (
    id_solicitacao INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    perfil_solicitado ENUM('Aluno', 'Professor') NOT NULL,

    -- Dados informados pelo solicitante quando o perfil for Aluno.
    matricula VARCHAR(50) NULL,
    curso VARCHAR(100) NULL,
    periodo INT NULL,

    -- Dados informados pelo solicitante quando o perfil for Professor.
    identificacao_funcional VARCHAR(50) NULL,
    area_vinculo VARCHAR(100) NULL,

    -- Dados acadêmicos complementados/confirmados pela Gestão na análise.
    situacao_academica VARCHAR(50) NULL,
    data_vinculo DATE NULL,

    -- Estado e rastreabilidade da análise.
    status_solicitacao ENUM('Pendente', 'Aprovada', 'Rejeitada')
        NOT NULL DEFAULT 'Pendente',
    data_solicitacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_analise DATETIME NULL,
    id_gestor_analise INT NULL,
    observacao_analise TEXT NULL,

    -- Colunas geradas preservam o histórico encerrado e bloqueiam duplicidades
    -- apenas entre solicitações pendentes.
    id_usuario_pendente INT
        GENERATED ALWAYS AS (
            CASE WHEN status_solicitacao = 'Pendente' THEN id_usuario ELSE NULL END
        ) VIRTUAL,
    matricula_pendente VARCHAR(50)
        GENERATED ALWAYS AS (
            CASE
                WHEN status_solicitacao = 'Pendente'
                     AND perfil_solicitado = 'Aluno'
                THEN matricula
                ELSE NULL
            END
        ) VIRTUAL,
    identificacao_funcional_pendente VARCHAR(50)
        GENERATED ALWAYS AS (
            CASE
                WHEN status_solicitacao = 'Pendente'
                     AND perfil_solicitado = 'Professor'
                THEN identificacao_funcional
                ELSE NULL
            END
        ) VIRTUAL,

    CONSTRAINT uq_solicitacao_usuario_pendente
        UNIQUE (id_usuario_pendente),
    CONSTRAINT uq_solicitacao_matricula_pendente
        UNIQUE (matricula_pendente),
    CONSTRAINT uq_solicitacao_funcional_pendente
        UNIQUE (identificacao_funcional_pendente),

    CONSTRAINT fk_solicitacoes_usuarios
        FOREIGN KEY (id_usuario)
        REFERENCES usuarios (id_usuario)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_solicitacoes_gestor
        FOREIGN KEY (id_gestor_analise)
        REFERENCES usuarios (id_usuario)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT chk_solicitacao_dados_perfil CHECK (
        (
            perfil_solicitado = 'Aluno'
            AND matricula IS NOT NULL
            AND curso IS NOT NULL
            AND periodo IS NOT NULL
            AND identificacao_funcional IS NULL
            AND area_vinculo IS NULL
        )
        OR
        (
            perfil_solicitado = 'Professor'
            AND identificacao_funcional IS NOT NULL
            AND matricula IS NULL
            AND curso IS NULL
            AND periodo IS NULL
        )
    ),
    CONSTRAINT chk_solicitacao_periodo
        CHECK (periodo IS NULL OR periodo > 0),
    CONSTRAINT chk_solicitacao_analise CHECK (
        (
            status_solicitacao = 'Pendente'
            AND data_analise IS NULL
            AND id_gestor_analise IS NULL
        )
        OR
        (
            status_solicitacao IN ('Aprovada', 'Rejeitada')
            AND data_analise IS NOT NULL
            AND id_gestor_analise IS NOT NULL
        )
    ),

    KEY idx_solicitacoes_status_data (status_solicitacao, data_solicitacao)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
