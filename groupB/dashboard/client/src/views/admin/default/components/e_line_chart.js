// Chakra imports
import {
  Box,
  Flex,
  Text,
  useColorModeValue,
} from "@chakra-ui/react";
// Custom components
import Card from "components/card/Card.js";
import LineChart from "components/charts/LineChart";
import React, { useState, useEffect } from "react"; // Import useState
import LineChartMenu from 'views/admin/default/components/line_chart_menu';  
import { e_score_line } from "variables/charts"; 

export default function TotalSpent(props) {
  const { data, ...rest } = props; // Destructure data from props

  // Chakra Color Mode
  const textColor = useColorModeValue("secondaryGray.900", "white");
  const bgFocus = useColorModeValue(
    { bg: "secondaryGray.300" },
    { bg: "whiteAlpha.100" }
  );

  // Get the company names for the menu and ensure they are unique
  const menuItems = data ? [...new Set(data.map(item => item.CompanyName))] : [];

  // Set up state for the selected company
  const [selectedCompany, setSelectedCompany] = useState(menuItems[0]); // Default to the first company



  // Update selectedCompany when menuItems change
  useEffect(() => {
    if (menuItems.length > 0) {
      setSelectedCompany(menuItems[0]);
    }
  }, [menuItems]);

  console.log("Selected Company: ", selectedCompany);

  // Check if data is null or empty
  if (!data || data.length === 0) {
    return (
      <Box>
        <Text>No data available to display.</Text>
      </Box>
    );
  }

  // Prepare data for the line chart
  const chartData = e_score_line(data);

  // Filter e_line_chart_data based on the selected company
  const e_line_chart_data = chartData
    .filter(entry => entry.name === selectedCompany)
    .slice(0, 1); // Ensure only one line is displayed

  console.log("e_line_chart_data: ", e_line_chart_data);

  // Extract unique years for x-axis categories
  const years = [...new Set(data.map(item => item.ReportYear))];

  // Update chart options with the extracted years
  const updatedChartOptions = {
    xaxis: {
      categories: years, // Set the categories to the extracted years
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
          Company Environment Score Trend
        </Text>
        <LineChartMenu 
          menuItems={menuItems} 
          onSelectCompany={setSelectedCompany} // Pass the function to update the selected company
        />
      </Flex>
      <Flex w='100%' flexDirection={{ base: "column", lg: "row" }}>
        <Box minH='260px' minW='100%' mt='auto'>
          <LineChart
            chartData={e_line_chart_data} // Use prepared chart data
            chartOptions={updatedChartOptions}
          />
        </Box>
      </Flex>
    </Card>
  );
}