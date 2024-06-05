import uuid
from dataclasses import dataclass

import requests
from pydantic import AnyHttpUrl


@dataclass
class AuthAPI:
    auth_url: AnyHttpUrl
    api_path: str = "auth/check"

    def check_role(self, public_user_id: uuid.UUID, token: str) -> bool:
        try:
            result = requests.get(
                url=f"{self.auth_url}{self.api_path}",
                params={"public_user_id": public_user_id, "token": token},
            )
        except Exception as e:
            print(e)
        else:
            if result.status_code == 200:
                return True
        return False
