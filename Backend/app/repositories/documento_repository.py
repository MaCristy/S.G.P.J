
from sqlalchemy.orm import Session

from app.models.documento import Documento
from app.models.caso_juridico import CasoJuridico
from app.models.atendimento import Atendimento


class DocumentoRepository:

    # Lista todos os documentos, começando pelos mais recentes.
    @staticmethod
    def listar(db: Session):
        return (
            db.query(Documento)
            .order_by(Documento.data_inclusao.desc())
            .all()
        )

    # Lista documentos vinculados aos casos ou atendimentos relacionados ao aluno.
    @staticmethod
    def listar_por_aluno(db: Session, id_aluno: int):
        return (
            db.query(Documento)
            .outerjoin(
                CasoJuridico,
                Documento.id_caso == CasoJuridico.id_caso
            )
            .outerjoin(
                Atendimento,
                Documento.id_atendimento == Atendimento.id_atendimento
            )
            .filter(
                (CasoJuridico.id_aluno_responsavel == id_aluno)
                |
                (Atendimento.id_caso.in_(
                    db.query(CasoJuridico.id_caso).filter(
                        CasoJuridico.id_aluno_responsavel == id_aluno
                    )
                ))
            )
            # Evita duplicidade quando o documento corresponde a mais de um vínculo.
            .distinct()
            .order_by(Documento.data_inclusao.desc())
            .all()
        )

    # Lista documentos vinculados aos casos ou atendimentos supervisionados pelo professor.
    @staticmethod
    def listar_por_professor(db: Session, id_professor: int):
        return (
            db.query(Documento)
            .outerjoin(
                CasoJuridico,
                Documento.id_caso == CasoJuridico.id_caso
            )
            .outerjoin(
                Atendimento,
                Documento.id_atendimento == Atendimento.id_atendimento
            )
            .filter(
                (CasoJuridico.id_professor_orientador == id_professor)
                |
                (Atendimento.id_caso.in_(
                    db.query(CasoJuridico.id_caso).filter(
                        CasoJuridico.id_professor_orientador == id_professor
                    )
                ))
            )
            # Evita duplicidade quando o documento corresponde a mais de um vínculo.
            .distinct()
            .order_by(Documento.data_inclusao.desc())
            .all()
        )

    # Busca um documento pelo seu identificador.
    @staticmethod
    def buscar_por_id(db: Session, id_documento: int):
        return (
            db.query(Documento)
            .filter(Documento.id_documento == id_documento)
            .first()
        )

    # Busca um documento ao verificar se está relacionado a um caso acessível ao aluno.
    @staticmethod
    def buscar_por_id_e_aluno(
        db: Session,
        id_documento: int,
        id_aluno: int
    ):
        return (
            db.query(Documento)
            .outerjoin(
                CasoJuridico,
                Documento.id_caso == CasoJuridico.id_caso
            )
            .outerjoin(
                Atendimento,
                Documento.id_atendimento == Atendimento.id_atendimento
            )
            .filter(
                Documento.id_documento == id_documento,
                (
                    CasoJuridico.id_aluno_responsavel == id_aluno
                )
                |
                (
                    Atendimento.id_caso.in_(
                        db.query(CasoJuridico.id_caso).filter(
                            CasoJuridico.id_aluno_responsavel == id_aluno
                        )
                    )
                )
            )
            .first()
        )

    # Busca um documento ao verificar se está relacionado a um caso supervisionado pelo professor.
    @staticmethod
    def buscar_por_id_e_professor(
        db: Session,
        id_documento: int,
        id_professor: int
    ):
        return (
            db.query(Documento)
            .outerjoin(
                CasoJuridico,
                Documento.id_caso == CasoJuridico.id_caso
            )
            .outerjoin(
                Atendimento,
                Documento.id_atendimento == Atendimento.id_atendimento
            )
            .filter(
                Documento.id_documento == id_documento,
                (
                    CasoJuridico.id_professor_orientador == id_professor
                )
                |
                (
                    Atendimento.id_caso.in_(
                        db.query(CasoJuridico.id_caso).filter(
                            CasoJuridico.id_professor_orientador == id_professor
                        )
                    )
                )
            )
            .first()
        )

    # Lista os documentos vinculados a um caso jurídico.
    @staticmethod
    def listar_por_caso(db: Session, id_caso: int):
        return (
            db.query(Documento)
            .filter(Documento.id_caso == id_caso)
            .order_by(Documento.data_inclusao.desc())
            .all()
        )

    # Lista os documentos vinculados a um atendimento.
    @staticmethod
    def listar_por_atendimento(db: Session, id_atendimento: int):
        return (
            db.query(Documento)
            .filter(Documento.id_atendimento == id_atendimento)
            .order_by(Documento.data_inclusao.desc())
            .all()
        )

    # Cadastra um documento e confirma sua persistência no banco de dados.
    @staticmethod
    def criar(db: Session, dados: dict):
        documento = Documento(**dados)

        db.add(documento)
        db.commit()
        db.refresh(documento)

        return documento

    # Atualiza os campos informados e recarrega os dados persistidos.
    @staticmethod
    def atualizar(db: Session, documento: Documento, dados: dict):
        for campo, valor in dados.items():
            setattr(documento, campo, valor)

        db.commit()
        db.refresh(documento)

        return documento
