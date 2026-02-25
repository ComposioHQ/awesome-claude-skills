---
name: auth-implementation
description: Expert guidance for implementing secure authentication systems including OAuth 2.0, SAML, OIDC, JWT, passwordless authentication, passkeys, and biometrics. Covers protocol selection, security best practices, common pitfalls at scale, and enterprise patterns. Use when implementing login flows, SSO, API authentication, machine identity, or any identity management features.
---

# Auth Implementation

Expert guidance for implementing production-grade authentication systems based on patterns proven at billion-user scale. This skill helps you choose the right authentication approach, implement it securely, and avoid common pitfalls that cause security vulnerabilities or scale issues.

## When to Use This Skill

Use this skill when you need to:
- Implement user authentication (login, signup, password reset)
- Add Single Sign-On (SSO) capabilities
- Secure APIs with proper authentication
- Migrate from passwords to passwordless authentication
- Implement machine identity for AI agents or services
- Design multi-tenant authentication architecture
- Handle session management and token lifecycle
- Meet enterprise security and compliance requirements

## Protocol Selection Framework

### Decision Matrix

Choose your authentication protocol based on these factors:

**OAuth 2.0 + OIDC (OpenID Connect)**
- **Use when**: Third-party integrations, social login, mobile apps, microservices
- **Best for**: Consumer applications, delegated authorization, API access
- **Complexity**: Medium to High
- **Scale characteristics**: Excellent (stateless with JWT)
- **Common flows**: Authorization Code, PKCE, Client Credentials

**SAML 2.0**
- **Use when**: Enterprise B2B integrations, existing IdP infrastructure
- **Best for**: Enterprise SSO, compliance requirements, legacy systems
- **Complexity**: High
- **Scale characteristics**: Good (but XML parsing overhead)
- **Common patterns**: SP-initiated, IdP-initiated flows

**JWT (JSON Web Tokens)**
- **Use when**: Stateless authentication, microservices, mobile/SPA apps
- **Best for**: API authentication, distributed systems
- **Complexity**: Low to Medium
- **Scale characteristics**: Excellent (no database lookups)
- **Critical**: Proper signing, validation, and expiration handling

**Passwordless (Magic Links, OTP)**
- **Use when**: Improving UX, reducing password fatigue
- **Best for**: Consumer apps, low-friction experiences
- **Complexity**: Medium
- **Scale characteristics**: Very Good (fewer credential databases)
- **Consider**: Email/SMS delivery reliability

**Passkeys (WebAuthn/FIDO2)**
- **Use when**: Maximum security with great UX
- **Best for**: High-security applications, modern browsers
- **Complexity**: Medium to High
- **Scale characteristics**: Excellent (public-key cryptography)
- **Adoption**: Growing rapidly, becoming standard

**API Keys**
- **Use when**: Simple service-to-service authentication
- **Best for**: Internal services, development tools
- **Complexity**: Low
- **Scale characteristics**: Good (but rotation challenges)
- **Warning**: NOT suitable for user authentication or long-term secrets

### Anti-Pattern Alert: Wrong Protocol Choices

**DON'T use Basic Auth for production APIs** - Credentials in every request, no rotation, poor security posture

**DON'T use API keys for user authentication** - No scope control, difficult rotation, creates exponential security debt at scale

**DON'T force human identity patterns on machine identities** - AI agents need service accounts, not user accounts with passwords

**DON'T implement custom crypto** - Use battle-tested libraries and protocols

## Implementation Patterns

### OAuth 2.0 with PKCE (Authorization Code Flow)

This is the gold standard for modern web and mobile applications.

```python
# Server-side OAuth 2.0 implementation pattern
import secrets
import hashlib
import base64
from datetime import datetime, timedelta

class OAuthServer:
    def __init__(self):
        self.auth_codes = {}  # In production: use Redis with TTL
        self.tokens = {}  # In production: use database
    
    def generate_authorization_code(self, client_id, redirect_uri, 
                                   code_challenge, code_challenge_method, scope):
        """Generate authorization code with PKCE support"""
        if code_challenge_method not in ['S256', 'plain']:
            raise ValueError("Invalid code_challenge_method")
        
        # Generate secure authorization code
        auth_code = secrets.token_urlsafe(32)
        
        # Store authorization code with PKCE parameters (5 min TTL)
        self.auth_codes[auth_code] = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'code_challenge': code_challenge,
            'code_challenge_method': code_challenge_method,
            'scope': scope,
            'expires_at': datetime.utcnow() + timedelta(minutes=5),
            'used': False
        }
        
        return auth_code
    
    def verify_code_verifier(self, code_verifier, code_challenge, method):
        """Verify PKCE code verifier against stored challenge"""
        if method == 'S256':
            # Hash the verifier and compare
            computed = base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode()).digest()
            ).decode().rstrip('=')
            return computed == code_challenge
        elif method == 'plain':
            return code_verifier == code_challenge
        return False
    
    def exchange_code_for_token(self, auth_code, code_verifier, client_id):
        """Exchange authorization code for access token"""
        # Retrieve stored authorization code
        code_data = self.auth_codes.get(auth_code)
        
        if not code_data:
            raise ValueError("Invalid authorization code")
        
        # Validate authorization code
        if code_data['used']:
            raise ValueError("Authorization code already used")
        
        if datetime.utcnow() > code_data['expires_at']:
            raise ValueError("Authorization code expired")
        
        if code_data['client_id'] != client_id:
            raise ValueError("Client ID mismatch")
        
        # Verify PKCE code verifier
        if not self.verify_code_verifier(
            code_verifier, 
            code_data['code_challenge'],
            code_data['code_challenge_method']
        ):
            raise ValueError("Invalid code verifier")
        
        # Mark code as used (prevents replay attacks)
        code_data['used'] = True
        
        # Generate tokens
        access_token = self._generate_jwt_token(
            client_id, 
            code_data['scope'],
            expires_in=3600  # 1 hour
        )
        
        refresh_token = secrets.token_urlsafe(64)
        
        # Store refresh token
        self.tokens[refresh_token] = {
            'client_id': client_id,
            'scope': code_data['scope'],
            'expires_at': datetime.utcnow() + timedelta(days=30)
        }
        
        return {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_token': refresh_token,
            'scope': code_data['scope']
        }
    
    def _generate_jwt_token(self, client_id, scope, expires_in):
        """Generate JWT access token (simplified - use PyJWT in production)"""
        # In production: use proper JWT library with RS256 signing
        import jwt
        
        payload = {
            'sub': client_id,
            'scope': scope,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=expires_in)
        }
        
        # CRITICAL: Use RS256 with proper key management
        token = jwt.encode(payload, 'your-secret-key', algorithm='HS256')
        return token
```

