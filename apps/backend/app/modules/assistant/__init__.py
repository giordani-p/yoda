"""Módulo `assistant`: orquestração conversacional e integração com o LLM.

Interface pública: somente o que é exportado aqui pode ser usado fora do módulo.
"""

from app.modules.assistant.router import router

__all__ = ["router"]
