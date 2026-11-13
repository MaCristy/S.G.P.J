"""
Pacote de Services do S.G.P.J.

Services contêm a lógica de negócio (RN01 a RN10) e orquestram
chamadas aos repositories dentro de transações controladas.

Módulos futuros:
    auth_service.py           — RN01: Autenticação, JWT, bcrypt
    assistido_service.py      — RF03, RN09: Cadastro e validação de assistidos
    caso_service.py           — RF05, RF06, RN02, RN03, RN06: Abertura e encerramento
    atendimento_service.py    — RF04, RN10: Registro de atendimentos
    atividade_service.py      — RF07, RF08, RN04: Gestão de atividades
    prazo_service.py          — RF09, RN05: Cálculo e alerta de prazos
    documento_service.py      — RF10, RN08: Upload e acesso a documentos
    historico_service.py      — RF11, RN07: Rastreabilidade e imutabilidade
    dashboard_service.py      — RF14: Indicadores gerenciais consolidados
    supervisao_service.py     — RF13, RN08: Visão do orientador
"""

