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
import { G_score_line_option } from "variables/charts"; 

const processChartData = (data) => {
  const companyData = {};
  data.forEach(item => {
    if (!companyData[item.CompanyName]) {
      companyData[item.CompanyName] = [];
    }
    companyData[item.CompanyName].push({
      x: item.Year,
      y: item.Governance_Score
    });
  });

  return Object.entries(companyData).map(([name, data]) => ({
    name,
    data: data.sort((a, b) => a.x - b.x)
  }));
};

export default function TotalSpent(props) {
  const { data, ...rest } = props;

  const textColor = useColorModeValue("secondaryGray.900", "white");

  const [chartData, setChartData] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState(null);

  useEffect(() => {
    if (data && data.length > 0) {
      const processedData = processChartData(data);
      setChartData(processedData);
    }
  }, [data]);

  const menuItems = useMemo(() => 
    chartData.map(item => item.name)
  , [chartData]);

  const currentChartData = useMemo(() => {
    if (selectedCompany) {
      return chartData.filter(entry => entry.name === selectedCompany);
    }
    return chartData.length > 0 ? [chartData[0]] : [];
  }, [chartData, selectedCompany]);

  const updatedChartOptions = useMemo(() => ({
    ...G_score_line_option,
    xaxis: {
      ...G_score_line_option.xaxis,
      type: 'numeric',
      labels: {
        formatter: function(value) {
          return Math.round(value);
        }
      }
    },
  }), []);

  const handleCompanySelect = useCallback((company) => {
    setSelectedCompany(prev => company === prev ? null : company);
  }, []);

  if (!data || data.length === 0) {
    return (
      <Box>
        <Text>No data available to display.</Text>
      </Box>
    );
  }

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
          textAlign="left"
          alignSelf="flex-start"
        >
          Governance Score Trend by Company (3-Year Forecast)
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
              key={selectedCompany || 'default'}
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
