import jwt
from config import settings


class VerifyToken():
    def __init__(self, token, permissions=None, scopes=None):
        self.settings = settings
        self.token = token
        self.permissions = permissions
        self.scopes = scopes

        jwks_url = f'https://{self.settings.auth0_domain}/.well-known/jwks.json'

        self.jwks_client = jwt.PyJWKClient(jwks_url)

    def verify(self):
        # This gets the 'kid' from the passed token
        try:
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(
                self.token
            ).key
        except jwt.exceptions.PyJWKClientError as error:
            return {"status": "error", "msg": error.__str__()}
        except jwt.exceptions.DecodeError as error:
            return {"status": "error", "msg": error.__str__()}

        try:
            payload = jwt.decode(
                self.token,
                self.signing_key,
                algorithms=self.settings.auth0_algorithms,
                audience=self.settings.auth0_api_audience,
                issuer=self.settings.auth0_issuer,
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}

        return payload
