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
import { e_score_line, E_score_line_option } from "variables/charts"; 

export default function TotalSpent(props) {
  const { data, ...rest } = props;

  const textColor = useColorModeValue("secondaryGray.900", "white");

  const [chartData, setChartData] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState(null);

  useEffect(() => {
    if (data && data.length > 0) {
      const processedData = e_score_line(data);
      // console.log("Processed chart data:", processedData);
      setChartData(processedData);
    }
  }, [data]);

  const menuItems = useMemo(() => 
    data ? [...new Set(data.map(item => item.CompanyName))] : []
  , [data]);

  const currentChartData = useMemo(() => {
    if (selectedCompany) {
      const selectedData = chartData.filter(entry => entry.name === selectedCompany);
      console.log("Selected company data:", selectedData);
      return selectedData;
    } else {
      // console.log("Setting default data:", chartData.length > 0 ? [chartData[0]] : []);
      return chartData.length > 0 ? [chartData[0]] : [];
    }
  }, [chartData, selectedCompany]);

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

  const years = [...new Set(data.map(item => item.ReportYear))].sort((a, b) => a - b);

  const updatedChartOptions = {
    ...E_score_line_option,
    xaxis: {
      categories: years,
    },
  };

  // console.log("Rendering with currentChartData:", currentChartData);

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
          Environmental Score Trend by Company
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
              key={selectedCompany || 'default'} // Add this line
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