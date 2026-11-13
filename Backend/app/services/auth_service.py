
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.core.security import verificar_senha, criar_token_acesso


def autenticar_usuario(
    db: Session,
    email_institucional: str,
    senha: str
):
    usuario = (
        db.query(Usuario)
        .filter(Usuario.email_institucional == email_institucional)
        .first()
    )

    if not usuario:
        return None

    if usuario.situacao_conta != "Ativo":
        return None

    if not verificar_senha(senha, usuario.senha_armazenada):
        return None

    token = criar_token_acesso({
        "sub": str(usuario.id_usuario),
        "perfil": usuario.perfil
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }
