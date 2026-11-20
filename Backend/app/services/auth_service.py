
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.core.security import verificar_senha, criar_token_acesso


# Realiza a autenticação do usuário no sistema.
def autenticar_usuario(
    db: Session,
    email_institucional: str,
    senha: str
):
    # Busca o usuário pelo e-mail institucional informado.
    usuario = (
        db.query(Usuario)
        .filter(Usuario.email_institucional == email_institucional)
        .first()
    )

    # Impede a autenticação caso o usuário não exista.
    if not usuario:
        return None

    # Permite o acesso somente a contas ativas.
    if usuario.situacao_conta != "Ativo":
        return None

    # Verifica se a senha informada corresponde à senha armazenada.
    if not verificar_senha(senha, usuario.senha_armazenada):
        return None

    # Gera o token de acesso com o identificador e o perfil do usuário.
    token = criar_token_acesso({
        "sub": str(usuario.id_usuario),
        "perfil": usuario.perfil
    })

    # Retorna o token no formato esperado pela autenticação Bearer.
    return {
        "access_token": token,
        "token_type": "bearer"
    }
