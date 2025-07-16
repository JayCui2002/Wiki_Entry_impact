import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Alert, Button } from '@mui/material';
import { DataGrid, GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import { useApi } from '../contexts/ApiContext';
import { Link as RouterLink } from 'react-router-dom';

const columns: GridColDef[] = [
  { field: 'id', headerName: 'ID', width: 90 },
  {
    field: 'display_name',
    headerName: 'Display Name',
    width: 200,
    editable: false,
  },
  {
    field: 'wikipedia_username',
    headerName: 'Wikipedia Username',
    width: 200,
    editable: false,
  },
  {
    field: 'overall_impact_score',
    headerName: 'Impact Score',
    type: 'number',
    width: 150,
  },
  {
    field: 'primary_language',
    headerName: 'Language',
    width: 120,
  },
  {
      field: 'contribution_type',
      headerName: 'Contributor Type',
      width: 180,
  },
  {
    field: 'actions',
    headerName: 'Actions',
    type: 'actions',
    width: 150,
    renderCell: (params: GridRenderCellParams) => (
      <Button
        variant="contained"
        size="small"
        component={RouterLink}
        to={`/contributors/${params.id}`}
      >
        View Details
      </Button>
    ),
  },
];

const Contributors: React.FC = () => {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { fetchData } = useApi();

  useEffect(() => {
    const getContributors = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchData('/contributors', { params: { limit: 2000 } });
        setRows(data);
      } catch (err) {
        setError('Failed to fetch contributors.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    getContributors();
  }, [fetchData]);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Contributors
      </Typography>
      {error && <Alert severity="error">{error}</Alert>}
      <Paper sx={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={rows}
          columns={columns}
          loading={loading}
          initialState={{
            pagination: {
              paginationModel: {
                pageSize: 10,
              },
            },
          }}
          pageSizeOptions={[10, 25, 50]}
          checkboxSelection
          disableRowSelectionOnClick
        />
      </Paper>
    </Box>
  );
};

export default Contributors; 