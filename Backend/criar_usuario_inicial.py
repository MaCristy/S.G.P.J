
import getpass

from pydantic import EmailStr, TypeAdapter, ValidationError

from app.db.session import SessionLocal
from app.models.usuario import Usuario
from app.core.security import gerar_hash_senha


# Prepara o validador utilizado para verificar o formato do e-mail.
validador_email = TypeAdapter(EmailStr)


# Realiza o cadastro do primeiro usuário com perfil de Gestão.
def criar_usuario_inicial():
    # Abre uma sessão de conexão com o banco de dados.
    db = SessionLocal()

    try:
        # Verifica se já existe algum usuário cadastrado.
        usuario_existente = db.query(Usuario).first()

        if usuario_existente:
            print("\nJá existe pelo menos um usuário cadastrado.")
            print("Nenhum novo usuário foi criado.")
            return

        print("\n=== CADASTRO DO PRIMEIRO USUÁRIO DO S.G.P.J. ===")

        # Solicita os dados necessários para o cadastro inicial.
        nome = input("Nome completo: ").strip()
        email = input("E-mail institucional: ").strip().lower()

        # Solicita a senha sem exibi-la no terminal.
        senha = getpass.getpass("Senha: ")
        confirmar_senha = getpass.getpass("Confirme a senha: ")

        # Verifica o preenchimento dos campos obrigatórios.
        if not nome or not email or not senha:
            print("\nTodos os campos são obrigatórios.")
            return

        # Verifica o limite de caracteres permitido para o e-mail.
        if len(email) > 150:
            print("\nO e-mail deve possuir no máximo 150 caracteres.")
            return

        # Valida o formato do endereço de e-mail informado.
        try:
            validador_email.validate_python(email)
        except ValidationError:
            print("\nInforme um endereço de e-mail válido.")
            return

        # Confere se as duas senhas informadas são iguais.
        if senha != confirmar_senha:
            print("\nAs senhas não correspondem.")
            return

        # Aplica os limites de tamanho definidos pelo sistema.
        if len(senha) < 8:
            print("\nA senha deve possuir pelo menos 8 caracteres.")
            return

        if len(senha) > 128:
            print("\nA senha deve possuir no máximo 128 caracteres.")
            return

        # Prepara o usuário inicial com perfil de Gestão e conta ativa.
        novo_usuario = Usuario(
            nome=nome,
            email_institucional=email,
            senha_armazenada=gerar_hash_senha(senha),
            perfil="Gestão",
            situacao_conta="Ativo"
        )

        # Persiste o novo usuário no banco de dados.
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)

        # Apresenta a confirmação do cadastro realizado.
        print("\nUsuário de Gestão cadastrado com sucesso!")
        print(f"Identificador: {novo_usuario.id_usuario}")
        print(f"Nome: {novo_usuario.nome}")
        print(f"E-mail: {novo_usuario.email_institucional}")
        print(f"Perfil: {novo_usuario.perfil}")

    except Exception as erro:
        # Desfaz a transação caso ocorra algum erro no cadastro.
        db.rollback()
        print(f"\nErro ao cadastrar o usuário: {erro}")

    finally:
        # Garante o encerramento da sessão com o banco de dados.
        db.close()


# Executa o cadastro somente quando o arquivo é iniciado diretamente.
if __name__ == "__main__":
    criar_usuario_inicial()
