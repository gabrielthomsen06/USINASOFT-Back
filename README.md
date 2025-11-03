# UsinaSoft - Backend (Django)

Este repositório contém o backend do UsinaSoft, um sistema de gestão de usinagem construído com Django e Django REST Framework. Ele expõe uma API REST consumida por um frontend (web ou mobile) para gerenciar usuários, clientes, peças, ordens de produção, atividades, comentários e anexos.

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
- Criar e acompanhar Ordens de Produção (OPs) e seus itens
- Criar atividades associadas a OPs/itens/peças
- Adicionar comentários e anexos às atividades
- Consultar indicadores agregados de produção

### Funcionalidades Automáticas

- **Criação automática de atividades:** Quando uma nova peça é cadastrada, o sistema automaticamente cria uma atividade de produção com título "Produzir peça {código}" contendo os detalhes da peça (cliente, quantidade, data de entrega) no campo descrição e metadata.

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

Usando pip/venv:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # gere via poetry export se necessário
python manage.py migrate
python manage.py createsuperuser  # Crie um usuário para testar a autenticação
python manage.py runserver
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

| Método   | Endpoint           | Descrição                       |
| -------- | ------------------ | ------------------------------- |
| `GET`    | `/api/pecas/`      | Listar todas as peças           |
| `POST`   | `/api/pecas/`      | Criar nova peça                 |
| `GET`    | `/api/pecas/{id}/` | Detalhes de uma peça específica |
| `PUT`    | `/api/pecas/{id}/` | Atualizar peça completamente    |
| `PATCH`  | `/api/pecas/{id}/` | Atualizar peça parcialmente     |
| `DELETE` | `/api/pecas/{id}/` | Excluir peça                    |

### Ordens de Produção (OPs)

| Método   | Endpoint         | Descrição                          |
| -------- | ---------------- | ---------------------------------- |
| `GET`    | `/api/ops/`      | Listar todas as ordens de produção |
| `POST`   | `/api/ops/`      | Criar nova ordem de produção       |
| `GET`    | `/api/ops/{id}/` | Detalhes de uma OP específica      |
| `PUT`    | `/api/ops/{id}/` | Atualizar OP completamente         |
| `PATCH`  | `/api/ops/{id}/` | Atualizar OP parcialmente          |
| `DELETE` | `/api/ops/{id}/` | Excluir OP                         |

### Itens de Ordem de Produção

| Método   | Endpoint              | Descrição                      |
| -------- | --------------------- | ------------------------------ |
| `GET`    | `/api/itens-op/`      | Listar todos os itens de OP    |
| `POST`   | `/api/itens-op/`      | Criar novo item de OP          |
| `GET`    | `/api/itens-op/{id}/` | Detalhes de um item específico |
| `PUT`    | `/api/itens-op/{id}/` | Atualizar item completamente   |
| `PATCH`  | `/api/itens-op/{id}/` | Atualizar item parcialmente    |
| `DELETE` | `/api/itens-op/{id}/` | Excluir item                   |

### Indicadores

| Método | Endpoint                    | Descrição                         |
| ------ | --------------------------- | --------------------------------- |
| `GET`  | `/api/indicadores/summary/` | Resumo de indicadores de produção |

### Atividades

| Método   | Endpoint                | Descrição                            |
| -------- | ----------------------- | ------------------------------------ |
| `GET`    | `/api/atividades/`      | Listar todas as atividades           |
| `POST`   | `/api/atividades/`      | Criar nova atividade                 |
| `GET`    | `/api/atividades/{id}/` | Detalhes de uma atividade específica |
| `PUT`    | `/api/atividades/{id}/` | Atualizar atividade completamente    |
| `PATCH`  | `/api/atividades/{id}/` | Atualizar atividade parcialmente     |
| `DELETE` | `/api/atividades/{id}/` | Excluir atividade                    |

### Comentários

