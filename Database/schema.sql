-- =============================================================================
-- SISTEMA DE GESTÃO DA PRÁTICA JURÍDICA (S.G.P.J.)
-- Projeto de Estágio Supervisionado — Ciência da Computação — UNINASSAU
-- Autora: Maria Cristina Nogueira Paulino (João Pessoa - PB, 2026)
-- Script DDL: Modelagem Física Relacional Oficial Consolidada (Master Schema)
-- Arquivo: Database/schema.sql
--
-- REQUISITOS DE AMBIENTE:
-- 1. Versão Mínima do SGBD: MySQL 8.0.16 ou superior.
--    (Justificativa: versões anteriores a 8.0.16 analisavam sintaticamente as
--     cláusulas CHECK, mas as ignoravam; a partir do MySQL 8.0.16, as restrições
--     CHECK são ativamente validadas e aplicadas pelo mecanismo do SGBD).
-- 2. Contexto de Execução: O banco de dados 'sgpj' deve estar previamente criado.
--    Este script utiliza a instrução 'USE sgpj;' para garantir a seleção correta.
-- 3. Instalação Nova / Master: Contém as 10 tabelas, 10 índices de performance
--    (incluindo 'idx_historico_caso_data') e 5 gatilhos de integridade/auditoria.
-- =============================================================================

-- Seleção explícita do banco de dados oficial do sistema
USE sgpj;

-- Configurações de modo SQL e timezone de sessão
SET @OLD_SQL_MODE = @@SQL_MODE, SQL_MODE = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------------------------------
-- 1. TABELA: usuarios (Doc. Seção 4.1 e 4.2)
-- Finalidade: Conta de acesso, credenciais, perfil e estado de ativação.
-- -----------------------------------------------------------------------------
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    email_institucional VARCHAR(150) NOT NULL,
    senha_armazenada VARCHAR(255) NOT NULL,
    perfil VARCHAR(50) NOT NULL,
    situacao_conta VARCHAR(30) NOT NULL DEFAULT 'Ativo',
    data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ultimo_acesso DATETIME NULL,
    CONSTRAINT uq_usuario_email UNIQUE (email_institucional)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 2. TABELA: alunos (Doc. Seção 4.1 e 4.2 - "Aluno/Estagiário")
