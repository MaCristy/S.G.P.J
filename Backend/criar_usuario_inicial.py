
import getpass

from app.db.session import SessionLocal
from app.models.usuario import Usuario
from app.core.security import gerar_hash_senha


def criar_usuario_inicial():
    db = SessionLocal()

    try:
        usuario_existente = db.query(Usuario).first()

        if usuario_existente:
            print("\nJá existe pelo menos um usuário cadastrado.")
            print("Nenhum novo usuário foi criado.")
            return

        print("\n=== CADASTRO DO PRIMEIRO USUÁRIO DO S.G.P.J. ===")

        nome = input("Nome completo: ").strip()
        email = input("E-mail institucional: ").strip().lower()

        senha = getpass.getpass("Senha: ")
        confirmar_senha = getpass.getpass("Confirme a senha: ")

        if not nome or not email or not senha:
            print("\nTodos os campos são obrigatórios.")
            return

        if senha != confirmar_senha:
            print("\nAs senhas não correspondem.")
            return

        if len(senha) < 8:
            print("\nA senha deve possuir pelo menos 8 caracteres.")
            return

        novo_usuario = Usuario(
            nome=nome,
            email_institucional=email,
            senha_armazenada=gerar_hash_senha(senha),
            perfil="Gestão",
            situacao_conta="Ativo"
        )

        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)

        print("\nUsuário de Gestão cadastrado com sucesso!")
        print(f"Identificador: {novo_usuario.id_usuario}")
        print(f"Nome: {novo_usuario.nome}")
        print(f"E-mail: {novo_usuario.email_institucional}")
        print(f"Perfil: {novo_usuario.perfil}")

    except Exception as erro:
        db.rollback()
        print(f"\nErro ao cadastrar o usuário: {erro}")

    finally:
        db.close()


if __name__ == "__main__":
    criar_usuario_inicial()
