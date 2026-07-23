OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Chaleao Clawmachine Server API",
        "description": "Template Flask aplicando DDD por domínio (user, qr).",
        "version": "1.0.0",
    },
    "paths": {
        "/users": {
            "post": {
                "tags": ["users"],
                "summary": "Cria um usuário",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/CreateUserRequest"}
                        }
                    },
                },
                "responses": {
                    "201": {
                        "description": "Usuário criado",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/User"}
                            }
                        },
                    },
                    "400": {
                        "description": "Dados inválidos",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    },
                },
            },
            "get": {
                "tags": ["users"],
                "summary": "Lista todos os usuários",
                "responses": {
                    "200": {
                        "description": "Lista de usuários",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/User"},
                                }
                            }
                        },
                    }
                },
            },
        },
        "/users/{user_id}": {
            "get": {
                "tags": ["users"],
                "summary": "Busca um usuário por id",
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Usuário encontrado",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/User"}
                            }
                        },
                    },
                    "404": {
                        "description": "Usuário não encontrado",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    },
                },
            },
            "put": {
                "tags": ["users"],
                "summary": "Atualiza um usuário (parcial)",
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/UpdateUserRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Usuário atualizado",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/User"}
                            }
                        },
                    },
                    "400": {
                        "description": "Dados inválidos",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    },
                    "404": {
                        "description": "Usuário não encontrado",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    },
                },
            },
        },
        "/api/qrid": {
            "get": {
                "tags": ["totem"],
                "summary": "Abre uma sessão de totem e retorna o id da sessão + url do formulário",
                "description": (
                    "O id retornado é um id de sessão do totem (não um usuário). O totem "
                    "usa esse mesmo id em /start, /play e /matchresult; o servidor resolve "
                    "qual usuário está por trás quando o celular conecta."
                ),
                "responses": {
                    "200": {
                        "description": "Id da sessão e url gerados",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/QrIdResponse"}
                            }
                        },
                    }
                },
            }
        },
        "/api/start/{session_id}": {
            "get": {
                "tags": ["totem"],
                "summary": "Polling do totem: 'active' quando algum usuário conecta à sessão",
                "parameters": [
                    {
                        "name": "session_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Id da sessão (o mesmo uuid do QR)",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "'active' se há usuário vinculado, senão 'inactive'",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/StatusResponse"}
                            }
                        },
                    }
                },
            }
        },
        "/api/play/{session_id}": {
            "get": {
                "tags": ["totem"],
                "summary": "Polling do totem: 'form' quando a sessão está pronta para jogar",
                "parameters": [
                    {
                        "name": "session_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Id da sessão (o mesmo uuid do QR)",
                    }
                ],
                "responses": {
                    "200": {
                        "description": (
                            "'form' quando pronto para jogar (cadastro concluído ou "
                            "retornante elegível); senão o status atual ou 'inactive'"
                        ),
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/StatusResponse"}
                            }
                        },
                    }
                },
            }
        },
        "/api/matchresult": {
            "post": {
                "tags": ["totem"],
                "summary": "Registra o resultado da partida (id = id da sessão do totem)",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/MatchResultRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Usuário atualizado com o resultado da partida",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/User"}
                            }
                        },
                    },
                    "400": {
                        "description": "Resultado inválido (deve ser 'win' ou 'lose')",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    },
                    "404": {
                        "description": "Usuário não encontrado",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    },
                },
            }
        },
        "/pages/form/{user_id}/complete": {
            "post": {
                "tags": ["pages"],
                "summary": "Conclui o cadastro do formulário (name, email, phone criptografados + email_hash)",
                "description": (
                    "Se o email_hash já pertencer a outro usuário, não sobrescreve o usuário "
                    "atual: verifica o cooldown de 12h desse usuário existente e, se elegível, "
                    "marca-o como play_again; caso contrário, direciona para play_error. "
                    "Se for um email novo, atualiza o usuário atual (status vira form). "
                    "Em qualquer sucesso, define o cookie 'user_id' e retorna a URL de redirecionamento."
                ),
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/CompleteFormRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Redirecionamento a seguir (/continue ou /play_error)",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/RedirectResponse"}
                            }
                        },
                    },
                    "400": {
                        "description": "Dados inválidos ou campos ausentes",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    },
                    "404": {
                        "description": "Usuário não encontrado",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    },
                },
            }
        },
    },
    "components": {
        "schemas": {
            "UserStatus": {
                "type": "string",
                "enum": ["active", "form", "play", "complete", "play_again"],
            },
            "User": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "name": {"type": "string", "nullable": True},
                    "email": {"type": "string", "nullable": True},
                    "email_hash": {"type": "string", "nullable": True},
                    "phone": {"type": "string", "nullable": True},
                    "status": {"$ref": "#/components/schemas/UserStatus"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "last_plays": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "played_at": {"type": "string", "format": "date-time"},
                                "won": {"type": "boolean", "nullable": True},
                            },
                        },
                    },
                },
            },
            "MatchResultRequest": {
                "type": "object",
                "required": ["id", "result"],
                "properties": {
                    "id": {"type": "string", "description": "Id da sessão do totem (uuid do QR)"},
                    "result": {"type": "string", "enum": ["win", "lose"]},
                },
            },
            "CreateUserRequest": {
                "type": "object",
                "required": ["name", "email", "phone"],
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone": {"type": "string"},
                    "status": {"$ref": "#/components/schemas/UserStatus"},
                },
            },
            "UpdateUserRequest": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "email_hash": {"type": "string"},
                    "phone": {"type": "string"},
                    "status": {"$ref": "#/components/schemas/UserStatus"},
                },
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {"error": {"type": "string"}},
            },
            "CompleteFormRequest": {
                "type": "object",
                "required": ["name", "email", "email_hash", "phone"],
                "properties": {
                    "name": {"type": "string", "description": "Nome criptografado"},
                    "email": {"type": "string", "description": "Email criptografado"},
                    "email_hash": {"type": "string", "description": "SHA-256 do email em texto puro"},
                    "phone": {"type": "string", "description": "Telefone criptografado"},
                },
            },
            "RedirectResponse": {
                "type": "object",
                "properties": {"redirect": {"type": "string"}},
            },
            "QrIdResponse": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "url": {"type": "string", "format": "uri"},
                },
            },
            "StatusResponse": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["active", "form", "play", "complete", "inactive"],
                    }
                },
            },
        }
    },
}
