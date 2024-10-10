// Chakra imports
import { Box, Flex, Text, Select, useColorModeValue } from "@chakra-ui/react";
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
  const cardColor = useColorModeValue("white", "navy.700");
  const cardShadow = useColorModeValue(
    "0px 18px 40px rgba(112, 144, 176, 0.12)",
    "unset"
  );
  return (
    <Card p='20px' align='center' direction='column' w='100%' {...rest}>
      <Flex
        px={{ base: "0px", "2xl": "10px" }}
        justifyContent='space-between'
        alignItems='center'
        w='100%'
        mb='8px'>
        <Text color={textColor} fontSize='md' fontWeight='600' mt='4px'>
          ESG Metrics Pie Chart
        </Text>
        {/* <Select
          fontSize='sm'
          variant='subtle'
          defaultValue='monthly'
          width='unset'
          fontWeight='700'>
          <option value='daily'>Daily</option>
          <option value='monthly'>Monthly</option>
          <option value='yearly'>Yearly</option>
        </Select> */}
      </Flex>

      <PieChart
        h='100%'
        w='100%'
        chartData={ESG_metrics_pieChartData}
        chartOptions={ESG_metrics_pieChartOptions}
      />

      <VSeparator mx={{ base: "60px", xl: "60px", "2xl": "60px" }} />
<Card
  bg={cardColor}
  boxShadow={cardShadow}
  w='100%'
  p='15px'
  px='20px'
  mt='15px'
  mx='auto'>
  <Flex flexDirection='column'>
    <Flex flexDirection='row' justifyContent='space-between' mb='15px'>
      <Flex direction='column' py='5px'>
        <Flex align='center'>
          <Box h='8px' w='8px' bg='#38ef7d' borderRadius='50%' me='4px' />
          <Text
            fontSize='xs'
            color='secondaryGray.600'
            fontWeight='700'
            mb='5px'>
            Environmental
          </Text>
        </Flex>
        <Text fontSize='lg' color={textColor} fontWeight='700'>
          30%
        </Text>
      </Flex>
      <Flex direction='column' py='5px' me='10px'>
        <Flex align='center'>
          <Box h='8px' w='8px' bg='#6AD2FF' borderRadius='50%' me='4px' />
          <Text
            fontSize='xs'
            color='secondaryGray.600'
            fontWeight='700'
            mb='5px'>
            Social
          </Text>
        </Flex>
        <Text fontSize='lg' color={textColor} fontWeight='700'>
          30%
        </Text>
      </Flex>
      <Flex direction='column' py='5px' me='10px'>
        <Flex align='center'>
          <Box h='8px' w='8px' bg='#f7b733' borderRadius='50%' me='4px' />
          <Text
            fontSize='xs'
            color='secondaryGray.600'
            fontWeight='700'
            mb='5px'>
            Governance
          </Text>
        </Flex>
        <Text fontSize='lg' color={textColor} fontWeight='700'>
          20%
        </Text>
      </Flex>
    </Flex>
  </Flex>
</Card>



    </Card>
  );
}
