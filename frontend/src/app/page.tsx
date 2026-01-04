 "use client";

import { Box, Container, Typography, Button, Stack } from "@mui/material";
import Link from "next/link";

export default function Home() {
  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        bgcolor: "background.default",
      }}
    >
      <Container maxWidth="md">
        <Stack spacing={4}>
          <Typography variant="h3" fontWeight={600}>
            SanctionDefender
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Sanction screening for compliance teams. Run single and batch screenings,
            manage clearing decisions, and generate audit-ready reports.
          </Typography>
          <Stack direction="row" spacing={2}>
            <Button component={Link} href="/login" variant="contained" color="primary">
              Log in
            </Button>
            <Button component={Link} href="/dashboard" variant="outlined" color="primary">
              Go to app
            </Button>
          </Stack>
        </Stack>
      </Container>
    </Box>
  );
}
