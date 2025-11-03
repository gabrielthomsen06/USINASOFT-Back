# UsinaSoft - Backend (Django)

Este repositório contém o backend do UsinaSoft, um sistema de gestão de usinagem construído com Django e Django REST Framework. Ele expõe uma API REST consumida por um frontend (web ou mobile) para gerenciar usuários, clientes, peças e ordens de produção.

## Sumário

- Sobre o projeto
- Requisitos
- Como rodar localmente
- Estrutura de endpoints (para o frontend)
- Exemplos de requests
- Notas e convenções

## Sobre o projeto

UsinaSoft é uma aplicação para gerenciar o fluxo de produção em uma oficina de usinagem. O backend fornece recursos para:

- Gerenciar usuários (criação, atualização, listagem)
- Registrar logs de ações
- Gerenciar clientes e peças
- Criar e acompanhar Ordens de Produção (OPs) vinculadas ao número da nota fiscal
- Consultar indicadores agregados de produção (OPs e peças)

### Lógica de Produção

**Nota Fiscal → Ordem de Produção:**

O sistema usa o número da nota fiscal física como código da Ordem de Produção. Quando uma peça é cadastrada:

1. O frontend/API envia o campo `ordem_producao_codigo` (número da NF)
2. O sistema verifica se existe uma OP com esse código:
   - **Se não existir:** cria automaticamente uma nova OP com status "aberta"
   - **Se já existir:** associa a peça à OP existente
3. A peça fica vinculada à OP e pode ter status individual: `em_fila`, `em_andamento`, `pausada`, `concluida`, `cancelada`

**Controle de Produção:**

- Cada OP contém múltiplas peças (relacionamento muitos-para-um)
- O status da OP é **atualizado automaticamente** baseado no status das peças:
  - **Quando todas as peças estão concluídas** → OP muda para `concluida` automaticamente
  - **Quando pelo menos uma peça está em andamento** → OP muda para `em_andamento` automaticamente
  - **Quando uma peça é deletada** → Status da OP é recalculado
- Os indicadores calculam automaticamente percentuais de conclusão, tempo médio de produção e estatísticas por status

**⚠️ Importante para o Frontend:**

O frontend **NÃO precisa** atualizar manualmente o status da OP. Basta atualizar o status das peças individuais, e o backend cuida de atualizar a OP automaticamente através de signals do Django.

### Fluxo Visual da Atualização Automática

```
Frontend                          Backend
   │                                 │
   ├─ PATCH /api/pecas/{id}/        │
   │  { status: "concluida" }       │
   │                                 │
   └─────────────────────────────────▶ 1. Salva a peça
                                      │
                                      ├─ 2. Signal post_save dispara
                                      │
                                      ├─ 3. verificar_e_atualizar_status()
                                      │    • Conta peças concluídas
                                      │    • Conta peças em andamento
                                      │    • Atualiza status da OP
                                      │
   ◀─────────────────────────────────┤ 4. Retorna peça com op_status
   │                                 │     atualizado
   │
   └─ Frontend vê op_status = "concluida" ✨
```

Essa documentação descreve como o frontend deve consumir a API exposta pelo backend.

## Requisitos

- Python 3.10+
- Poetry (recomendado) ou pip

Dependências principais (definidas em `pyproject.toml`):

- Django >= 4.2
- djangorestframework
- django-cors-headers

## Como rodar localmente

Usando poetry (recomendado):

```bash
poetry install
poetry run python manage.py migrate
poetry run python manage.py createsuperuser  # Crie um usuário para testar a autenticação
poetry run python manage.py runserver
```

Padrão de base da API: `http://localhost:8000/api/`

## Autenticação

A API usa autenticação baseada em JWT (JSON Web Tokens). Todos os endpoints (exceto criação de usuários e login) requerem um token válido no cabeçalho `Authorization`.

### Como fazer login

Envie uma requisição POST para `/api/auth/token/` com as credenciais:

```json
{
  "email": "usuario@example.com",
  "password": "senha123"
}
```

**Resposta de sucesso:**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Como usar o token

Inclua o token de acesso no cabeçalho de todas as requisições subsequentes:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Renovação de token

Quando o token de acesso expirar, use o token de refresh para obter um novo:

POST `/api/auth/token/refresh/`

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Nota:** A criação de usuários (`POST /api/usuarios/`) não requer autenticação para permitir registro inicial.

