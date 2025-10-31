from cryptography.fernet import Fernet
from app.config import settings
from app.utils.logger import logger

class EncryptionService:
    def __init__(self):
        try:
            self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            raise
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        try:
            return self.cipher.encrypt(data.encode()).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt encrypted string"""
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def encrypt_api_key(self, api_key: str) -> str:
        """Encrypt API key for storage"""
        return self.encrypt(api_key)
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt API key for use"""
        return self.decrypt(encrypted_key)

encryption_service = EncryptionService()

