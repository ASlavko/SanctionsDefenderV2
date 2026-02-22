"use client";

import { useState } from "react";
import {
    Box,
    Typography,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableRow,
    Chip,
    CircularProgress,
    Alert,
    Stack,
    ToggleButton,
    ToggleButtonGroup,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { fetchSanctionListKPIs, type SanctionListKPI } from "@/lib/api";

export default function SanctionListsPage() {
    const [days, setDays] = useState(1);

    const { data, isLoading, isError } = useQuery<SanctionListKPI[]>({
        queryKey: ["sanction-list-kpis", days],
        queryFn: () => fetchSanctionListKPIs(days),
        refetchInterval: 60000, // Refresh every minute
    });

    const handleDaysChange = (
        event: React.MouseEvent<HTMLElement>,
        newDays: number | null,
    ) => {
        if (newDays !== null) {
            setDays(newDays);
        }
    };

    if (isLoading) {
        return (
            <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "400px" }}>
                <CircularProgress />
            </Box>
        );
    }

    if (isError) {
        return (
            <Box sx={{ p: 3 }}>
                <Alert severity="error">Failed to load sanction list KPIs. Please try again later.</Alert>
            </Box>
        );
    }

    // Flag mapping for each sanction list using images for better compatibility
    const getFlagComponent = (source: string) => {
        const flagCodes: Record<string, string> = {
            "EU": "eu",
            "UK": "gb",
            "US": "us",
            "US_NON_SDN": "us"
        };
        const code = flagCodes[source];
        if (!code) return <Box sx={{ width: 48, height: 32, bgcolor: 'divider', borderRadius: 0.5 }} />;

        return (
            <Box
                component="img"
                src={`https://flagcdn.com/w80/${code}.png`}
                alt={source}
                sx={{
                    width: 48,
                    height: 'auto',
                    boxShadow: 2,
                    borderRadius: 0.5,
                    border: '1px solid',
                    borderColor: 'divider'
                }}
            />
        );
    };

    // Custom sort order
    const sortOrder = ["EU", "UK", "US", "US_NON_SDN"];
    const sortedData = data ? [...data].sort((a, b) => {
        const indexA = sortOrder.indexOf(a.source);
        const indexB = sortOrder.indexOf(b.source);
        // If not in sortOrder, put at end
        if (indexA === -1) return 1;
        if (indexB === -1) return -1;
        return indexA - indexB;
    }) : [];

    return (
        <Box>
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 3 }}>
                <Typography variant="h4" fontWeight={600}>
                    Sanction Lists Overview
                </Typography>
                <ToggleButtonGroup
                    value={days}
                    exclusive
                    onChange={handleDaysChange}
                    size="small"
                    color="primary"
                >
                    <ToggleButton value={1}>1 Day</ToggleButton>
                    <ToggleButton value={7}>7 Days</ToggleButton>
                    <ToggleButton value={30}>30 Days</ToggleButton>
                </ToggleButtonGroup>
            </Box>

            <Paper sx={{ p: 3 }}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell><strong>List</strong></TableCell>
                            <TableCell><strong>Last Updated</strong></TableCell>
                            <TableCell align="right"><strong>Total Entities</strong></TableCell>
                            <TableCell align="right"><strong>Added</strong></TableCell>
                            <TableCell align="right"><strong>Updated</strong></TableCell>
                            <TableCell align="right"><strong>Removed</strong></TableCell>
                            <TableCell><strong>Breakdown</strong></TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {sortedData.map((kpi) => (
                            <TableRow key={kpi.source} hover>
                                <TableCell>
                                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                                        {getFlagComponent(kpi.source)}
                                        <Chip label={kpi.source} color="primary" variant="outlined" />
                                    </Box>
                                </TableCell>
                                <TableCell>
                                    {kpi.last_update
                                        ? new Date(kpi.last_update).toLocaleString(undefined, {
                                            dateStyle: "medium",
                                            timeStyle: "short",
                                        })
                                        : "N/A"}
                                </TableCell>
                                <TableCell align="right">
                                    <Typography variant="h6" color="primary">
                                        {kpi.total_records.toLocaleString()}
                                    </Typography>
                                </TableCell>
                                <TableCell align="right">
                                    {kpi.records_added > 0 ? (
                                        <Chip label={`+${kpi.records_added}`} color="success" size="small" />
                                    ) : (
                                        <Typography color="text.secondary">0</Typography>
                                    )}
                                </TableCell>
                                <TableCell align="right">
                                    {kpi.records_updated > 0 ? (
                                        <Chip label={kpi.records_updated} color="warning" size="small" />
                                    ) : (
                                        <Typography color="text.secondary">0</Typography>
                                    )}
                                </TableCell>
                                <TableCell align="right">
                                    {kpi.records_removed > 0 ? (
                                        <Chip label={`-${kpi.records_removed}`} color="error" size="small" />
                                    ) : (
                                        <Typography color="text.secondary">0</Typography>
                                    )}
                                </TableCell>
                                <TableCell>
                                    <Stack spacing={0.5}>
                                        {kpi.breakdown.individual_count > 0 && (
                                            <Typography variant="caption" color="text.secondary">
                                                👤 Individuals: {kpi.breakdown.individual_count.toLocaleString()}
                                            </Typography>
                                        )}
                                        {kpi.breakdown.entity_count > 0 && (
                                            <Typography variant="caption" color="text.secondary">
                                                🏢 Entities: {kpi.breakdown.entity_count.toLocaleString()}
                                            </Typography>
                                        )}
                                        {kpi.breakdown.vessel_count > 0 && (
                                            <Typography variant="caption" color="text.secondary">
                                                🚢 Vessels: {kpi.breakdown.vessel_count.toLocaleString()}
                                            </Typography>
                                        )}
                                        {kpi.breakdown.aircraft_count > 0 && (
                                            <Typography variant="caption" color="text.secondary">
                                                ✈️ Aircraft: {kpi.breakdown.aircraft_count.toLocaleString()}
                                            </Typography>
                                        )}
                                        {kpi.breakdown.other_count > 0 && (
                                            <Typography variant="caption" color="text.secondary">
                                                ❓ Other: {kpi.breakdown.other_count.toLocaleString()}
                                            </Typography>
                                        )}
                                    </Stack>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </Paper>
        </Box>
    );
}