**Key Security Points:**
- **Always use PKCE** - Protects against authorization code interception
- **Short-lived auth codes** - 5 minutes maximum
- **One-time use codes** - Mark as used immediately to prevent replay
- **Validate redirect_uri** - Exact match against registered URIs
- **Never reuse refresh tokens** - Rotate on each use (refresh token rotation)

### JWT Token Management

```python
# JWT token validation and management
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

class JWTTokenManager:
    def __init__(self, public_key, private_key):
        self.public_key = public_key  # RS256 public key
        self.private_key = private_key  # RS256 private key
        self.algorithm = 'RS256'  # NEVER use HS256 for production
        self.token_blacklist = set()  # In production: use Redis
    
    def generate_token(self, user_id, scope, token_type='access'):
        """Generate JWT token with proper claims"""
        now = datetime.utcnow()
        
        # Access tokens: short-lived (1 hour)
        # Refresh tokens: longer-lived (30 days) with different audience
        expires_in = 3600 if token_type == 'access' else 2592000
        
        payload = {
            'sub': str(user_id),  # Subject (user ID)
            'iat': now,  # Issued at
            'exp': now + timedelta(seconds=expires_in),  # Expiration
            'nbf': now,  # Not before
            'jti': self._generate_jti(),  # JWT ID for tracking
            'scope': scope,  # Permissions
            'type': token_type,  # Token type
            'iss': 'https://your-domain.com',  # Issuer
            'aud': 'your-api'  # Audience
        }
        
        token = jwt.encode(payload, self.private_key, algorithm=self.algorithm)
        return token
    
    def validate_token(self, token, required_scope=None):
        """Validate JWT token with comprehensive checks"""
        try:
            # Decode and verify token
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm],
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_nbf': True,
                    'verify_iat': True,
                    'verify_aud': True,
                    'verify_iss': True
                },
                audience='your-api',
                issuer='https://your-domain.com'
            )
            
            # Check if token is blacklisted (for logout)
            jti = payload.get('jti')
            if jti in self.token_blacklist:
                raise jwt.InvalidTokenError("Token has been revoked")
            
            # Verify required scope if specified
            if required_scope:
                token_scopes = payload.get('scope', '').split()
                if required_scope not in token_scopes:
                    raise jwt.InvalidTokenError("Insufficient scope")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {str(e)}")
    
    def revoke_token(self, token):
        """Revoke token by adding to blacklist"""
        try:
            # Decode without verification to get jti
            payload = jwt.decode(token, options={"verify_signature": False})
            jti = payload.get('jti')
            
            if jti:
                # Add to blacklist with TTL equal to token expiration
                self.token_blacklist.add(jti)
                # In production: Redis SETEX with TTL
                
        except Exception as e:
            raise ValueError(f"Failed to revoke token: {str(e)}")
    
    def _generate_jti(self):
        """Generate unique JWT ID"""
        import secrets
        return secrets.token_urlsafe(16)
    
    def require_auth(self, required_scope=None):
        """Decorator for protecting API endpoints"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Extract token from Authorization header
                auth_header = request.headers.get('Authorization')
                
                if not auth_header:
                    return jsonify({'error': 'Missing authorization header'}), 401
                
                try:
                    scheme, token = auth_header.split()
                    if scheme.lower() != 'bearer':
                        return jsonify({'error': 'Invalid authorization scheme'}), 401
                    
                    # Validate token
                    payload = self.validate_token(token, required_scope)
                    
                    # Add user info to request context
                    request.user_id = payload['sub']
                    request.scopes = payload.get('scope', '').split()
                    
                    return f(*args, **kwargs)
                    
                except ValueError as e:
                    return jsonify({'error': str(e)}), 401
                except Exception as e:
                    return jsonify({'error': 'Authentication failed'}), 401
            
            return decorated_function
        return decorator
```

**Critical JWT Security Rules:**

1. **NEVER use HS256 in production** - Use RS256 with proper key management
2. **Always validate signature** - Verify with public key
3. **Check expiration** - Enforce token expiry strictly
4. **Validate audience and issuer** - Prevent token misuse
5. **Use short expiration times** - 1 hour for access tokens maximum
6. **Don't store sensitive data in JWT** - Tokens are visible to clients
7. **Implement token revocation** - Use blacklist or short TTLs

### Passwordless Authentication (Magic Links)

```python
# Passwordless authentication implementation
import secrets
import hashlib
from datetime import datetime, timedelta

class PasswordlessAuth:
    def __init__(self, email_service):
        self.email_service = email_service
        self.magic_links = {}  # In production: use Redis with TTL
        self.rate_limits = {}  # Rate limiting per email
    
    def initiate_login(self, email):
        """Generate and send magic link"""
        # Rate limiting: max 3 attempts per 10 minutes
        if not self._check_rate_limit(email):
            raise ValueError("Too many login attempts. Please try again later.")
        
        # Generate secure token
        token = secrets.token_urlsafe(32)
        
        # Hash token for storage (don't store plaintext)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Store token data with 15-minute expiration
        self.magic_links[token_hash] = {
            'email': email,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(minutes=15),
            'used': False,
            'ip_address': self._get_client_ip(),  # Track for security
            'user_agent': self._get_user_agent()
        }
        
        # Generate magic link URL
        magic_link = f"https://your-domain.com/auth/verify?token={token}"
        
        # Send email with magic link
        self.email_service.send_magic_link(email, magic_link)
        
        return {'message': 'Magic link sent to your email'}
    
    def verify_magic_link(self, token):
        """Verify magic link token and authenticate user"""
        # Hash the provided token
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Retrieve token data
        token_data = self.magic_links.get(token_hash)
        
        if not token_data:
            raise ValueError("Invalid or expired magic link")
        
        # Validate token
        if token_data['used']:
            raise ValueError("This magic link has already been used")
        
        if datetime.utcnow() > token_data['expires_at']:
            raise ValueError("This magic link has expired")
        
        # Security check: compare IP and user agent
        if not self._verify_request_context(token_data):
            # Log suspicious activity
            self._log_security_event(
                'magic_link_context_mismatch',
                token_data['email']
            )
            raise ValueError("Security validation failed")
        
        # Mark token as used
        token_data['used'] = True
        
        # Create user session
        email = token_data['email']
        user = self._get_or_create_user(email)
        
        # Generate session token
        session_token = self._create_session(user['id'])
        
        return {
            'user': user,
            'session_token': session_token
        }
    
    def _check_rate_limit(self, email):
        """Rate limit magic link requests"""
        now = datetime.utcnow()
        
        if email not in self.rate_limits:
            self.rate_limits[email] = []
        
        # Remove attempts older than 10 minutes
        self.rate_limits[email] = [
            timestamp for timestamp in self.rate_limits[email]
            if now - timestamp < timedelta(minutes=10)
        ]
        
        # Check if under limit (3 attempts per 10 minutes)
        if len(self.rate_limits[email]) >= 3:
            return False
        
        # Add current attempt
        self.rate_limits[email].append(now)
        return True
    
    def _verify_request_context(self, token_data):
        """Verify IP and user agent match (loose check)"""
        # Get current request context
        current_ip = self._get_client_ip()
        current_ua = self._get_user_agent()
        
        # Loose matching: IP prefix and basic UA check
        # Too strict breaks legitimate use (mobile vs desktop)
        ip_match = current_ip.split('.')[0:2] == token_data['ip_address'].split('.')[0:2]
        
        return ip_match  # Be lenient with user agent
    
    def _get_client_ip(self):
        """Get client IP address"""
        # In production: handle X-Forwarded-For properly
        return "127.0.0.1"
    
    def _get_user_agent(self):
        """Get client user agent"""
        return "Mozilla/5.0"
    
    def _get_or_create_user(self, email):
        """Get existing user or create new one"""
        # Implementation depends on your user model
        return {'id': 'user_123', 'email': email}
    
    def _create_session(self, user_id):
        """Create authenticated session"""
        # Implementation depends on your session management
        return secrets.token_urlsafe(32)
    
    def _log_security_event(self, event_type, email):
        """Log security events for monitoring"""
        # In production: send to security monitoring system
        print(f"Security event: {event_type} for {email}")
```

