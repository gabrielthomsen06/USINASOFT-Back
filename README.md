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
poetry run python manage.py createsuperuser  # opcional
poetry run python manage.py runserver
```

Usando pip/venv:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # gere via poetry export se necessário
python manage.py migrate
python manage.py createsuperuser  # opcional
python manage.py runserver
```

Padrão de base da API: `http://localhost:8000/api/`

## Autenticação

No estado atual do projeto a configuração dos ViewSets usa permissões abertas (`AllowAny`) em muitos endpoints. Se o projeto for configurado para usar autenticação (Token, JWT ou Session), o frontend deverá enviar o cabeçalho `Authorization: Bearer <token>` (ou `Token <token>` conforme a configuração).

## Endpoints principais

Observação: as rotas são registradas com um `DefaultRouter` em `usinasoft/urls.py`. Abaixo estão os principais recursos expostos e os métodos REST suportados (ModelViewSet padrões: GET list, POST create, GET detail, PUT/PATCH update, DELETE destroy quando aplicável).

- /api/usuarios/ [GET, POST]
  - Listar usuários / criar usuário
  - Payload (criar): { "email": "user@example.com", "password": "senha", "first_name": "...", "last_name": "..." }

- /api/usuarios/{id}/ [GET, PUT, PATCH, DELETE]

- /api/logs/ [GET]
  - Logs de ações (somente leitura)

- /api/clientes/ [GET, POST]
  - Cliente: { "nome": "Cliente X", "contato": "...", "email": "...", "endereco": "..." }

- /api/clientes/{id}/ [GET, PUT, PATCH, DELETE]

- /api/pecas/ [GET, POST]
  - Peça: { "cliente": <cliente_id>, "codigo": "ABC123", "descricao": "...", "pedido": "...", "quantidade": 10, "data_entrega": "YYYY-MM-DD" }

- /api/pecas/{id}/ [GET, PUT, PATCH, DELETE]

- /api/ops/ [GET, POST]
  - Ordem de Produção: campos incluem "numero", "criado_por", "data_inicio_prevista", "data_fim_prevista", "status", "observacoes"

- /api/ops/{id}/ [GET, PUT, PATCH, DELETE]

- /api/itens-op/ [GET, POST]
  - Item de OP: { "ordem": <ordem_id>, "peca": <peca_id>, "quantidade": 100, "lote": "L001" }

- /api/itens-op/{id}/ [GET, PUT, PATCH, DELETE]

- /api/indicadores/summary/ [GET]
  - Endpoint custom para agregar indicadores de Ordens de Produção.
  - Query params (opcionais): `start` (YYYY-MM-DD), `end` (YYYY-MM-DD), `date_field` (data_fim_prevista | data_inicio_prevista | created_at)
  - Exemplo de resposta:
    {
      "periodo": {"start":"2025-01-01","end":"2025-01-31","date_field":"data_fim_prevista"},
      "total": 150,
      "por_status": {"aberta":10,"em_andamento":45,"pausada":5,"concluida":85,"cancelada":5},
      "agrupado": {"emFila":10,"emAndamento":50,"concluidas":85}
    }

- /api/atividades/ [GET, POST]
  - Atividade: campos incluem "titulo", "descricao", "responsavel" (user id), "ordem" (ordem id), "ordem_item" (item id), "peca" (peca id), "status", "prioridade", "data_inicio", "data_fim", "posicao", "metadata"

- /api/atividades/{id}/ [GET, PUT, PATCH, DELETE]

- /api/comentarios/ [GET, POST]
  - Comentário: { "atividade": <atividade_id>, "autor": <usuario_id>, "texto": "..." }

- /api/comentarios/{id}/ [GET, PUT, PATCH, DELETE]

- /api/anexos/ [GET, POST]
  - Anexo: campos incluem "content_type" (id do ContentType), "object_id", "arquivo_path" (ou use upload via endpoint custom no futuro), "nome_original", "mime_type", "tamanho", "criado_por"

- /api/anexos/{id}/ [GET, PUT, PATCH, DELETE]


## Exemplos para o frontend

Exemplo usando fetch (criar usuário):

```javascript
fetch('http://localhost:8000/api/usuarios/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'senha123',
    first_name: 'João',
    last_name: 'Silva'
  })
})
.then(r => r.json())
.then(data => console.log(data))
```

Exemplo usando axios (listar peças):

```javascript
import axios from 'axios'

axios.get('http://localhost:8000/api/pecas/')
  .then(resp => console.log(resp.data))
  .catch(err => console.error(err))
```

Consulta de indicadores com parâmetros de data:

```javascript
axios.get('http://localhost:8000/api/indicadores/summary/', {
  params: { start: '2025-01-01', end: '2025-01-31', date_field: 'data_fim_prevista' }
}).then(r => console.log(r.data))
```

Upload de arquivos / anexos

No momento a API expõe o `AnexoSerializer` com campos descritivos; se precisar enviar arquivos via multipart/form-data, verifique se há uma view/endpoint custom que aceite uploads (caso contrário, envie metadados e armazene os arquivos externamente).

Exemplo básico usando FormData:

```javascript
const fd = new FormData()
fd.append('criado_por', 1)
fd.append('object_id', 123)
fd.append('content_type', 7) // id do ContentType
fd.append('arquivo', fileInput.files[0]) // se houver suporte de upload

fetch('http://localhost:8000/api/anexos/', {
  method: 'POST',
  body: fd,
  // não setar Content-Type, o browser define boundary
})
.then(r => r.json())
.then(d => console.log(d))
```

## Convenções e dicas

- Todas as rotas seguem o padrão REST do `DefaultRouter` do DRF. Para recursos listados acima, as URLs base são `/api/<recurso>/` e `/api/<recurso>/{id}/`.
- Filtros, paginação e ordenação podem ser habilitados no backend. Atualmente os ViewSets definem `queryset` com ordenação padrão.
- Campos read-only: muitos serializers incluem campos de leitura como `created_at`, `updated_at`, e campos derivados (ex.: `cliente_nome`, `peca_codigo`). Não envie esses campos no POST/PUT.
- Para listar relações, envie apenas os IDs das entidades relacionadas (ex.: `cliente: 3`, `peca: 12`).
