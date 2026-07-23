import atexit
import signal
import sys

from app import create_app
from app.log_sender import log, start_flush_worker

app = create_app()

# Robô de flush: tenta subir o spool para o servidor e remove os enviados.
start_flush_worker()

_shutdown_logged = False


def _log_shutdown():
    global _shutdown_logged
    if _shutdown_logged:
        return
    _shutdown_logged = True
    log("Servidor encerrado", level="DEBUG", tags=["server_shutdown"])


atexit.register(_log_shutdown)


def _handle_signal(signum, _frame):
    # docker stop envia SIGTERM: atexit não roda sozinho nesse caso.
    _log_shutdown()
    sys.exit(0)


signal.signal(signal.SIGTERM, _handle_signal)
signal.signal(signal.SIGINT, _handle_signal)


if __name__ == "__main__":
    log("Servidor iniciado", level="DEBUG", tags=["server_startup"])
    app.run(host="0.0.0.0", debug=True)
