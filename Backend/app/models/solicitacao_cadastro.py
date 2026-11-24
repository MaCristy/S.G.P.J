
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Text,
    Enum,
    ForeignKey,
    Computed,
    UniqueConstraint,
    CheckConstraint,
    Index,
    func
)

from app.db.base import Base


# Representa as solicitações públicas de cadastro de alunos e professores.
class SolicitacaoCadastro(Base):

    __tablename__ = "solicitacoes_cadastro"

    # Identificador único da solicitação.
    id_solicitacao = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # Identifica o usuário associado à solicitação.
    id_usuario = Column(
        Integer,
        ForeignKey(
            "usuarios.id_usuario",
            ondelete="RESTRICT",
            onupdate="CASCADE"
        ),
        nullable=False
    )

    # Define qual perfil está sendo solicitado.
    perfil_solicitado = Column(
        Enum("Aluno", "Professor", name="perfil_solicitado_enum"),
        nullable=False
    )

    # Armazena os dados acadêmicos informados pelo aluno.
    matricula = Column(
        String(50),
        nullable=True
    )

    curso = Column(
        String(100),
        nullable=True
    )

    periodo = Column(
        Integer,
        nullable=True
    )

    # Armazena os dados funcionais informados pelo professor.
    identificacao_funcional = Column(
        String(50),
        nullable=True
    )

    area_vinculo = Column(
        String(100),
        nullable=True
    )

    # Armazena os dados acadêmicos confirmados pela Gestão.
    situacao_academica = Column(
        String(50),
        nullable=True
    )

    data_vinculo = Column(
        Date,
        nullable=True
    )

    # Controla a situação atual da solicitação.
    status_solicitacao = Column(
        Enum(
            "Pendente",
            "Aprovada",
            "Rejeitada",
            name="status_solicitacao_enum"
        ),
        nullable=False,
        server_default="Pendente"
    )

    # Registra automaticamente a data de criação da solicitação.
    data_solicitacao = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    # Registra quando a Gestão realizou a análise.
    data_analise = Column(
        DateTime,
        nullable=True
    )

    # Identifica o gestor responsável pela análise.
    id_gestor_analise = Column(
        Integer,
        ForeignKey(
            "usuarios.id_usuario",
            ondelete="RESTRICT",
            onupdate="CASCADE"
        ),
        nullable=True
    )

    # Armazena observações sobre a aprovação ou rejeição.
    observacao_analise = Column(
        Text,
        nullable=True
    )

    # Coluna gerada pelo banco para identificar solicitações pendentes
    # do mesmo usuário, impedindo solicitações simultâneas duplicadas.
    id_usuario_pendente = Column(
        Integer,
        Computed(
            """
            CASE
                WHEN status_solicitacao = 'Pendente'
                THEN id_usuario
                ELSE NULL
            END
            """,
            persisted=False
        ),
        nullable=True
    )

    # Coluna gerada pelo banco para impedir solicitações pendentes
    # duplicadas com a mesma matrícula acadêmica.
    matricula_pendente = Column(
        String(50),
        Computed(
            """
            CASE
                WHEN status_solicitacao = 'Pendente'
                     AND perfil_solicitado = 'Aluno'
                THEN matricula
                ELSE NULL
            END
            """,
            persisted=False
        ),
        nullable=True
    )

    # Coluna gerada pelo banco para impedir solicitações pendentes
    # duplicadas com a mesma identificação funcional.
    identificacao_funcional_pendente = Column(
        String(50),
        Computed(
            """
            CASE
                WHEN status_solicitacao = 'Pendente'
                     AND perfil_solicitado = 'Professor'
                THEN identificacao_funcional
                ELSE NULL
            END
            """,
            persisted=False
        ),
        nullable=True
    )

    # Define as restrições, relacionamentos e índices da tabela.
    __table_args__ = (

        # Permite apenas uma solicitação pendente por usuário.
        UniqueConstraint(
            "id_usuario_pendente",
            name="uq_solicitacao_usuario_pendente"
        ),

        # Impede duas solicitações pendentes com a mesma matrícula.
        UniqueConstraint(
            "matricula_pendente",
            name="uq_solicitacao_matricula_pendente"
        ),

        # Impede duas solicitações pendentes com a mesma identificação.
        UniqueConstraint(
            "identificacao_funcional_pendente",
            name="uq_solicitacao_funcional_pendente"
        ),

        # Garante que os campos preenchidos correspondam ao perfil solicitado.
        CheckConstraint(
            """
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
            """,
            name="chk_solicitacao_dados_perfil"
        ),

        # Garante que o período acadêmico seja positivo.
        CheckConstraint(
            "periodo IS NULL OR periodo > 0",
            name="chk_solicitacao_periodo"
        ),

        # Exige os dados de análise quando a solicitação for encerrada.
        CheckConstraint(
            """
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
            """,
            name="chk_solicitacao_analise"
        ),

        # Facilita consultas por situação e data da solicitação.
        Index(
            "idx_solicitacoes_status_data",
            "status_solicitacao",
            "data_solicitacao"
        )
    )