-- Finalidade: Dados específicos do estudante, associado a uma conta de usuário.
-- -----------------------------------------------------------------------------
CREATE TABLE alunos (
    id_aluno INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    matricula VARCHAR(50) NOT NULL,
    curso VARCHAR(100) NOT NULL,
    periodo INT NOT NULL,
    situacao_academica VARCHAR(50) NOT NULL,
    data_vinculo DATE NOT NULL,
    CONSTRAINT uq_aluno_usuario UNIQUE (id_usuario),
    CONSTRAINT uq_aluno_matricula UNIQUE (matricula),
    CONSTRAINT fk_alunos_usuarios FOREIGN KEY (id_usuario) 
        REFERENCES usuarios (id_usuario) 
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 3. TABELA: professores (Doc. Seção 4.1 e 4.2 - "Professor/Orientador")
-- Finalidade: Dados específicos do orientador, associado a uma conta de usuário.
-- -----------------------------------------------------------------------------
CREATE TABLE professores (
    id_professor INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    identificacao_funcional VARCHAR(50) NOT NULL,
    area_vinculo VARCHAR(100) NULL,
    situacao VARCHAR(30) NOT NULL DEFAULT 'Ativo',
    CONSTRAINT uq_professor_usuario UNIQUE (id_usuario),
    CONSTRAINT uq_professor_funcional UNIQUE (identificacao_funcional),
    CONSTRAINT fk_professores_usuarios FOREIGN KEY (id_usuario) 
        REFERENCES usuarios (id_usuario) 
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 4. TABELA: assistidos (Doc. Seção 4.1 e 4.2)
-- Finalidade: Dados necessários à identificação e ao contato da pessoa atendida.
-- -----------------------------------------------------------------------------
CREATE TABLE assistidos (
    id_assistido INT AUTO_INCREMENT PRIMARY KEY,
    nome_completo VARCHAR(200) NOT NULL,
    identificador_cadastral VARCHAR(50) NOT NULL,
    contato VARCHAR(100) NOT NULL,
    endereco TEXT NULL,
    observacoes_administrativas TEXT NULL,
    data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    situacao VARCHAR(30) NOT NULL DEFAULT 'Ativo',
    CONSTRAINT uq_assistido_identificador UNIQUE (identificador_cadastral)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 5. TABELA: casos_juridicos (Doc. Seção 4.1 e 4.2)
-- Finalidade: Demanda acompanhada, estado, datas e responsáveis.
-- Estados sugeridos na documentação: 'Em triagem', 'Aberto', 'Em Andamento', 'Suspenso', 'Encerrado'.
-- -----------------------------------------------------------------------------
CREATE TABLE casos_juridicos (
    id_caso INT AUTO_INCREMENT PRIMARY KEY,
    codigo_interno VARCHAR(50) NOT NULL,
    id_assistido INT NOT NULL,
    titulo_assunto VARCHAR(200) NOT NULL,
    descricao TEXT NOT NULL,
    area_juridica VARCHAR(100) NOT NULL,
    situacao ENUM('Em triagem', 'Aberto', 'Em Andamento', 'Suspenso', 'Encerrado') NOT NULL DEFAULT 'Em triagem',
    data_abertura DATE NOT NULL,
    data_encerramento DATE NULL,
    id_aluno_responsavel INT NULL,
    id_professor_orientador INT NULL,
    CONSTRAINT uq_caso_codigo UNIQUE (codigo_interno),
    -- Restrição UNIQUE composta técnica para suporte de integridade referencial cruzada (Garantia 1)
    CONSTRAINT uq_caso_assistido UNIQUE (id_caso, id_assistido),
    CONSTRAINT fk_casos_assistidos FOREIGN KEY (id_assistido) 
        REFERENCES assistidos (id_assistido) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_casos_alunos FOREIGN KEY (id_aluno_responsavel) 
        REFERENCES alunos (id_aluno) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_casos_professores FOREIGN KEY (id_professor_orientador) 
        REFERENCES professores (id_professor) 
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 6. TABELA: atendimentos (Doc. Seção 4.1 e 4.2)
-- Finalidade: Registra data, descrição, assistido e usuário que fez o registro.
-- -----------------------------------------------------------------------------
CREATE TABLE atendimentos (
    id_atendimento INT AUTO_INCREMENT PRIMARY KEY,
    id_assistido INT NOT NULL,
    id_caso INT NULL,
    id_usuario_registro INT NOT NULL,
    data_hora DATETIME NOT NULL,
    tipo VARCHAR(80) NOT NULL,
    descricao_objetiva TEXT NOT NULL,
    encaminhamento TEXT NULL,
    data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_atendimentos_assistidos FOREIGN KEY (id_assistido) 
        REFERENCES assistidos (id_assistido) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_atendimentos_usuarios FOREIGN KEY (id_usuario_registro) 
        REFERENCES usuarios (id_usuario) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    -- Quando id_caso não for NULL, garante que o caso pertença ao mesmo assistido.
    -- A FK composta também garante a existência do caso; por isso não há FK simples duplicada.
    CONSTRAINT fk_atendimentos_caso_assistido FOREIGN KEY (id_caso, id_assistido) 
        REFERENCES casos_juridicos (id_caso, id_assistido) 
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 7. TABELA: atividades (Doc. Seção 4.1 e 4.2)
-- Finalidade: Ação prevista ou realizada dentro de um caso.
-- Estados sugeridos na documentação: 'Pendente', 'Em andamento', 'Concluída', 'Cancelada'.
-- -----------------------------------------------------------------------------
CREATE TABLE atividades (
    id_atividade INT AUTO_INCREMENT PRIMARY KEY,
    id_caso INT NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    descricao TEXT NOT NULL,
    id_responsavel INT NOT NULL,
    situacao ENUM('Pendente', 'Em andamento', 'Concluída', 'Cancelada') NOT NULL DEFAULT 'Pendente',
    prioridade VARCHAR(30) NOT NULL DEFAULT 'Média',
    data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_prevista DATE NULL,
    data_conclusao DATETIME NULL,
    -- Restrição UNIQUE composta técnica para suporte de integridade referencial cruzada (Garantia 2)
    CONSTRAINT uq_atividade_caso UNIQUE (id_atividade, id_caso),
    CONSTRAINT fk_atividades_casos FOREIGN KEY (id_caso) 
        REFERENCES casos_juridicos (id_caso) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_atividades_usuarios FOREIGN KEY (id_responsavel) 
        REFERENCES usuarios (id_usuario) 
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 8. TABELA: prazos (Doc. Seção 4.1 e 4.2)
-- Finalidade: Data relevante associada a um caso e, opcionalmente, a uma atividade.
-- Estados sugeridos na documentação: 'Pendente', 'Concluído', 'Vencido'.
-- -----------------------------------------------------------------------------
CREATE TABLE prazos (
    id_prazo INT AUTO_INCREMENT PRIMARY KEY,
    id_caso INT NOT NULL,
    id_atividade INT NULL,
    descricao VARCHAR(255) NOT NULL,
    data_limite DATE NOT NULL,
    situacao ENUM('Pendente', 'Concluído', 'Vencido') NOT NULL DEFAULT 'Pendente',
    id_responsavel INT NOT NULL,
    observacoes TEXT NULL,
    data_conclusao DATETIME NULL,
    CONSTRAINT fk_prazos_casos FOREIGN KEY (id_caso) 
        REFERENCES casos_juridicos (id_caso) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_prazos_usuarios FOREIGN KEY (id_responsavel) 
        REFERENCES usuarios (id_usuario) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    -- Chave estrangeira composta para Garantia 2: quando id_atividade for informada,
    -- a atividade vinculada deve pertencer obrigatoriamente ao mesmo caso indicado em id_caso.
    CONSTRAINT fk_prazos_atividade_caso FOREIGN KEY (id_atividade, id_caso) 
        REFERENCES atividades (id_atividade, id_caso) 
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 9. TABELA: documentos (Doc. Seção 4.1 e 4.2)
-- Finalidade: Metadados e referência de arquivo associado a caso ou atendimento.
-- Classificação de acesso mantida sem DEFAULT (aguardando homologação da coordenação).
-- -----------------------------------------------------------------------------
CREATE TABLE documentos (
    id_documento INT AUTO_INCREMENT PRIMARY KEY,
    id_caso INT NULL,
    id_atendimento INT NULL,
    nome VARCHAR(255) NOT NULL,
    tipo VARCHAR(80) NOT NULL,
    caminho_armazenamento VARCHAR(500) NOT NULL,
    data_inclusao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_usuario_inclusao INT NOT NULL,
    classificacao_acesso VARCHAR(50) NULL,
    CONSTRAINT fk_documentos_casos FOREIGN KEY (id_caso) 
        REFERENCES casos_juridicos (id_caso) 
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_documentos_atendimentos FOREIGN KEY (id_atendimento) 
        REFERENCES atendimentos (id_atendimento) 
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_documentos_usuarios FOREIGN KEY (id_usuario_inclusao) 
        REFERENCES usuarios (id_usuario) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    -- Pelo menos uma associação de contexto deve estar preenchida (requer MySQL 8.0.16+)
    CONSTRAINT chk_documento_referencia CHECK (id_caso IS NOT NULL OR id_atendimento IS NOT NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 10. TABELA: historico_caso (Doc. Seção 4.1 e 4.2 - "Histórico / Registro de Ocorrência")
-- Finalidade: Ocorrências relevantes, usuário responsável, data/hora e referência.
-- Aplicação mandatória da RN07: registros imutáveis (append-only).
-- -----------------------------------------------------------------------------
CREATE TABLE historico_caso (
    id_historico INT AUTO_INCREMENT PRIMARY KEY,
    id_caso INT NOT NULL,
    id_usuario_responsavel INT NOT NULL,
    tipo_ocorrencia VARCHAR(100) NOT NULL,
    descricao TEXT NOT NULL,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    referencia_registro_afetado VARCHAR(100) NULL,
    CONSTRAINT fk_historico_casos FOREIGN KEY (id_caso) 
        REFERENCES casos_juridicos (id_caso) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_historico_usuarios FOREIGN KEY (id_usuario_responsavel) 
        REFERENCES usuarios (id_usuario) 
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- ÍNDICES DE OTIMIZAÇÃO E PERFORMANCE (RF09, RF12, RF13, RF14 e Dashboard)
-- -----------------------------------------------------------------------------
CREATE INDEX idx_assistidos_busca ON assistidos (nome_completo, identificador_cadastral);
CREATE INDEX idx_casos_aluno ON casos_juridicos (id_aluno_responsavel);
CREATE INDEX idx_casos_professor ON casos_juridicos (id_professor_orientador);
CREATE INDEX idx_casos_situacao ON casos_juridicos (situacao);
CREATE INDEX idx_atendimentos_data ON atendimentos (data_hora);
CREATE INDEX idx_atividades_situacao ON atividades (situacao);
CREATE INDEX idx_prazos_alerta ON prazos (data_limite, situacao);
CREATE INDEX idx_documentos_caso ON documentos (id_caso);
CREATE INDEX idx_documentos_atendimento ON documentos (id_atendimento);
CREATE INDEX idx_historico_caso_data ON historico_caso (id_caso, data_hora);

-- -----------------------------------------------------------------------------
-- TRIGGERS DE INTEGRIDADE, CONSISTÊNCIA CRUZADA E AUDITORIA (RN07, RNF Integridade)
-- -----------------------------------------------------------------------------

DELIMITER //

-- -----------------------------------------------------------------------------
-- GARANTIA RN07: Imutabilidade do histórico (Proibição de UPDATE e DELETE)
-- -----------------------------------------------------------------------------
CREATE TRIGGER trg_historico_bloqueio_update
BEFORE UPDATE ON historico_caso
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'RN07: Registros da tabela historico_caso sao imutaveis e nao podem ser alterados.';
END//

CREATE TRIGGER trg_historico_bloqueio_delete
BEFORE DELETE ON historico_caso
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'RN07: Registros da tabela historico_caso nao podem ser excluidos silenciosamente.';
END//

-- -----------------------------------------------------------------------------
-- NOTA TÉCNICA (GARANTIAS 1 E 2):
-- As Garantias 1 (mesmo assistido entre atendimento e caso) e 2 (mesmo caso entre
-- prazo e atividade) são garantidas de forma nativa e declarativa pelas chaves
-- estrangeiras compostas 'fk_atendimentos_caso_assistido' e 'fk_prazos_atividade_caso'.
-- Dispensam-se triggers procedurais para esses dois cenários, evitando consultas
-- redundantes a cada operação de escrita.
-- -----------------------------------------------------------------------------

-- -----------------------------------------------------------------------------
-- GARANTIA 3: Consistência Documental (Caso e Atendimento Simultâneos)
-- Valida que, se o documento possuir simultaneamente id_caso e id_atendimento,
-- o atendimento obrigatoriamente pertença àquele mesmo caso.
-- -----------------------------------------------------------------------------
CREATE TRIGGER trg_documentos_consistencia_bi
BEFORE INSERT ON documentos
FOR EACH ROW
BEGIN
    DECLARE v_caso_atendimento INT;
    IF NEW.id_caso IS NOT NULL AND NEW.id_atendimento IS NOT NULL THEN
        SELECT id_caso INTO v_caso_atendimento 
        FROM atendimentos 
        WHERE id_atendimento = NEW.id_atendimento;

        IF v_caso_atendimento IS NULL OR v_caso_atendimento <> NEW.id_caso THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Garantia 3: O atendimento vinculado ao documento nao pertence ao mesmo caso associado.';
        END IF;
    END IF;
END//

CREATE TRIGGER trg_documentos_consistencia_bu
BEFORE UPDATE ON documentos
FOR EACH ROW
BEGIN
    DECLARE v_caso_atendimento INT;
    IF NEW.id_caso IS NOT NULL AND NEW.id_atendimento IS NOT NULL THEN
        SELECT id_caso INTO v_caso_atendimento 
        FROM atendimentos 
        WHERE id_atendimento = NEW.id_atendimento;

        IF v_caso_atendimento IS NULL OR v_caso_atendimento <> NEW.id_caso THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Garantia 3: O atendimento vinculado ao documento nao pertence ao mesmo caso associado.';
        END IF;
    END IF;
END//

-- -----------------------------------------------------------------------------
-- GARANTIA 3 (Proteção Bidirecional): Impedir que alteração de caso em atendimento
-- viole documentos com duplo vínculo sem a sequência transacional controlada.
-- -----------------------------------------------------------------------------
CREATE TRIGGER trg_atendimentos_consistencia_documental_bu
BEFORE UPDATE ON atendimentos
FOR EACH ROW
BEGIN
    DECLARE v_docs_conflitantes INT DEFAULT 0;
    -- Se o id_caso do atendimento estiver sendo alterado ou desvinculado (definido para NULL)
    IF NOT (NEW.id_caso <=> OLD.id_caso) THEN
        SELECT COUNT(*) INTO v_docs_conflitantes 
        FROM documentos 
        WHERE id_atendimento = OLD.id_atendimento 
          AND id_caso IS NOT NULL;

        IF v_docs_conflitantes > 0 THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Garantia 3: Nao e possivel alterar ou desvincular o caso deste atendimento: existem documentos vinculados simultaneamente a ambos. Execute a sequencia transacional controlada.';
        END IF;
    END IF;
END//

DELIMITER ;

-- Restaura configurações do modo SQL
SET SQL_MODE = @OLD_SQL_MODE;
