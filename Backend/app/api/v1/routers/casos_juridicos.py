
"""
Rotas de gerenciamento dos casos jurídicos do S.G.P.J.

Responsabilidades:
    - Listar e consultar casos jurídicos.
    - Filtrar casos por assistido.
    - Cadastrar novos casos.
    - Controlar a atualização e validação dos casos.
    - Gerenciar o encerramento e a reabertura.
    - Registrar alterações no histórico dos casos.
"""

# Data utilizada no preenchimento automático do encerramento dos casos
from datetime import date

# Componentes do FastAPI para criação de rotas, dependências e respostas HTTP
from fastapi import APIRouter, Depends, HTTPException, status

# Sessão de conexão com o banco de dados
from sqlalchemy.orm import Session

# Dependências de conexão e autenticação
from app.api.deps import get_db, get_current_user

# Modelo do usuário autenticado
from app.models.usuario import Usuario

# Schemas para validação dos dados de entrada e saída
from app.schemas.caso_juridico import (
    CasoJuridicoCreate,
    CasoJuridicoUpdate,
    CasoJuridicoResponse
)

# Serviço responsável pelas regras de negócio dos casos jurídicos
from app.services.caso_juridico import CasoJuridicoService

# Repositórios utilizados nas consultas e atualizações do caso
from app.repositories.caso_juridico import CasoJuridicoRepository
from app.repositories.professor import ProfessorRepository

# Modelo responsável pelo registro do histórico dos casos
from app.models.historico_caso import HistoricoCaso


# ============================================================
# 1. CONFIGURAÇÃO DO ROTEADOR
# Define o prefixo e a identificação das rotas de casos jurídicos.
# ============================================================

router = APIRouter(
    prefix="/casos-juridicos",
    tags=["Casos Jurídicos"]
)


# ============================================================
# 2. LISTAGEM DE CASOS JURÍDICOS
# Retorna os casos conforme o perfil e as permissões do usuário.
# ============================================================

@router.get(
    "/",
    response_model=list[CasoJuridicoResponse]
)
def listar_casos(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user)
):
    try:
        # Gestão pode consultar todos os casos
        if usuario_atual.perfil == "Gestão":
            return CasoJuridicoService.listar(db)

        # Aluno consulta os casos sob sua responsabilidade
        if usuario_atual.perfil == "Aluno":
            return CasoJuridicoService.listar_por_aluno(
                db,
                usuario_atual.id_usuario
            )

        # Professor consulta os casos sob sua orientação
        if usuario_atual.perfil == "Professor":
            return CasoJuridicoService.listar_por_professor(
                db,
                usuario_atual.id_usuario
            )

        # Bloqueia perfis sem autorização para listar casos
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão para listar casos jurídicos."
        )

    # Trata situações em que os registros não são encontrados
    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )


# ============================================================
# 3. LISTAGEM DE CASOS POR ASSISTIDO
# Retorna somente os casos vinculados ao assistido informado
# e que estejam disponíveis para o usuário autenticado.
# ============================================================

@router.get(
    "/assistido/{id_assistido}",
    response_model=list[CasoJuridicoResponse]
)
def listar_casos_por_assistido(
    id_assistido: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user)
):
    try:
        # Gestão pode consultar todos os casos do assistido
        if usuario_atual.perfil == "Gestão":
            return CasoJuridicoService.listar_por_assistido(
                db, id_assistido
            )

        # Obtém os casos vinculados ao aluno autenticado
        if usuario_atual.perfil == "Aluno":
            casos = CasoJuridicoService.listar_por_aluno(
                db, usuario_atual.id_usuario
            )

        # Obtém os casos supervisionados pelo professor autenticado
        elif usuario_atual.perfil == "Professor":
            casos = CasoJuridicoService.listar_por_professor(
                db, usuario_atual.id_usuario
            )

        else:
            # Bloqueia perfis sem autorização para consultar os casos
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não possui permissão para consultar esses casos."
            )

        # Filtra os casos acessíveis pelo identificador do assistido
        return [
            caso for caso in casos
            if caso.id_assistido == id_assistido
        ]

    # Trata situações em que os registros não são encontrados
    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )


# ============================================================
# 4. CONSULTA DE CASO JURÍDICO
# Busca um caso específico, verificando se o usuário possui
# vínculo autorizado com ele.
# ============================================================

@router.get(
    "/{id_caso}",
    response_model=CasoJuridicoResponse
)
def buscar_caso(
    id_caso: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user)
):
    try:
        # Gestão pode consultar qualquer caso
        if usuario_atual.perfil == "Gestão":
            return CasoJuridicoService.buscar_por_id(
                db, id_caso
            )

        # Obtém os casos vinculados ao aluno autenticado
        if usuario_atual.perfil == "Aluno":
            casos = CasoJuridicoService.listar_por_aluno(
                db, usuario_atual.id_usuario
            )

        # Obtém os casos supervisionados pelo professor autenticado
        elif usuario_atual.perfil == "Professor":
            casos = CasoJuridicoService.listar_por_professor(
                db, usuario_atual.id_usuario
            )

        else:
            # Bloqueia perfis sem autorização para consultar casos
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não possui permissão para consultar este caso."
            )

        # Procura o caso solicitado entre os registros acessíveis
        for caso in casos:
            if caso.id_caso == id_caso:
                return caso

        # Impede o acesso a casos inexistentes ou sem vínculo autorizado
        raise LookupError(
            "Caso jurídico não encontrado ou sem vínculo autorizado."
        )

    # Retorna erro quando o caso não existe ou não está acessível
    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )


