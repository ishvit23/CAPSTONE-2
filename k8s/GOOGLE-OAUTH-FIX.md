# Google OAuth Setup - Correct Configuration

## Two Different Sections in Google Cloud Console

### 1. Authorized JavaScript origins (NO paths allowed)
This is where you put just the domain/port:
- ✅ `http://localhost:30080`
- ✅ `http://localhost:30081`
- ❌ `http://localhost:30081/api/auth/google/callback/` (WRONG - has a path)

### 2. Authorized redirect URIs (paths REQUIRED)
This is where you put the full callback URL:
- ✅ `http://localhost:30081/api/auth/google/callback/`
- ✅ `http://localhost:8000/api/auth/google/callback/` (for local dev)

## Step-by-Step Instructions

1. Go to: https://console.cloud.google.com/apis/credentials

2. Click on your OAuth 2.0 Client ID

3. In "Authorized JavaScript origins", add:
   ```
   http://localhost:30080
   http://localhost:30081
   ```
   (No trailing slashes, no paths - just the base URLs)

4. In "Authorized redirect URIs", add:
   ```
   http://localhost:30081/api/auth/google/callback/
   ```
   (Full path with trailing slash)

5. Click **Save**

6. Wait 1-2 minutes for changes to propagate

## Quick Summary

| Section | What to Add | Example |
|---------|-------------|---------|
| JavaScript origins | Base URLs only (no path) | `http://localhost:30080` |
| Redirect URIs | Full callback path | `http://localhost:30081/api/auth/google/callback/` |

