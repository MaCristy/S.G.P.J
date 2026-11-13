---
name: react-frontend
description: >-
  Orientações e padrões para o desenvolvimento do Frontend em React do Sistema de Gestão da Prática Jurídica (S.G.P.J.), incluindo arquitetura de componentes, layout institucional UNINASSAU, gestão de rotas, consumo da API REST e acessibilidade.
---

# Diretrizes de Desenvolvimento Frontend (React) - S.G.P.J.

Este guia estabelece os padrões técnicos, visuais e arquiteturais para o desenvolvimento da interface do **Sistema de Gestão da Prática Jurídica (S.G.P.J.)**, alinhando os requisitos do documento oficial da UNINASSAU com as recomendações técnicas de implementação.

---

## 1. Identidade Visual e Design System (Requisitos Oficiais UNINASSAU)

A interface deve adotar um padrão estritamente institucional, priorizando clareza, legibilidade e baixa sobrecarga visual (Seção 11 do documento).

### 1.1. Paleta de Cores Oficial

| Cor / Função | Hexadecimal | Aplicação no Sistema (Doc. Seção 11.2) |
| :--- | :--- | :--- |
| **Azul Institucional** | `#003874` | Barra lateral, títulos, links e item ativo. |
| **Amarelo Destaque** | `#E3B103` | Marcadores, foco e destaques pontuais. |
| **Branco** | `#FFFFFF` | Cartões, formulários e área de conteúdo. |
| **Cinza Muito Claro** | `#F4F5FA` | Fundo geral da aplicação. |
| **Cinza de Borda** | `#D9DEE8` | Divisórias, campos e tabelas. |
| **Preto** | `#202938` | Títulos, rótulos e texto corrente. |
| **Texto Secundário** | `#667085` | Ajuda, datas e metadados. |
| **Verde** | `#16803C` | Sucesso e itens concluídos. |
| **Âmbar** | `#A15C00` | Prazos próximos e atenção. |
| **Vermelho** | `#B42318` | Erros, prazos vencidos e ações destrutivas. |
| **Azul Claro** | `#EAF2FB` | Avisos informativos. |

### 1.2. Tipografia, Espaçamento e Formas (Doc. Seção 11.4)
* **Tipografia:** Família `Inter` (como alternativas oficiais: `Roboto` ou `Arial`, com fallbacks).
  * Título de página: `24–28px`, peso semibold/bold.
  * Título de seção: `18–20px`, peso semibold.
  * Texto padrão: `14–16px`, peso regular.
  * Rótulos e metadados: `12–14px`, mantendo contraste.
* **Espaçamento:** Escala baseada estritamente em múltiplos de 8px: `8px`, `16px`, `24px` e `32px`.
* **Contornos:** Bordas discretas de `1px` com raio sugerido entre `6px` e `10px`.

---

## 2. Recomendações Técnicas de Implementação (Não-Obrigatórias)

> **Nota:** As ferramentas abaixo constituem **recomendações de engenharia** para acelerar o desenvolvimento e manter a fidelidade visual, não sendo exigências literais do documento:
> * **Tailwind CSS:** Recomendado para aplicar a paleta e a escala de 8px de forma declarativa e padronizada.
> * **Lucide React:** Recomendado como biblioteca de ícones para garantir a regra da Seção 11.4 ("Uma única família visual; ícones simples e reconhecíveis").

---

## 3. Padrão das Telas Principais (Doc. Seção 11.7)

O documento define 9 telas principais para a aplicação:
1. **Login:** Identificação do S.G.P.J., campos de e-mail institucional e senha, botão de entrada e mensagens de erro.
2. **Dashboard:** Título "Visão geral", cartões com os indicadores gerenciais e lista de itens que exigem atenção.
3. **Assistidos:** Busca, botão "Novo assistido", tabela com campos essenciais e ações de visualizar/editar conforme permissão.
4. **Atendimentos:** Formulário com assistido, data/hora, responsável, descrição objetiva e encaminhamento; histórico cronológico.
5. **Casos Jurídicos:** Filtros por situação, estudante e orientador; tabela com código, assunto, assistido, responsável, situação e datas; ação para abrir caso.
6. **Detalhes do Caso:** Cabeçalho com código e situação, resumo, responsáveis e abas dedicadas para *Atividades*, *Prazos*, *Documentos* e *Histórico*.
7. **Atividades e Prazos:** Listagem com responsável, situação e data limite; destaque visual e textual para prazos próximos ou vencidos.
8. **Supervisão:** Painel exclusivo do professor para acompanhar casos e atividades sob sua orientação, com filtros por estudante, situação e período.
9. **Usuários e Perfis:** Área restrita à gestão/coordenação para listagem de contas, perfis e ações administrativas.

### Proposta de Mapeamento de Rotas (Recomendação Técnica):
As rotas abaixo são uma sugestão de implementação SPA em React para contemplar as 9 telas:
* `/login`
* `/dashboard`
* `/assistidos`
* `/atendimentos`
* `/casos`
* `/casos/:id` (com navegação por abas)
* `/atividades-prazos`
* `/supervisao`
* `/usuarios`

---

## 4. Padronização de Estados e Tratamento de Supervisão

### 4.1. Estados Oficiais das Entidades (Doc. Seção 5.1)
* **Caso:** `Em triagem`, `Aberto`, `Em Andamento`, `Suspenso` e `Encerrado`.
* **Atividade:** `Pendente`, `Em andamento`, `Concluída` e `Cancelada`.
* **Prazo:** `Pendente`, `Concluído` e `Vencido`.

### 4.2. Tratamento Visual de Estados (Doc. Seção 11.6)
* **Pendente:** Rótulo neutro ou azul claro, acompanhado de texto explicativo.
* **Em andamento:** Azul claro (`#EAF2FB`).
* **Concluído:** Verde (`#16803C`), com rótulo "Concluído".
* **Próximo do prazo:** Amarelo/âmbar (`#A15C00`), com data explícita e rótulo de atenção.
* **Atrasado / Vencido:** Vermelho (`#B42318`), com indicação textual e prazo visível.
* **"Devolvido para correção":** Na tabela 11.6 é apresentado como tratamento visual de atenção (para atividades que necessitam de ajuste após revisão do orientador). **Atenção:** Permanece como uma situação de revisão/supervisão pendente de definição formal pela equipe (se será um status adicional ou uma observação/ocorrência no histórico), sem alteração precoce no modelo oficial de dados.

---

## 5. Padrões de Componentes e Acessibilidade (Doc. Seção 11.5 e 11.8)

* **Botões:** Primário (azul/texto branco), Secundário (branco/borda cinza), Destaque (amarelo pontual com alto contraste) e Destrutivo (vermelho para exclusão com confirmação).
* **Formulários:** Rótulos sempre visíveis acima do campo (não depender de placeholders), indicação visual de campos obrigatórios e mensagens de erro contextualizadas.
* **Acessibilidade:**
  * Priorizar o uso em computadores (desktop first), considerando o uso intensivo de tabelas e autos.
  * Não comunicar estados apenas por cores; sempre incluir rótulos textuais descritivos.
  * Manter contraste WCAG e ordem de tabulação lógica.

---

## 6. Integração com a API Backend

* Centralizar requisições em um cliente HTTP (recomendação: Axios ou Fetch com módulo dedicado).
* Enviar token de autenticação no cabeçalho `Authorization: Bearer <token>`.
* Tratar códigos HTTP (`401` para redirecionamento ao login, `403` para bloqueio de perfil, `422` para erros de validação).
