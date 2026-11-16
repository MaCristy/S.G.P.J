
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.repositories.prazo_repository import PrazoRepository
from app.models.usuario import Usuario


class PrazoService:

    @staticmethod
    def _buscar_id_aluno(db: Session, id_usuario: int):
        resultado = db.execute(
            text("""
                SELECT id_aluno
                FROM alunos
                WHERE id_usuario = :id_usuario
            """),
            {"id_usuario": id_usuario}
        ).first()

        return resultado.id_aluno if resultado else None

    @staticmethod
    def _buscar_id_professor(db: Session, id_usuario: int):
        resultado = db.execute(
            text("""
                SELECT id_professor
                FROM professores
                WHERE id_usuario = :id_usuario
                  AND situacao = 'Ativo'
            """),
            {"id_usuario": id_usuario}
        ).first()

        return resultado.id_professor if resultado else None

    @staticmethod
    def _buscar_prazo_permitido(
        db: Session,
        id_prazo: int,
        usuario: Usuario
    ):
        if usuario.perfil == "Gestão":
            return PrazoRepository.buscar_por_id(db, id_prazo)

        if usuario.perfil == "Aluno":
            id_aluno = PrazoService._buscar_id_aluno(
                db, usuario.id_usuario
            )

            if not id_aluno:
                return None

            return PrazoRepository.buscar_por_id_e_aluno(
                db, id_prazo, id_aluno
            )

        if usuario.perfil == "Professor":
            id_professor = PrazoService._buscar_id_professor(
                db, usuario.id_usuario
            )

            if not id_professor:
                return None

            return PrazoRepository.buscar_por_id_e_professor(
                db, id_prazo, id_professor
            )

        raise PermissionError(
            "Perfil sem permissão para acessar prazos."
        )

    @staticmethod
    def listar(db: Session, usuario: Usuario):
        if usuario.perfil == "Gestão":
            return PrazoRepository.listar(db)

        if usuario.perfil == "Aluno":
            id_aluno = PrazoService._buscar_id_aluno(
                db, usuario.id_usuario
            )

            if not id_aluno:
                return []

            return PrazoRepository.listar_por_aluno(
                db, id_aluno
            )

        if usuario.perfil == "Professor":
            id_professor = PrazoService._buscar_id_professor(
                db, usuario.id_usuario
            )

            if not id_professor:
                return []

            return PrazoRepository.listar_por_professor(
                db, id_professor
            )

        raise PermissionError(
            "Perfil sem permissão para consultar prazos."
        )

    @staticmethod
    def buscar_por_id(
        db: Session,
        id_prazo: int,
        usuario: Usuario
    ):
        prazo = PrazoService._buscar_prazo_permitido(
            db, id_prazo, usuario
        )

        if not prazo:
            raise LookupError("Prazo não encontrado.")

        return prazo

    @staticmethod
    def listar_por_caso(
        db: Session,
        id_caso: int,
        usuario: Usuario
    ):
        caso = db.execute(
            text("""
                SELECT id_caso
                FROM casos_juridicos
                WHERE id_caso = :id_caso
            """),
            {"id_caso": id_caso}
        ).first()

        if not caso:
            raise LookupError("Caso jurídico não encontrado.")

        prazos = PrazoService.listar(db, usuario)

        return [
            prazo for prazo in prazos
            if prazo.id_caso == id_caso
        ]

    @staticmethod
    def listar_por_responsavel(
        db: Session,
        id_responsavel: int,
        usuario: Usuario
    ):
        if usuario.perfil == "Gestão":
            return PrazoRepository.listar_por_responsavel(
                db, id_responsavel
            )

        if usuario.perfil == "Aluno":
            if id_responsavel != usuario.id_usuario:
                raise PermissionError(
                    "Você só pode consultar seus próprios prazos."
                )

        elif usuario.perfil != "Professor":
            raise PermissionError(
                "Perfil sem permissão para consultar prazos."
            )

        prazos = PrazoService.listar(db, usuario)

        return [
            prazo for prazo in prazos
            if prazo.id_responsavel == id_responsavel
        ]

    @staticmethod
    def _validar_relacionamentos(
        db: Session,
        id_caso: int,
        id_atividade: int | None,
        id_responsavel: int
    ):
        caso_existe = db.execute(
            text("""
                SELECT id_caso
                FROM casos_juridicos
                WHERE id_caso = :id_caso
            """),
            {"id_caso": id_caso}
        ).first()

        if not caso_existe:
            raise ValueError(
                "O caso jurídico informado não existe."
            )

        usuario_existe = db.execute(
            text("""
                SELECT id_usuario
                FROM usuarios
                WHERE id_usuario = :id_responsavel
                  AND situacao_conta = 'Ativo'
            """),
            {"id_responsavel": id_responsavel}
        ).first()

        if not usuario_existe:
            raise ValueError(
                "O usuário responsável não existe ou está inativo."
            )

        if id_atividade is not None:
            atividade_existe = db.execute(
                text("""
                    SELECT id_atividade
                    FROM atividades
                    WHERE id_atividade = :id_atividade
                      AND id_caso = :id_caso
                """),
                {
                    "id_atividade": id_atividade,
                    "id_caso": id_caso
                }
            ).first()

            if not atividade_existe:
                raise ValueError(
                    "A atividade informada não existe ou "
                    "não pertence ao caso selecionado."
                )

    @staticmethod
    def criar(db: Session, dados, usuario: Usuario):
        if usuario.perfil != "Gestão":
            raise PermissionError(
                "Somente Gestão pode cadastrar prazos."
            )

        PrazoService._validar_relacionamentos(
            db,
            dados.id_caso,
            dados.id_atividade,
            dados.id_responsavel
        )

        dados_prazo = dados.model_dump()

        if dados.situacao == "Concluído":
            dados_prazo["data_conclusao"] = datetime.now()

        try:
            return PrazoRepository.criar(db, dados_prazo)

        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível cadastrar o prazo. "
                "Verifique os dados informados."
            )

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def atualizar(
        db: Session,
        id_prazo: int,
        dados,
        usuario: Usuario
    ):
        if usuario.perfil != "Gestão":
            raise PermissionError(
                "Somente Gestão pode atualizar prazos."
            )

        prazo = PrazoService.buscar_por_id(
            db, id_prazo, usuario
        )

        dados_atualizacao = dados.model_dump(
            exclude_unset=True
        )

        id_caso = dados_atualizacao.get(
            "id_caso", prazo.id_caso
        )

        id_atividade = dados_atualizacao.get(
            "id_atividade", prazo.id_atividade
        )

        id_responsavel = dados_atualizacao.get(
            "id_responsavel", prazo.id_responsavel
        )

        PrazoService._validar_relacionamentos(
            db,
            id_caso,
            id_atividade,
            id_responsavel
        )

        nova_situacao = dados_atualizacao.get(
            "situacao", prazo.situacao
        )

        if nova_situacao == "Concluído":
            if prazo.situacao != "Concluído":
                dados_atualizacao["data_conclusao"] = datetime.now()

        elif "situacao" in dados_atualizacao:
            dados_atualizacao["data_conclusao"] = None

        try:
            return PrazoRepository.atualizar(
                db, prazo, dados_atualizacao
            )

        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível atualizar o prazo."
            )

        except Exception:
            db.rollback()
            raise
