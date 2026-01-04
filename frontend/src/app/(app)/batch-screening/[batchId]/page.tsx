"use client";
import { use } from "react";

import {
  Box,
  Typography,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Chip,
  Button,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { fetchBatchDetailPaginated } from "@/lib/api";
import type { PaginatedBatchDetailResponse } from "@/lib/api";
import Link from "next/link";
import { useState } from "react";
import { createDecision, getDecisionAudit } from "@/lib/api";

// Helper: get user id (stub, replace with real auth)
function getUserId() {
  return "user1";
}
// Decision action component for a match
function DecisionActions({
  inputName,
  sanctionId,
}: {
  inputName: string;
  sanctionId: string;
}) {
  const [status, setStatus] = useState<MatchStatus | null>(null);
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // Use backend enum values
  const handleDecision = async (decision: MatchStatus) => {
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      await createDecision(
        inputName,
        sanctionId,
        decision,
        getUserId(),
        comment
      );
      setStatus(decision);
      setSuccess(true);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Stack spacing={1} direction="row" alignItems="center">
      <Button size="small" onClick={() => handleDecision("TRUE_MATCH")}>
        Confirm
      </Button>
      <Button size="small" onClick={() => handleDecision("FALSE_POSITIVE")}>
        Clear
      </Button>
      <Button size="small" onClick={() => handleDecision("REVISIT")}>
        Revisit
      </Button>
      <input
        type="text"
        placeholder="Comment"
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        style={{ width: 120 }}
      />
      {loading && <Typography variant="caption">Saving...</Typography>}
      {error && (
        <Typography color="error" variant="caption">
          {error}
        </Typography>
      )}
      {success && (
        <Typography color="success.main" variant="caption">
          Saved
        </Typography>
      )}
    </Stack>
  );
}
// Audit history component for a decision
function AuditHistory({ decisionId }: { decisionId: number }) {
  const [history, setHistory] = useState<DecisionAudit[] | null>(null);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await getDecisionAudit(decisionId);
      setHistory(data);
      setOpen(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Button size="small" onClick={loadHistory} disabled={loading}>
        {loading ? "Loading..." : "Audit history"}
      </Button>
      {open && history && (
        <Paper sx={{ p: 2, mt: 1 }}>
          <Typography variant="subtitle2">Audit history</Typography>
          <ul style={{ margin: 0, paddingLeft: 16 }}>
            {history.map((h) => (
              <li key={h.id}>
                [{new Date(h.timestamp).toLocaleString()}] {h.action} by{" "}
                {h.user_id}
                {h.comment ? ` – ${h.comment}` : ""}
              </li>
            ))}
          </ul>
          <Button size="small" onClick={() => setOpen(false)}>
            Close
          </Button>
        </Paper>
      )}
    </>
  );
}



export default function BatchDetailPage({ params }: { params: Promise<{ batchId: string }> }) {
  const { batchId } = use(params);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);
  const [status, setStatus] = useState<string | undefined>("PENDING");
  const [search, setSearch] = useState("");

  const { data, isLoading, isError, refetch } = useQuery<PaginatedBatchDetailResponse>({
    queryKey: ["batch-detail", batchId, page, rowsPerPage, status, search],
    queryFn: () => fetchBatchDetailPaginated(batchId, {
      limit: rowsPerPage,
      offset: page * rowsPerPage,
      status,
      search: search.trim() || undefined,
    }),
    refetchInterval: 5000,
  });

  // Status options for filter
  const statusOptions = [
    { value: undefined, label: "All" },
    { value: "PENDING", label: "Pending" },
    { value: "TRUE_MATCH", label: "Confirmed" },
    { value: "FALSE_POSITIVE", label: "Cleared" },
    { value: "NO_MATCH", label: "No match" },
    { value: "REVISIT", label: "Revisit" },
  ];

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight={600}>
          Batch {batchId}
        </Typography>
        <Button component={Link} href="/batch-screening" variant="outlined" size="small">
          Back to batches
        </Button>
      </Stack>

      <Paper sx={{ p: 3, mb: 2 }}>
        <Stack direction="row" spacing={2} alignItems="center">
          <Typography>Status:</Typography>
          <select value={status ?? ""} onChange={e => setStatus(e.target.value || undefined)}>
            {statusOptions.map(opt => (
              <option key={opt.value ?? "all"} value={opt.value ?? ""}>{opt.label}</option>
            ))}
          </select>
          <Typography>Search:</Typography>
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Input name..."
            style={{ width: 180 }}
          />
          <Button size="small" variant="outlined" onClick={() => { setPage(0); refetch(); }}>Apply</Button>
        </Stack>
      </Paper>

      {isLoading && <Typography>Loading batch details...</Typography>}
      {isError && <Typography color="error">Could not load batch details.</Typography>}

      {data && (
        <Stack spacing={3}>
          <Paper sx={{ p: 3 }}>
            <Stack spacing={1}>
              <Typography variant="h6">Batch info</Typography>
              <Typography variant="body2" color="text.secondary">
                Filename: {data.batch.filename}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Status: {data.batch.status}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total records: {data.batch.total_records} | Flagged: {data.batch.flagged_count ?? "-"}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Uploaded at: {new Date(data.batch.uploaded_at).toLocaleString(undefined, {
                  dateStyle: "short",
                  timeStyle: "short",
                })}
              </Typography>
            </Stack>
          </Paper>

          <Paper sx={{ p: 3 }}>
            <Stack spacing={2}>
              <Typography variant="h6">Screening results</Typography>
              {data.results.length === 0 && (
                <Typography color="text.secondary">
                  No results found for this filter/search.
                </Typography>
              )}
              {data.results.length > 0 && (
                <>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>ID</TableCell>
                        <TableCell>Input name</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Matches</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {data.results.map((r) => (
                        <TableRow key={r.id}>
                          <TableCell>{r.id}</TableCell>
                          <TableCell>{r.input_name}</TableCell>
                          <TableCell>
                            <Chip
                              label={r.match_status}
                              size="small"
                              color={
                                r.match_status === "NO_MATCH"
                                  ? "success"
                                  : r.match_status === "PENDING"
                                  ? "warning"
                                  : "error"
                              }
                              variant="outlined"
                            />
                          </TableCell>
                          <TableCell>
                            {r.matches && r.matches.length > 0 ? (
                              <ul style={{ margin: 0, paddingLeft: 16 }}>
                                {r.matches.map((m, i) => (
                                  <li key={i}>
                                    <strong>{m.match_score.toFixed(1)}</strong> – {m.sanction_id} – {m.match_name}
                                    <DecisionActions inputName={r.input_name} sanctionId={m.sanction_id} />
                                  </li>
                                ))}
                              </ul>
                            ) : (
                              "-"
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                  {/* Pagination controls */}
                  <Stack direction="row" spacing={2} alignItems="center" mt={2}>
                    <Button
                      size="small"
                      variant="outlined"
                      disabled={page === 0}
                      onClick={() => setPage((p) => Math.max(0, p - 1))}
                    >
                      Previous
                    </Button>
                    <Typography>
                      Page {page + 1} of {Math.ceil(data.total / rowsPerPage)}
                    </Typography>
                    <Button
                      size="small"
                      variant="outlined"
                      disabled={(page + 1) * rowsPerPage >= data.total}
                      onClick={() => setPage((p) => p + 1)}
                    >
                      Next
                    </Button>
                  </Stack>
                </>
              )}
            </Stack>
          </Paper>
        </Stack>
      )}
    </Box>
  );
}
