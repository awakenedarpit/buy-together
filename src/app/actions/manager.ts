"use server";

import { timingSafeEqual } from "node:crypto";
import { redirect } from "next/navigation";
import { z } from "zod";
import { getCurrentUser } from "@/lib/auth";
import { createAdminClient } from "@/lib/supabase/server";

export type ManagerSetupState = { message: string; success?: boolean } | undefined;

export async function setupManager(_state: ManagerSetupState, formData: FormData): Promise<ManagerSetupState> {
  const secret = z.string().min(1).max(256).safeParse(formData.get("setupSecret"));
  if (!secret.success) return { message: "Enter the manager setup key." };
  const expected = process.env.MANAGER_SETUP_SECRET;
  if (!expected || Buffer.byteLength(secret.data) !== Buffer.byteLength(expected) || !timingSafeEqual(Buffer.from(secret.data), Buffer.from(expected))) {
    return { message: "That manager setup key is not valid." };
  }
  const context = await getCurrentUser().catch(() => null);
  if (!context) return { message: "Sign in with the account you want to make a manager, then try again." };
  try {
    const admin = createAdminClient();
    const { data, error } = await admin.from("profiles").update({ role: "MANAGER" }).eq("id", context.user.id).select("id").single();
    if (error || !data) return { message: "Manager access couldn't be enabled. Verify the database schema and try again." };
  } catch {
    return { message: "Manager setup isn't enabled on this deployment. Ask the project owner to check its server configuration." };
  }
  redirect("/manager");
}
