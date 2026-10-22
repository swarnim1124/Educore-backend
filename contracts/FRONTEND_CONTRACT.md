# Frontend API Contract - m_AAA / sm_auth

All requests are POST to the backend API URL.
There are NO other endpoints or HTTP methods.

---

## 1. Request Envelope (ALL Requests)

Every request MUST have exactly these top-level keys:

  mod        : string  (REQUIRED)
  subMod     : string  (REQUIRED)
  action     : string  (REQUIRED)
  actionType : string  (REQUIRED)
  payload    : object  (optional, defaults to {})

NO other top-level keys. Not 'module', not 'submodule'.

---

## 2. Response Envelope (ALL Responses)

  status  : 'success' | 'error'
  message : string
  data    : object

---

## 3. Actions

---------------------------------------------------------------------
ACTION 1: Login
---------------------------------------------------------------------
mod        : m_AAA
subMod     : sm_auth
action     : session
actionType : add
payload:
  username : string  (REQUIRED) - email address
  password : string  (REQUIRED) - plaintext password
  captcha  : string  (optional) - CAPTCHA value, only when enforced
  (no force parameter needed - concurrent sessions are logged out automatically)

Success response data:
  token          : string  - JWT bearer token to store in localStorage
  captchaRequired: boolean - whether CAPTCHA is enforced (currently always false)

Error messages:
  'Invalid username or password'
  'Username and password are required'
  'Login successful'             - When logging in with no other active sessions
  'logged in from another device' - When logging in and automatically logging out an active session on another device

---------------------------------------------------------------------
ACTION 2: Logout
---------------------------------------------------------------------
mod        : m_AAA
subMod     : sm_auth
action     : session
actionType : delete
payload    : {}
AUTH       : Bearer token REQUIRED in Authorization header

---------------------------------------------------------------------
ACTION 3: Change Password
---------------------------------------------------------------------
mod        : m_AAA
subMod     : sm_auth
action     : password
actionType : update
payload:
  currentPassword : string (REQUIRED)
  newPassword     : string (REQUIRED) - min 8 chars, must differ from current
AUTH       : Bearer token REQUIRED

Error messages:
  'Current password is incorrect'
  'New password must be different from the current password'
  'New password must be at least 8 characters long'

---------------------------------------------------------------------
ACTION 4: Forgot Password - Initiate
---------------------------------------------------------------------
mod        : m_AAA
subMod     : sm_auth
action     : passwordReset
actionType : add
payload:
  email : string (REQUIRED)
AUTH       : None required

Success response data:
  resetToken : string - (DEV ONLY: returned directly, prod sends via email)
  note       : string

---------------------------------------------------------------------
ACTION 5: Forgot Password - Validate Token
---------------------------------------------------------------------
mod        : m_AAA
subMod     : sm_auth
action     : passwordReset
actionType : view
payload:
  token : string (REQUIRED) - reset token from Action 4
AUTH       : None required

Error messages:
  'Invalid or expired token'
  'Token has expired'

---------------------------------------------------------------------
ACTION 6: Forgot Password - Execute Reset
---------------------------------------------------------------------
mod        : m_AAA
subMod     : sm_auth
action     : passwordReset
actionType : update
payload:
  token       : string (REQUIRED) - reset token from Action 4
  newPassword : string (REQUIRED)
AUTH       : None required

Error messages:
  'Token and newPassword are required'
  'Invalid or expired token'
  'Token has expired'

---------------------------------------------------------------------
ACTION 7: Get Current User
---------------------------------------------------------------------
mod        : m_AAA
subMod     : sm_auth
action     : user
actionType : view
payload    : {}
AUTH       : Bearer token REQUIRED

Success response data:
  user_id        : int
  email          : string
  roles          : string[]
  permissions    : string[]
  institution_id : int
  org_id         : int

---

## 4. HTTP Status Codes

200  - Request processed (always check status field in body)
422  - Invalid Request Payload (missing mod/subMod/action/actionType)
401  - Missing or invalid Bearer token
403  - Insufficient permissions
500  - Internal server error (returns error message and full stack trace in development)

---

## 5. Logging and Debugging Features

The backend automatically logs every API request to `logs/oneapp_requests.log` and `logs/oneapp_errors.log`.
- **Request Object Logging**: The entire incoming request envelope is captured under `request.request_body`.
- **Credential Masking**: Sensitive fields (`password`, `secret`, `token`, `key`, `captcha`) are automatically sanitized to `********`.
- **Response Tracking**: Successful responses include the returned payload in log files for complete auditability.

---

## 6. Common Fix for 422 Invalid Request Payload

This error ALWAYS means a required top-level field is missing.
Check that utils/api.js function signature uses:
  { mod, subMod, action, actionType, payload }
NOT:
  { module, submodule, action, actionType, payload }

And the JSON body sent to the server uses exactly:
  mod, subMod, action, actionType, payload