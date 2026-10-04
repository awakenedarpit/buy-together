# Security Architecture & Policies

## Project: Buy Together
**Security Level**: High / Production-Ready Standards  
**Audience**: Developers, Auditors, AI Agents  

---

## 1. Threat Model & Defense In Depth

| Threat Vector | Potential Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Credential Theft / Password Leak** | Unauthorized account takeover | Passwords hashed with bcrypt (work factor 12). Plaintext never stored or logged. |
| **JWT Tampering / Forgery** | Privilege escalation | HMAC-SHA256 signature verified using secure `JWT_SECRET`. Expiration checked on every request. |
| **Insecure Direct Object Reference (IDOR)** | Member modifies/deletes another member's requests | Service layer strictly enforces `item.user_id == current_user.id`. |
| **Privilege Escalation** | Regular member accesses manager routes | Role-based dependency (`require_manager`) validates `role == 'MANAGER'`. |
| **SQL Injection** | Data leak or database corruption | SQLAlchemy ORM parameterized queries exclusively; no raw concatenated SQL strings. |
| **Cross-Site Scripting (XSS)** | Session hijacking | React auto-escapes rendered text; Pydantic sanitizes input strings. |
| **Prompt Injection / AI Poisoning** | Model outputs malicious JSON | Model output is treated as untrusted; validated via Pydantic; zero direct DB or shell execution. |
| **Information Leakage** | Attackers probe internal stack traces | Global exception handler masks unhandled 500 errors. |

---

## 2. Authentication & Credential Security

1. **Password Storage**:
   - Uses `bcrypt` with automated salting.
   - Minimum password length: 8 characters.
2. **JWT Tokens**:
   - Cryptographic signature: `HS256` (or `RS256` in enterprise deployments).
   - Standard claims: `sub` (User ID), `role`, `exp` (default 24 hours), `iat`.
   - Revocation: Expired tokens rejected immediately; client removes token on logout.

---

## 3. Role-Based Access Control (RBAC)

Two primary roles exist:
1. `MEMBER`:
   - Can submit messages and create requests.
   - Can read, update, and delete **only their own** request items.
   - Forbidden from accessing manager routes (`/api/v1/manager/*`).
2. `MANAGER`:
   - Possesses all `MEMBER` capabilities.
   - Can inspect all member requests across the group.
   - Can enter, modify, and batch-update unit prices.
   - Can transition request statuses (`PENDING`, `APPROVED`, `PURCHASED`, `REJECTED`).

---

## 4. Object Ownership Validation (IDOR Prevention)

Every item modification or deletion request validates ownership before performing mutations:

```python
# Ownership verification pattern
async def update_member_request(
    db: AsyncSession, 
    item_id: int, 
    user_id: int, 
    update_data: RequestItemUpdate
) -> RequestItem:
    item = await db.get(RequestItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Request item not found")
    if item.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden: You cannot modify another member's request")
    
    # Apply updates...
```

---

## 5. Secret Management

1. **Zero Secrets in Git**:
   - `.env` is explicitly listed in `.gitignore`.
   - `.env.example` contains only non-secret placeholders and documentation.
2. **Environment Variable Injection**:
   - Configuration is validated at runtime using `pydantic-settings`.
   - If `JWT_SECRET` is unset or set to an insecure default in production, application startup aborts immediately.

---

## 6. Safe Error Responses

In production mode:
- Standardized error format: `{"detail": "Error description"}`.
- Unhandled exceptions trigger structured log entries on the server with stack traces, but client receives only:
  ```json
  {
    "detail": "An internal server error occurred. Please contact the administrator."
  }
  ```
