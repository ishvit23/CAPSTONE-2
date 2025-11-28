# Google OAuth Setup for Kubernetes

## Current Configuration

**Backend Service:** Exposed on NodePort `30081`
**Redirect URI:** `http://localhost:30081/api/auth/google/callback/`

## Steps to Fix redirect_uri_mismatch Error

### 1. Go to Google Cloud Console
- Visit: https://console.cloud.google.com/
- Navigate to: **APIs & Services** → **Credentials**

### 2. Find Your OAuth 2.0 Client
- Click on your OAuth 2.0 Client ID (the one with your Client ID)

### 3. Update Authorized Redirect URIs
In the **Authorized redirect URIs** section, make sure you have EXACTLY:

```
http://localhost:30081/api/auth/google/callback/
```

**Important:**
- Must include `http://` (not `https://`)
- Must include `localhost:30081` (the NodePort)
- Must include `/api/auth/google/callback/` (the exact path)
- Must include the trailing slash `/`

### 4. Save Changes
- Click **Save** at the bottom
- Wait a few seconds for changes to propagate

### 5. Verify in Kubernetes
The redirect URI in your Kubernetes secret should match:

```yaml
GOOGLE_REDIRECT_URI: "http://localhost:30081/api/auth/google/callback/"
```

### 6. Test
- Clear your browser cache/cookies for Google
- Try signing in again at `http://localhost:30080`

## Common Issues

### Still getting redirect_uri_mismatch?
1. **Check for typos** - The URI must match EXACTLY (case-sensitive, trailing slash matters)
2. **Wait a few minutes** - Google changes can take 1-2 minutes to propagate
3. **Clear browser cache** - Old redirect URIs might be cached
4. **Check multiple OAuth clients** - Make sure you're editing the correct one

### Multiple redirect URIs?
You can add multiple redirect URIs if needed:
- `http://localhost:30081/api/auth/google/callback/` (for local K8s)
- `http://localhost:8000/api/auth/google/callback/` (for local dev)
- Your production URL when deployed

## Verification

To verify the backend is using the correct redirect URI, check the logs:

```powershell
kubectl logs -n digibuddy -l app=backend | Select-String "redirect"
```

The redirect URI in the Google OAuth request should match what's in Google Cloud Console.

