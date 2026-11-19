
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.usuario import Usuario
from app.schemas.caso_juridico import (
    CasoJuridicoCreate,
    CasoJuridicoUpdate,
    CasoJuridicoResponse
)
from app.services.caso_juridico import CasoJuridicoService
from app.repositories.caso_juridico import CasoJuridicoRepository
from app.repositories.professor import ProfessorRepository
from app.models.historico_caso import HistoricoCaso


router = APIRouter(
    prefix="/casos-juridicos",
    tags=["Casos Jurídicos"]
)


@router.get(
    "/",
    response_model=list[CasoJuridicoResponse]
)
def listar_casos(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user)
):
    try:
        if usuario_atual.perfil == "Gestão":
            return CasoJuridicoService.listar(db)

        if usuario_atual.perfil == "Aluno":
            return CasoJuridicoService.listar_por_aluno(
                db,
                usuario_atual.id_usuario
            )

        if usuario_atual.perfil == "Professor":
            return CasoJuridicoService.listar_por_professor(
                db,
                usuario_atual.id_usuario
            )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão para listar casos jurídicos."
        )

    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )


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
        if usuario_atual.perfil == "Gestão":
            return CasoJuridicoService.listar_por_assistido(
                db, id_assistido
            )

        if usuario_atual.perfil == "Aluno":
            casos = CasoJuridicoService.listar_por_aluno(
                db, usuario_atual.id_usuario
            )

        elif usuario_atual.perfil == "Professor":
            casos = CasoJuridicoService.listar_por_professor(
                db, usuario_atual.id_usuario
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não possui permissão para consultar esses casos."
            )

        return [
            caso for caso in casos
            if caso.id_assistido == id_assistido
        ]

    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )


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
        if usuario_atual.perfil == "Gestão":
            return CasoJuridicoService.buscar_por_id(
                db, id_caso
            )

        if usuario_atual.perfil == "Aluno":
            casos = CasoJuridicoService.listar_por_aluno(
                db, usuario_atual.id_usuario
            )

        elif usuario_atual.perfil == "Professor":
            casos = CasoJuridicoService.listar_por_professor(
                db, usuario_atual.id_usuario
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não possui permissão para consultar este caso."
            )

        for caso in casos:
            if caso.id_caso == id_caso:
                return caso

        raise LookupError(
            "Caso jurídico não encontrado ou sem vínculo autorizado."
        )

    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )


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
        if usuario_atual.perfil not in ["Aluno", "Gestão"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não possui permissão para cadastrar casos jurídicos."
            )

        return CasoJuridicoService.criar(
            db, dados, usuario_atual
        )

    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )

    except PermissionError as erro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(erro)
        )

    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro)
        )


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
        caso = CasoJuridicoService.buscar_por_id(db, id_caso)

        dados_atualizados = dados.model_dump(
            exclude_unset=True
        )

        if usuario_atual.perfil == "Professor":
            professor = ProfessorRepository.buscar_por_usuario(
                db, usuario_atual.id_usuario
            )

            if not professor or professor.situacao != "Ativo":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cadastro de professor não encontrado ou inativo."
                )

            if caso.id_professor_orientador != professor.id_professor:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Caso jurídico não encontrado ou sem vínculo de orientação."
                )

            if set(dados_atualizados) != {"situacao"}:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="O professor pode validar somente a situação do caso."
                )

            if caso.situacao != "Em triagem":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Somente casos em triagem podem ser validados."
                )

            if dados_atualizados["situacao"] != "Aberto":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A validação do professor deve alterar a situação para 'Aberto'."
                )

        elif usuario_atual.perfil != "Gestão":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não possui permissão para atualizar este caso."
            )

        if not dados_atualizados:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum dado foi enviado para atualização."
            )

        # Impede que a data de encerramento seja informada manualmente.
        if "data_encerramento" in dados_atualizados:
            raise ValueError(
                "A data de encerramento é preenchida automaticamente pelo sistema."
            )

        # Impede o envio de situação nula.
        if (
            "situacao" in dados_atualizados
            and dados_atualizados["situacao"] is None
        ):
            raise ValueError(
                "A situação do caso não pode ser nula."
            )

        # Verifica se o código interno já pertence a outro caso.
        if "codigo_interno" in dados_atualizados:
            codigo = dados_atualizados["codigo_interno"]

            caso_existente = CasoJuridicoRepository.buscar_por_codigo(
                db, codigo
            )

            if caso_existente and caso_existente.id_caso != id_caso:
                raise ValueError(
                    "Já existe outro caso com esse código interno."
                )

        # Verifica se o assistido existe.
        if "id_assistido" in dados_atualizados:
            from app.repositories.assistido import AssistidoRepository

            assistido = AssistidoRepository.buscar_por_id(
                db, dados_atualizados["id_assistido"]
            )

            if not assistido:
                raise LookupError("Assistido não encontrado.")

        # Verifica se o aluno responsável existe.
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

        # Verifica se o professor orientador existe.
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

        situacao_anterior = caso.situacao

        # Controla automaticamente a data de encerramento.
        if "situacao" in dados_atualizados:
            nova_situacao = dados_atualizados["situacao"]

            if (
                nova_situacao == "Encerrado"
                and situacao_anterior != "Encerrado"
            ):
                dados_atualizados["data_encerramento"] = date.today()

            elif (
                situacao_anterior == "Encerrado"
                and nova_situacao != "Encerrado"
            ):
                dados_atualizados["data_encerramento"] = None

        # Guarda os valores anteriores dos campos que serão alterados.
        dados_anteriores = {
            campo: getattr(caso, campo)
            for campo in dados_atualizados
        }

        # Realiza a atualização do caso.
        CasoJuridicoRepository.atualizar(
            db, caso, dados_atualizados
        )

        # Identifica somente as alterações efetivamente realizadas.
        alteracoes = []

        for campo, valor_anterior in dados_anteriores.items():
            valor_novo = getattr(caso, campo)

            if valor_anterior != valor_novo:
                alteracoes.append(
                    f"{campo}: '{valor_anterior}' para '{valor_novo}'"
                )

        # Registra as alterações no histórico do caso.
        if alteracoes:
            mudou_situacao = (
                "situacao" in dados_anteriores
                and dados_anteriores["situacao"] != caso.situacao
            )

            if (
                mudou_situacao
                and situacao_anterior == "Em triagem"
                and caso.situacao == "Aberto"
            ):
                tipo_ocorrencia = "Validação de caso"

            elif mudou_situacao:
                tipo_ocorrencia = "Alteração de situação do caso"

            else:
                tipo_ocorrencia = "Atualização de dados do caso"

            descricao = (
                f"O caso jurídico foi atualizado. "
                f"Alterações: {'; '.join(alteracoes)}"
            )

            db.add(
                HistoricoCaso(
                    id_caso=caso.id_caso,
                    id_usuario_responsavel=usuario_atual.id_usuario,
                    tipo_ocorrencia=tipo_ocorrencia,
                    descricao=descricao,
                    referencia_registro_afetado=f"caso:{caso.id_caso}"
                )
            )

        db.commit()
        db.refresh(caso)

        return caso

    except LookupError as erro:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro)
        )

    except ValueError as erro:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro)
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise
