from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import engine, Base, get_db, encrypt_data, decrypt_data
from app.models import TokenVault
from app.schemas import SanitizeRequest, SanitizeResponse, DesanitizeRequest, DesanitizeResponse
from app.engine import mask_text

app = FastAPI(title="The Personal Privacy Guard API", version="1.0.0")

# 1. DATABASE TABLE INITIALIZATION
# This event runs automatically when the API starts up to ensure tables exist in Postgres
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        # Automatically creates the 'token_vault' table if it doesn't exist
        await conn.run_sync(Base.metadata.create_all)

# 2. SANITIZE ENDPOINT (Masks, Encrypts, & Saves to Postgres)
@app.post("/sanitize", response_model=SanitizeResponse, status_code=status.HTTP_201_CREATED)
async def sanitize_payload(payload: SanitizeRequest, db: AsyncSession = Depends(get_db)):
    raw_text = payload.text
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Text payload cannot be empty.")
        
    # Execute high-speed regex parsing
    sanitized_text, tokens_found = mask_text(raw_text)
    
    # Securely encrypt and save each found token to the PostgreSQL Vault
    for token_id, (real_value, entity_type) in tokens_found.items():
        encrypted_bytes = encrypt_data(real_value)
        
        db_entry = TokenVault(
            token_id=token_id,
            encrypted_value=encrypted_bytes,
            entity_type=entity_type
        )
        db.add(db_entry)
        
    # Commit changes asynchronously to keep processing lightning-fast
    if tokens_found:
        await db.commit()
        
    return SanitizeResponse(
        original_text=raw_text,
        sanitized_text=sanitized_text
    )

# 3. DESANITIZE ENDPOINT (Looks up, Decrypts, & Restores Text)
@app.post("/desanitize", response_model=DesanitizeResponse)
async def desanitize_payload(payload: DesanitizeRequest, db: AsyncSession = Depends(get_db)):
    masked_text = payload.text
    restored_text = masked_text
    
    # Query your entire secure vault from Postgres to match tokens
    result = await db.execute(select(TokenVault))
    vault_entries = result.scalars().all()
    
    # Iterate and swap any matching placeholder back to clear text
    for entry in vault_entries:
        if entry.token_id in restored_text:
            # Decrypt the binary block on the fly using our secure key
            real_clear_value = decrypt_data(entry.encrypted_value)
            restored_text = restored_text.replace(entry.token_id, real_clear_value)
            
    return DesanitizeResponse(restored_text=restored_text)
