
-- Adiciona o vínculo entre o assistido e o aluno que realizou o cadastro.

ALTER TABLE assistidos
ADD COLUMN id_aluno_cadastro INT NULL AFTER id_assistido,
ADD INDEX idx_assistidos_aluno_cadastro (id_aluno_cadastro),
ADD CONSTRAINT fk_assistidos_aluno_cadastro
    FOREIGN KEY (id_aluno_cadastro)
    REFERENCES alunos (id_aluno)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;
