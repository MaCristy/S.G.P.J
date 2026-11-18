
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from app.repositories.atividade import AtividadeRepository
from app.schemas.atividade import AtividadeCreate, AtividadeUpdate
from app.models.usuario import Usuario


class AtividadeService:

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
    def _buscar_atividade_permitida(
        db: Session,
        id_atividade: int,
        usuario: Usuario
    ):
        if usuario.perfil == "Gestão":
            return AtividadeRepository.buscar_por_id(
                db, id_atividade
            )

        if usuario.perfil == "Aluno":
            id_aluno = AtividadeService._buscar_id_aluno(
                db, usuario.id_usuario
            )

            if not id_aluno:
                return None

            return AtividadeRepository.buscar_por_id_e_aluno(
                db, id_atividade, id_aluno
            )

        if usuario.perfil == "Professor":
            id_professor = AtividadeService._buscar_id_professor(
                db, usuario.id_usuario
            )

            if not id_professor:
                return None

            return AtividadeRepository.buscar_por_id_e_professor(
                db, id_atividade, id_professor
            )

        raise PermissionError("Perfil sem permissão para acessar atividades.")

    @staticmethod
    def listar(db: Session, usuario: Usuario):
        if usuario.perfil == "Gestão":
            return AtividadeRepository.listar(db)

        if usuario.perfil == "Aluno":
            id_aluno = AtividadeService._buscar_id_aluno(
                db, usuario.id_usuario
            )

            if not id_aluno:
                return []

            return AtividadeRepository.listar_por_aluno(
                db, id_aluno
            )

        if usuario.perfil == "Professor":
            id_professor = AtividadeService._buscar_id_professor(
                db, usuario.id_usuario
            )

            if not id_professor:
                return []

            return AtividadeRepository.listar_por_professor(
                db, id_professor
            )

        raise PermissionError("Perfil sem permissão para consultar atividades.")

    @staticmethod
    def buscar_por_id(
        db: Session,
        id_atividade: int,
        usuario: Usuario
    ):
        atividade = AtividadeService._buscar_atividade_permitida(
            db, id_atividade, usuario
        )

        if not atividade:
            raise LookupError("Atividade não encontrada.")

        return atividade

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

        if usuario.perfil == "Gestão":
            return AtividadeRepository.listar_por_caso(
                db, id_caso
            )

        atividades = AtividadeService.listar(db, usuario)

        return [
            atividade
            for atividade in atividades
            if atividade.id_caso == id_caso
        ]

    @staticmethod
    def listar_por_responsavel(
        db: Session,
        id_responsavel: int,
        usuario: Usuario
    ):
        if usuario.perfil == "Gestão":
            return AtividadeRepository.listar_por_responsavel(
                db, id_responsavel
            )

        if usuario.perfil == "Aluno":
            if id_responsavel != usuario.id_usuario:
                raise PermissionError(
                    "Você só pode consultar suas próprias atividades."
                )

        atividades = AtividadeService.listar(db, usuario)

        return [
            atividade
            for atividade in atividades
            if atividade.id_responsavel == id_responsavel
        ]

    @staticmethod
    def criar(
        db: Session,
        dados: AtividadeCreate,
        usuario: Usuario
    ):
        if usuario.perfil not in ("Aluno", "Gestão"):
            raise PermissionError(
                "Somente alunos e Gestão podem cadastrar atividades."
            )

        caso = db.execute(
            text("""
                SELECT id_caso,
                       id_aluno_responsavel,
                       situacao
                FROM casos_juridicos
                WHERE id_caso = :id_caso
            """),
            {"id_caso": dados.id_caso}
        ).first()

        if not caso:
            raise LookupError("Caso jurídico não encontrado.")

        # RN13: impedir cadastro de atividades em casos encerrados.
        if caso.situacao == "Encerrado":
            raise ValueError(
                "Não é permitido cadastrar novas atividades "
                "em casos encerrados."
            )

        if usuario.perfil == "Aluno":
            id_aluno = AtividadeService._buscar_id_aluno(
                db, usuario.id_usuario
            )

            if not id_aluno or caso.id_aluno_responsavel != id_aluno:
                raise PermissionError(
                    "Você só pode cadastrar atividades nos seus próprios casos."
                )

            id_responsavel = usuario.id_usuario

        else:
            id_responsavel = dados.id_responsavel

        responsavel = db.execute(
            text("""
                SELECT id_usuario
                FROM usuarios
                WHERE id_usuario = :id_usuario
                  AND situacao_conta = 'Ativo'
            """),
            {"id_usuario": id_responsavel}
        ).first()

        if not responsavel:
            raise LookupError("Usuário responsável não encontrado ou inativo.")

        dados_atividade = dados.model_copy(
            update={"id_responsavel": id_responsavel}
        )

        if dados.situacao == "Concluída":
            data_conclusao = datetime.now()
        else:
            data_conclusao = None

        try:
            atividade = AtividadeRepository.criar(
                db, dados_atividade
            )

            if data_conclusao:
                atividade.data_conclusao = data_conclusao

            db.commit()
            db.refresh(atividade)

            return atividade

        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível cadastrar a atividade. "
                "Verifique os dados e os vínculos informados."
            )

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def atualizar(
        db: Session,
        id_atividade: int,
        dados: AtividadeUpdate,
        usuario: Usuario
    ):
        atividade = AtividadeService._buscar_atividade_permitida(
            db, id_atividade, usuario
        )

        if not atividade:
            raise LookupError("Atividade não encontrada.")

        dados_atualizacao = dados.model_dump(
            exclude_unset=True,
            exclude_none=True
        )

        if usuario.perfil == "Aluno":
            if "id_responsavel" in dados_atualizacao:
                raise PermissionError(
                    "O aluno não pode alterar o responsável pela atividade."
                )

        if usuario.perfil == "Professor":
            if "id_responsavel" in dados_atualizacao:
                raise PermissionError(
                    "O professor não pode alterar o responsável pela atividade."
                )

        if "id_caso" in dados_atualizacao:
            caso = db.execute(
                text("""
                    SELECT id_caso, id_aluno_responsavel,
                           id_professor_orientador
                    FROM casos_juridicos
                    WHERE id_caso = :id_caso
                """),
                {"id_caso": dados_atualizacao["id_caso"]}
            ).first()

            if not caso:
                raise LookupError("Caso jurídico não encontrado.")

            if usuario.perfil == "Aluno":
                id_aluno = AtividadeService._buscar_id_aluno(
                    db, usuario.id_usuario
                )

                if not id_aluno or caso.id_aluno_responsavel != id_aluno:
                    raise PermissionError(
                        "Você não pode transferir a atividade para outro caso."
                    )

            if usuario.perfil == "Professor":
                id_professor = AtividadeService._buscar_id_professor(
                    db, usuario.id_usuario
                )

                if (
                    not id_professor
                    or caso.id_professor_orientador != id_professor
                ):
                    raise PermissionError(
                        "Você não pode transferir a atividade para um caso "
                        "que não está sob sua orientação."
                    )

        if "id_responsavel" in dados_atualizacao:
            responsavel = db.execute(
                text("""
                    SELECT id_usuario
                    FROM usuarios
                    WHERE id_usuario = :id_usuario
                      AND situacao_conta = 'Ativo'
                """),
                {"id_usuario": dados_atualizacao["id_responsavel"]}
            ).first()

            if not responsavel:
                raise LookupError(
                    "Usuário responsável não encontrado ou inativo."
                )

        if dados_atualizacao.get("situacao") == "Concluída":
            if not atividade.data_conclusao:
                dados_atualizacao["data_conclusao"] = datetime.now()

        try:
            atividade = AtividadeRepository.atualizar(
                db,
                atividade,
                dados_atualizacao
            )

            db.commit()
            db.refresh(atividade)

            return atividade

        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível atualizar a atividade."
            )

        except Exception:
            db.rollback()
            raise