**Passwordless Best Practices:**

1. **Short token expiration** - 10-15 minutes maximum
2. **One-time use tokens** - Mark as used immediately
3. **Hash tokens in storage** - Don't store plaintext
4. **Rate limit requests** - Prevent abuse
5. **Monitor for anomalies** - Track unusual patterns
6. **Validate request context** - Check IP/user agent loosely
7. **Secure email delivery** - Use reputable email service

### Passkeys (WebAuthn) Implementation

```javascript
// Client-side passkey registration
async function registerPasskey(username) {
    try {
        // Request registration options from server
        const optionsResponse = await fetch('/auth/passkey/register-options', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username })
        });
        
        const options = await optionsResponse.json();
        
        // Convert challenge from base64url
        options.publicKey.challenge = base64urlDecode(options.publicKey.challenge);
        options.publicKey.user.id = base64urlDecode(options.publicKey.user.id);
        
        // Create credential
        const credential = await navigator.credentials.create({
            publicKey: options.publicKey
        });
        
        // Prepare credential for server
        const credentialData = {
            id: credential.id,
            rawId: base64urlEncode(credential.rawId),
            type: credential.type,
            response: {
                clientDataJSON: base64urlEncode(credential.response.clientDataJSON),
                attestationObject: base64urlEncode(credential.response.attestationObject)
            }
        };
        
        // Send credential to server
        const registerResponse = await fetch('/auth/passkey/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(credentialData)
        });
        
        const result = await registerResponse.json();
        
        if (result.success) {
            console.log('Passkey registered successfully');
            return result;
        } else {
            throw new Error(result.error);
        }
        
    } catch (error) {
        console.error('Passkey registration failed:', error);
        throw error;
    }
}

// Client-side passkey authentication
async function authenticateWithPasskey(username) {
    try {
        // Request authentication options from server
        const optionsResponse = await fetch('/auth/passkey/auth-options', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username })
        });
        
        const options = await optionsResponse.json();
        
        // Convert challenge from base64url
        options.publicKey.challenge = base64urlDecode(options.publicKey.challenge);
        
        // Get credential
        const credential = await navigator.credentials.get({
            publicKey: options.publicKey
        });
        
        // Prepare credential for server
        const credentialData = {
            id: credential.id,
            rawId: base64urlEncode(credential.rawId),
            type: credential.type,
            response: {
                clientDataJSON: base64urlEncode(credential.response.clientDataJSON),
                authenticatorData: base64urlEncode(credential.response.authenticatorData),
                signature: base64urlEncode(credential.response.signature),
                userHandle: base64urlEncode(credential.response.userHandle)
            }
        };
        
        // Send credential to server for verification
        const authResponse = await fetch('/auth/passkey/authenticate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(credentialData)
        });
        
        const result = await authResponse.json();
        
        if (result.success) {
            console.log('Authentication successful');
            // Store session token
            localStorage.setItem('session_token', result.token);
            return result;
        } else {
            throw new Error(result.error);
        }
        
    } catch (error) {
        console.error('Passkey authentication failed:', error);
        throw error;
    }
}

// Utility functions
function base64urlEncode(buffer) {
    const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)));
    return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}

function base64urlDecode(base64url) {
    const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
    const binary = atob(base64);
    return Uint8Array.from(binary, c => c.charCodeAt(0));
}
```

```python
# Server-side passkey verification (Python with webauthn library)
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json
)
from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor,
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement
)

class PasskeyAuthenticator:
    def __init__(self, rp_id, rp_name):
        self.rp_id = rp_id  # e.g., "example.com"
        self.rp_name = rp_name  # e.g., "Example Corp"
        self.origin = f"https://{rp_id}"
        self.credentials = {}  # In production: use database
        self.challenges = {}  # In production: use Redis with TTL
    
    def generate_registration_options(self, user_id, username, display_name):
        """Generate options for passkey registration"""
        # Create registration options
        options = generate_registration_options(
            rp_id=self.rp_id,
            rp_name=self.rp_name,
            user_id=user_id,
            user_name=username,
            user_display_name=display_name,
            authenticator_selection=AuthenticatorSelectionCriteria(
                user_verification=UserVerificationRequirement.REQUIRED,
                resident_key="preferred"  # Discoverable credentials
            ),
            timeout=60000  # 60 seconds
        )
        
        # Store challenge for verification
        self.challenges[user_id] = options.challenge
        
        return options_to_json(options)
    
    def verify_registration(self, user_id, credential_data):
        """Verify and store passkey registration"""
        # Get stored challenge
        expected_challenge = self.challenges.get(user_id)
        
        if not expected_challenge:
            raise ValueError("No registration challenge found")
        
        try:
            # Verify registration response
            verification = verify_registration_response(
                credential=credential_data,
                expected_challenge=expected_challenge,
                expected_origin=self.origin,
                expected_rp_id=self.rp_id
            )
            
            # Store credential
            credential_id = verification.credential_id
            self.credentials[credential_id] = {
                'user_id': user_id,
                'public_key': verification.credential_public_key,
                'sign_count': verification.sign_count,
                'credential_type': verification.credential_type,
                'created_at': datetime.utcnow()
            }
            
            # Clean up challenge
            del self.challenges[user_id]
            
            return {
                'success': True,
                'credential_id': credential_id
            }
            
        except Exception as e:
            raise ValueError(f"Registration verification failed: {str(e)}")
    
    def generate_authentication_options(self, username=None):
        """Generate options for passkey authentication"""
        # Get user's credentials (if username provided)
        allowed_credentials = []
        if username:
            user_creds = [
                cred for cred in self.credentials.values()
                if cred['user_id'] == username
            ]
            allowed_credentials = [
                PublicKeyCredentialDescriptor(id=cred_id)
                for cred_id, cred in self.credentials.items()
                if cred['user_id'] == username
            ]
        
        # Generate authentication options
        options = generate_authentication_options(
            rp_id=self.rp_id,
            timeout=60000,
            allow_credentials=allowed_credentials,
            user_verification=UserVerificationRequirement.REQUIRED
        )
        
        # Store challenge
        challenge_id = secrets.token_urlsafe(16)
        self.challenges[challenge_id] = options.challenge
        
        options_dict = options_to_json(options)
        options_dict['challenge_id'] = challenge_id
        
        return options_dict
    
    def verify_authentication(self, challenge_id, credential_data):
        """Verify passkey authentication"""
        # Get stored challenge
        expected_challenge = self.challenges.get(challenge_id)
        
        if not expected_challenge:
            raise ValueError("No authentication challenge found")
        
        # Get credential
        credential_id = credential_data.get('id')
        stored_credential = self.credentials.get(credential_id)
        
        if not stored_credential:
            raise ValueError("Unknown credential")
        
        try:
            # Verify authentication response
            verification = verify_authentication_response(
                credential=credential_data,
                expected_challenge=expected_challenge,
                expected_origin=self.origin,
                expected_rp_id=self.rp_id,
                credential_public_key=stored_credential['public_key'],
                credential_current_sign_count=stored_credential['sign_count']
            )
            
            # Update sign count (prevents cloned authenticators)
            stored_credential['sign_count'] = verification.new_sign_count
            
            # Clean up challenge
            del self.challenges[challenge_id]
            
            # Generate session token
            user_id = stored_credential['user_id']
            session_token = self._create_session(user_id)
            
            return {
                'success': True,
                'user_id': user_id,
                'token': session_token
            }
            
        except Exception as e:
            raise ValueError(f"Authentication verification failed: {str(e)}")
    
    def _create_session(self, user_id):
        """Create authenticated session"""
        return secrets.token_urlsafe(32)
```

