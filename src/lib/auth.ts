import "server-only";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";

export type UserProfile = {
  id: string;
  email: string;
  name: string;
  role: "MEMBER" | "MANAGER";
};

export async function getCurrentUser() {
  const supabase = await createClient();
  const { data, error } = await supabase.auth.getUser();
  if (error || !data.user) return null;
  return { supabase, user: data.user };
}

export async function requireUser(next = "/dashboard") {
  let context;
  try {
    context = await getCurrentUser();
  } catch {
    redirect(`/login?next=${encodeURIComponent(next)}&setup=1`);
  }
  if (!context) redirect(`/login?next=${encodeURIComponent(next)}`);
  return context;
}

export async function getProfile(supabase: Awaited<ReturnType<typeof createClient>>, user: { id: string; email?: string; user_metadata?: Record<string, unknown> }): Promise<UserProfile | null> {
  const { data, error } = await supabase.from("profiles").select("id,email,name,role").eq("id", user.id).maybeSingle();
  if (error || !data) return null;
  const role = data.role === "MANAGER" ? "MANAGER" : "MEMBER";
  return {
    id: data.id,
    email: data.email || user.email || "",
    name: data.name || String(user.user_metadata?.name ?? "Member"),
    role,
  };
}
