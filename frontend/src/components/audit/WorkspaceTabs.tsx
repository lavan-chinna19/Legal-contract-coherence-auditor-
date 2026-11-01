"use client";
import { useEffect, useRef } from "react";
export function WorkspaceTabs<T extends string>({ label, options, value, onChange }: {
  label: string; options: readonly { id: T; label: string }[]; value: T; onChange: (id: T) => void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const group = ref.current, active = group?.querySelector<HTMLElement>('[aria-selected="true"]');
    if (!group || !active) return;
    const box = active.getBoundingClientRect(), viewport = group.getBoundingClientRect();
    if (box.left < viewport.left) group.scrollBy({ left: box.left - viewport.left });
    else if (box.right > viewport.right) group.scrollBy({ left: box.right - viewport.right });
  }, [value]);
  return <div ref={ref} className="workspace-tabs" role="tablist" aria-label={label}>{options.map((item, i) => <button key={item.id} type="button" id={`view-${item.id}`}
    role="tab" aria-selected={value === item.id} aria-controls={`panel-${item.id}`} tabIndex={value === item.id ? 0 : -1}
    onClick={() => onChange(item.id)} onKeyDown={e => {
      let next = i;
      if (e.key === "ArrowRight") next = (i + 1) % options.length;
      else if (e.key === "ArrowLeft") next = (i + options.length - 1) % options.length;
      else if (e.key === "Home") next = 0;
      else if (e.key === "End") next = options.length - 1;
      else return;
      e.preventDefault(); onChange(options[next].id); document.getElementById(`view-${options[next].id}`)?.focus();
    }}>{item.label}</button>)}</div>;
}
