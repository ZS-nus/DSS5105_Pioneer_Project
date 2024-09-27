import React from "react";

// Chakra imports
import { Box, Flex, Icon, Text, useColorModeValue } from "@chakra-ui/react";
import BarChart from "components/charts/BarChart";

// Custom components
import Card from "components/card/Card.js";
import {
  barChartDataDailyTraffic,
  g_barChartOptionsDailyTraffic,
  createBarChartData,
} from "variables/charts";



export default function EBarChart(props) {
  const { data, ...rest } = props; // Destructure data from props



  // Chakra Color Mode
  const textColor = useColorModeValue("secondaryGray.900", "white");

  // Check if data is null or empty
  if (!data || data.length === 0) {
    return (
      <Box>
        <Text>No data available to display.</Text>
      </Box>
    );
  }


  // Set x-axis categories to company names
  const xAxisCategories = data.map(item => item.CompanyName);


  // Ensure chartData is structured correctly for ApexCharts
  const finalChartData = [
    {
      name: "Environmental Scores",
      data: createBarChartData(data).data, // This should be an array of env_score_weighted values
    },
  ];


  return (
    <Card align='center' direction='column' w='100%' {...rest}>
      <Flex justify='space-between' align='start' px='10px' pt='5px'>
        <Flex flexDirection='column' align='start' me='20px'>
        <Flex w='100%'>
          <Text
              color={textColor}
              fontSize='20px'
              fontWeight='700'
              lineHeight='100%'>
              Governance Rating
            </Text>
          </Flex>
          <Flex w='100%'>
          </Flex>
          <Flex align='end'>
            {/* <Text
              color={textColor}
              fontSize='34px'
              fontWeight='700'
              lineHeight='100%'>
              2.579
            </Text>
            <Text
              ms='6px'
              color='secondaryGray.600'
              fontSize='sm'
              fontWeight='500'>
              Visitors
            </Text> */}
          </Flex>
        </Flex>
        {/* <Flex align='center'>
          <Icon as={RiArrowUpSFill} color='green.500' />
          <Text color='green.500' fontSize='sm' fontWeight='700'>
            +2.45%
          </Text>
        </Flex> */}
      </Flex>
      <Box h='240px' mt='auto'>
        <BarChart
          chartData={finalChartData}// Pass the categories to the chart
          chartOptions={{ ...g_barChartOptionsDailyTraffic, xaxis: { ...g_barChartOptionsDailyTraffic.xaxis, categories: xAxisCategories } }} // Update x-axis categories in options
        />
      </Box>
    </Card>
  );
}
