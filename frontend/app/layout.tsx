import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Nav from "@/components/Nav";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Bengaluru Traffic Pulse",
  description:
    "Root-cause analysis and live congestion tracking for Bengaluru's recurring festival-weekend gridlock.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col bg-[var(--background)] text-[var(--text-primary)]">
        <Nav />
        <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col px-6 py-8">
          {children}
        </main>
        <footer className="border-t border-[var(--border-hairline)] py-6 text-center text-xs text-[var(--text-muted)]">
          Traffic data via TomTom. Congestion severity is this project&apos;s own speed-ratio scale, not
          Bengaluru Traffic Police&apos;s queue-length scale.
        </footer>
      </body>
    </html>
  );
}
