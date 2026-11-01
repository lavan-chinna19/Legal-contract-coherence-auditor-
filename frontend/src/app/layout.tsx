import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import "./cleanup.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "LexAudit | Legal Contract Coherence Auditor",
  description:
    "Academic NLP research prototype for auditing legal contract coherence, clause-level anomalies, structural rules, and explainability. Not legal advice.",
};

const THEME_INITIALIZATION_SCRIPT = `(function() {
  try {
    var stored = localStorage.getItem('lexaudit_theme');
    var resolved = 'light';
    if (stored === 'dark') {
      resolved = 'dark';
    } else if (stored === 'system') {
      resolved = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    } else {
      resolved = 'light';
    }
    document.documentElement.setAttribute('data-theme', resolved);
    document.documentElement.setAttribute('data-theme-preference', stored || 'light');
    document.documentElement.style.colorScheme = resolved;
  } catch (e) {}
})();`;

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      data-theme="light"
      suppressHydrationWarning
      className={`${geistSans.variable} ${geistMono.variable}`}
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_INITIALIZATION_SCRIPT }} />
      </head>
      <body>
        <script dangerouslySetInnerHTML={{ __html: THEME_INITIALIZATION_SCRIPT }} />
        {children}
      </body>
    </html>
  );
}
