// Chakra imports
import { SimpleGrid, Text, useColorModeValue, Flex, Box, VStack } from "@chakra-ui/react";
import Card from "components/card/Card.js";
import React, { useState, useEffect, useCallback, useMemo } from "react";
import Information from "views/admin/profile/components/Information";
import LineChartMenu from 'views/admin/default/components/line_chart_menu';  
import { fetchESGCommentary } from '../../../../api';  // Import the function
import { debounce } from 'lodash';  // Import debounce from lodash

// Assets
const processData = (data) => {
  const companyData = {};
  data.forEach(item => {
    if (!companyData[item.CompanyName]) {
      companyData[item.CompanyName] = item;
    }
  });
  return companyData;
};

export default function ESG_analysis(props) {
  const { data, ...rest } = props;
  // Chakra Color Mode
  const textColorPrimary = useColorModeValue("secondaryGray.900", "white");
  const textColorSecondary = "gray.400";
  const cardShadow = useColorModeValue(
    "0px 18px 40px rgba(112, 144, 176, 0.12)",
    "unset"
  );
  const textColor = useColorModeValue("secondaryGray.900", "white");

  const [processedData, setProcessedData] = useState({});
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [commentary, setCommentary] = useState("");

  const fetchCommentary = useCallback(
    debounce((companyId) => {
      if (companyId) {
        fetchESGCommentary(companyId)
          .then(response => {
            setCommentary(response.data.commentary);
          })
          .catch(error => {
            console.error("Error fetching commentary:", error);
            setCommentary("Failed to fetch commentary.");
          });
      }
    }, 300),
    []
  );

  useEffect(() => {
    if (data && data.length > 0) {
      const processed = processData(data);
      setProcessedData(processed);
      const firstCompanyName = data[0].CompanyName;  // Change this line
      const firstCompanyId = data[0].CompanyID;
      setSelectedCompany(firstCompanyName);  // Set the name, not the ID
      fetchCommentary(firstCompanyId);  // Still fetch commentary using the ID
    }
  }, [data, fetchCommentary]);

  const menuItems = useMemo(() => 
    Object.keys(processedData)
  , [processedData]);

  const handleCompanySelect = useCallback((companyName) => {
    const selectedCompanyData = processedData[companyName];
    if (selectedCompanyData) {
      setSelectedCompany(companyName);
      fetchCommentary(selectedCompanyData.CompanyID);
    }
  }, [fetchCommentary, processedData]);

  return (
    <Card mb={{ base: "0px", "2xl": "20px" }} {...rest}>
      <Flex mb="8px" justifyContent="space-between" align="center">
        <VStack align="start" spacing={0}>
          <Text
            color={textColorPrimary}
            fontWeight='bold'
            fontSize='2xl'
            mt='10px'
            mb='4px'>
            ESG Analysis
          </Text>
          <Text
            color={textColorPrimary}
            fontSize='xl'>
            {selectedCompany || "Select a company"}
          </Text>
        </VStack>
        <LineChartMenu 
          menuItems={menuItems} 
          onSelectCompany={handleCompanySelect}
          selectedCompany={selectedCompany}
        />
      </Flex>
      <Text color={textColorPrimary} fontSize='md' me='26px' mb='40px'>
        {commentary || "Select a company to view its ESG analysis."}
      </Text>
    </Card>
  );
}