### Testando a autenticação

1. **Crie um usuário** (não requer auth):

   ```bash
   curl -X POST http://localhost:8000/api/usuarios/ \
     -H "Content-Type: application/json" \
     -d '{"email": "teste@example.com", "password": "senha123", "first_name": "Teste", "last_name": "User"}'
   ```

2. **Faça login** para obter tokens:

   ```bash
   curl -X POST http://localhost:8000/api/auth/token/ \
     -H "Content-Type: application/json" \
     -d '{"email": "teste@example.com", "password": "senha123"}'
   ```

3. **Use o token** em requisições autenticadas:
   ```bash
   curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     http://localhost:8000/api/pecas/
   ```

## Endpoints da API

### Autenticação

| Método | Endpoint                   | Descrição                                    |
| ------ | -------------------------- | -------------------------------------------- |
| `POST` | `/api/auth/token/`         | Obter tokens de acesso e refresh (login)     |
| `POST` | `/api/auth/token/refresh/` | Renovar token de acesso usando refresh token |

### Usuários

| Método   | Endpoint              | Descrição                                    |
| -------- | --------------------- | -------------------------------------------- |
| `GET`    | `/api/usuarios/`      | Listar todos os usuários                     |
| `POST`   | `/api/usuarios/`      | Criar novo usuário (não requer autenticação) |
| `GET`    | `/api/usuarios/{id}/` | Detalhes de um usuário específico            |
| `PUT`    | `/api/usuarios/{id}/` | Atualizar usuário completamente              |
| `PATCH`  | `/api/usuarios/{id}/` | Atualizar usuário parcialmente               |
| `DELETE` | `/api/usuarios/{id}/` | Excluir usuário                              |

### Logs de Ação

| Método | Endpoint     | Descrição                       |
| ------ | ------------ | ------------------------------- |
| `GET`  | `/api/logs/` | Listar logs de ações do sistema |

### Clientes

| Método   | Endpoint              | Descrição                         |
| -------- | --------------------- | --------------------------------- |
| `GET`    | `/api/clientes/`      | Listar todos os clientes          |
| `POST`   | `/api/clientes/`      | Criar novo cliente                |
| `GET`    | `/api/clientes/{id}/` | Detalhes de um cliente específico |
| `PUT`    | `/api/clientes/{id}/` | Atualizar cliente completamente   |
| `PATCH`  | `/api/clientes/{id}/` | Atualizar cliente parcialmente    |
| `DELETE` | `/api/clientes/{id}/` | Excluir cliente                   |

### Peças

| Método   | Endpoint           | Descrição                                                          |
| -------- | ------------------ | ------------------------------------------------------------------ |
| `GET`    | `/api/pecas/`      | Listar todas as peças                                              |
| `POST`   | `/api/pecas/`      | Criar nova peça (cria/associa OP automaticamente via NF)           |
| `GET`    | `/api/pecas/{id}/` | Detalhes de uma peça específica                                    |
| `PUT`    | `/api/pecas/{id}/` | Atualizar peça completamente                                       |
| `PATCH`  | `/api/pecas/{id}/` | Atualizar peça parcialmente (ex: mudar status para "em_andamento") |
| `DELETE` | `/api/pecas/{id}/` | Excluir peça                                                       |

**Campos importantes ao criar peça:**

- `ordem_producao_codigo` (write-only): Número da nota fiscal para criar/associar OP
- `cliente`: ID do cliente
- `codigo`: Código único da peça
- `quantidade`: Quantidade a produzir
- `status`: Status da peça (padrão: `em_fila`)

### Ordens de Produção (OPs)

| Método   | Endpoint         | Descrição                                                                       |
| -------- | ---------------- | ------------------------------------------------------------------------------- |
| `GET`    | `/api/ops/`      | Listar todas as ordens de produção                                              |
| `POST`   | `/api/ops/`      | Criar nova ordem de produção manualmente (geralmente automática via peça)       |
| `GET`    | `/api/ops/{id}/` | Detalhes de uma OP específica (inclui total de peças e percentual de conclusão) |
| `PUT`    | `/api/ops/{id}/` | Atualizar OP completamente                                                      |
| `PATCH`  | `/api/ops/{id}/` | Atualizar OP parcialmente (ex: mudar status)                                    |
| `DELETE` | `/api/ops/{id}/` | Excluir OP (cuidado: pode afetar peças vinculadas)                              |

