
from sqlalchemy.orm import Session

from app.models.caso_juridico import CasoJuridico
from app.models.aluno import Aluno
from app.models.professor import Professor
from app.models.usuario import Usuario

from app.repositories.historico_caso_repository import (
    HistoricoCasoRepository
)


class HistoricoCasoService:

    # Busca o cadastro acadêmico do aluno associado ao usuário.
    @staticmethod
    def _buscar_id_aluno(db: Session, id_usuario: int):
        aluno = (
            db.query(Aluno)
            .filter(Aluno.id_usuario == id_usuario)
            .first()
        )

        if not aluno:
            raise LookupError(
                "Cadastro de aluno não encontrado."
            )

        return aluno.id_aluno

    # Busca o cadastro ativo do professor associado ao usuário.
    @staticmethod
    def _buscar_id_professor(db: Session, id_usuario: int):
        professor = (
            db.query(Professor)
            .filter(
                Professor.id_usuario == id_usuario,
                Professor.situacao == "Ativo"
            )
            .first()
        )

        if not professor:
            raise LookupError(
                "Cadastro de professor não encontrado ou inativo."
            )

        return professor.id_professor

    # Lista os registros históricos conforme as permissões do perfil.
    @staticmethod
    def listar(db: Session, usuario: Usuario):
        if usuario.perfil == "Gestão":
            return HistoricoCasoRepository.listar(db)

        if usuario.perfil == "Aluno":
            id_aluno = HistoricoCasoService._buscar_id_aluno(
                db, usuario.id_usuario
            )
            return HistoricoCasoRepository.listar_por_aluno(
                db, id_aluno
            )

        if usuario.perfil == "Professor":
            id_professor = HistoricoCasoService._buscar_id_professor(
                db, usuario.id_usuario
            )
            return HistoricoCasoRepository.listar_por_professor(
                db, id_professor
            )

        raise PermissionError(
            "Você não possui permissão para consultar o histórico."
        )

    # Busca um registro histórico específico respeitando as permissões do usuário.
    @staticmethod
    def buscar_por_id(
        db: Session,
        id_historico: int,
        usuario: Usuario
    ):
        if usuario.perfil == "Gestão":
            historico = HistoricoCasoRepository.buscar_por_id(
                db, id_historico
            )

        elif usuario.perfil == "Aluno":
            id_aluno = HistoricoCasoService._buscar_id_aluno(
                db, usuario.id_usuario
            )
            historico = HistoricoCasoRepository.buscar_por_id_e_aluno(
                db, id_historico, id_aluno
            )

        elif usuario.perfil == "Professor":
            id_professor = HistoricoCasoService._buscar_id_professor(
                db, usuario.id_usuario
            )
            historico = HistoricoCasoRepository.buscar_por_id_e_professor(
                db, id_historico, id_professor
            )

        else:
            raise PermissionError(
                "Você não possui permissão para consultar este histórico."
            )

        if not historico:
            raise LookupError(
                "Registro histórico não encontrado."
            )

        return historico

    # Lista os registros históricos associados a um caso específico.
    @staticmethod
    def listar_por_caso(
        db: Session,
        id_caso: int,
        usuario: Usuario
    ):
        if usuario.perfil == "Gestão":
            return HistoricoCasoRepository.listar_por_caso(
                db, id_caso
            )

        # Filtra os registros a partir dos casos acessíveis ao usuário.
        historicos = HistoricoCasoService.listar(db, usuario)

        return [
            historico
            for historico in historicos
            if historico.id_caso == id_caso
        ]

    # Lista os registros históricos associados a um usuário responsável.
    @staticmethod
    def listar_por_usuario(
        db: Session,
        id_usuario_responsavel: int,
        usuario: Usuario
    ):
        if usuario.perfil == "Gestão":
            return HistoricoCasoRepository.listar_por_usuario(
                db, id_usuario_responsavel
            )

        # Restringe a consulta aos históricos que o usuário pode acessar.
        historicos = HistoricoCasoService.listar(db, usuario)

        return [
            historico
            for historico in historicos
            if historico.id_usuario_responsavel
            == id_usuario_responsavel
        ]

    # Registra uma ocorrência no histórico do caso jurídico.
    @staticmethod
    def criar(
        db: Session,
        dados,
        usuario: Usuario
    ):
        # Verifica se o perfil possui permissão para registrar ocorrências.
        if usuario.perfil not in ["Aluno", "Professor", "Gestão"]:
            raise PermissionError(
                "Você não possui permissão para registrar ocorrências no histórico."
            )

        # Verifica se o caso jurídico informado existe.
        caso = (
            db.query(CasoJuridico)
            .filter(CasoJuridico.id_caso == dados.id_caso)
            .first()
        )

        if not caso:
            raise LookupError(
                "Caso jurídico não encontrado."
            )

        # Verifica se o aluno é o responsável pelo caso.
        if usuario.perfil == "Aluno":
            id_aluno = HistoricoCasoService._buscar_id_aluno(
                db, usuario.id_usuario
            )

            if caso.id_aluno_responsavel != id_aluno:
                raise PermissionError(
                    "Você não possui permissão para registrar ocorrências neste caso."
                )

        # Verifica se o professor é o orientador do caso.
        elif usuario.perfil == "Professor":
            id_professor = HistoricoCasoService._buscar_id_professor(
                db, usuario.id_usuario
            )

            if caso.id_professor_orientador != id_professor:
                raise PermissionError(
                    "Você não possui permissão para registrar ocorrências neste caso."
                )

        # Define o usuário autenticado como responsável pelo registro.
        historico_dados = dados.model_dump()
        historico_dados["id_usuario_responsavel"] = usuario.id_usuario

        try:
            return HistoricoCasoRepository.criar(
                db,
                historico_dados
            )

        # Desfaz a transação caso ocorra algum erro durante o registro.
        except Exception:
            db.rollback()
            raise
