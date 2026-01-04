 "use client";

import {
  Box,
  Typography,
  Paper,
  Stack,
  Button,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  LinearProgress,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ChangeEvent, useRef, useState } from "react";
import { apiUrl } from "@/lib/api";
import type { BatchResponse } from "@/types/batch";
import Link from "next/link";

async function fetchBatches(): Promise<BatchResponse[]> {
  const res = await fetch(apiUrl("/api/v1/batch/"));
  if (!res.ok) {
    throw new Error("Failed to load batches");
  }
  return res.json();
}

async function uploadBatch(file: File): Promise<BatchResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(apiUrl("/api/v1/batch/upload"), {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Upload failed");
  }

  return res.json();
}

export default function BatchScreeningPage() {
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const { data: batches, isLoading, isError } = useQuery({
    queryKey: ["batches"],
    queryFn: fetchBatches,
    refetchInterval: 5000,
  });

  const uploadMutation = useMutation({
    mutationFn: uploadBatch,
    onSuccess: () => {
      setUploadError(null);
      queryClient.invalidateQueries({ queryKey: ["batches"] });
    },
    onError: (error: any) => {
      setUploadError(error.message ?? "Upload failed");
    },
  });

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    uploadMutation.mutate(file);
    // Reset input so same file can be uploaded again if needed
    e.target.value = "";
  };

  const triggerFileSelect = () => {
    fileInputRef.current?.click();
  };

  return (
    <Box>
      <Typography variant="h4" mb={3} fontWeight={600}>
        Batch screening
      </Typography>

      <Stack spacing={3}>
        <Paper sx={{ p: 3 }}>
          <Stack spacing={2}>
            <Typography variant="h6">Upload batch file</Typography>
            <Typography variant="body2" color="text.secondary">
              Upload a CSV or Excel file with business partner names. The first column (or a column
              named &quot;Name&quot; / &quot;Naziv&quot; / &quot;Ime&quot;) will be used for screening.
            </Typography>
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,.xls,.xlsx"
              style={{ display: "none" }}
              onChange={handleFileChange}
            />
            <Stack direction="row" spacing={2} alignItems="center">
              <Button
                variant="contained"
                color="primary"
                onClick={triggerFileSelect}
                disabled={uploadMutation.isPending}
              >
                {uploadMutation.isPending ? "Uploading..." : "Select file"}
              </Button>
              {uploadError && (
                <Typography variant="body2" color="error">
                  {uploadError}
                </Typography>
              )}
            </Stack>
          </Stack>
        </Paper>

        <Paper sx={{ p: 3 }}>
          <Stack spacing={2}>
            <Typography variant="h6">Recent batches</Typography>
            {isLoading && <Typography>Loading batches...</Typography>}
            {isError && (
              <Typography color="error">Could not load batches from the backend.</Typography>
            )}
            {batches && batches.length === 0 && (
              <Typography color="text.secondary">No batches yet. Upload your first file.</Typography>
            )}
            {batches && batches.length > 0 && (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Filename</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Total records</TableCell>
                    <TableCell>Flagged</TableCell>
                    <TableCell>Uploaded at</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {batches.map((batch) => (
                    <TableRow key={batch.id}>
                      <TableCell>{batch.id}</TableCell>
                      <TableCell>{batch.filename}</TableCell>
                      <TableCell>
                        {batch.status}
                        {batch.status === "PROCESSING" && <LinearProgress sx={{ mt: 1 }} />}
                      </TableCell>
                      <TableCell>{batch.total_records}</TableCell>
                      <TableCell>{batch.flagged_count ?? "-"}</TableCell>
                      <TableCell>
                        {new Date(batch.uploaded_at).toLocaleString(undefined, {
                          dateStyle: "short",
                          timeStyle: "short",
                        })}
                      </TableCell>
                      <TableCell align="right">
                        <Button
                          component={Link}
                          href={`/batch-screening/${batch.id}`}
                          size="small"
                          variant="outlined"
                        >
                          View
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </Stack>
        </Paper>
      </Stack>
    </Box>
  );
}
