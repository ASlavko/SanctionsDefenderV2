
"use client";
import React, { useState } from "react";
import { Box, Typography, Paper, Stack, Table, TableHead, TableRow, TableCell, TableBody, Chip, Button, TextField, Dialog, DialogTitle, DialogContent, DialogActions } from "@mui/material";
import { runSingleScreening, fetchSearchLogHistory, createDecision, getDecisionAudit } from "@/lib/api";
import type { ScreeningMatch, MatchDecision, DecisionAudit, MatchStatus } from "@/types/batch";

export default function SingleScreeningPage() {
  // Use real user/company context from users (1).json
  // Example: Slavko Ažman
  const user_id = "5c215268-4275-4f63-9ab1-ec82e2e5b475";
  const company_id = "d0d28712-898e-4b87-bb2c-0dcdc07b70c2";

  const [searchTerm, setSearchTerm] = useState("");
  const [lastSearchTerm, setLastSearchTerm] = useState("");
  const [searchType, setSearchType] = useState("COMPANY");
  const [results, setResults] = useState<any[] | null>(null);
  const [resultCount, setResultCount] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Inline decision state for each match
  const [comments, setComments] = useState<{ [key: number]: string }>({});
  const [decisionLoading, setDecisionLoading] = useState<{ [key: number]: boolean }>({});
  const [auditHistory, setAuditHistory] = useState<DecisionAudit[]>([]);
  const [showAudit, setShowAudit] = useState(false);
  const [history, setHistory] = useState<any[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  // Fetch search log history on mount
  React.useEffect(() => {
    if (!company_id || !user_id) return;
    setHistoryLoading(true);
    fetchSearchLogHistory({ company_id, user_id })
      .then(setHistory)
      .catch(() => setHistory([]))
      .finally(() => setHistoryLoading(false));
  }, [company_id, user_id]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);
    setResultCount(null);
    setLastSearchTerm(searchTerm); // Store the last search term
    try {
      const res = await runSingleScreening({
        search_term: searchTerm,
        search_type: searchType,
        user_id,
        company_id,
      });
      setResults(res.matches);
      setResultCount(res.result_count);
      // Refresh history after search
      fetchSearchLogHistory({ company_id, user_id }).then(setHistory);
    } catch (err: any) {
      setError(err.message || "Search failed");
    } finally {
      setLoading(false);
      setSearchTerm(""); // Auto-clear UI
    }
  };



  // Inline decision handlers
  const handleCommentChange = (idx: number, value: string) => {
    setComments((prev) => ({ ...prev, [idx]: value }));
  };

  const handleInlineDecision = async (match: any, idx: number, status: MatchStatus) => {
    setDecisionLoading((prev) => ({ ...prev, [idx]: true }));
    try {
      await createDecision(
        match.match_name,
        match.sanction_id,
        status,
        user_id,
        comments[idx] || ""
      );
      // Optionally, show a success indicator or disable buttons
    } catch (err) {
      // Optionally, show error
    } finally {
      setDecisionLoading((prev) => ({ ...prev, [idx]: false }));
    }
  };

  const openAudit = async () => {
    // TODO: Replace with real decision_id and company filter
    const audits = await getDecisionAudit(1); // Only show for user's company
    setAuditHistory(audits);
    setShowAudit(true);
  };

  return (
    <Box>
      <Typography variant="h4" mb={3} fontWeight={600}>
        Single Screening
      </Typography>
      <Paper sx={{ p: 3, mb: 3 }}>
        <form onSubmit={handleSearch} style={{ display: "flex", gap: 16, alignItems: "center" }}>
          <TextField
            label="Search term"
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            required
            size="small"
            sx={{ minWidth: 220 }}
          />
          <Stack direction="row" spacing={2} alignItems="center">
            <label>
              <input
                type="radio"
                value="COMPANY"
                // ...existing code...
                                value="COMPANY"
                                checked={searchType === "COMPANY"}
                                onChange={() => setSearchType("COMPANY")}
                              />
                              Company
                            </label>
                            <label>
                              <input
                                type="radio"
                                value="INDIVIDUAL"
                                checked={searchType === "INDIVIDUAL"}
                                onChange={() => setSearchType("INDIVIDUAL")}
                              />
                              Individual
                            </label>
                          </Stack>
                          <Button type="submit" variant="contained" disabled={loading || !searchTerm}>
                            {loading ? "Searching..." : "Screen"}
                          </Button>
                        </form>
                        {error && <Typography color="error" mt={2}>{error}</Typography>}
                      </Paper>

                      {/* Results and history blocks (already wrapped in fragment) */}
                      <>
                        {results && resultCount! > 0 && (
                          <Paper sx={{ p: 3, mb: 3 }}>
                            <Typography variant="h6" mb={2}>Screening Results</Typography>
                            <Typography variant="subtitle1" mb={2}>
                              Searched for: <b>{lastSearchTerm}</b>
                            </Typography>
                            <Table size="small">
                              <TableBody>
                                {results.map((m, i) => {
                                  const flat = { ...m, ...(m.record || {}) };
                                  // Helper to pretty print values
                                  const pretty = (value: any) => {
                                    if (value === null || value === undefined) return '—';
                                    if (Array.isArray(value)) return value.length ? value.join(", ") : "—";
                                    if (typeof value === 'string' && value.startsWith('[') && value.endsWith(']')) {
                                      try {
                                        const arr = JSON.parse(value);
                                        if (Array.isArray(arr)) return arr.length ? arr.join(", ") : "—";
                                      } catch {}
                                    }
                                    if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(value)) {
                                      return new Date(value).toLocaleString();
                                    }
                                    if (typeof value === 'boolean') return value ? 'Yes' : 'No';
                                    return String(value);
                                  };
                                  return (
                                    <React.Fragment key={i}>
                                      <TableRow>
                                        <TableCell>
                                          <b>List:</b> {(() => {
                                            const val = (flat.list_type || '').toUpperCase();
                                            if (val.includes('EU')) return <span title="EU">🇪🇺</span>;
                                            if (val.includes('UK')) return <span title="UK">🇬🇧</span>;
                                            if (val.includes('US')) return <span title="US">🇺🇸</span>;
                                            return pretty(flat.list_type);
                                          })()}
                                        </TableCell>
                                        <TableCell><b>ID:</b> {pretty(flat.id)}</TableCell>
                                        <TableCell><b>Original Name:</b> {pretty(flat.original_name)}</TableCell>
                                        <TableCell><b>Alias Names:</b> {pretty(flat.alias_names)}</TableCell>
                                      </TableRow>
                                      <TableRow>
                                        <TableCell><b>Programme:</b> {pretty(flat.programe)}</TableCell>
                                        <TableCell><b>Function:</b> {pretty(flat.function)}</TableCell>
                                        <TableCell><b>Nationality:</b> {pretty(flat.nationality)}</TableCell>
                                        <TableCell><b>Date of Birth:</b> {pretty(flat.date_of_birth)}</TableCell>
                                      </TableRow>
                                      <TableRow>
                                        <TableCell colSpan={4}>
                                          <Stack direction="row" spacing={2} alignItems="center">
                                            <Button
                                              size="small"
                                              color="error"
                                              variant="contained"
                                              disabled={decisionLoading[i]}
                                              onClick={() => handleInlineDecision(m, i, "CONFIRMED")}
                                            >
                                              Confirm
                                            </Button>
                                            <Button
                                              size="small"
                                              color="success"
                                              variant="contained"
                                              disabled={decisionLoading[i]}
                                              onClick={() => handleInlineDecision(m, i, "CLEARED")}
                                            >
                                              Clear
                                            </Button>
                                            <TextField
                                              size="small"
                                              placeholder="Optional comment"
                                              value={comments[i] || ""}
                                              onChange={e => handleCommentChange(i, e.target.value)}
                                              multiline
                                              minRows={1}
                                              maxRows={3}
                                              sx={{ minWidth: 180 }}
                                            />
                                          </Stack>
                                        </TableCell>
                                      </TableRow>
                                      <TableRow>
                                        <TableCell colSpan={4}><hr /></TableCell>
                                      </TableRow>
                                    </React.Fragment>
                                  );
                                })}
                              </TableBody>
                            </Table>
                          </Paper>
                        )}

                        <Paper sx={{ p: 3 }}>
                          <Typography variant="h6" mb={2}>Your Search History</Typography>
                          {historyLoading ? (
                            <Typography>Loading history...</Typography>
                          ) : history.length === 0 ? (
                            <Typography>No previous searches.</Typography>
                          ) : (
                            <Table size="small">
                              <TableHead>
                                <TableRow>
                                  <TableCell>Date</TableCell>
                                  <TableCell>Search Term</TableCell>
                                  <TableCell>Type</TableCell>
                                  <TableCell>Result Count</TableCell>
                                </TableRow>
                              </TableHead>
                              <TableBody>
                                {history.map((h, idx) => (
                                  <TableRow key={idx}>
                                    <TableCell>{new Date(h.timestamp).toLocaleString()}</TableCell>
                                    <TableCell>{h.search_term}</TableCell>
                                    <TableCell>{h.search_type}</TableCell>
                                    <TableCell>{h.result_count}</TableCell>
                                  </TableRow>
                                ))}
                              </TableBody>
                            </Table>
                          )}
                        </Paper>
                      </>

                      {/* Audit dialog */}
                      <Dialog open={showAudit} onClose={() => setShowAudit(false)} maxWidth="md" fullWidth>
                        <DialogTitle>Decision Audit History</DialogTitle>
                        <DialogContent>
                          <Table size="small">
                            <TableHead>
                              <TableRow>
                                <TableCell>Action</TableCell>
                                <TableCell>Old Value</TableCell>
                                <TableCell>New Value</TableCell>
                                <TableCell>User</TableCell>
                                <TableCell>Timestamp</TableCell>
                                <TableCell>Comment</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {auditHistory.map((a) => (
                                <TableRow key={a.id}>
                                  <TableCell>{a.action}</TableCell>
                                  <TableCell>{a.old_value}</TableCell>
                                  <TableCell>{a.new_value}</TableCell>
                                  <TableCell>{a.user_id}</TableCell>
                                  <TableCell>{new Date(a.timestamp).toLocaleString()}</TableCell>
                                  <TableCell>{a.comment}</TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </DialogContent>
                        <DialogActions>
                          <Button onClick={() => setShowAudit(false)}>Close</Button>
                        </DialogActions>
                      </Dialog>
                    </Box>
                  );
          }





