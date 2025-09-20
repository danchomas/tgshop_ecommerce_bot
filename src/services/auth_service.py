import os

class AuthService:
    def __init__(self, user_id):
        self.user_id = user_id

    async def isAdmin(self):
        admin_id = os.getenv("ADMIN_ID")
        if admin_id and str(self.user_id) == str(admin_id):
            return True
        return False
