 "use client";

import { Box, Card, CardContent, Grid, Typography } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { apiUrl } from "@/lib/api";

async function fetchHealth() {
  const res = await fetch(apiUrl("/"));
  if (!res.ok) {
    throw new Error("Failed to fetch health");
  }
  return res.json();
}

export default function DashboardPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["health"],
    queryFn: fetchHealth,
  });

  return (
    <Box>
      <Typography variant="h4" mb={3} fontWeight={600}>
        Dashboard
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">
                Engine status
              </Typography>
              {isLoading && <Typography>Checking...</Typography>}
              {isError && <Typography color="error">Backend not reachable</Typography>}
              {data && (
                <Typography fontWeight={600}>
                  {data.status === "ok" && data.engine_loaded ? "Online" : "Not ready"}
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}


