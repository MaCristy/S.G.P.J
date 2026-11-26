
from sqlalchemy.orm import Session

from app.models.solicitacao_cadastro import SolicitacaoCadastro
from app.models.usuario import Usuario


class SolicitacaoCadastroRepository:
    """
    Centraliza as consultas e operações de persistência
    das solicitações de cadastro.
    """

    # Associa o nome e o e-mail do usuário à solicitação consultada.
    @staticmethod
    def associar_dados_usuario(solicitacao, nome, email):
        solicitacao.nome = nome
        solicitacao.email_institucional = email

        return solicitacao

    # Lista as solicitações, permitindo filtrar pelo status.
    @staticmethod
    def listar(db: Session, status_solicitacao: str | None = None):

        consulta = db.query(
            SolicitacaoCadastro,
            Usuario.nome,
            Usuario.email_institucional
        ).join(
            Usuario,
            Usuario.id_usuario == SolicitacaoCadastro.id_usuario
        )

        # Aplica o filtro quando um status é informado.
        if status_solicitacao:
            consulta = consulta.filter(
                SolicitacaoCadastro.status_solicitacao
                == status_solicitacao
            )

        # Apresenta primeiro as solicitações mais recentes.
        resultados = consulta.order_by(
            SolicitacaoCadastro.data_solicitacao.desc(),
            SolicitacaoCadastro.id_solicitacao.desc()
        ).all()

        # Associa os dados do usuário a cada solicitação.
        return [
            SolicitacaoCadastroRepository.associar_dados_usuario(
                solicitacao,
                nome,
                email
            )
            for solicitacao, nome, email in resultados
        ]

    # Busca uma solicitação pelo identificador, incluindo os dados do usuário.
    @staticmethod
    def buscar_por_id(db: Session, id_solicitacao: int):

        resultado = db.query(
            SolicitacaoCadastro,
            Usuario.nome,
            Usuario.email_institucional
        ).join(
            Usuario,
            Usuario.id_usuario == SolicitacaoCadastro.id_usuario
        ).filter(
            SolicitacaoCadastro.id_solicitacao == id_solicitacao
        ).first()

        if not resultado:
            return None

        solicitacao, nome, email = resultado

        return SolicitacaoCadastroRepository.associar_dados_usuario(
            solicitacao,
            nome,
            email
        )

    # Busca a solicitação pendente de determinado usuário.
    @staticmethod
    def buscar_pendente_por_usuario(db: Session, id_usuario: int):

        return db.query(SolicitacaoCadastro).filter(
            SolicitacaoCadastro.id_usuario == id_usuario,
            SolicitacaoCadastro.status_solicitacao == "Pendente"
        ).first()

    # Busca uma solicitação pendente pela matrícula acadêmica.
    @staticmethod
    def buscar_pendente_por_matricula(db: Session, matricula: str):

        return db.query(SolicitacaoCadastro).filter(
            SolicitacaoCadastro.matricula == matricula,
            SolicitacaoCadastro.status_solicitacao == "Pendente"
        ).first()

    # Busca uma solicitação pendente pela identificação funcional.
    @staticmethod
    def buscar_pendente_por_identificacao_funcional(
        db: Session,
        identificacao_funcional: str
    ):

        return db.query(SolicitacaoCadastro).filter(
            SolicitacaoCadastro.identificacao_funcional
            == identificacao_funcional,
            SolicitacaoCadastro.status_solicitacao == "Pendente"
        ).first()

    # Recupera a solicitação mais recente de determinado usuário.
    @staticmethod
    def buscar_ultima_por_usuario(db: Session, id_usuario: int):

        return db.query(SolicitacaoCadastro).filter(
            SolicitacaoCadastro.id_usuario == id_usuario
        ).order_by(
            SolicitacaoCadastro.data_solicitacao.desc(),
            SolicitacaoCadastro.id_solicitacao.desc()
        ).first()

    # Cria uma solicitação com os dados preparados pelo serviço.
    @staticmethod
    def criar(db: Session, dados: dict):

        solicitacao = SolicitacaoCadastro(**dados)

        # Adiciona a solicitação à sessão do banco de dados.
        db.add(solicitacao)

        return solicitacao

    # Atualiza somente os campos definidos pelo serviço.
    @staticmethod
    def atualizar(
        db: Session,
        solicitacao: SolicitacaoCadastro,
        dados: dict
    ):

        for campo, valor in dados.items():
            setattr(solicitacao, campo, valor)

        # Mantém a solicitação associada à sessão do banco de dados.
        db.add(solicitacao)

        return solicitacao
