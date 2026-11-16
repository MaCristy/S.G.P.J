from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, check_role
from app.models.usuario import Usuario
from app.schemas.caso_juridico import (
    CasoJuridicoCreate,
    CasoJuridicoUpdate,
    CasoJuridicoResponse
)
from app.services.caso_juridico import CasoJuridicoService
from app.repositories.caso_juridico import CasoJuridicoRepository


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
    usuario_atual: Usuario = Depends(check_role("Gestão"))
):
    try:
        return CasoJuridicoService.criar(db, dados)

    except LookupError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
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
    usuario_atual: Usuario = Depends(check_role("Gestão"))
):
    try:
        caso = CasoJuridicoService.buscar_por_id(db, id_caso)

        dados_atualizados = dados.model_dump(exclude_unset=True)

        if not dados_atualizados:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum dado foi enviado para atualização."
            )

        if "codigo_interno" in dados_atualizados:
            codigo = dados_atualizados["codigo_interno"]

            caso_existente = CasoJuridicoRepository.buscar_por_codigo(
                db, codigo
            )

            if caso_existente and caso_existente.id_caso != id_caso:
                raise ValueError(
                    "Já existe outro caso com esse código interno."
                )

        if "id_assistido" in dados_atualizados:
            from app.repositories.assistido import AssistidoRepository

            assistido = AssistidoRepository.buscar_por_id(
                db, dados_atualizados["id_assistido"]
            )

            if not assistido:
                raise LookupError("Assistido não encontrado.")

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

        CasoJuridicoRepository.atualizar(
            db, caso, dados_atualizados
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
