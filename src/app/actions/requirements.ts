"use server";

import { revalidatePath } from "next/cache";
import { z } from "zod";
import { getCurrentUser } from "@/lib/auth";
import { extractRequirements } from "@/lib/requirements";

export type RequirementState = { message: string; success?: boolean } | undefined;

const inputSchema = z.string().trim().min(1, "Tell us what you need first.").max(1000, "Keep your request under 1,000 characters.");
const editSchema = z.object({
  id: z.string().uuid("This item is no longer available."),
  name: z.string().trim().min(1).max(60),
  quantity: z.coerce.number().int().min(1, "Quantity must be at least 1.").max(1000, "Quantity must be 1,000 or less."),
  unit: z.string().trim().min(1).max(24),
  variant: z.string().trim().max(60),
});

export async function addRequirements(_state: RequirementState, formData: FormData): Promise<RequirementState> {
  const parsedText = inputSchema.safeParse(formData.get("message"));
  if (!parsedText.success) return { message: parsedText.error.issues[0]?.message ?? "Enter a purchase requirement." };
  const context = await getCurrentUser().catch(() => null);
  if (!context) return { message: "Your session expired. Sign in again to continue." };
  const items = await extractRequirements(parsedText.data);
  if (items.length === 0) return { message: "We couldn't identify an item. Try a quantity and a common product, such as “2 notebook and 1 blue pen”." };
  if (items.some((item) => !Number.isInteger(item.quantity) || item.quantity < 1 || item.quantity > 1000)) {
    return { message: "We found an invalid quantity. Please rephrase your request." };
  }

  const { supabase, user } = context;
  const { data: message, error: messageError } = await supabase.from("messages").insert({ user_id: user.id, original_text: parsedText.data }).select("id").single();
  if (messageError || !message) return { message: "We couldn't save your request. Please try again." };
  const { error: itemsError } = await supabase.from("request_items").insert(items.map((item) => ({
    message_id: message.id,
    user_id: user.id,
    name: item.name,
    quantity: item.quantity,
    unit: item.unit,
    variant: item.variant,
  })));
  if (itemsError) {
    await supabase.from("messages").delete().eq("id", message.id).eq("user_id", user.id);
    return { message: "We couldn't save the extracted items. Please try again." };
  }
  revalidatePath("/dashboard");
  revalidatePath("/manager");
  return { success: true, message: `${items.length} ${items.length === 1 ? "item" : "items"} added to your list.` };
}

export async function updateRequirementItem(formData: FormData): Promise<void> {
  const parsed = editSchema.safeParse({
    id: formData.get("id"), name: formData.get("name"), quantity: formData.get("quantity"),
    unit: formData.get("unit"), variant: formData.get("variant") ?? "",
  });
  if (!parsed.success) return;
  const context = await getCurrentUser().catch(() => null);
  if (!context) return;
  await context.supabase.from("request_items").update({
    name: parsed.data.name.toLowerCase(), quantity: parsed.data.quantity,
    unit: parsed.data.unit.toLowerCase(), variant: parsed.data.variant.trim().toLowerCase() || null,
  }).eq("id", parsed.data.id).eq("user_id", context.user.id);
  revalidatePath("/dashboard");
  revalidatePath("/manager");
}

export async function deleteRequirementItem(formData: FormData): Promise<void> {
  const id = z.string().uuid().safeParse(formData.get("id"));
  if (!id.success) return;
  const context = await getCurrentUser().catch(() => null);
  if (!context) return;
  await context.supabase.from("request_items").delete().eq("id", id.data).eq("user_id", context.user.id);
  revalidatePath("/dashboard");
  revalidatePath("/manager");
}
