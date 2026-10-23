"use client";

import React, { createContext, useContext, useEffect, useState, useMemo } from "react";

export type ThemePreference = "light" | "dark" | "system";
export type ResolvedTheme = "light" | "dark";

interface ThemeContextType {
  preference: ThemePreference;
  resolvedTheme: ResolvedTheme;
  setThemePreference: (pref: ThemePreference) => void;
}

const ThemeContext = createContext<ThemeContextType>({
  preference: "light",
  resolvedTheme: "light",
  setThemePreference: () => {},
});

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [preference, setPreference] = useState<ThemePreference>("light");
  const [resolvedTheme, setResolvedTheme] = useState<ResolvedTheme>("light");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    try {
      const stored = localStorage.getItem("lexaudit_theme") as ThemePreference | null;
      const initialPref: ThemePreference =
        stored === "light" || stored === "dark" || stored === "system" ? stored : "light";

      const mql = window.matchMedia("(prefers-color-scheme: dark)");
      const resolve = (pref: ThemePreference): ResolvedTheme => {
        if (pref === "dark") return "dark";
        if (pref === "system") return mql.matches ? "dark" : "light";
        return "light";
      };

      const resolved = resolve(initialPref);
      document.documentElement.setAttribute("data-theme", resolved);
      document.documentElement.setAttribute("data-theme-preference", initialPref);
      document.documentElement.style.colorScheme = resolved;

      queueMicrotask(() => {
        setPreference(initialPref);
        setResolvedTheme(resolved);
        setMounted(true);
      });

      const handleMediaChange = () => {
        const currentPref = (localStorage.getItem("lexaudit_theme") as ThemePreference) || "light";
        if (currentPref === "system") {
          const sysResolved: ResolvedTheme = mql.matches ? "dark" : "light";
          setResolvedTheme(sysResolved);
          document.documentElement.setAttribute("data-theme", sysResolved);
          document.documentElement.style.colorScheme = sysResolved;
        }
      };

      mql.addEventListener("change", handleMediaChange);

      return () => {
        mql.removeEventListener("change", handleMediaChange);
      };
    } catch {
      queueMicrotask(() => {
        setMounted(true);
      });
    }
  }, []);

  const setThemePreference = (pref: ThemePreference) => {
    setPreference(pref);
    try {
      localStorage.setItem("lexaudit_theme", pref);
    } catch {
      // Ignore storage errors in restricted contexts
    }

    const mql = window.matchMedia("(prefers-color-scheme: dark)");
    const resolved: ResolvedTheme =
      pref === "dark" ? "dark" : pref === "system" ? (mql.matches ? "dark" : "light") : "light";

    setResolvedTheme(resolved);
    document.documentElement.setAttribute("data-theme", resolved);
    document.documentElement.setAttribute("data-theme-preference", pref);
    document.documentElement.style.colorScheme = resolved;
  };

  const contextValue = useMemo(
    () => ({
      preference: mounted ? preference : "light",
      resolvedTheme: mounted ? resolvedTheme : "light",
      setThemePreference,
    }),
    [mounted, preference, resolvedTheme]
  );

  return <ThemeContext.Provider value={contextValue}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  return useContext(ThemeContext);
}