# ============================================================
# 5. CADASTRO DE CASO JURÍDICO
# Permite que Alunos e Gestão cadastrem novos casos.
# As regras de criação são aplicadas pelo serviço.
# ============================================================

@router.post(
    "/",
    response_model=CasoJuridicoResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_caso(
    dados: CasoJuridicoCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user)
):
    try:
        # Somente Aluno e Gestão podem cadastrar casos
        if usuario_atual.perfil not in ["Aluno", "Gestão"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não possui permissão para cadastrar casos jurídicos."
            )

        # Encaminha os dados e o usuário autenticado ao serviço
        return CasoJuridicoService.criar(
            db, dados, usuario_atual
        )

    # Trata referências a registros inexistentes
    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )

    # Trata tentativas de operação sem permissão
    except PermissionError as erro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(erro)
        )

    # Trata dados inválidos ou inconsistências no cadastro
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro)
        )


# ============================================================
# 6. ATUALIZAÇÃO DE CASO JURÍDICO
# Controla as alterações realizadas por Gestão e Professor.
#
# Professor:
#     - Só pode validar casos sob sua orientação.
#     - Só pode alterar a situação de "Em triagem" para "Aberto".
#
# Gestão:
#     - Pode realizar as atualizações administrativas permitidas.
#
# Também controla o encerramento, a reabertura e o histórico.
# ============================================================

