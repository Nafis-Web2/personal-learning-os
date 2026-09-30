# Production authentication

The production app uses Supabase Auth and maps each verified Supabase subject to the existing `auth_identities` + `users` records.

Backend environment variables:
- `SUPABASE_URL`
- `SUPABASE_PUBLISHABLE_KEY`
- `OWNER_EMAIL` (the only email allowed to use this private Learning OS)

Frontend environment variables:
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`
- `NEXT_PUBLIC_API_BASE_URL`

Production `/users/{user_id}/...` routes require a valid bearer token and reject attempts to access a different Learning OS user ID.
