import type { Metadata } from "next";
import "./globals.css";
import MUIThemeProvider from "./providers/mui-theme-provider";

export const metadata: Metadata = {
  title: "SanctionDefender",
  description: "Sanction screening for compliance teams",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <MUIThemeProvider>{children}</MUIThemeProvider>
      </body>
    </html>
  );
}
