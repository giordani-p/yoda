"""Módulo `conversations`: conversas, mensagens, histórico e paginação.

Interface pública: somente o que é exportado aqui pode ser usado fora do módulo.
"""

from app.modules.conversations.router import router

__all__ = ["router"]