**Campos importantes:**

- `codigo`: Código da OP (número da NF) - único
- `cliente`: ID do cliente
- `status`: Status da OP (`aberta`, `em_andamento`, `concluida`)
- `total_pecas` (read-only): Total de peças nesta OP
- `pecas_concluidas` (read-only): Número de peças concluídas
- `percentual_conclusao` (read-only): Percentual calculado automaticamente

### Indicadores

| Método | Endpoint                    | Descrição                                       |
| ------ | --------------------------- | ----------------------------------------------- |
| `GET`  | `/api/indicadores/summary/` | Resumo de indicadores de produção (OPs e peças) |

**Parâmetros de query:**

- `start`: Data inicial (formato: YYYY-MM-DD) - padrão: 30 dias atrás
- `end`: Data final (formato: YYYY-MM-DD) - padrão: hoje
- `date_field`: Campo para filtro (`created_at` ou `updated_at`) - padrão: `created_at`

**Resposta inclui:**

- Total de OPs e distribuição por status
- Percentual de cada status
- Tempo médio de produção (em dias)
- Total de peças e distribuição por status

### Parâmetros de Query Comuns

- `?page=N` - Paginação (padrão: 100 itens por página)
- `?ordering=campo` - Ordenação (use `-campo` para decrescente)

### Parâmetros Específicos do Endpoint de Indicadores

- `?start=YYYY-MM-DD` - Data inicial do período
- `?end=YYYY-MM-DD` - Data final do período
- `?date_field=campo` - Campo de data para filtro (`created_at` ou `updated_at`)

## Exemplos para o frontend

### 1. Criar usuário (não requer autenticação)

```javascript
fetch("http://localhost:8000/api/usuarios/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: "user@example.com",
    password: "senha123",
    first_name: "João",
    last_name: "Silva",
  }),
})
  .then((r) => r.json())
  .then((data) => console.log(data));
```

### 2. Login e obter token JWT

```javascript
fetch("http://localhost:8000/api/auth/token/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: "user@example.com",
    password: "senha123",
  }),
})
  .then((r) => r.json())
  .then((data) => {
    // Salvar o token para usar nas próximas requisições
    localStorage.setItem("access_token", data.access);
    localStorage.setItem("refresh_token", data.refresh);
  });
```

### 3. Criar cliente

```javascript
const token = localStorage.getItem("access_token");

fetch("http://localhost:8000/api/clientes/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  },
  body: JSON.stringify({
    nome: "Cliente Exemplo",
    contato: "João Silva",
    email: "contato@exemplo.com",
    endereco: "Rua Exemplo, 123",
  }),
})
  .then((r) => r.json())
  .then((data) => console.log(data));
```

### 4. Criar peça (cria/associa OP automaticamente)

```javascript
const token = localStorage.getItem("access_token");

fetch("http://localhost:8000/api/pecas/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  },
  body: JSON.stringify({
    ordem_producao_codigo: "NF-12345", // Número da nota fiscal
    cliente: "uuid-do-cliente",
    codigo: "PEC-001",
    descricao: "Eixo de transmissão",
    quantidade: 50,
    data_entrega: "2025-12-31",
    status: "em_fila",
  }),
})
  .then((r) => r.json())
  .then((data) => console.log(data));
```

### 5. Listar peças com filtros

```javascript
import axios from "axios";

const token = localStorage.getItem("access_token");

axios
  .get("http://localhost:8000/api/pecas/", {
    headers: { Authorization: `Bearer ${token}` },
    params: {
      status: "em_andamento",
      ordering: "-created_at",
    },
  })
  .then((resp) => console.log(resp.data))
  .catch((err) => console.error(err));
```

### 6. Atualizar status de peça

```javascript
const token = localStorage.getItem("access_token");

fetch("http://localhost:8000/api/pecas/uuid-da-peca/", {
  method: "PATCH",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  },
  body: JSON.stringify({
    status: "concluida",
  }),
})
  .then((r) => r.json())
  .then((data) => {
    console.log(data);
    // ✅ A OP vinculada será atualizada automaticamente pelo backend
    // Se esta era a última peça pendente, a OP mudará para "concluida"
  });
```

**Comportamento automático:**