**Passkey Implementation Best Practices:**

1. **Always require user verification** - PIN, biometric, or device password
2. **Use discoverable credentials** - Better UX (no username needed)
3. **Track sign counter** - Detects cloned authenticators
4. **Implement fallback auth** - Not all devices support passkeys yet
5. **Clear challenges after use** - Prevent replay attacks
6. **Allow multiple passkeys per user** - For different devices
7. **Provide credential management** - Let users add/remove passkeys

## Common Security Pitfalls

### Pitfall #1: Insecure Token Storage

**WRONG:**
```javascript
// Storing tokens in localStorage vulnerable to XSS
localStorage.setItem('access_token', token);

// Including token in URL parameters
window.location = `/dashboard?token=${token}`;
```

**RIGHT:**
```javascript
// Use httpOnly cookies for tokens (protected from XSS)
// Server sets cookie:
response.set_cookie(
    'access_token',
    token,
    httponly=True,
    secure=True,  # HTTPS only
    samesite='Strict',  # CSRF protection
    max_age=3600
)

// For SPAs that need token access, use short-lived tokens
// and refresh mechanism with httpOnly refresh token
```

### Pitfall #2: No Token Expiration or Rotation

**WRONG:**
```python
# Long-lived tokens without expiration
token = generate_token(user_id)  # Never expires
```

**RIGHT:**
```python
# Short-lived access tokens with refresh mechanism
access_token = generate_token(user_id, expires_in=3600)  # 1 hour
refresh_token = generate_refresh_token(user_id, expires_in=2592000)  # 30 days

# Rotate refresh tokens on each use
def refresh_access_token(old_refresh_token):
    # Validate old refresh token
    user_id = validate_refresh_token(old_refresh_token)
    
    # Generate new tokens
    new_access_token = generate_token(user_id, expires_in=3600)
    new_refresh_token = generate_refresh_token(user_id, expires_in=2592000)
    
    # Invalidate old refresh token
    revoke_token(old_refresh_token)
    
    return new_access_token, new_refresh_token
```

### Pitfall #3: Missing Rate Limiting

**WRONG:**
```python
# No rate limiting on authentication endpoints
@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    return authenticate(username, password)
```

**RIGHT:**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Strict limit on login
def login():
    username = request.json['username']
    password = request.json['password']
    
    # Additional: account-level rate limiting
    if is_account_locked(username):
        return {'error': 'Account temporarily locked'}, 429
    
    result = authenticate(username, password)
    
    if not result['success']:
        increment_failed_attempts(username)
    else:
        reset_failed_attempts(username)
    
    return result
```

### Pitfall #4: Weak Session Management

**WRONG:**
```python
# Predictable session IDs
session_id = f"session_{user_id}_{timestamp}"

# Sessions never expire
sessions[session_id] = user_id
```

**RIGHT:**
```python
import secrets
from datetime import datetime, timedelta

class SessionManager:
    def __init__(self):
        self.sessions = {}  # In production: use Redis
    
    def create_session(self, user_id):
        # Generate cryptographically secure session ID
        session_id = secrets.token_urlsafe(32)
        
        self.sessions[session_id] = {
            'user_id': user_id,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(hours=24),
            'last_activity': datetime.utcnow(),
            'ip_address': get_client_ip(),
            'user_agent': get_user_agent()
        }
        
        return session_id
    
    def validate_session(self, session_id):
        session = self.sessions.get(session_id)
        
        if not session:
            return None
        
        # Check expiration
        if datetime.utcnow() > session['expires_at']:
            del self.sessions[session_id]
            return None
        
        # Check for session fixation attacks
        if not self._verify_session_context(session):
            del self.sessions[session_id]
            return None
        
        # Update last activity (sliding expiration)
        session['last_activity'] = datetime.utcnow()
        
        return session['user_id']
    
    def revoke_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]
```

### Pitfall #5: No CSRF Protection

**WRONG:**
```html
<!-- State-changing operations without CSRF tokens -->
<form action="/api/delete-account" method="POST">
    <button type="submit">Delete Account</button>
</form>
```

**RIGHT:**
```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# Generate CSRF token for each session
@app.route('/api/csrf-token')
def get_csrf_token():
    return {'csrf_token': generate_csrf()}

# Validate CSRF token on state-changing operations
@app.route('/api/delete-account', methods=['POST'])
@csrf.exempt  # Use custom validation
def delete_account():
    # Validate CSRF token from header
    csrf_token = request.headers.get('X-CSRF-Token')
    if not validate_csrf_token(csrf_token):
        return {'error': 'Invalid CSRF token'}, 403
    
    # Process request
    return {'success': True}
