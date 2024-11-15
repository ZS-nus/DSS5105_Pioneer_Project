'use client';
import React, { useEffect } from 'react';
import { fetchEnvMetrics } from '../../../../api';
import {
  Box,
  Flex,
  Table,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tr,
  useColorModeValue,
} from '@chakra-ui/react';
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table';
import Card from 'components/card/Card';
import LineChartMenu from 'views/admin/default/components/line_chart_menu';  

const columnHelper = createColumnHelper();

export default function ComplexTable({ onCompanySelect }) {
  const [data, setData] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);
  const [sorting, setSorting] = React.useState([]);
  const [selectedCompany, setSelectedCompany] = React.useState(null);

  const textColor = useColorModeValue('secondaryGray.900', 'white');
  const borderColor = useColorModeValue('gray.200', 'whiteAlpha.100');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetchEnvMetrics();
        setData(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Error fetching data');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const columns = [
    columnHelper.accessor('CompanyName', {
      id: 'company_name',
      header: () => (
        <Text
          justifyContent="space-between"
          align="left"
          fontSize={{ sm: '10px', lg: '12px' }}
          color="gray.400"
        >
          NAME
        </Text>
      ),
      cell: (info) => (
        <Flex align="center">
          <Text color={textColor} fontSize="md" fontWeight="700">
            {info.getValue()}
          </Text>
        </Flex>
      ),
    }),
    columnHelper.accessor('ReportYear', {
      id: 'report_year',
      header: () => (
        <Text
          justifyContent="space-between"
          align="left"
          fontSize={{ sm: '10px', lg: '12px' }}
          color="gray.400"
        >
          Year
        </Text>
      ),
      cell: (info) => (
        <Flex align="center">
          <Text color={textColor} fontSize="md" fontWeight="700">
            {info.getValue()}
          </Text>
        </Flex>
      ),
    }),
    columnHelper.accessor('EnergyConsumption_score', {
      id: 'EnergyConsumption_score',
      header: () => (
        <Text
          justifyContent="space-between"
          align="left"
          fontSize={{ sm: '10px', lg: '12px' }}
          color="gray.400"
        >
          Energy Used
        </Text>
      ),
      cell: (info) => (
        <Flex align="left">
          <Text color={textColor} fontSize="md" fontWeight="700">
            {info.getValue()}
          </Text>
        </Flex>
      ),
    }),
    columnHelper.accessor('GHGEmissions_score', {
      id: 'GHGEmissions_score',
      header: () => (
        <Text
          justifyContent="space-between"
          align="left"
          fontSize={{ sm: '10px', lg: '12px' }}
          color="gray.400"
        >
          GHG Emissions
        </Text>
      ),
      cell: (info) => (
        <Flex align="center">
          <Text color={textColor} fontSize="md" fontWeight="700">
            {info.getValue()}
          </Text>
        </Flex>
      ),
    }),
    columnHelper.accessor('WaterUsage_score', {
      id: 'WaterUsage_score',
      header: () => (
        <Text
          justifyContent="space-between"
          align="left"
          fontSize={{ sm: '10px', lg: '12px' }}
          color="gray.400"
        >
          Water Usage
        </Text>
      ),
      cell: (info) => (
        <Flex align="left">
          <Text color={textColor} fontSize="md" fontWeight="700">
            {info.getValue()}
          </Text>
        </Flex>
      ),
    }),
    columnHelper.accessor('WasteGenerated_score', {
      id: 'WasteGenerated_score',
      header: () => (
        <Text
          justifyContent="space-between"
          align="left"
          fontSize={{ sm: '10px', lg: '12px' }}
          color="gray.400"
        >
          Waste Generated
        </Text>
      ),
      cell: (info) => (
        <Flex align="center">
          <Text color={textColor} fontSize="md" fontWeight="700">
            {info.getValue()}
          </Text>
        </Flex>
      ),
    }),
  ];

  const menuItems = React.useMemo(() => 
    [...new Set(data.map(item => item.CompanyName))],
    [data]
  );

  const handleCompanySelect = React.useCallback((company) => {
    setSelectedCompany(company);
    if (onCompanySelect) {
      onCompanySelect(company);
    }
  }, [onCompanySelect]);

  const filteredData = React.useMemo(() => {
    if (selectedCompany) {
      return data.filter(item => item.CompanyName === selectedCompany);
    }
    const firstCompany = data.length > 0 ? data[0].CompanyName : null;
    return firstCompany ? data.filter(item => item.CompanyName === firstCompany) : [];
  }, [data, selectedCompany]);

  useEffect(() => {
    if (data.length > 0 && !selectedCompany) {
      setSelectedCompany(data[0].CompanyName);
    }
  }, [data, selectedCompany]);

  const table = useReactTable({
    data: filteredData,
    columns,
    state: {
      sorting,
    },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    debugTable: true,
  });

  console.log('Table data:', table.getRowModel().rows);

  if (loading) return <Text>Loading...</Text>;
  if (error) return <Text>Error: {error}</Text>;

  return (
    <Card
      flexDirection="column"
      w="100%"
      px="0px"
      overflowX={{ sm: 'scroll', lg: 'hidden' }}
    >
      <Flex px="25px" mb="8px" justifyContent="space-between" align="center">
        <Text
          color={textColor}
          fontSize="22px"
          fontWeight="700"
          lineHeight="100%"
        >
          Environmental Metrics
        </Text>
        <LineChartMenu 
          menuItems={menuItems} 
          onSelectCompany={handleCompanySelect}
          selectedCompany={selectedCompany}
        />
      </Flex>
      <Box>
        <Table variant="simple" color="gray.500" mb="24px" mt="12px">
          <Thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <Tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <Th
                    key={header.id}
                    colSpan={header.colSpan}
                    pe="10px"
                    borderColor={borderColor}
                    cursor="pointer"
                    onClick={header.column.getToggleSortingHandler()}
                  >
                    <Flex
                      justifyContent="space-between"
                      align="center"
                      fontSize={{ sm: '10px', lg: '12px' }}
                      color="gray.400"
                    >
                      {flexRender(
                        header.column.columnDef.header,
                        header.getContext()
                      )}
                      {{
                        asc: '',
                        desc: '',
                      }[header.column.getIsSorted()] ?? null}
                    </Flex>
                  </Th>
                ))}
              </Tr>
            ))}
          </Thead>
          <Tbody>
            {table
              .getRowModel()
              .rows.slice(0, 11)
              .map((row) => (
                <Tr key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <Td
                      key={cell.id}
                      fontSize={{ sm: '14px' }}
                      minW={{ sm: '150px', md: '200px', lg: 'auto' }}
                      borderColor="transparent"
                    >
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </Td>
                  ))}
                </Tr>
              ))}
          </Tbody>
        </Table>
      </Box>
    </Card>
  );
}