- Quando você muda o status de uma peça para `concluida`, o backend verifica automaticamente se todas as peças da OP estão concluídas
- Se sim, a OP é marcada como `concluida` automaticamente
- Se você muda uma peça para `em_andamento`, a OP muda para `em_andamento` (se ainda não estiver)
- O frontend **não precisa fazer nenhuma requisição adicional** para atualizar a OP

### 7. Consultar indicadores

```javascript
axios
  .get("http://localhost:8000/api/indicadores/summary/", {
    headers: { Authorization: `Bearer ${token}` },
    params: {
      start: "2025-01-01",
      end: "2025-01-31",
      date_field: "created_at",
    },
  })
  .then((r) => console.log(r.data));
```

**Resposta esperada:**

```json
{
  "periodo": {
    "start": "2025-01-01",
    "end": "2025-01-31",
    "date_field": "created_at"
  },
  "ordens_producao": {
    "total": 10,
    "por_status": {
      "aberta": 3,
      "em_andamento": 5,
      "concluida": 2
    },
    "detalhes_por_status": [
      {
        "status": "aberta",
        "rotulo": "Aberta",
        "quantidade": 3,
        "percentual": 30.0
      }
      // ...
    ],
    "tempo_medio_producao_dias": 5.5
  },
  "pecas": {
    "total": 50,
    "por_status": {
      "em_fila": 10,
      "em_andamento": 20,
      "concluida": 15,
      "pausada": 3,
      "cancelada": 2
    }
  }
}
```

## Convenções e dicas

- **Todas as rotas seguem o padrão REST do DRF:** URLs base são `/api/<recurso>/` e `/api/<recurso>/{id}/`
- **Autenticação obrigatória:** Exceto para criação de usuário e login, todos os endpoints requerem token JWT
- **Filtros e ordenação:** Use parâmetros de query como `?status=em_andamento&ordering=-created_at`
- **Campos read-only:** Não envie campos como `created_at`, `updated_at`, `cliente_nome`, `total_pecas` em POST/PUT
- **Relacionamentos:** Envie apenas os UUIDs das entidades relacionadas (ex.: `"cliente": "uuid-do-cliente"`)
- **Criação automática de OP:** Ao criar uma peça, sempre envie `ordem_producao_codigo` (número da NF)
- **Status de peças:** Atualize via PATCH para transições de status (`em_fila` → `em_andamento` → `concluida`)

## Fluxo de trabalho recomendado

1. **Criar cliente** via POST `/api/clientes/`
2. **Criar peça** via POST `/api/pecas/` com `ordem_producao_codigo` (NF)
   - O sistema cria ou associa automaticamente à OP
3. **Listar OPs** via GET `/api/ops/` para ver OPs criadas
4. **Atualizar status das peças** conforme o progresso da produção
   - Use PATCH `/api/pecas/{id}/` para mudar status (`em_fila` → `em_andamento` → `concluida`)
   - **A OP é atualizada automaticamente** sem precisar de chamada adicional
5. **Consultar indicadores** via GET `/api/indicadores/summary/` para dashboards

## Atualização Automática de Status da OP

O sistema implementa **lógica automática** para atualizar o status da Ordem de Produção baseado no status das peças:

### Regras de Atualização

| Situação das Peças                           | Status da OP Resultante |
| -------------------------------------------- | ----------------------- |
| Todas as peças estão `concluida`             | `concluida`             |
| Pelo menos uma peça está `em_andamento`      | `em_andamento`          |
| Todas em `em_fila`, `pausada` ou `cancelada` | Mantém status atual     |

### Como funciona no código

Quando você atualiza o status de uma peça:

```javascript
// Frontend atualiza a peça
await fetch(`/api/pecas/${pecaId}/`, {
  method: "PATCH",
  body: JSON.stringify({ status: "concluida" }),
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  },
});

// ✅ Backend automaticamente:
// 1. Salva a peça com novo status
// 2. Dispara um signal (post_save)
// 3. Verifica todas as peças da OP
// 4. Atualiza o status da OP se necessário
// 5. Retorna a peça atualizada com op_status atualizado
```

### Recomendações para o Frontend

**✅ Faça:**

- Atualize o status das peças individualmente via PATCH
- Após atualizar uma peça, **refaça GET** na OP para obter o status atualizado
- Use os campos `op_codigo` e `op_status` retornados no serializer da peça

**❌ Não faça:**

