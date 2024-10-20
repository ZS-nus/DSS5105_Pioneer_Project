import React, { useState, useEffect, useCallback, useMemo } from "react";
import {
  Box,
  Flex,
  Text,
  useColorModeValue,
} from "@chakra-ui/react";
import Card from "components/card/Card.js";
import LineChart from "components/charts/LineChart";
import LineChartMenu from 'views/admin/default/components/line_chart_menu';  
import { ESG_predict_line_option } from "variables/charts"; 
import { fetchESGPredict } from "api"; // Import the fetchESGPredict function

export default function TotalSpent(props) {
  const { ...rest } = props;

  const textColor = useColorModeValue("secondaryGray.900", "white");

  const [chartData, setChartData] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetchESGPredict();
        const processedData = esg_score_line(response.data);
        console.log("response:", response.data);
        setChartData(processedData);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching ESG predict data:', err);
        setError('Failed to fetch ESG predict data');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const menuItems = useMemo(() => 
    chartData ? [...new Set(chartData.map(item => item.name))] : []
  , [chartData]);

  const currentChartData = useMemo(() => {
    if (selectedCompany) {
      const selectedData = chartData.filter(entry => entry.name === selectedCompany);
      console.log("Selected company data:", selectedData);
      return selectedData;
    } else {
      return chartData.length > 0 ? [chartData[0]] : [];
    }
  }, [chartData, selectedCompany]);

  const handleCompanySelect = useCallback((company) => {
    setSelectedCompany(prev => company === prev ? null : company);
  }, []);

  if (loading) return <Box><Text>Loading...</Text></Box>;
  if (error) return <Box><Text>Error: {error}</Text></Box>;

  if (!chartData || chartData.length === 0) {
    return (
      <Box>
        <Text>No data available to display.</Text>
      </Box>
    );
  }

  const years = [...new Set(chartData.flatMap(item => item.data.map(d => d.x)))].sort((a, b) => a - b);

  const updatedChartOptions = {
    ...ESG_predict_line_option,
    xaxis: {
      ...ESG_predict_line_option.xaxis,
      categories: years,
    },
  };

  return (
    <Card
      justifyContent='center'
      align='center'
      direction='column'
      w='100%'
      mb='0px'
      {...rest}>
      <Flex px="25px" mb="8px" justifyContent="space-between" align="center">
        <Text
          color={textColor}
          fontSize="18px"
          fontWeight="700"
          lineHeight="100%"
        >
          Predicted ESG Score by Company
        </Text>
        <LineChartMenu 
          menuItems={menuItems} 
          onSelectCompany={handleCompanySelect}
          selectedCompany={selectedCompany}
        />
      </Flex>
      <Flex w='100%' flexDirection={{ base: "column", lg: "row" }}>
        <Box minH='260px' minW='100%' mt='auto'>
          {currentChartData.length > 0 ? (
            <LineChart
              key={selectedCompany}
              chartData={currentChartData}
              chartOptions={updatedChartOptions}
            />
          ) : (
            <Text>No data available for the selected company.</Text>
          )}
        </Box>
      </Flex>
    </Card>
  );
}

// Helper function to process the data
function esg_score_line(data) {
  const companyData = {};
  data.forEach(item => {
    if (!companyData[item.CompanyName]) {
      companyData[item.CompanyName] = [];
    }
    companyData[item.CompanyName].push({
      x: item.Year,
      y: item.ESG_score,
      dataType: item.Data_Type
    });
  });

  return Object.entries(companyData).map(([name, data]) => ({
    name,
    data: data.sort((a, b) => a.x - b.x)
  }));
}
