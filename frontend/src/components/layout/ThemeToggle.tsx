"use client";

import React from "react";
import { Sun, Moon, Monitor } from "lucide-react";
import { useTheme, ThemePreference } from "./ThemeContext";

export function ThemeToggle() {
  const { preference, setThemePreference } = useTheme();

  const options: { id: ThemePreference; label: string; icon: React.ReactNode }[] = [
    { id: "light", label: "Light", icon: <Sun size={14} aria-hidden="true" /> },
    { id: "dark", label: "Dark", icon: <Moon size={14} aria-hidden="true" /> },
    { id: "system", label: "System", icon: <Monitor size={14} aria-hidden="true" /> },
  ];

  return (
    <div
      className="theme-toggle-group"
      role="radiogroup"
      aria-label="Theme Preference Selector"
    >
      {options.map((opt) => {
        const isSelected = preference === opt.id;
        return (
          <button
            key={opt.id}
            id={`theme-btn-${opt.id}`}
            type="button"
            role="radio"
            aria-checked={isSelected}
            aria-label={`${opt.label} theme`}
            className={`theme-toggle-btn ${isSelected ? "active" : ""}`}
            onClick={() => setThemePreference(opt.id)}
            tabIndex={isSelected ? 0 : -1}
            onKeyDown={(e) => {
              if (e.key === "ArrowRight" || e.key === "ArrowDown") {
                e.preventDefault();
                const nextIdx = (options.findIndex((o) => o.id === opt.id) + 1) % options.length;
                setThemePreference(options[nextIdx].id);
                document.getElementById(`theme-btn-${options[nextIdx].id}`)?.focus();
              } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
                e.preventDefault();
                const prevIdx = (options.findIndex((o) => o.id === opt.id) - 1 + options.length) % options.length;
                setThemePreference(options[prevIdx].id);
                document.getElementById(`theme-btn-${options[prevIdx].id}`)?.focus();
              }
            }}
          >
            {opt.icon}
            <span>{opt.label}</span>
          </button>
        );
      })}
    </div>
  );
}
