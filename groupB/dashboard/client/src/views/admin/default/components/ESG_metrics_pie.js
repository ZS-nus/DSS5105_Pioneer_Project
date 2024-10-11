// Chakra imports
import { Box, Flex, Text, useColorModeValue } from "@chakra-ui/react";
// Custom components
import Card from "components/card/Card.js";
import PieChart from "components/charts/PieChart";
import { ESG_metrics_pieChartData, ESG_metrics_pieChartOptions } from "variables/charts";
import { VSeparator } from "components/separator/Separator";
import React from "react";

export default function Conversion(props) {
  const { ...rest } = props;

  // Chakra Color Mode
  const textColor = useColorModeValue("secondaryGray.900", "white");

  return (
    <Card p='10px' align='center' direction='column' w='100%' h='100%' {...rest}>

      <Text
        color={textColor}
        fontWeight='bold'
        fontSize='2xl'
        mt='10px'
        mb='4px'>
        ESG Metrics 
      </Text>
      <br></br>
      <br></br>
      <br></br> 
      {/* <Flex justify="center" align="center" w="100%" h="calc(100% - 24px)"> */}
        {/* <Box w="100%" h="100%"> */}
          <PieChart
            chartData={ESG_metrics_pieChartData}
            chartOptions={ESG_metrics_pieChartOptions}
          />
        {/* </Box> */}
      {/* </Flex> */}
    </Card>
  );
}
