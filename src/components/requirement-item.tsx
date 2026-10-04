import { Pencil, Trash2 } from "lucide-react";
import { deleteRequirementItem, updateRequirementItem } from "@/app/actions/requirements";

export type RequirementItemView = {
  id: string;
  message_id: string;
  name: string;
  quantity: number;
  unit: string;
  variant: string | null;
  created_at: string;
};

export function RequirementItem({ item }: { item: RequirementItemView }) {
  const unitLabel = item.quantity === 1 ? item.unit : `${item.unit}${item.unit === "piece" ? "s" : ""}`;
  return (
    <article className="requirement-item">
      <div className="item-main"><span className="item-mark">{item.name.slice(0, 1).toUpperCase()}</span><div className="item-copy"><strong>{item.name}</strong><span>{item.variant || "No variant"}</span></div></div>
      <div className="item-quantity"><strong>{item.quantity}</strong><span>{unitLabel}</span></div>
      <details className="item-edit">
        <summary className="icon-button" aria-label={`Edit ${item.name}`} title="Edit item"><Pencil size={16} /></summary>
        <div className="edit-popover"><form action={updateRequirementItem} className="edit-form">
          <input type="hidden" name="id" value={item.id} />
          <label>Item<input name="name" defaultValue={item.name} maxLength={60} required /></label>
          <div className="edit-row"><label>Qty<input name="quantity" type="number" defaultValue={item.quantity} min={1} max={1000} required /></label><label>Unit<input name="unit" defaultValue={item.unit} maxLength={24} required /></label></div>
          <label>Variant<input name="variant" defaultValue={item.variant ?? ""} maxLength={60} placeholder="Optional" /></label>
          <button className="button button-primary button-small" type="submit">Save changes</button>
        </form></div>
      </details>
      <form action={deleteRequirementItem}><input type="hidden" name="id" value={item.id} /><button className="icon-button delete-button" type="submit" aria-label={`Delete ${item.name}`} title="Delete item"><Trash2 size={16} /></button></form>
    </article>
  );
}
