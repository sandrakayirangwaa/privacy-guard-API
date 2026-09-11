from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, LargeBinary
from app.database import Base

class TokenVault(Base):
    __tablename__ = "token_vault"

    token_id = Column(String, primary_key=True, index=True)
    encrypted_value = Column(LargeBinary, nullable=False)
    entity_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