```

## Machine Identity for AI Agents

AI agents require different authentication patterns than humans. Traditional user-centric identity systems break at machine scale.

### The Machine Identity Challenge

**Problem:** AI agents outnumber humans 100:1 in enterprise systems, but most companies force machine identities through human identity patterns.

**Consequences:**
- Static API keys create exponential security debt
- No automated credential rotation
- Poor audit trails for machine actions
- Credential sprawl across repositories and configs

### Service Account Pattern for AI Agents

```python
class MachineIdentityManager:
    """Manage machine identities for AI agents and services"""
    
    def __init__(self):
        self.service_accounts = {}
        self.credentials = {}
    
    def create_service_account(self, name, description, scopes):
        """Create dedicated service account for AI agent"""
        account_id = f"sa_{secrets.token_urlsafe(16)}"
        
        self.service_accounts[account_id] = {
            'name': name,
            'description': description,
            'scopes': scopes,
            'created_at': datetime.utcnow(),
            'enabled': True,
            'credentials': []
        }
        
        return account_id
    
    def generate_credential(self, account_id, credential_type='jwt'):
        """Generate time-limited credential for service account"""
        account = self.service_accounts.get(account_id)
        
        if not account or not account['enabled']:
            raise ValueError("Invalid or disabled service account")
        
        if credential_type == 'jwt':
            # Generate JWT with service account claims
            credential = self._generate_service_jwt(
                account_id,
                account['scopes'],
                expires_in=86400  # 24 hours
            )
        elif credential_type == 'rotating_secret':
            # Generate rotating secret (e.g., for legacy integrations)
            credential = self._generate_rotating_secret(account_id)
        
        # Track credential for rotation
        credential_id = secrets.token_urlsafe(16)
        self.credentials[credential_id] = {
            'account_id': account_id,
            'type': credential_type,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(days=1),
            'rotated': False
        }
        
        account['credentials'].append(credential_id)
        
        return credential
    
    def rotate_credential(self, credential_id):
        """Rotate machine credential (zero-downtime)"""
        old_cred = self.credentials.get(credential_id)
        
        if not old_cred:
            raise ValueError("Credential not found")
        
        account_id = old_cred['account_id']
        
        # Generate new credential
        new_credential = self.generate_credential(
            account_id,
            credential_type=old_cred['type']
        )
        
        # Mark old credential as rotated (keep valid for grace period)
        old_cred['rotated'] = True
        old_cred['grace_expires_at'] = datetime.utcnow() + timedelta(hours=1)
        
        return new_credential
    
    def validate_service_credential(self, credential):
        """Validate machine credential"""
        # Parse and validate JWT or rotating secret
        # Check if credential is expired or rotated
        # Return service account ID and scopes
        pass
    
    def _generate_service_jwt(self, account_id, scopes, expires_in):
        """Generate JWT for service account"""
        import jwt
        
        payload = {
            'sub': account_id,
            'type': 'service_account',
            'scopes': scopes,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=expires_in)
        }
        
        return jwt.encode(payload, 'service-account-key', algorithm='RS256')
    
    def _generate_rotating_secret(self, account_id):
        """Generate rotating secret credential"""
        return {
            'client_id': account_id,
            'client_secret': secrets.token_urlsafe(64),
            'expires_in': 86400
        }
```

**Machine Identity Best Practices:**

1. **Dedicated service accounts** - Don't use user accounts for machines
2. **Time-limited credentials** - 24-48 hour maximum, auto-rotate
3. **Scope-based permissions** - Least privilege principle
4. **Audit logging** - Track all machine identity actions
5. **Automated rotation** - Zero-downtime credential updates
6. **Secret management** - Use vault solutions (HashiCorp Vault, AWS Secrets Manager)
7. **Workload identity** - Use cloud provider workload identity when possible

### AI Agent Authentication Pattern

```python
class AIAgentAuthenticator:
    """Authentication specifically designed for AI agents"""
    
    def authenticate_agent(self, agent_id, agent_signature, request_context):
        """Authenticate AI agent with context validation"""
        
        # Verify agent signature (e.g., signed JWT from agent runtime)
        agent_claims = self._verify_agent_signature(agent_signature)
        
        if agent_claims['agent_id'] != agent_id:
            raise ValueError("Agent ID mismatch")
        
        # Validate request context
        if not self._validate_agent_context(agent_claims, request_context):
            raise ValueError("Invalid agent context")
        
        # Check agent authorization
        if not self._is_agent_authorized(agent_id, request_context['action']):
            raise ValueError("Agent not authorized for this action")
        
        # Generate time-limited access token
        access_token = self._generate_agent_token(
            agent_id,
            request_context,
            expires_in=3600
        )
        
        return access_token
    
    def _verify_agent_signature(self, signature):
        """Verify signed claims from AI agent runtime"""
        # Verify signature from trusted agent runtime
        # Extract and validate agent claims
        pass
    
    def _validate_agent_context(self, claims, context):
        """Validate AI agent execution context"""
        # Check agent runtime environment
        # Validate execution parameters
        # Verify workspace/project permissions
        return True
    
    def _is_agent_authorized(self, agent_id, action):
        """Check if agent is authorized for specific action"""
        # Check agent permissions against action
        # Validate scope and resource access
        return True
    
    def _generate_agent_token(self, agent_id, context, expires_in):
        """Generate access token for AI agent"""
        import jwt
        
        payload = {
            'sub': agent_id,
            'type': 'ai_agent',
            'context': context,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=expires_in)
        }
        
        return jwt.encode(payload, 'agent-signing-key', algorithm='RS256')
```

## Enterprise Authentication Requirements

### Single Sign-On (SSO) Implementation

```python
# SAML 2.0 Service Provider implementation
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings

class SAMLAuthenticator:
    """SAML 2.0 Service Provider for Enterprise SSO"""
    
    def __init__(self, settings):
        self.settings = settings
        self.pending_auth = {}  # In production: use Redis
    
    def initiate_sso(self, idp_name, relay_state=None):
        """Initiate SSO login with Identity Provider"""
        # Prepare SAML authentication request
        auth = OneLogin_Saml2_Auth(
            self._prepare_request(),
            self.settings[idp_name]
        )
        
        # Generate authentication request
        sso_url = auth.login(return_to=relay_state)
        
        # Store request ID for validation
        request_id = auth.get_last_request_id()
        self.pending_auth[request_id] = {
            'idp_name': idp_name,
            'created_at': datetime.utcnow(),
            'relay_state': relay_state
        }
        
        return sso_url
    
    def process_sso_response(self, saml_response):
        """Process SAML response from Identity Provider"""
        # Parse SAML response
        auth = OneLogin_Saml2_Auth(
            self._prepare_request(),
            self.settings
        )
        
        auth.process_response()
        
        # Validate response
        errors = auth.get_errors()
        if errors:
            raise ValueError(f"SAML validation failed: {errors}")
        
        if not auth.is_authenticated():
            raise ValueError("Authentication failed")
        
        # Extract user attributes
        attributes = auth.get_attributes()
        name_id = auth.get_nameid()
        session_index = auth.get_session_index()
        
        # Get user information
        email = attributes.get('email', [name_id])[0]
        first_name = attributes.get('firstName', [''])[0]
        last_name = attributes.get('lastName', [''])[0]
        groups = attributes.get('groups', [])
        
        # Create or update user
        user = self._get_or_create_user(email, first_name, last_name, groups)
        
        # Create session with SAML context
        session_token = self._create_session(
            user['id'],
            session_index=session_index,
            idp_name=attributes.get('idp', ['unknown'])[0]
        )
        
        return {
            'user': user,
            'session_token': session_token,
            'relay_state': auth.get_attribute('RelayState')
        }
    
    def initiate_slo(self, session_token):
        """Initiate Single Logout"""
        session = self._get_session(session_token)
        
        auth = OneLogin_Saml2_Auth(
            self._prepare_request(),
            self.settings
        )
        
        # Generate logout request
        slo_url = auth.logout(
            name_id=session['user_id'],
            session_index=session['session_index']
        )
        
        return slo_url
    
    def process_slo_response(self, saml_response):
        """Process Single Logout response"""
        auth = OneLogin_Saml2_Auth(
            self._prepare_request(),
            self.settings
        )
        
        # Process logout response
        auth.process_slo()
        
        errors = auth.get_errors()
        if errors:
            raise ValueError(f"SLO validation failed: {errors}")
        
        return {'success': True}
```

### Multi-Tenancy Authentication

```python
class MultiTenantAuthenticator:
    """Handle authentication for multi-tenant SaaS applications"""
    
    def __init__(self):
        self.tenants = {}
        self.user_tenants = {}
    
    def authenticate_user(self, email, password, tenant_identifier):
        """Authenticate user within specific tenant context"""
        # Resolve tenant
        tenant = self._resolve_tenant(tenant_identifier)
        
        if not tenant:
            raise ValueError("Invalid tenant")
        
        # Check tenant status
        if not tenant['active']:
            raise ValueError("Tenant is not active")
        
        # Authenticate user
        user = self._verify_credentials(email, password, tenant['id'])
        
        if not user:
            raise ValueError("Invalid credentials")
        
        # Verify user belongs to tenant
        if not self._user_belongs_to_tenant(user['id'], tenant['id']):
            raise ValueError("User not authorized for this tenant")
        
        # Generate tenant-scoped token
        token = self._generate_tenant_token(
            user['id'],
            tenant['id'],
            tenant['subscription_tier']
        )
        
        return {
            'user': user,
            'tenant': tenant,
            'token': token
        }
    
    def _resolve_tenant(self, identifier):
        """Resolve tenant from various identifiers"""
        # Support multiple tenant identification methods:
        # 1. Subdomain (acme.yourapp.com)
        # 2. Custom domain (app.acmecorp.com)
        # 3. Tenant ID or slug
        
        if identifier.endswith('.yourapp.com'):
            # Extract subdomain
            tenant_slug = identifier.split('.')[0]
            return self._get_tenant_by_slug(tenant_slug)
        else:
            # Direct tenant ID or custom domain lookup
            return self._get_tenant(identifier)
    
    def _generate_tenant_token(self, user_id, tenant_id, subscription_tier):
        """Generate JWT token with tenant context"""
        import jwt
        
        payload = {
            'sub': user_id,
            'tenant_id': tenant_id,
            'tier': subscription_tier,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        # IMPORTANT: Use tenant-specific signing key for isolation
        signing_key = self._get_tenant_signing_key(tenant_id)
        
        return jwt.encode(payload, signing_key, algorithm='RS256')
    
    def validate_tenant_token(self, token, expected_tenant_id=None):
        """Validate tenant-scoped JWT token"""
        import jwt
        
        # Decode without verification to get tenant_id
        unverified = jwt.decode(token, options={"verify_signature": False})
        tenant_id = unverified.get('tenant_id')
        
        if expected_tenant_id and tenant_id != expected_tenant_id:
            raise ValueError("Token tenant mismatch")
        
        # Get tenant-specific signing key
        signing_key = self._get_tenant_signing_key(tenant_id)
        
        # Verify token with tenant key
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=['RS256']
        )
        
        return payload
```

## Session Management Best Practices

### Secure Session Implementation

```python
import secrets
from datetime import datetime, timedelta
from typing import Optional

