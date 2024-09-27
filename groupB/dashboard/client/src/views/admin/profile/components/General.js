// Chakra imports
import { SimpleGrid, Text, useColorModeValue } from "@chakra-ui/react";
// Custom components
import Card from "components/card/Card.js";
import React from "react";
import Information from "views/admin/profile/components/Information";

// Assets
export default function GeneralInformation(props) {
  const { ...rest } = props;
  // Chakra Color Mode
  const textColorPrimary = useColorModeValue("secondaryGray.900", "white");
  const textColorSecondary = "gray.400";
  const cardShadow = useColorModeValue(
    "0px 18px 40px rgba(112, 144, 176, 0.12)",
    "unset"
  );
  return (
    <Card mb={{ base: "0px", "2xl": "20px" }} {...rest}>
      <Text
        color={textColorPrimary}
        fontWeight='bold'
        fontSize='2xl'
        mt='10px'
        mb='4px'>
        Project Information
      </Text>
      <Text color={textColorSecondary} fontSize='md' me='26px' mb='40px'>
      This project focuses on automating the extraction and analysis of Environmental, Social, 
      and Governance (ESG) data from unstructured reports, such as corporate sustainability reports and financial filings.
      This project is essential for businesses, investors, and analysts who need accurate, reliable, and easily comparable ESG data to make informed decisions about corporate sustainability.
      </Text>
      <SimpleGrid columns='2' gap='20px'>
        <Information
          boxShadow={cardShadow}
          title='Module'
          value='DSS5105'
        />
        <Information
          boxShadow={cardShadow}
          title='Team Members'
          value='8'
        />
        <Information
          boxShadow={cardShadow}
          title='Techonologies Used'
          value='Python, React, Node.js, MySQL, AWS, Firebase'
        />


      </SimpleGrid>
    </Card>
  );
}
