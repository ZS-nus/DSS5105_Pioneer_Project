// Chakra imports
import { SimpleGrid, Text, useColorModeValue,Flex, Box } from "@chakra-ui/react";
import Card from "components/card/Card.js";
import React, { useState, useMemo, useCallback } from "react";
import Information from "views/admin/profile/components/Information";
import LineChartMenu from 'views/admin/default/components/line_chart_menu';  

// Assets
export default function GeneralInformation(props) {
  const { data, ...rest } = props;
  // Chakra Color Mode
  const textColorPrimary = useColorModeValue("secondaryGray.900", "white");
  const textColorSecondary = "gray.400";
  const cardShadow = useColorModeValue(
    "0px 18px 40px rgba(112, 144, 176, 0.12)",
    "unset"
  );
  const textColor = useColorModeValue("secondaryGray.900", "white");

  const [selectedCompany, setSelectedCompany] = useState(null);

  const menuItems = useMemo(() => 
    data ? [...new Set(data.map(item => item.CompanyName))] : []
  , [data]);

  const handleCompanySelect = useCallback((company) => {
    setSelectedCompany(prev => company === prev ? null : company);
  }, []);

  return (
    <Card mb={{ base: "0px", "2xl": "20px" }} {...rest}>
      <Flex px="25px" mb="8px" justifyContent="space-between" align="center">
        <Text
            color={textColorPrimary}
            fontWeight='bold'
            fontSize='2xl'
            mt='10px'
            mb='4px'>
            ESG Analysis
        </Text>
        <LineChartMenu 
          menuItems={menuItems} 
          onSelectCompany={handleCompanySelect}
          selectedCompany={selectedCompany}
        />
      </Flex>
      <Text color={textColorPrimary} fontSize='md' me='26px' mb='40px'>
      This project focuses on automating the extraction and analysis of Environmental, Social, 
      and Governance (ESG) data from unstructured reports, such as corporate sustainability reports and financial filings.
      This project is essential for businesses, investors, and analysts who need accurate, reliable, and easily comparable ESG data to make informed decisions about corporate sustainability.
      </Text>
    </Card>
  );
}
