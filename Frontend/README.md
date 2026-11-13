# S.G.P.J. — Front-end

Front-end inicial do Sistema de Gestão da Prática Jurídica, desenvolvido com React, Vite e JavaScript.

## Requisitos
- Node.js LTS instalado
- npm

## Executar localmente
Abra o terminal nesta pasta (`Frontend`) e execute:

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

Acesse: http://127.0.0.1:5173

## Build de produção
```powershell
npm run build
npm run preview
```

## Estrutura
- `src/components`: componentes reutilizáveis
- `src/layouts`: estruturas compartilhadas das páginas
- `src/pages`: páginas e telas
- `src/routes`: configuração de rotas
- `src/services`: comunicação futura com a API
- `src/contexts`: contextos React, incluindo futura autenticação
- `src/assets`: imagens e outros recursos
- `src/styles`: estilos globais e tokens visuais

## Perfis previstos
- Aluno/Estagiário
- Professor/Orientador
- Gestão/Coordenação

O controle real de identidade, autenticação e autorização deverá ser implementado e validado pelo backend. Esta versão inicial não simula login nem concede permissões.
