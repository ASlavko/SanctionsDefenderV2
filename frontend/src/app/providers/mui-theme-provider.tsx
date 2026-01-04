"use client";

import { CssBaseline, ThemeProvider, createTheme } from "@mui/material";
import { ReactNode } from "react";
import QueryClientProvider from "./query-client-provider";

const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1d4ed8", // blue-700
    },
    secondary: {
      main: "#0f766e", // teal-700
    },
    background: {
      default: "#f9fafb",
    },
  },
});

export default function MUIThemeProvider({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <QueryClientProvider>{children}</QueryClientProvider>
    </ThemeProvider>
  );
}


