"use client";

import { AppBar, Box, Container, Toolbar, Typography, Button, Stack } from "@mui/material";
import Link from "next/link";
import { ReactNode } from "react";

export default function AppLayout({ children }: { children: ReactNode }) {
  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "background.default" }}>
      <AppBar position="static" color="primary">
        <Toolbar>
          <Typography
            variant="h6"
            component={Link}
            href="/dashboard"
            sx={{ flexGrow: 1, textDecoration: "none", color: "inherit", fontWeight: 600 }}
          >
            SanctionDefender
          </Typography>
          <Stack direction="row" spacing={2}>
            <Button color="inherit" component={Link} href="/single-screening">
              Single screening
            </Button>
            <Button color="inherit" component={Link} href="/batch-screening">
              Batch screening
            </Button>
            <Button color="inherit" component={Link} href="/sanction-lists">
              Sanction Lists
            </Button>
          </Stack>
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {children}
      </Container>
    </Box>
  );
}


