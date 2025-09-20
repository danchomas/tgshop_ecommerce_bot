# Проверка прав администратора
import os

# Сервис аутентификации пользователей
class AuthService:
    def __init__(self, user_id):
        self.user_id = str(user_id)

    # Проверка является ли пользователь администратором
    async def isAdmin(self):
        admin_id = os.getenv("ADMIN_ID")
        if admin_id and self.user_id == str(admin_id):
            return True
        return False
