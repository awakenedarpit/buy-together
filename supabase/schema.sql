-- Buy Together schema for Supabase PostgreSQL.
-- Apply once in Supabase SQL Editor or with `supabase db push`.

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text not null unique,
  name text not null default 'Member',
  role text not null default 'MEMBER' check (role in ('MEMBER', 'MANAGER')),
  created_at timestamptz not null default now()
);

create table if not exists public.messages (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  original_text text not null check (char_length(original_text) between 1 and 1000),
  created_at timestamptz not null default now()
);

create table if not exists public.request_items (
  id uuid primary key default gen_random_uuid(),
  message_id uuid not null references public.messages(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null check (char_length(name) between 1 and 60),
  quantity integer not null check (quantity between 1 and 1000),
  unit text not null default 'piece' check (char_length(unit) between 1 and 24),
  variant text check (variant is null or char_length(variant) <= 60),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists messages_user_created_idx on public.messages (user_id, created_at desc);
create index if not exists request_items_user_created_idx on public.request_items (user_id, created_at desc);
create index if not exists request_items_message_idx on public.request_items (message_id);
create index if not exists request_items_aggregate_idx on public.request_items (name, variant, unit);

create or replace function public.set_updated_at()
returns trigger language plpgsql set search_path = public as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists request_items_set_updated_at on public.request_items;
create trigger request_items_set_updated_at
before update on public.request_items
for each row execute function public.set_updated_at();

-- RLS policies use this SECURITY DEFINER function to avoid recursive profile policies.
create or replace function public.is_manager()
returns boolean language sql stable security definer set search_path = public as $$
  select exists (
    select 1 from public.profiles
    where id = (select auth.uid()) and role = 'MANAGER'
  );
$$;
revoke all on function public.is_manager() from public;
grant execute on function public.is_manager() to authenticated;

create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, email, name, role)
  values (
    new.id,
    coalesce(new.email, ''),
    coalesce(nullif(trim(new.raw_user_meta_data ->> 'name'), ''), 'Member'),
    'MEMBER'
  )
  on conflict (id) do update
    set email = excluded.email,
        name = coalesce(nullif(trim(new.raw_user_meta_data ->> 'name'), ''), public.profiles.name);
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
after insert or update of email on auth.users
for each row execute function public.handle_new_user();

alter table public.profiles enable row level security;
alter table public.messages enable row level security;
alter table public.request_items enable row level security;

drop policy if exists "Members read own profile; managers read all" on public.profiles;
create policy "Members read own profile; managers read all"
on public.profiles for select to authenticated
using (id = (select auth.uid()) or (select public.is_manager()));

-- Deliberately no client-side profile UPDATE/INSERT policy: role changes are server-only.
drop policy if exists "Members read own messages; managers read all" on public.messages;
create policy "Members read own messages; managers read all"
on public.messages for select to authenticated
using (user_id = (select auth.uid()) or (select public.is_manager()));
drop policy if exists "Members create own messages" on public.messages;
create policy "Members create own messages"
on public.messages for insert to authenticated
with check (user_id = (select auth.uid()));
drop policy if exists "Members update own messages" on public.messages;
create policy "Members update own messages"
on public.messages for update to authenticated
using (user_id = (select auth.uid())) with check (user_id = (select auth.uid()));
drop policy if exists "Members delete own messages" on public.messages;
create policy "Members delete own messages"
on public.messages for delete to authenticated
using (user_id = (select auth.uid()));

drop policy if exists "Members read own items; managers read all" on public.request_items;
create policy "Members read own items; managers read all"
on public.request_items for select to authenticated
using (user_id = (select auth.uid()) or (select public.is_manager()));
drop policy if exists "Members create own items" on public.request_items;
create policy "Members create own items"
on public.request_items for insert to authenticated
with check (
  user_id = (select auth.uid())
  and exists (
    select 1 from public.messages m
    where m.id = request_items.message_id and m.user_id = (select auth.uid())
  )
);
drop policy if exists "Members update own items" on public.request_items;
create policy "Members update own items"
on public.request_items for update to authenticated
using (user_id = (select auth.uid()))
with check (
  user_id = (select auth.uid())
  and exists (
    select 1 from public.messages m
    where m.id = request_items.message_id and m.user_id = (select auth.uid())
  )
);
drop policy if exists "Members delete own items" on public.request_items;
create policy "Members delete own items"
on public.request_items for delete to authenticated
using (user_id = (select auth.uid()));

grant usage on schema public to authenticated;
grant select on public.profiles to authenticated;
grant select, insert, update, delete on public.messages to authenticated;
grant select, insert, update, delete on public.request_items to authenticated;

-- Optional one-time demo promotion after registering the selected manager account:
-- update public.profiles set role = 'MANAGER' where email = 'manager@example.com';
