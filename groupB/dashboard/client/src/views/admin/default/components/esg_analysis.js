// Chakra imports
import { SimpleGrid, Text, useColorModeValue, Flex, Box, VStack } from "@chakra-ui/react";
import Card from "components/card/Card.js";
import React, { useState, useEffect, useCallback, useMemo } from "react";
import Information from "views/admin/profile/components/Information";
import LineChartMenu from 'views/admin/default/components/line_chart_menu';  
import { fetchESGCommentary } from '../../../../api';
import { debounce } from 'lodash';

// Process data helper function
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

  // State management
  const [processedData, setProcessedData] = useState({});
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [commentary, setCommentary] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch commentary function
  const fetchCommentary = useCallback(async (companyId) => {
    if (!companyId) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetchESGCommentary(companyId);
      if (response.data && response.data.commentary) {
        setCommentary(response.data.commentary);
      } else {
        setCommentary("No analysis available for this company.");
      }
    } catch (error) {
      console.error("Error fetching commentary:", error);
      setError("Failed to fetch company analysis. Please try again later.");
      setCommentary("");
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Initialize data and fetch first company's commentary
  useEffect(() => {
    if (data && data.length > 0) {
      const processed = processData(data);
      setProcessedData(processed);
      
      // Set initial company and fetch its commentary
      const firstCompanyName = Object.keys(processed)[0];
      const firstCompanyData = processed[firstCompanyName];
      
      if (firstCompanyData) {
        setSelectedCompany(firstCompanyName);
        fetchCommentary(firstCompanyData.CompanyID);
      }
    }
  }, [data, fetchCommentary]);

  // Memoize menu items
  const menuItems = useMemo(() => 
    Object.keys(processedData)
  , [processedData]);

  // Handle company selection
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
      
      {isLoading ? (
        <Text color={textColorSecondary} fontSize='md' me='26px' mb='40px'>
          Loading analysis...
        </Text>
      ) : error ? (
        <Text color="red.500" fontSize='md' me='26px' mb='40px'>
          {error}
        </Text>
      ) : (
        <Text color={textColorPrimary} fontSize='md' me='26px' mb='40px'>
          {commentary || "Select a company to view its ESG analysis."}
        </Text>
      )}
    </Card>
  );
}
