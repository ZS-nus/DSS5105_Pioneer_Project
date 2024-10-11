import React, { useMemo } from "react";

// Chakra imports
import { Box, Flex, Icon, Text, useColorModeValue } from "@chakra-ui/react";
import BarChart from "components/charts/BarChart";

// Custom components
import Card from "components/card/Card.js";
import {
  barChartDataDailyTraffic,
  s_barChartOptionsDailyTraffic,
  s_barChartData,
} from "variables/charts";



export default function SBarChart(props) {
  const { data, ...rest } = props; // Destructure data from props

  const textColor = useColorModeValue("secondaryGray.900", "white");

  // Move useMemo to the top level
  const { chartData, labels, latestYear } = useMemo(() => {
    if (!data || data.length === 0) {
      return { chartData: [], labels: [], latestYear: null };
    }
    const { labels, data: chartData } = s_barChartData(data);
    const latestYear = Math.max(...data.map(item => item.ReportYear));
    return { chartData, labels, latestYear };
  }, [data]);

  // Check if data is null or empty
  if (!data || data.length === 0) {
    return (
      <Box>
        <Text>No data available to display.</Text>
      </Box>
    );
  }

  const finalChartData = [
    {
      name: "Social Scores",
      data: chartData,
    },
  ];

  const chartOptions = {
    ...s_barChartOptionsDailyTraffic,
    xaxis: {
      ...s_barChartOptionsDailyTraffic.xaxis,
      categories: labels,
    },
  };


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
              Social Rating {latestYear ? `(${latestYear})` : ''}
            </Text>
          </Flex>
        </Flex>
      </Flex>
      <Box h='240px' mt='auto'>
        <BarChart
          chartData={finalChartData}
          chartOptions={chartOptions}
        />
      </Box>
    </Card>
  );
}