@router.patch(
    "/{id_caso}",
    response_model=CasoJuridicoResponse
)
def atualizar_caso(
    id_caso: int,
    dados: CasoJuridicoUpdate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user)
):
    try:
        # Recupera o caso que será atualizado
        caso = CasoJuridicoService.buscar_por_id(db, id_caso)

        # Obtém somente os campos enviados na requisição
        dados_atualizados = dados.model_dump(
            exclude_unset=True
        )

        # ----------------------------------------------------
        # 6.1. VALIDAÇÃO DAS PERMISSÕES DO PROFESSOR
        # ----------------------------------------------------

        if usuario_atual.perfil == "Professor":

            # Localiza o cadastro de professor vinculado ao usuário
            professor = ProfessorRepository.buscar_por_usuario(
                db, usuario_atual.id_usuario
            )

            # Verifica se o professor existe e está ativo
            if not professor or professor.situacao != "Ativo":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cadastro de professor não encontrado ou inativo."
                )

            # Verifica se o caso está sob orientação desse professor
            if caso.id_professor_orientador != professor.id_professor:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Caso jurídico não encontrado ou sem vínculo de orientação."
                )

            # Professor só pode alterar o campo de situação
            if set(dados_atualizados) != {"situacao"}:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="O professor pode validar somente a situação do caso."
                )

            # Somente casos em triagem podem ser validados
            if caso.situacao != "Em triagem":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Somente casos em triagem podem ser validados."
                )

            # A validação deve alterar a situação para Aberto
            if dados_atualizados["situacao"] != "Aberto":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A validação do professor deve alterar a situação para 'Aberto'."
                )

        # Outros perfis, exceto Gestão, não podem atualizar casos
        elif usuario_atual.perfil != "Gestão":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não possui permissão para atualizar este caso."
            )

        # ----------------------------------------------------
        # 6.2. VALIDAÇÃO DOS DADOS RECEBIDOS
        # ----------------------------------------------------

        # Impede atualizações sem nenhum campo informado
        if not dados_atualizados:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum dado foi enviado para atualização."
            )

        # Impede que a data de encerramento seja informada manualmente
        if "data_encerramento" in dados_atualizados:
            raise ValueError(
                "A data de encerramento é preenchida automaticamente pelo sistema."
            )

        # Impede o envio de situação nula
        if (
            "situacao" in dados_atualizados
            and dados_atualizados["situacao"] is None
        ):
            raise ValueError(
                "A situação do caso não pode ser nula."
            )

        # Verifica se o código interno já pertence a outro caso
        if "codigo_interno" in dados_atualizados:
            codigo = dados_atualizados["codigo_interno"]

            caso_existente = CasoJuridicoRepository.buscar_por_codigo(
                db, codigo
            )

            if caso_existente and caso_existente.id_caso != id_caso:
                raise ValueError(
                    "Já existe outro caso com esse código interno."
                )

        # Verifica se o assistido informado existe
        if "id_assistido" in dados_atualizados:
            from app.repositories.assistido import AssistidoRepository

            assistido = AssistidoRepository.buscar_por_id(
                db, dados_atualizados["id_assistido"]
            )

            if not assistido:
                raise LookupError("Assistido não encontrado.")

        # Verifica se o aluno responsável informado existe
        if "id_aluno_responsavel" in dados_atualizados:
            id_aluno = dados_atualizados["id_aluno_responsavel"]

            if id_aluno is not None:
                from sqlalchemy import text

                aluno = db.execute(
                    text("""
                        SELECT id_aluno
                        FROM alunos
                        WHERE id_aluno = :id_aluno
                    """),
                    {"id_aluno": id_aluno}
                ).first()

                if not aluno:
                    raise LookupError("Aluno responsável não encontrado.")

        # Verifica se o professor orientador informado existe
        if "id_professor_orientador" in dados_atualizados:
            id_professor = dados_atualizados["id_professor_orientador"]

            if id_professor is not None:
                from sqlalchemy import text

                professor = db.execute(
                    text("""
                        SELECT id_professor
                        FROM professores
                        WHERE id_professor = :id_professor
                    """),
                    {"id_professor": id_professor}
                ).first()

                if not professor:
                    raise LookupError("Professor orientador não encontrado.")

        # ----------------------------------------------------
        # 6.3. CONTROLE DO ENCERRAMENTO E DA REABERTURA
        # ----------------------------------------------------

        # Guarda a situação atual antes de realizar a atualização
        situacao_anterior = caso.situacao

        # Controla automaticamente a data de encerramento
        if "situacao" in dados_atualizados:
            nova_situacao = dados_atualizados["situacao"]

            # Ao encerrar o caso, registra a data atual
            if (
                nova_situacao == "Encerrado"
                and situacao_anterior != "Encerrado"
            ):
                dados_atualizados["data_encerramento"] = date.today()

            # Ao reabrir o caso, remove a data de encerramento
            elif (
                situacao_anterior == "Encerrado"
                and nova_situacao != "Encerrado"
            ):
                dados_atualizados["data_encerramento"] = None

        # ----------------------------------------------------
        # 6.4. REGISTRO DOS DADOS ANTERIORES
        # ----------------------------------------------------

        # Guarda os valores anteriores dos campos que serão alterados
        dados_anteriores = {
            campo: getattr(caso, campo)
            for campo in dados_atualizados
        }

        # ----------------------------------------------------
        # 6.5. EXECUÇÃO DA ATUALIZAÇÃO
        # ----------------------------------------------------

        # Encaminha os dados validados ao repositório
        CasoJuridicoRepository.atualizar(
            db, caso, dados_atualizados
        )

        # ----------------------------------------------------
        # 6.6. IDENTIFICAÇÃO DAS ALTERAÇÕES
        # ----------------------------------------------------

        # Compara os valores anteriores com os valores atualizados
        alteracoes = []

        for campo, valor_anterior in dados_anteriores.items():
            valor_novo = getattr(caso, campo)

            if valor_anterior != valor_novo:
                alteracoes.append(
                    f"{campo}: '{valor_anterior}' para '{valor_novo}'"
                )

        # ----------------------------------------------------
        # 6.7. REGISTRO NO HISTÓRICO DO CASO
        # ----------------------------------------------------

        # Registra somente quando alguma alteração foi realizada
        if alteracoes:
            mudou_situacao = (
                "situacao" in dados_anteriores
                and dados_anteriores["situacao"] != caso.situacao
            )

            # Identifica a validação realizada pelo professor
            if (
                mudou_situacao
                and situacao_anterior == "Em triagem"
                and caso.situacao == "Aberto"
            ):
                tipo_ocorrencia = "Validação de caso"

            # Identifica outras alterações na situação do caso
            elif mudou_situacao:
                tipo_ocorrencia = "Alteração de situação do caso"

            # Identifica alterações nos demais dados do caso
            else:
                tipo_ocorrencia = "Atualização de dados do caso"

            # Descreve os campos que foram efetivamente modificados
            descricao = (
                f"O caso jurídico foi atualizado. "
                f"Alterações: {'; '.join(alteracoes)}"
            )

            # Adiciona o registro ao histórico
            db.add(
                HistoricoCaso(
                    id_caso=caso.id_caso,
                    id_usuario_responsavel=usuario_atual.id_usuario,
                    tipo_ocorrencia=tipo_ocorrencia,
                    descricao=descricao,
                    referencia_registro_afetado=f"caso:{caso.id_caso}"
                )
            )

        # ----------------------------------------------------
        # 6.8. CONFIRMAÇÃO DA TRANSAÇÃO
        # ----------------------------------------------------

        # Salva as alterações e atualiza os dados do objeto
        db.commit()
        db.refresh(caso)

        return caso

    # Caso o registro relacionado não seja encontrado, desfaz a transação
    except LookupError as erro:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )

    # Caso os dados sejam inválidos, desfaz a transação
    except ValueError as erro:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro)
        )

    # Preserva as respostas HTTP e desfaz alterações pendentes
    except HTTPException:
        db.rollback()
        raise

    # Em qualquer outro erro, desfaz a transação e propaga a exceção
    except Exception:
        db.rollback()
        raise