- Não tente atualizar manualmente o status da OP
- Não implemente lógica de contagem de peças concluídas no frontend
- Não faça múltiplas requisições simultâneas para atualizar peças da mesma OP (pode causar condições de corrida)

### Exemplo Completo - Concluir Produção

```javascript
// Cenário: Operador marca a última peça como concluída

async function concluirPeca(pecaId) {
  const token = localStorage.getItem("access_token");

  // 1. Atualizar status da peça
  const response = await fetch(`http://localhost:8000/api/pecas/${pecaId}/`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ status: "concluida" }),
  });

  const pecaAtualizada = await response.json();

  // 2. O backend já atualizou a OP automaticamente!
  // Você pode ver o status atualizado nos campos read-only:
  console.log("Status da OP:", pecaAtualizada.op_status);

  // 3. Opcional: Buscar dados completos da OP
  const opResponse = await fetch(
    `http://localhost:8000/api/ops/${pecaAtualizada.ordem_producao}/`,
    {
      headers: { Authorization: `Bearer ${token}` },
    }
  );

  const op = await opResponse.json();

  if (op.status === "concluida") {
    // 🎉 Todas as peças foram concluídas!
    console.log(`OP ${op.codigo} foi concluída automaticamente!`);
    console.log(`Percentual: ${op.percentual_conclusao}%`);
    console.log(`Total de peças: ${op.total_pecas}`);
    console.log(`Peças concluídas: ${op.pecas_concluidas}`);

    // Mostrar notificação de sucesso, etc.
  }
}
```

### Monitoramento em Tempo Real

Para dashboards e monitores de produção, você pode:

1. **Polling periódico** de `/api/ops/` para atualizar lista de OPs
2. **WebSockets** (se implementar futuramente) para notificações em tempo real
3. **Atualizar após cada ação** do usuário que mude status de peças

## Casos de Uso - Integração Frontend

### Caso 1: Dashboard de Produção

```javascript
// Componente React/Vue que mostra OPs em andamento
async function carregarOPsEmAndamento() {
  const response = await fetch(
    "http://localhost:8000/api/ops/?status=em_andamento",
    {
      headers: { Authorization: `Bearer ${token}` },
    }
  );

  const data = await response.json();

  // Renderizar cards de OPs com:
  data.results.forEach((op) => {
    console.log(`OP ${op.codigo}: ${op.percentual_conclusao}% concluída`);
    console.log(`${op.pecas_concluidas}/${op.total_pecas} peças prontas`);

    // ✅ Status é sempre preciso porque é atualizado automaticamente
  });
}
```

### Caso 2: Tela de Produção de Peça

```javascript
// Operador marca peça como iniciada
async function iniciarProducaoPeca(pecaId) {
  await fetch(`http://localhost:8000/api/pecas/${pecaId}/`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ status: "em_andamento" }),
  });

  // ✅ OP da peça mudou automaticamente para "em_andamento"
  // Você pode mostrar isso na UI sem fazer chamada adicional

  // Opcional: Recarregar dados da OP
  await atualizarDadosOP();
}

