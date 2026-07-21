# Template Flask com DDD — Design

Data: 2026-07-21

## Objetivo

Criar um template simples de aplicação Flask aplicando Domain-Driven Design (DDD),
com uma entidade de exemplo `User` implementada ponta a ponta (rota -> use case ->
domínio -> repositório), servindo como esqueleto de referência para futuros
projetos/módulos.

## Escopo

- Entidade `User`: `id (uuid)`, `name`, `email`, `cpf`, `status`.
- `status` é um Enum: `active`, `form`, `play`, `complete`.
- CRUD básico **sem delete** (create, get by id, list, update).
- Persistência em MongoDB via PyMongo.
- Validação de entrada via Pydantic.
- Rotas Flask organizadas com Blueprint.
- Sem testes automatizados neste escopo (fica como próximo passo sugerido no README).

## Arquitetura

Fluxo de dependência: `interface` -> `application` -> `domain` <- `infrastructure`.
O domínio não depende de nada externo; a infraestrutura implementa as interfaces
definidas pelo domínio; a camada de interface (HTTP) depende da camada de
aplicação (use cases), nunca diretamente da infraestrutura.

```
app/
  domain/
    entities/user.py                    # Entidade User
    value_objects/user_status.py        # Enum UserStatus
    repositories/user_repository.py     # Interface abstrata (ABC)
  application/
    dto/user_dto.py                     # CreateUserDTO, UpdateUserDTO, UserResponseDTO (Pydantic)
    use_cases/
      create_user.py
      get_user.py
      list_users.py
      update_user.py
  infrastructure/
    db/mongo.py                         # Conexão PyMongo
    repositories/mongo_user_repository.py  # Implementa UserRepository
  interface/
    http/
      users/
        routes.py                       # Blueprint '/users'
  config.py                             # Config lida de variáveis de ambiente
  __init__.py                           # App factory: monta conexão, repo, use cases, registra blueprint
main.py                                 # Entrypoint (create_app().run())
requirements.txt
.env.example
README.md
```

## Camada de domínio

- **`User`** (entidade): construtor valida invariantes mínimas (campos
  obrigatórios não vazios). Método `update(name=None, email=None, cpf=None,
  status=None)` aplica atualização parcial mantendo os valores atuais quando
  não informado.
- **`UserStatus`** (Enum): `ACTIVE`, `FORM`, `PLAY`, `COMPLETE`.
- **`UserRepository`** (ABC): `add(user)`, `get_by_id(id) -> User | None`,
  `list_all() -> list[User]`, `update(user)`.

## Camada de aplicação

- **DTOs Pydantic**:
  - `CreateUserDTO`: name, email, cpf, status (opcional, default `active`).
  - `UpdateUserDTO`: todos os campos opcionais.
  - `UserResponseDTO`: serialização de saída.
- **Use cases** (recebem o repositório via injeção no construtor, sem
  dependência de Flask):
  - `CreateUserUseCase`
  - `GetUserUseCase`
  - `ListUsersUseCase`
  - `UpdateUserUseCase`

## Camada de infraestrutura

- **`mongo.py`**: conexão PyMongo lida de `MONGO_URI` / `MONGO_DB_NAME`
  (variáveis de ambiente via `python-dotenv`), expõe a collection `users`.
- **`MongoUserRepository`**: implementa `UserRepository`, convertendo entre
  documento Mongo (`_id` como string do UUID) e a entidade `User`.

## Camada de interface (HTTP)

Blueprint `users_bp`, prefixo `/users`:

| Método | Rota          | Ação                     | Respostas       |
|--------|---------------|--------------------------|-----------------|
| POST   | `/users`      | Cria usuário             | 201, 400        |
| GET    | `/users/<id>` | Busca por id             | 200, 404        |
| GET    | `/users`      | Lista todos              | 200             |
| PUT    | `/users/<id>` | Atualiza (parcial)       | 200, 400, 404   |

Sem rota de delete, conforme solicitado.

Erros de validação Pydantic retornam 400 com detalhes do erro; usuário não
encontrado retorna 404.

## Config / entrypoint

- `config.py`: classe `Config` lendo `MONGO_URI` e `MONGO_DB_NAME`.
- `app/__init__.py`: `create_app()` monta conexão Mongo, repositório
  concreto, injeta nos use cases e registra o blueprint.
- `main.py`: chama `create_app()` e roda `app.run()`.
- `requirements.txt`: `flask`, `pymongo`, `pydantic`, `python-dotenv`.
- `.env.example`: `MONGO_URI=mongodb://localhost:27017`,
  `MONGO_DB_NAME=clawmachine`.

## Próximos passos (fora de escopo)

- Testes automatizados (unitários para use cases/domínio, integração para
  rotas).
- Autenticação/autorização.
- Paginação na listagem de usuários.
