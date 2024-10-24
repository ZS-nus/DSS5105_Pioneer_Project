import React, { useState, useEffect } from 'react';
import {
  Box,
  Flex,
  Progress,
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
import { fetchESGScoreData } from '../../../../api';

const columnHelper = createColumnHelper();

export default function TopCreatorTable(props) {
  const [esgData, setESGData] = useState([]);
  // Set initial sorting state to sort by Final_ESG_score in descending order
  const [sorting, setSorting] = useState([
    { id: 'FinalESGScore', desc: true }
  ]);
  const textColor = useColorModeValue('secondaryGray.900', 'white');
  const textColorSecondary = useColorModeValue('secondaryGray.600', 'white');
  const borderColor = useColorModeValue('gray.200', 'whiteAlpha.100');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetchESGScoreData();
        // Process the data to get the latest report for each company
        const latestReports = response.data.reduce((acc, curr) => {
          if (!acc[curr.CompanyID] || curr.ReportYear > acc[curr.CompanyID].ReportYear) {
            acc[curr.CompanyID] = curr;
          }
          return acc;
        }, {});
        setESGData(Object.values(latestReports));
      } catch (error) {
        console.error('Error fetching ESG data:', error);
      }
    };
    fetchData();
  }, []);

  const columns = [
    columnHelper.accessor('CompanyName', {
      id: 'CompanyName',
      header: () => (
        <Text
          justifyContent="space-between"
          align="center"
          fontSize={{ sm: '10px', lg: '12px' }}
          color="gray.400"
        >
          Company
        </Text>
      ),
      cell: (info) => (
        <Flex align="center">
          <Text color={textColor} fontSize="sm" fontWeight="600">
            {info.getValue()}
          </Text>
        </Flex>
      ),
    }),
    columnHelper.accessor('ReportYear', {
      id: 'ReportYear',
      header: () => (
        <Text
          justifyContent="space-between"
          align="center"
          fontSize={{ sm: '10px', lg: '12px' }}
          color="gray.400"
        >
          Report Year
        </Text>
      ),
      cell: (info) => (
        <Text color={textColorSecondary} fontSize="sm" fontWeight="500">
          {info.getValue()}
        </Text>
      ),
    }),
    columnHelper.accessor('Final_ESG_score', {
      id: 'FinalESGScore',
      header: () => (
        <Text
          justifyContent="space-between"
          align="center"
          fontSize={{ sm: '10px', lg: '12px' }}
          color="gray.400"
        >
          ESG Score
        </Text>
      ),
      cell: (info) => {
        const score = info.getValue();
        // Scale the score to 0-100 range for the Progress component
        const scaledScore = score !== undefined ? (score / 10) * 100 : 0;
        return (
          <Flex align="center">
            <Progress
              variant="table"
              colorScheme="brandScheme"
              h="8px"
              w="108px"
              value={scaledScore}
              max={100}  // Explicitly set the maximum value
            />
            <Text ml={2} color={textColorSecondary} fontSize="sm" fontWeight="500">
              {score !== undefined ? score.toFixed(2) : 'N/A'}
            </Text>
          </Flex>
        );
      },
    }),
  ];

  const table = useReactTable({
    data: esgData,
    columns,
    state: {
      sorting,
    },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    debugTable: true,
  });

  return (
    <Flex
      direction="column"
      w="100%"
      overflowX={{ sm: 'scroll', lg: 'hidden' }}
    >
      <Flex
        align={{ sm: 'flex-start', lg: 'center' }}
        justify="space-between"
        w="100%"
        px="22px"
        pb="20px"
        mb="10px"
        boxShadow="0px 40px 58px -20px rgba(112, 144, 176, 0.26)"
      >
        <Text color={textColor} fontSize="xl" fontWeight="600">
          ESG Ranking
        </Text>
      </Flex>
      <Box>
        <Table variant="simple" color="gray.500" mt="12px">
          <Thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <Tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
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
                          header.getContext(),
                        )}
                        {{
                          asc: '',
                          desc: '',
                        }[header.column.getIsSorted()] ?? null}
                      </Flex>
                    </Th>
                  );
                })}
              </Tr>
            ))}
          </Thead>
          <Tbody>
            {table
              .getRowModel()
              .rows.map((row) => {
                return (
                  <Tr key={row.id}>
                    {row.getVisibleCells().map((cell) => {
                      return (
                        <Td
                          key={cell.id}
                          fontSize={{ sm: '14px' }}
                          minW={{ sm: '150px', md: '200px', lg: 'auto' }}
                          borderColor="transparent"
                        >
                          {flexRender(
                            cell.column.columnDef.cell,
                            cell.getContext(),
                          )}
                        </Td>
                      );
                    })}
                  </Tr>
                );
              })}
          </Tbody>
        </Table>
      </Box>
    </Flex>
  );
}