import os
from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

# Load configurations from our hidden .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

cipher = Fernet(ENCRYPTION_KEY.encode())

def encrypt_data(plain_text: str) -> bytes:
    """Converts sensitive text into secure encrypted bytes before hitting Postgres."""
    return cipher.encrypt(plain_text.encode('utf-8'))

def decrypt_data(encrypted_bytes: bytes) -> str:
    """Decrypted database bytes back into raw clear text."""
    return cipher.decrypt(encrypted_bytes).decode('utf-8')

engine = create_async_engine(DATABASE_URL, echo=False, pool_size=20, max_overflow=10)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
