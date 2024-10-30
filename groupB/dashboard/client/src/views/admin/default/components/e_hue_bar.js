// Chakra imports
import {
  Box,
  Button,
  Flex,
  Icon,
  Text,
  useColorModeValue,
} from "@chakra-ui/react";
import Card from "components/card/Card.js";
// Custom components
import BarChart from "components/charts/BarChart";
import React, { useState, useEffect, useCallback, useMemo } from "react";
import LineChartMenu from './line_chart_menu';
import { MdBarChart } from "react-icons/md";
import { barChartOptionsConsumption } from "variables/charts";

const processChartData = (data) => {
  const companyData = {};
  data.forEach(item => {
    if (!companyData[item.CompanyName]) {
      companyData[item.CompanyName] = [];
    }
    companyData[item.CompanyName].push({
      x: item.ReportYear,
      y: item.Environmental_Score
    });
  });

  return Object.entries(companyData).map(([name, data]) => ({
    name,
    data: data.sort((a, b) => a.x - b.x)
  }));
};

export default function EHueBar(props) {
  const { data, ...rest } = props;

  // Chakra Color Mode
  const textColor = useColorModeValue("secondaryGray.900", "white");
  const iconColor = useColorModeValue("brand.500", "white");
  const bgButton = useColorModeValue("secondaryGray.300", "whiteAlpha.100");
  const bgHover = useColorModeValue(
    { bg: "secondaryGray.400" },
    { bg: "whiteAlpha.50" }
  );
  const bgFocus = useColorModeValue(
    { bg: "secondaryGray.300" },
    { bg: "whiteAlpha.100" }
  );

  // Add state management
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
    <Card align='center' direction='column' w='100%' {...rest}>
      <Flex align='center' w='100%' px='15px' py='10px' justifyContent="space-between">
        <Text
          me='auto'
          color={textColor}
          fontSize='xl'
          fontWeight='700'
          lineHeight='100%'>
          Company Environmental Score
        </Text>
          <LineChartMenu 
          menuItems={menuItems} 
          onSelectCompany={handleCompanySelect}
          selectedCompany={selectedCompany}
        />
      </Flex>

      <Box h='240px' mt='auto'>
        {currentChartData.length > 0 ? (
          <BarChart
            key={selectedCompany || 'default'}
            chartData={currentChartData}
            chartOptions={barChartOptionsConsumption}
          />
        ) : (
          <Text>No data available for the selected company.</Text>
        )}
      </Box>
    </Card>
  );
}
