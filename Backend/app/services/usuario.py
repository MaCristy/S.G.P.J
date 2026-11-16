
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.repositories.usuario import UsuarioRepository
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.core.security import gerar_hash_senha


class UsuarioService:

    @staticmethod
    def listar(db: Session):
        return UsuarioRepository.listar(db)

    @staticmethod
    def buscar_por_id(db: Session, id_usuario: int):
        usuario = UsuarioRepository.buscar_por_id(db, id_usuario)

        if not usuario:
            raise LookupError("Usuário não encontrado.")

        return usuario

    @staticmethod
    def criar(db: Session, dados: UsuarioCreate):
        usuario_existente = UsuarioRepository.buscar_por_email(
            db, dados.email_institucional
        )

        if usuario_existente:
            raise ValueError("Já existe um usuário cadastrado com esse e-mail.")

        senha_hash = gerar_hash_senha(dados.senha)

        try:
            usuario = UsuarioRepository.criar(
                db, dados, senha_hash
            )

            db.commit()
            db.refresh(usuario)

            return usuario

        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível cadastrar o usuário. "
                "Verifique se o e-mail já está cadastrado."
            )

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def atualizar(
        db: Session,
        id_usuario: int,
        dados: UsuarioUpdate
    ):
        usuario = UsuarioService.buscar_por_id(db, id_usuario)

        dados_atualizacao = dados.model_dump(
            exclude_unset=True
        )

        if not dados_atualizacao:
            raise ValueError(
                "Informe pelo menos um campo para atualizar."
            )

        if "email_institucional" in dados_atualizacao:
            usuario_existente = UsuarioRepository.buscar_por_email(
                db,
                dados_atualizacao["email_institucional"]
            )

            if (
                usuario_existente
                and usuario_existente.id_usuario != id_usuario
            ):
                raise ValueError(
                    "Já existe outro usuário cadastrado com esse e-mail."
                )

        if "senha" in dados_atualizacao:
            dados_atualizacao["senha_armazenada"] = gerar_hash_senha(
                dados_atualizacao.pop("senha")
            )

        try:
            usuario = UsuarioRepository.atualizar(
                db,
                usuario,
                dados_atualizacao
            )

            db.commit()
            db.refresh(usuario)

            return usuario

        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível atualizar o usuário. "
                "Verifique os dados informados."
            )

        except Exception:
            db.rollback()
            raise
