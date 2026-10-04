# Buy Together

Turn individual needs into smarter group purchases. Buy Together lets members describe purchases in everyday English or Hinglish, saves those requests in Supabase, and gives managers a live combined view of everything the group needs.

> **Live demo for this rebuild:** Not deployed yet. The existing legacy deployment is separate; a public URL for this Next.js/Supabase app can be added after its Supabase project and Vercel deployment are configured. No placeholder URL is presented as live.

## Features

- Email/password registration and login with Supabase Auth; new accounts default to `MEMBER`.
- Server-rendered member dashboard with private personal requirements.
- Optional Gemini structured extraction plus a deterministic parser that works without an API key.
- Add requirements from natural language; edit or delete individual items.
- Manager view for all member requirements, search/member filters, and dynamic totals grouped by item + variant + unit.
- Protected manager setup using a server-only setup secret and Supabase service-role key; a SQL promotion example is included as a fallback.
- PostgreSQL foreign keys, indexes, quantity checks, and row-level security policies.
- Responsive Next.js App Router interface styled with Tailwind CSS 4 and custom design tokens.

## Technology

- Next.js 16 App Router, React 19, TypeScript
- Supabase PostgreSQL, Auth, `@supabase/ssr`
- Tailwind CSS 4
- Gemini API (optional); always-available deterministic English/Hinglish fallback
- Vercel deployment target

## Local setup

Requirements: Node.js 20.9+ (Node 22 recommended) and npm.

```bash
git clone <your-repository-url>
cd buy-together
npm install
cp .env.example .env.local
```

Fill in `.env.local` as described below, then run:

```bash
npm run dev
```

Open <http://localhost:3000>. `npm run lint`, `npm run typecheck`, `npm test`, and `npm run build` are available for checks.

## Supabase setup

1. Create a Supabase project.
2. In **SQL Editor**, run [`supabase/schema.sql`](supabase/schema.sql). It creates `profiles`, `messages`, and `request_items`; a profile trigger; indexes; a manager-check function; and the RLS policies.
3. In **Authentication → Providers → Email**, enable email/password. For a quick hackathon demo, either disable email confirmation or configure an email provider so registrants can confirm before signing in.
4. Copy the project URL and anon/public key from **Project Settings → API** into `.env.local` or your deployment environment:

   ```dotenv
   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
   ```

   The anon key is intended for client authentication; database access remains constrained by RLS.
5. In Supabase **Authentication → URL Configuration**, add the local URL (`http://localhost:3000`) and the eventual production URL to the allowed redirect URLs.

### Manager account

To use the setup screen at `/manager/setup`, add both of these as **server-only** environment variables and register/sign in to the account to promote:

```dotenv
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
MANAGER_SETUP_SECRET=replace-with-a-long-random-secret
```

The manager route verifies the secret server-side and promotes only the signed-in user's profile. Never prefix the service-role key with `NEXT_PUBLIC_` or expose it in browser code. Alternatively, register the chosen account, then run this one-time statement in Supabase SQL Editor:

```sql
update public.profiles set role = 'MANAGER' where email = 'manager@example.com';
```

## Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `NEXT_PUBLIC_SUPABASE_URL` | Yes | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Yes | Supabase public anon key; RLS still applies |
| `SUPABASE_SERVICE_ROLE_KEY` | Manager setup only | Server-only manager promotion |
| `MANAGER_SETUP_SECRET` | Manager setup only | Separate shared secret for the protected setup action |
| `GEMINI_API_KEY` | No | Enables Gemini structured extraction; if missing or the call fails, the local parser is used |
| `GEMINI_MODEL` | No | Model name; defaults to `gemini-2.5-flash` |

The repository ignores environment files; `.env.example` is the only environment template committed.

## Deployment to Vercel

1. Push this repository to GitHub.
2. Import the repository in Vercel and select the default Next.js build settings (`npm run build`).
3. Add the Supabase settings above as project environment variables. Add `SUPABASE_SERVICE_ROLE_KEY` and `MANAGER_SETUP_SECRET` only if using the manager setup route; add `GEMINI_API_KEY` only if enabling Gemini.
4. Deploy. Add the Vercel production URL to Supabase Auth's allowed redirect URLs.
5. Register a member, add a request, and sign in with a second account. Promote a manager as documented above, then verify the manager aggregation.

**Deployment status:** The Next.js source builds and passes local checks. No Vercel URL is available until a Supabase project and Vercel deployment are configured.
