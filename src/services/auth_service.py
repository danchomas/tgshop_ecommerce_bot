import os

class AuthService:
    def __init__(self, user_id):
        self.user_id = user_id

    async def isAdmin(self):
        if self.user_id == os.getenv("ADMIN_ID"):
            return True
        return False