| Método   | Endpoint                 | Descrição                            |
| -------- | ------------------------ | ------------------------------------ |
| `GET`    | `/api/comentarios/`      | Listar todos os comentários          |
| `POST`   | `/api/comentarios/`      | Criar novo comentário                |
| `GET`    | `/api/comentarios/{id}/` | Detalhes de um comentário específico |
| `PUT`    | `/api/comentarios/{id}/` | Atualizar comentário completamente   |
| `PATCH`  | `/api/comentarios/{id}/` | Atualizar comentário parcialmente    |
| `DELETE` | `/api/comentarios/{id}/` | Excluir comentário                   |

### Anexos

| Método   | Endpoint            | Descrição                       |
| -------- | ------------------- | ------------------------------- |
| `GET`    | `/api/anexos/`      | Listar todos os anexos          |
| `POST`   | `/api/anexos/`      | Criar novo anexo                |
| `GET`    | `/api/anexos/{id}/` | Detalhes de um anexo específico |
| `PUT`    | `/api/anexos/{id}/` | Atualizar anexo completamente   |
| `PATCH`  | `/api/anexos/{id}/` | Atualizar anexo parcialmente    |
| `DELETE` | `/api/anexos/{id}/` | Excluir anexo                   |

### Parâmetros de Query Comuns

- `?page=N` - Paginação (padrão: 100 itens por página)
- `?ordering=campo` - Ordenação (use `-campo` para decrescente)

### Parâmetros Específicos do Endpoint de Indicadores

- `?start=YYYY-MM-DD` - Data inicial do período
- `?end=YYYY-MM-DD` - Data final do período
- `?date_field=campo` - Campo de data para filtro (`data_fim_prevista`, `data_inicio_prevista`, `created_at`)

## Exemplos para o frontend

Exemplo usando fetch (criar usuário):

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

Exemplo usando axios (listar peças):

```javascript
import axios from "axios";

axios
  .get("http://localhost:8000/api/pecas/")
  .then((resp) => console.log(resp.data))
  .catch((err) => console.error(err));
```

Consulta de indicadores com parâmetros de data:

```javascript
axios
  .get("http://localhost:8000/api/indicadores/summary/", {
    params: {
      start: "2025-01-01",
      end: "2025-01-31",
      date_field: "data_fim_prevista",
    },
  })
  .then((r) => console.log(r.data));
```

Upload de arquivos / anexos

No momento a API expõe o `AnexoSerializer` com campos descritivos; se precisar enviar arquivos via multipart/form-data, verifique se há uma view/endpoint custom que aceite uploads (caso contrário, envie metadados e armazene os arquivos externamente).

Exemplo básico usando FormData:

```javascript
const fd = new FormData();
fd.append("criado_por", 1);
fd.append("object_id", 123);
fd.append("content_type", 7); // id do ContentType
fd.append("arquivo", fileInput.files[0]); // se houver suporte de upload

fetch("http://localhost:8000/api/anexos/", {
  method: "POST",
  body: fd,
  // não setar Content-Type, o browser define boundary
})
  .then((r) => r.json())
  .then((d) => console.log(d));
```

## Convenções e dicas

- Todas as rotas seguem o padrão REST do `DefaultRouter` do DRF. Para recursos listados acima, as URLs base são `/api/<recurso>/` e `/api/<recurso>/{id}/`.
- Filtros, paginação e ordenação podem ser habilitados no backend. Atualmente os ViewSets definem `queryset` com ordenação padrão.
- Campos read-only: muitos serializers incluem campos de leitura como `created_at`, `updated_at`, e campos derivados (ex.: `cliente_nome`, `peca_codigo`). Não envie esses campos no POST/PUT.
- Para listar relações, envie apenas os IDs das entidades relacionadas (ex.: `cliente: 3`, `peca: 12`).

## Mudanças Recentes

- **Criação automática de atividades:** Implementada funcionalidade onde o cadastro de uma nova peça automaticamente cria uma atividade de produção associada.
- **Autenticação JWT implementada:** Todos os endpoints agora requerem autenticação, exceto criação de usuários e login.
- **Endpoints de autenticação:** `/api/auth/token/` (login) e `/api/auth/token/refresh/` (renovar token).
- **Pacotes atualizados:** Removidos pacotes desnecessários, mantido apenas `djangorestframework-simplejwt` para JWT.
- **Indicadores aprimorados:** Endpoint `/api/indicadores/summary/` agora retorna todos os status com percentuais calculados.
