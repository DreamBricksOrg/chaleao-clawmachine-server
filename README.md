# Chaleao Clawmachine Server

Template Flask aplicando Domain-Driven Design (DDD).

## Organização

Pastas organizadas por domínio. Cada domínio (ex: `user`) concentra sua
entidade, repositório, serviço e controller:

- `app/user/user_entity.py`: entidade `User` e o enum `UserStatus`.
- `app/user/user_repository.py`: acesso a dados (MongoDB).
- `app/user/user_service.py`: regras de aplicação (CRUD).
- `app/user/user_controller.py`: rotas HTTP (Flask Blueprint).
- `app/db/mongo.py`: conexão com o MongoDB, compartilhada entre domínios.

## Rodando localmente

1. Suba um MongoDB local (ex: `docker run -d -p 27017:27017 mongo`).
2. Copie `.env.example` para `.env` e ajuste se necessário.
3. Instale as dependências: `pip install -r requirements.txt`
4. Rode a aplicação: `python main.py`

## Endpoints (`/users`)

| Método | Rota          | Descrição       |
|--------|---------------|-----------------|
| POST   | `/users`      | Cria usuário    |
| GET    | `/users/<id>` | Busca por id    |
| GET    | `/users`      | Lista todos     |
| PUT    | `/users/<id>` | Atualiza (sem delete implementado) |

Exemplo:

```bash
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Ana", "email": "ana@example.com", "cpf": "11122233344"}'
```

## Próximos passos

- Adicionar testes automatizados (unitários para domínio/use cases,
  integração para rotas).
- Autenticação/autorização.
- Paginação na listagem de usuários.
