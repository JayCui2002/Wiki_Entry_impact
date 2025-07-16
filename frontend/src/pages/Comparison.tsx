import React, { useState } from 'react';
import { Box, Typography, TextField, Button, Alert, Paper } from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { useApi } from '../contexts/ApiContext';

const Comparison: React.FC = () => {
  const { fetchData } = useApi();
  const [ids, setIds] = useState('');
  const [rows, setRows] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 90 },
    { field: 'display_name', headerName: 'Display Name', width: 200 },
    { field: 'wikipedia_username', headerName: 'Username', width: 180 },
    { field: 'overall_impact_score', headerName: 'Impact', width: 120, type: 'number' },
  ];

  const handleCompare = async () => {
    setError(null);
    try {
      const data = await fetchData('/contributors/compare/', { params: { contributor_ids: ids } });
      setRows(data.contributors || []);
    } catch (err) {
      setError('Failed to fetch comparison data');
      console.error(err);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Comparison
      </Typography>
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <TextField
          label="Contributor IDs"
          variant="outlined"
          size="small"
          value={ids}
          onChange={(e) => setIds(e.target.value)}
          helperText="Enter comma-separated IDs"
        />
        <Button variant="contained" onClick={handleCompare}>
          Compare
        </Button>
      </Box>
      {error && <Alert severity="error">{error}</Alert>}
      <Paper sx={{ height: 400, width: '100%' }}>
        <DataGrid rows={rows} columns={columns} disableRowSelectionOnClick pageSizeOptions={[5, 10]} />
      </Paper>
    </Box>
  );
};

export default Comparison;
