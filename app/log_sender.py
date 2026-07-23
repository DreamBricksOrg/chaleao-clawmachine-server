import asyncio
import os
import sys
import threading
import types

# O pacote logcenter_sdk importa, no __init__, o middleware ASGI
# (LogCenterAuditMiddleware), que depende de starlette/uvicorn e não é usado
# em Flask. Registramos um stub do submódulo para evitar arrastar a stack ASGI.
if "logcenter_sdk.middleware" not in sys.modules:
    _stub = types.ModuleType("logcenter_sdk.middleware")
    setattr(_stub, "LogCenterAuditMiddleware", None)
    sys.modules["logcenter_sdk.middleware"] = _stub

from logcenter_sdk import LogCenterConfig, LogCenterSender

config = LogCenterConfig(
    base_url=os.getenv("LOG_API", "").rstrip("/"),
    project_id=os.getenv("LOG_PROJECT_ID", ""),
    api_key=os.getenv("LOG_API_KEY"),
    enabled=bool(os.getenv("LOG_API") and os.getenv("LOG_PROJECT_ID")),
    # flush_batch_size=1: o flush_spool do SDK remove o lote inteiro do arquivo
    # antes de enviar e, na 1ª falha, só re-enfileira o item corrente — perdendo
    # o resto do lote. Com lote de 1, falha mantém exatamente esse item no spool.
    flush_batch_size=1,
)

sender = LogCenterSender(config)


# O SDK envia o header de autenticação como "x_api_key" (underscore), mas o
# servidor LogCenter espera "x-api-key" (hífen) e retorna 401 "Missing API key"
# caso contrário. Sobrescrevemos headers() do client para usar o nome correto.
def _auth_headers():
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    if config.api_key:
        headers["x-api-key"] = config.api_key
    return headers


sender.http.headers = _auth_headers


def log(message, *, level="INFO", status=None, tags=None, data=None):
    """Envio síncrono de log (usa asyncio.run internamente).

    O SDK tenta enviar ao servidor primeiro; só grava no spool se o envio
    falhar. O reenvio do spool é feito pelo worker em background (start_flush_worker).
    """
    sender.send_sync(level, message, status=status, tags=tags, data=data)


_flush_thread = None
_flush_lock = threading.Lock()


def _flush_loop():
    # Loop próprio, com seu event loop, tentando subir o spool para o servidor.
    # flush_spool() reenvia em lotes e remove do spool os itens confirmados;
    # em caso de falha, recoloca no spool e tenta de novo no próximo ciclo.
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        try:
            # max_batches alto + flush_batch_size=1: drena o spool item a item,
            # parando na primeira falha (mantém os pendentes no arquivo).
            loop.run_until_complete(sender.flush_spool(max_batches=10000))
        except Exception:
            pass
        loop.run_until_complete(asyncio.sleep(config.flush_interval_s))


def start_flush_worker():
    """Sobe o robô de flush em uma thread daemon (idempotente)."""
    global _flush_thread
    if not config.enabled:
        return
    with _flush_lock:
        if _flush_thread is not None and _flush_thread.is_alive():
            return
        _flush_thread = threading.Thread(
            target=_flush_loop, name="logcenter-flush", daemon=True
        )
        _flush_thread.start()
