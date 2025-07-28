import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Alert, Button } from '@mui/material';
import { DataGrid, GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import { useApi } from '../contexts/ApiContext';
import { useLanguage } from '../contexts/LanguageContext';
import { Link as RouterLink } from 'react-router-dom';

const Contributors: React.FC = () => {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { fetchData } = useApi();
  const { t } = useLanguage();

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 90 },
    {
      field: 'display_name',
      headerName: t('contributors.displayName'),
      width: 200,
      editable: false,
    },
    {
      field: 'wikipedia_username',
      headerName: t('contributors.wikipediaUsername'),
      width: 200,
      editable: false,
    },
    {
      field: 'overall_impact_score',
      headerName: t('contributors.impact'),
      type: 'number',
      width: 150,
    },
    {
      field: 'primary_language',
      headerName: t('contributors.language'),
      width: 120,
    },
    {
        field: 'contribution_type',
        headerName: t('contributors.type'),
        width: 180,
    },
    {
      field: 'actions',
      headerName: t('contributors.actions'),
      type: 'actions',
      width: 150,
      renderCell: (params: GridRenderCellParams) => (
        <Button
          variant="contained"
          size="small"
          component={RouterLink}
          to={`/contributors/${params.id}`}
        >
          {t('contributors.viewDetails')}
        </Button>
      ),
    },
  ];

  useEffect(() => {
    const getContributors = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchData('/contributors', { params: { limit: 2000 } });
        setRows(data);
      } catch (err) {
        setError(t('contributors.fetchError') || 'Failed to fetch contributors.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    getContributors();
  }, [fetchData, t]);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        {t('contributors.title')}
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
          localeText={{
            // DataGrid本身的本地化文本
            noRowsLabel: t('contributors.noData'),
            toolbarColumns: t('common.columns'),
            toolbarFilters: t('common.filter'),
            toolbarDensity: t('common.density'),
            toolbarExport: t('common.export'),
          }}
        />
      </Paper>
    </Box>
  );
};

export default Contributors; 