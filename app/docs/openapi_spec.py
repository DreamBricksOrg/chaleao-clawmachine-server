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
                "tags": ["qr"],
                "summary": "Gera um id e a url do formulário associado",
                "responses": {
                    "200": {
                        "description": "Id e url gerados",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/QrIdResponse"}
                            }
                        },
                    }
                },
            }
        },
        "/start/{user_id}": {
            "get": {
                "tags": ["qr"],
                "summary": "Consulta o status de um usuário pelo id",
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
                        "description": "Status do usuário (ou 'inactive' se não encontrado)",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/StatusResponse"}
                            }
                        },
                    }
                },
            }
        },
    },
    "components": {
        "schemas": {
            "UserStatus": {
                "type": "string",
                "enum": ["active", "form", "play", "complete"],
            },
            "User": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "name": {"type": "string", "nullable": True},
                    "email": {"type": "string", "nullable": True},
                    "cpf": {"type": "string", "nullable": True},
                    "status": {"$ref": "#/components/schemas/UserStatus"},
                    "created_at": {"type": "string", "format": "date-time"},
                },
            },
            "CreateUserRequest": {
                "type": "object",
                "required": ["name", "email", "cpf"],
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "cpf": {"type": "string"},
                    "status": {"$ref": "#/components/schemas/UserStatus"},
                },
            },
            "UpdateUserRequest": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "cpf": {"type": "string"},
                    "status": {"$ref": "#/components/schemas/UserStatus"},
                },
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {"error": {"type": "string"}},
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
