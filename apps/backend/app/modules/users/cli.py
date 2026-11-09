"""Comando de terminal para criar usuários. Uso: `make create-user`.

Não existe cadastro pela API: o usuário é criado por quem tem acesso ao servidor.
"""

import argparse
import asyncio
import getpass
import sys

from app.core.exceptions import AppError
from app.modules.users.repository import UserRepository
from app.modules.users.service import MIN_PASSWORD_LENGTH, UserService
from app.shared.database import SessionLocal, engine

_MESSAGES = {
    "EMAIL_ALREADY_REGISTERED": "Já existe um usuário com este e-mail.",
    "INVALID_USER_DATA": (
        f"Informe um e-mail válido, um nome e uma senha com pelo menos "
        f"{MIN_PASSWORD_LENGTH} caracteres."
    ),
}


async def _create_user(email: str, name: str, password: str) -> None:
    try:
        async with SessionLocal() as session:
            user = await UserService(UserRepository(session)).create_user(email, name, password)
            print(f"Usuário criado: {user.email}")
    finally:
        await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria um usuário do Yoda.")
    parser.add_argument("--email", help="E-mail usado no login.")
    parser.add_argument("--name", help="Nome exibido na interface.")
    args = parser.parse_args()

    email = args.email or input("E-mail: ")
    name = args.name or input("Nome: ")
    # A senha é sempre pedida de forma interativa, para não ficar no histórico do terminal.
    password = getpass.getpass("Senha: ")
    if getpass.getpass("Confirme a senha: ") != password:
        sys.exit("As senhas não conferem.")

    try:
        asyncio.run(_create_user(email, name, password))
    except AppError as error:
        sys.exit(_MESSAGES.get(error.code, "Não foi possível criar o usuário."))


if __name__ == "__main__":
    main()
