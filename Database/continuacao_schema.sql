-- =============================================================================
-- SISTEMA DE GESTÃO DA PRÁTICA JURÍDICA (S.G.P.J.)
-- Projeto de Estágio Supervisionado — Ciência da Computação — UNINASSAU
-- Autora: Maria Cristina Nogueira Paulino (João Pessoa - PB, 2026)
-- Script Complementar Otimizado: Continuação da Instalação do Schema (MySQL 8.0.16+)
-- Arquivo: Database/continuacao_schema.sql
--
-- FINALIDADE:
-- Este script executa exclusivamente a criação das estruturas pendentes no banco
-- 'sgpj', após a interrupção da execução inicial (as 8 primeiras tabelas já
-- existem e não são recriadas aqui):
--   1. Tabela 'documentos' (com ON UPDATE RESTRICT e CHECK constraint).
--   2. Tabela 'historico_caso' (trilha de auditoria imutável).
--   3. Índices estratégicos de negócio (omitindo índices redundantes já
--      gerados automaticamente pelo InnoDB para suporte às Foreign Keys).
--   4. Triggers de auditoria (RN07) e integridade documental (Garantia 3).
-- =============================================================================

-- Seleção do banco de dados oficial existente
USE sgpj;

-- Configurações de modo SQL de sessão
SET @OLD_SQL_MODE = @@SQL_MODE, SQL_MODE = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------------------------------
-- 1. TABELA: documentos (Doc. Seção 4.1 e 4.2)
-- Correção aplicada: ON UPDATE RESTRICT nas FKs de casos e atendimentos
-- para compatibilidade com o CHECK constraint no MySQL 8.0.16+ (Erro 3823 evitado).
-- Nota: O InnoDB criará automaticamente índices para suporte a fk_documentos_casos (id_caso)
-- e fk_documentos_atendimentos (id_atendimento).
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
-- 2. TABELA: historico_caso (Doc. Seção 4.1 e 4.2 - "Histórico / Registro de Ocorrência")
-- Finalidade: Trilha de auditoria imutável (RN07).
-- Nota: O InnoDB criará automaticamente o índice para suporte a fk_historico_casos (id_caso).
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
-- 3. ÍNDICES DE PERFORMANCE E CONSULTAS DE NEGÓCIO
-- Foram mantidos exclusivamente os índices que agregam desempenho real a buscas
-- textuais, filtros de situação, agrupamentos do dashboard e intervalos de datas.
-- Índices estritamente redundantes com as FKs do InnoDB foram omitidos.
-- -----------------------------------------------------------------------------

-- Busca textual e cadastral de assistidos (RF03, RF12)
CREATE INDEX idx_assistidos_busca ON assistidos (nome_completo, identificador_cadastral);

-- Agrupamento do Dashboard e filtros por situação de caso (RF05, RF12, Indicador 5)
CREATE INDEX idx_casos_situacao ON casos_juridicos (situacao);

-- Relatórios e contagem de atendimentos por período (RF04, RF12, Indicador 1)
CREATE INDEX idx_atendimentos_data ON atendimentos (data_hora);

-- Monitoramento e contagem de tarefas por situação/pendência (RF07, RF08, Indicador 6)
CREATE INDEX idx_atividades_situacao ON atividades (situacao);

-- Consulta de risco: prazos processuais críticos por data limite e status (RF09, Indicador 7)
CREATE INDEX idx_prazos_alerta ON prazos (data_limite, situacao);

-- Histórico cronológico de ocorrências por caso (RF11)
CREATE INDEX idx_historico_caso_data ON historico_caso (id_caso, data_hora);
-- -----------------------------------------------------------------------------
-- NOTA TÉCNICA SOBRE ÍNDICES OMITIDOS POR REDUNDÂNCIA:
-- Os seguintes índices foram deliberadamente omitidos pois o InnoDB já cria
-- índices automáticos de mesmo prefixo para suporte às Foreign Keys:
--  - idx_casos_aluno: coberto pelo índice da FK 'fk_casos_alunos' (id_aluno_responsavel).
--  - idx_casos_professor: coberto pelo índice da FK 'fk_casos_professores' (id_professor_orientador).
--  - idx_documentos_caso: coberto pelo índice da FK 'fk_documentos_casos' (id_caso).
--  - idx_documentos_atendimento: coberto pelo índice da FK 'fk_documentos_atendimentos' (id_atendimento).
--  - idx_historico_caso_data: O índice composto idx_historico_caso_data (id_caso, data_hora) foi mantido porque atende a uma necessidade diferente do índice individual criado automaticamente pela chave estrangeira. Ele otimiza a recuperação das ocorrências de um caso em ordem cronológica, favorecendo a funcionalidade de linha do tempo do histórico.
-- -----------------------------------------------------------------------------

-- -----------------------------------------------------------------------------
-- 4. TRIGGERS DE INTEGRIDADE, CONSISTÊNCIA CRUZADA E AUDITORIA
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