// Operador marca peça como concluída
async function concluirProducaoPeca(pecaId) {
  const response = await fetch(`http://localhost:8000/api/pecas/${pecaId}/`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ status: "concluida" }),
  });

  const peca = await response.json();

  // Verificar se a OP foi concluída
  if (peca.op_status === "concluida") {
    // 🎉 Última peça! Mostrar celebração
    mostrarMensagem("Parabéns! Todas as peças da OP foram concluídas!");
  } else {
    // Ainda há peças pendentes
    const opResponse = await fetch(
      `http://localhost:8000/api/ops/${peca.ordem_producao}/`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    const op = await opResponse.json();

    mostrarMensagem(
      `Peça concluída! Faltam ${op.total_pecas - op.pecas_concluidas} peças.`
    );
  }
}
```

### Caso 3: Lista de Peças de uma OP

```javascript
// Mostrar todas as peças de uma OP específica
async function listarPecasDaOP(opId) {
  const response = await fetch(
    `http://localhost:8000/api/pecas/?ordem_producao=${opId}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  const data = await response.json();

  // Agrupar por status para visualização
  const porStatus = {
    em_fila: [],
    em_andamento: [],
    pausada: [],
    concluida: [],
    cancelada: [],
  };

  data.results.forEach((peca) => {
    porStatus[peca.status].push(peca);
  });

  // Renderizar em colunas tipo Kanban
  renderizarKanban(porStatus);
}
```

### Caso 4: Integração com Scanner de Código de Barras

```javascript
// Quando operador escaneia código da peça
async function processarScanPeca(codigoPeca) {
  // 1. Buscar peça pelo código
  const response = await fetch(
    `http://localhost:8000/api/pecas/?codigo=${codigoPeca}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  const data = await response.json();

  if (data.results.length === 0) {
    mostrarErro("Peça não encontrada!");
    return;
  }

  const peca = data.results[0];

  // 2. Verificar status atual
  if (peca.status === "em_fila") {
    // Iniciar produção
    await fetch(`http://localhost:8000/api/pecas/${peca.id}/`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ status: "em_andamento" }),
    });

    mostrarMensagem(`Produção iniciada para ${peca.codigo}`);
  } else if (peca.status === "em_andamento") {
    // Concluir produção
    await fetch(`http://localhost:8000/api/pecas/${peca.id}/`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ status: "concluida" }),
    });

    mostrarMensagem(`Peça ${peca.codigo} concluída!`);

    // ✅ OP atualizada automaticamente pelo backend
  }
}
```

## Mudanças na Versão Atual (v2.1)

### Nova Funcionalidade: Atualização Automática de Status da OP

- **✨ Novo:** Status da OP é atualizado automaticamente quando peças mudam de status
- **✨ Novo:** Quando todas as peças são concluídas, a OP muda para `concluida` automaticamente
- **✨ Novo:** Quando uma peça entra em `em_andamento`, a OP muda para `em_andamento` automaticamente
- **✨ Novo:** Signals do Django gerenciam a atualização sem intervenção manual
- **Frontend simplificado:** Não precisa mais atualizar manualmente o status da OP

### Refatoração Completa da Lógica de Produção (v2.0)

- **Removido:** App `atividades`, `comentários` e `anexos` - simplificação do sistema
- **Removido:** Modelo `OrdemProducaoItem` - relação agora é direta entre `Peca` e `OrdemProducao`
- **Nota Fiscal = Ordem de Produção:** O código da OP agora corresponde ao número da NF física
- **Criação automática de OP:** Ao cadastrar uma peça, a OP é criada ou associada automaticamente
- **Status de peças atualizado:** Agora são `em_fila`, `em_andamento`, `pausada`, `concluida`, `cancelada`
- **Status de OP simplificado:** Agora são apenas `aberta`, `em_andamento`, `concluida`
- **Indicadores recalculados:** Baseados apenas em OPs e peças, incluindo tempo médio de produção
- **Migrations resetadas:** Banco de dados limpo para refletir a nova estrutura

### Instruções para atualizar de versões antigas

Se você está vindo de uma versão anterior, siga estes passos:

#### Backend

1. **Backup do banco de dados** (se necessário preservar dados)

   ```bash
   cp db.sqlite3 db.sqlite3.backup
   ```

2. **Remover banco antigo:**

   ```bash
   rm db.sqlite3
   ```

3. **Remover migrations antigas:**

   ```bash
   find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
   ```

4. **Criar novas migrations:**

   ```bash
   poetry run python manage.py makemigrations
   ```

5. **Aplicar migrations:**

   ```bash
   poetry run python manage.py migrate
   ```

6. **Criar superusuário:**

   ```bash
   poetry run python manage.py createsuperuser
   ```

7. **Iniciar servidor:**
   ```bash
   poetry run python manage.py runserver
   ```

#### Frontend / Navegador

Se você estiver vendo erros 404 relacionados a `atividades`, `comentarios` ou `anexos`:

1. **Limpar cache do navegador**
2. **Limpar localStorage:**
   ```javascript
   // No console do navegador
   localStorage.clear();
   ```
3. **Fazer logout e login novamente** para obter novos tokens
4. **Atualizar a página** (Ctrl+F5 ou Cmd+Shift+R)

**⚠️ Importante:** Links antigos do Django Admin para atividades não funcionarão mais. Se você estava no meio de uma edição quando atualizou, apenas volte para a página inicial do admin.

### Autenticação JWT

- Todos os endpoints requerem autenticação, exceto criação de usuários e login
- Endpoints: `/api/auth/token/` (login) e `/api/auth/token/refresh/` (renovar token)
- Token deve ser enviado no header: `Authorization: Bearer {token}`
