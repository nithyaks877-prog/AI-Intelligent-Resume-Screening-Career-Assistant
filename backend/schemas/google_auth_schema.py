from pydantic import BaseModel


class GoogleLoginRequest(BaseModel):
    credential: str          # the ID token from Google's sign-in button
    role: str = "student"    # used only if this is a brand-new account
