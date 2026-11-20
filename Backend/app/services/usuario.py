
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.repositories.usuario import UsuarioRepository
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.core.security import gerar_hash_senha


class UsuarioService:

    # Lista todos os usuários cadastrados no sistema.
    @staticmethod
    def listar(db: Session):
        return UsuarioRepository.listar(db)

    # Busca um usuário pelo identificador e verifica sua existência.
    @staticmethod
    def buscar_por_id(db: Session, id_usuario: int):
        usuario = UsuarioRepository.buscar_por_id(db, id_usuario)

        if not usuario:
            raise LookupError("Usuário não encontrado.")

        return usuario

    # Cadastra um usuário, verificando o e-mail e protegendo sua senha.
    @staticmethod
    def criar(db: Session, dados: UsuarioCreate):
        # Impede o cadastro de usuários com e-mail já existente.
        usuario_existente = UsuarioRepository.buscar_por_email(
            db, dados.email_institucional
        )

        if usuario_existente:
            raise ValueError("Já existe um usuário cadastrado com esse e-mail.")

        # Gera o hash da senha antes de armazená-la no banco de dados.
        senha_hash = gerar_hash_senha(dados.senha)

        try:
            usuario = UsuarioRepository.criar(
                db, dados, senha_hash
            )

            db.commit()
            db.refresh(usuario)

            return usuario

        # Trata conflitos de integridade durante o cadastro.
        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível cadastrar o usuário. "
                "Verifique se o e-mail já está cadastrado."
            )

        # Desfaz a transação caso ocorra qualquer outro erro.
        except Exception:
            db.rollback()
            raise

    # Atualiza os dados de um usuário, tratando e-mail e senha quando necessário.
    @staticmethod
    def atualizar(
        db: Session,
        id_usuario: int,
        dados: UsuarioUpdate
    ):
        usuario = UsuarioService.buscar_por_id(db, id_usuario)

        # Considera somente os campos enviados na solicitação de atualização.
        dados_atualizacao = dados.model_dump(
            exclude_unset=True
        )

        # Impede uma atualização sem campos informados.
        if not dados_atualizacao:
            raise ValueError(
                "Informe pelo menos um campo para atualizar."
            )

        # Verifica se o novo e-mail já pertence a outro usuário.
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

        # Gera um novo hash quando a senha é alterada.
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

        # Trata conflitos de integridade durante a atualização.
        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Não foi possível atualizar o usuário. "
                "Verifique os dados informados."
            )

        # Desfaz a transação caso ocorra qualquer outro erro.
        except Exception:
            db.rollback()
            raise
