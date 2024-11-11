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
        ESG Data Extraction Model
      </Text>
      <Text color={textColorSecondary} fontSize='md' me='26px' mb='40px'>
      Our system utilizes an advanced Natural Language Processing (NLP) model to extract and analyze ESG (Environmental, Social, and Governance) 
      data from unstructured reports. The model is designed to process large volumes of corporate
       reports and extract key information related to sustainability practices across various industries.
      </Text>
      <SimpleGrid columns='2' gap='20px'>
        <Information
          boxShadow={cardShadow}
          title='Model'
          value='GMFT/TATR'
        />
        <Information
          boxShadow={cardShadow}
          title='Languages supported'
          value='English, Chinese'
        />
        <Information
          boxShadow={cardShadow}
          title='Database'
          value='MySQL'
        />
        <Information
          boxShadow={cardShadow}
          title='Cloud Service'
          value='AWS, Firebase'
        />
      </SimpleGrid>
    </Card>
  );
}