class SessionManager:
    """Production-grade session management"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.session_timeout = timedelta(hours=24)
        self.sliding_window = timedelta(minutes=30)
    
    def create_session(self, user_id: str, context: dict) -> str:
        """Create new authenticated session"""
        # Generate cryptographically secure session ID
        session_id = secrets.token_urlsafe(32)
        
        # Session data
        session_data = {
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'last_activity': datetime.utcnow().isoformat(),
            'ip_address': context.get('ip_address'),
            'user_agent': context.get('user_agent'),
            'authenticated_via': context.get('auth_method'),
            'mfa_verified': context.get('mfa_verified', False)
        }
        
        # Store in Redis with TTL
        self.redis.setex(
            f"session:{session_id}",
            int(self.session_timeout.total_seconds()),
            json.dumps(session_data)
        )
        
        # Track user's active sessions
        self.redis.sadd(f"user_sessions:{user_id}", session_id)
        
        return session_id
    
    def validate_session(self, session_id: str, context: dict) -> Optional[dict]:
        """Validate session and update activity"""
        # Get session data
        session_key = f"session:{session_id}"
        session_json = self.redis.get(session_key)
        
        if not session_json:
            return None
        
        session_data = json.loads(session_json)
        
        # Validate session context (detect session hijacking)
        if not self._validate_session_context(session_data, context):
            # Suspicious activity detected
            self.revoke_session(session_id)
            self._log_security_event('session_hijacking_attempt', session_data)
            return None
        
        # Check if session needs activity update (sliding window)
        last_activity = datetime.fromisoformat(session_data['last_activity'])
        if datetime.utcnow() - last_activity > self.sliding_window:
            # Update last activity timestamp
            session_data['last_activity'] = datetime.utcnow().isoformat()
            
            # Refresh TTL (sliding expiration)
            self.redis.setex(
                session_key,
                int(self.session_timeout.total_seconds()),
                json.dumps(session_data)
            )
        
        return session_data
    
    def revoke_session(self, session_id: str):
        """Revoke specific session"""
        # Get session to find user_id
        session_json = self.redis.get(f"session:{session_id}")
        
        if session_json:
            session_data = json.loads(session_json)
            user_id = session_data['user_id']
            
            # Remove from user's session list
            self.redis.srem(f"user_sessions:{user_id}", session_id)
        
        # Delete session
        self.redis.delete(f"session:{session_id}")
    
    def revoke_all_user_sessions(self, user_id: str):
        """Revoke all sessions for a user (e.g., password change)"""
        # Get all user sessions
        session_ids = self.redis.smembers(f"user_sessions:{user_id}")
        
        # Delete all sessions
        for session_id in session_ids:
            self.redis.delete(f"session:{session_id}")
        
        # Clear user session set
        self.redis.delete(f"user_sessions:{user_id}")
    
    def get_user_sessions(self, user_id: str) -> list:
        """Get all active sessions for user"""
        session_ids = self.redis.smembers(f"user_sessions:{user_id}")
        sessions = []
        
        for session_id in session_ids:
            session_json = self.redis.get(f"session:{session_id}")
            if session_json:
                session_data = json.loads(session_json)
                sessions.append({
                    'session_id': session_id,
                    'created_at': session_data['created_at'],
                    'last_activity': session_data['last_activity'],
                    'ip_address': session_data['ip_address'],
                    'user_agent': session_data['user_agent']
                })
        
        return sessions
    
    def _validate_session_context(self, session_data: dict, current_context: dict) -> bool:
        """Validate session context to detect hijacking"""
        # Get stored context
        stored_ip = session_data.get('ip_address')
        stored_ua = session_data.get('user_agent')
        
        current_ip = current_context.get('ip_address')
        current_ua = current_context.get('user_agent')
        
        # IP validation (allow some flexibility for mobile networks)
        if stored_ip and current_ip:
            # Check if IPs are in same /24 subnet
            stored_subnet = '.'.join(stored_ip.split('.')[:3])
            current_subnet = '.'.join(current_ip.split('.')[:3])
            
            if stored_subnet != current_subnet:
                return False
        
        # User agent validation (must match exactly)
        if stored_ua and current_ua:
            if stored_ua != current_ua:
                return False
        
        return True
    
    def _log_security_event(self, event_type: str, session_data: dict):
        """Log security events for monitoring"""
        # In production: send to SIEM or security monitoring
        print(f"Security Event: {event_type} - User: {session_data.get('user_id')}")
```

## Credential Storage Security

### Password Hashing

```python
import bcrypt
import secrets

class PasswordManager:
    """Secure password handling"""
    
    def __init__(self):
        # Use cost factor 12 or higher for production
        self.cost_factor = 12
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        # Generate salt
        salt = bcrypt.gensalt(rounds=self.cost_factor)
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        return password_hash.decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception:
            return False
    
    def needs_rehash(self, password_hash: str) -> bool:
        """Check if password needs rehashing (cost factor changed)"""
        # Extract current cost factor from hash
        try:
            current_cost = int(password_hash.split('$')[2])
            return current_cost < self.cost_factor
        except Exception:
            return True
    
    def generate_secure_password(self, length: int = 16) -> str:
        """Generate secure random password"""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password
```

**CRITICAL: Never use MD5, SHA1, or plain SHA256 for passwords. Always use bcrypt, scrypt, or Argon2.**

## Migration Strategies

### Migrating from Passwords to Passwordless

```python
class PasswordlessTransition:
    """Handle gradual migration to passwordless authentication"""
    
    def __init__(self):
        self.users = {}  # In production: use database
    
    def is_passwordless_enabled(self, user_id: str) -> bool:
        """Check if user has enabled passwordless authentication"""
        user = self.users.get(user_id)
        return user and user.get('passwordless_enabled', False)
    
    def authenticate_hybrid(self, email: str, credential: dict) -> dict:
        """Support both password and passwordless during transition"""
        user = self._get_user_by_email(email)
        
        if not user:
            raise ValueError("User not found")
        
        # Try passwordless first if enabled
        if user.get('passwordless_enabled'):
            if credential.get('type') == 'magic_link':
                return self._verify_magic_link(credential['token'])
            elif credential.get('type') == 'passkey':
                return self._verify_passkey(credential['data'])
        
        # Fall back to password authentication
        if credential.get('type') == 'password':
            if self._verify_password(user, credential['password']):
                # Prompt user to upgrade to passwordless
                return {
                    'authenticated': True,
                    'user': user,
                    'suggest_passwordless_upgrade': True
                }
        
        raise ValueError("Authentication failed")
    
    def enable_passwordless(self, user_id: str, method: str) -> dict:
        """Enable passwordless authentication for user"""
        user = self.users.get(user_id)
        
        if not user:
            raise ValueError("User not found")
        
        # Initialize passwordless credentials
        user['passwordless_enabled'] = True
        user['passwordless_method'] = method
        
        if method == 'passkey':
            # Generate passkey registration options
            return self._generate_passkey_options(user_id)
        elif method == 'magic_link':
            # User can immediately use magic links
            return {'success': True, 'message': 'Magic link authentication enabled'}
        
        return {'success': False, 'error': 'Unsupported method'}
    
    def deprecate_password(self, user_id: str):
        """Remove password after passwordless is confirmed working"""
        user = self.users.get(user_id)
        
        if not user:
            raise ValueError("User not found")
        
        # Verify passwordless is fully set up
        if not user.get('passwordless_enabled'):
            raise ValueError("Passwordless not enabled")
        
        # Verify user has successfully used passwordless at least once
        if not user.get('passwordless_verified'):
            raise ValueError("Passwordless not yet verified")
        
        # Remove password hash
        user['password_hash'] = None
        user['password_deprecated_at'] = datetime.utcnow().isoformat()
        
        # Send confirmation email
        self._send_password_removed_notification(user['email'])
        
        return {'success': True}
```

## Compliance and Standards

### GDPR Considerations

```python
class GDPRCompliantAuth:
    """Authentication with GDPR compliance"""
    
    def register_user(self, email: str, password: str, consent: dict) -> dict:
        """Register user with explicit consent tracking"""
        # Verify required consents
        required_consents = ['terms_of_service', 'privacy_policy']
        for consent_type in required_consents:
            if not consent.get(consent_type):
                raise ValueError(f"Missing required consent: {consent_type}")
        
        # Create user with consent record
        user_id = self._create_user(email, password)
        
        # Store consent record
        self._store_consent(user_id, {
            'terms_of_service': {
                'granted': True,
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0'
            },
            'privacy_policy': {
                'granted': True,
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0'
            }
        })
        
        return {'user_id': user_id, 'success': True}
    
    def export_user_data(self, user_id: str) -> dict:
        """Export all user data (GDPR Right to Data Portability)"""
        user_data = {
            'profile': self._get_user_profile(user_id),
            'authentication_history': self._get_auth_history(user_id),
            'consent_records': self._get_consent_records(user_id),
            'sessions': self._get_session_history(user_id)
        }
        
        return user_data
    
    def delete_user_data(self, user_id: str) -> dict:
        """Delete user data (GDPR Right to Erasure)"""
        # Verify user identity (require re-authentication)
        
        # Delete user data
        self._delete_user_profile(user_id)
        self._anonymize_auth_logs(user_id)
        self._delete_sessions(user_id)
        self._mark_user_deleted(user_id)
        
        return {'success': True, 'deleted_at': datetime.utcnow().isoformat()}
```

## Testing Authentication Systems

### Security Test Cases

```python
import pytest
from datetime import datetime, timedelta

class TestAuthentication:
    """Security-focused authentication tests"""
    
    def test_token_expiration(self):
        """Verify expired tokens are rejected"""
        # Generate expired token
        token = generate_token(user_id='test', expires_in=-3600)
        
        with pytest.raises(ValueError, match="Token has expired"):
            validate_token(token)
    
    def test_token_tampering(self):
        """Verify tampered tokens are rejected"""
        token = generate_token(user_id='test')
        
        # Tamper with token
        tampered = token[:-5] + "xxxxx"
        
        with pytest.raises(ValueError, match="Invalid token"):
            validate_token(tampered)
    
    def test_rate_limiting(self):
        """Verify rate limiting on login attempts"""
        email = "test@example.com"
        
        # Attempt multiple logins
        for i in range(5):
            try:
                login(email, "wrong_password")
            except:
                pass
        
        # Next attempt should be rate limited
        with pytest.raises(ValueError, match="Too many attempts"):
            login(email, "wrong_password")
    
    def test_session_hijacking_detection(self):
        """Verify session hijacking is detected"""
        # Create session from IP 192.168.1.1
        session_id = create_session(
            user_id='test',
            context={'ip_address': '192.168.1.1'}
        )
        
        # Attempt to use from different IP
        with pytest.raises(ValueError, match="Security validation failed"):
            validate_session(
                session_id,
                context={'ip_address': '10.0.0.1'}
            )
    
    def test_password_strength(self):
        """Verify password strength requirements"""
        weak_passwords = [
            'password',
            '12345678',
            'qwerty123',
            'Test123'  # No special char
        ]
        
        for pwd in weak_passwords:
            with pytest.raises(ValueError, match="Password too weak"):
                create_user('test@example.com', pwd)
    
    def test_oauth_pkce_required(self):
        """Verify PKCE is required for OAuth flows"""
        # Attempt OAuth without PKCE
        with pytest.raises(ValueError, match="code_challenge required"):
            generate_authorization_code(
                client_id='test',
                redirect_uri='https://app.example.com/callback',
                code_challenge=None  # Missing PKCE
            )
```

## Monitoring and Observability

### Authentication Metrics to Track

```python
class AuthMetrics:
    """Track critical authentication metrics"""
    
    def __init__(self, metrics_client):
        self.metrics = metrics_client
    
    def track_authentication_attempt(self, success: bool, method: str):
        """Track authentication attempts"""
        self.metrics.increment(
            'auth.attempts',
            tags={
                'success': success,
                'method': method
            }
        )
    
    def track_token_validation(self, valid: bool, reason: str = None):
        """Track token validation results"""
        self.metrics.increment(
            'auth.token.validation',
            tags={
                'valid': valid,
                'reason': reason or 'success'
            }
        )
    
    def track_security_event(self, event_type: str, severity: str):
        """Track security events"""
        self.metrics.increment(
            'auth.security_event',
            tags={
                'type': event_type,
                'severity': severity
            }
        )
        
        # Alert on high-severity events
        if severity == 'high':
            self._send_security_alert(event_type)
    
    def track_authentication_latency(self, duration_ms: float, method: str):
        """Track authentication performance"""
        self.metrics.histogram(
            'auth.duration',
            duration_ms,
            tags={'method': method}
        )
```

**Key Metrics to Monitor:**
- Authentication success/failure rate
- Token validation failures
- Rate limit hits
- Session hijacking attempts
- Password reset requests
- MFA verification failures
- Average authentication latency
- Geographic distribution of logins

## Summary: Authentication Decision Tree

```
Need Authentication?
│
├─ Public API? → API Keys (short-term) or OAuth Client Credentials
│
├─ User-facing Web/Mobile App?
│  ├─ B2C (Consumer)?
│  │  ├─ Simple UX priority? → Magic Links or Passkeys
│  │  └─ Social login? → OAuth 2.0 (Google, Apple, etc.)
│  │
│  └─ B2B (Enterprise)?
│     ├─ SSO required? → SAML 2.0 or OIDC
│     └─ No SSO? → OAuth 2.0 + OIDC with Passkeys
│
├─ Service-to-Service?
│  ├─ Same organization? → Service Accounts with JWT
│  ├─ Cloud native? → Workload Identity (AWS IAM Roles, etc.)
│  └─ Third-party? → OAuth Client Credentials
│
└─ AI Agent/Machine Identity?
   ├─ Short-lived tasks? → Time-limited JWT (24h)
   ├─ Long-running? → Service Account with rotating secrets
   └─ Multi-tenant? → Tenant-scoped service accounts
```

## Additional Resources

### Recommended Libraries

**Python:**
- `PyJWT` - JWT encoding/decoding
- `python-jose` - JWT with RSA support
- `bcrypt` - Password hashing
- `python-webauthn` - Passkeys/WebAuthn
- `python-saml` - SAML implementation

**Node.js:**
- `jsonwebtoken` - JWT handling
- `bcrypt` - Password hashing
- `@simplewebauthn/server` - WebAuthn server
- `passport-saml` - SAML strategy

**Security Tools:**
- `OWASP ZAP` - Security testing
- `HashiCorp Vault` - Secret management
- `Auth0` / `Okta` - Managed authentication (if building isn't required)

### Standards and Specifications

- **OAuth 2.0**: RFC 6749
- **OIDC**: OpenID Connect Core 1.0
- **SAML 2.0**: OASIS Standard
- **WebAuthn**: W3C Recommendation
- **JWT**: RFC 7519
- **PKCE**: RFC 7636

### Common Vulnerabilities (OWASP)

1. **Broken Authentication** - Improper credential management
2. **Insufficient Session Timeout** - Long-lived sessions
3. **Missing MFA** - Single-factor authentication
4. **Weak Password Policy** - Predictable passwords
5. **Insecure Token Storage** - XSS-vulnerable storage
6. **Missing Rate Limiting** - Brute force attacks
7. **Inadequate Logging** - Poor security monitoring

---

## Getting Help

This skill provides patterns proven at billion-user scale. When implementing:

1. **Start with security** - Choose the most secure option that meets requirements
2. **Use battle-tested libraries** - Don't implement crypto yourself
3. **Test thoroughly** - Security tests are not optional
4. **Monitor continuously** - Track metrics and security events
5. **Plan for scale** - Stateless JWT scales better than database sessions
6. **Rotate credentials** - Automate rotation for machine identities

For specific implementation questions, refer to:
- OWASP Authentication Cheat Sheet
- NIST Digital Identity Guidelines
- Cloud provider security documentation
- OAuth 2.0 Security Best Current Practice

Remember: **Authentication is the foundation of security. Get it right.**
