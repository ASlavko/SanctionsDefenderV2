"use client";

import { Box, Card, CardContent, Grid, Typography, Table, TableHead, TableBody, TableRow, TableCell, Button, Chip } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { apiUrl, fetchSearchLogHistory, listDecisions } from "@/lib/api";
import { USER_ID, COMPANY_ID } from "@/lib/constants";
import Link from "next/link";

async function fetchHealth() {
  const res = await fetch(apiUrl("/"));
  if (!res.ok) {
    throw new Error("Failed to fetch health");
  }
  return res.json();
}

export default function DashboardPage() {
  const { data: healthData, isLoading: healthLoading, isError: healthError } = useQuery({
    queryKey: ["health"],
    queryFn: fetchHealth,
  });

  const { data: recentScreenings } = useQuery({
    queryKey: ["recentScreenings"],
    queryFn: () => fetchSearchLogHistory({ company_id: COMPANY_ID, limit: 5 }),
    refetchInterval: 10000,
  });

  const { data: pendingDecisions } = useQuery({
    queryKey: ["pendingDecisions"],
    queryFn: () => listDecisions(true),
    refetchInterval: 10000,
  });

  return (
    <Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 3 }}>
        <Typography variant="h4" fontWeight={600}>
          Dashboard
        </Typography>
        <Box>
          <Button component={Link} href="/single-screening" variant="contained" sx={{ mr: 1 }}>Screening</Button>
          <Button component={Link} href="/batch-screening" variant="outlined">Batch</Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Status
              </Typography>
              {healthLoading && <Typography>Checking...</Typography>}
              {healthError && <Typography color="error">Backend not reachable</Typography>}
              {healthData && (
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">Engine</Typography>
                  <Typography variant="h5" color={healthData.status === "ok" ? "success.main" : "error.main"}>
                    {healthData.status === "ok" && healthData.engine_loaded ? "Online" : "Not ready"}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
                <Typography variant="h6">Recent Screenings</Typography>
                <Button component={Link} href="/single-screening" size="small">View All</Button>
              </Box>

              {!recentScreenings || recentScreenings.length === 0 ? (
                <Typography color="text.secondary">No recent screenings found.</Typography>
              ) : (
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Time</TableCell>
                      <TableCell>Search Term</TableCell>
                      <TableCell>Results</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recentScreenings.map((screening) => (
                      <TableRow key={screening.id}>
                        <TableCell>{new Date(screening.timestamp).toLocaleTimeString()}</TableCell>
                        <TableCell>{screening.search_term}</TableCell>
                        <TableCell>{screening.result_count}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
                <Typography variant="h6">My Pending Decisions</Typography>
                <Chip label={pendingDecisions?.length || 0} color="primary" size="small" />
              </Box>

              {!pendingDecisions || pendingDecisions.length === 0 ? (
                <Typography color="text.secondary">No pending decisions.</Typography>
              ) : (
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Entity</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Date</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {pendingDecisions.slice(0, 5).map((decision: any) => (
                      <TableRow key={decision.id}>
                        <TableCell>{decision.search_term_normalized}</TableCell>
                        <TableCell><Chip label={decision.decision} size="small" color="warning" variant="outlined" /></TableCell>
                        <TableCell>{new Date(decision.created_at).toLocaleDateString()}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}


