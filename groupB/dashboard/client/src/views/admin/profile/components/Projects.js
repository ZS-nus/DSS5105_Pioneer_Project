// Chakra imports
import { Text, useColorModeValue } from "@chakra-ui/react";
// Custom components
import Card from "components/card/Card.js";
import React from "react";
import Project from "views/admin/profile/components/Project";

export default function Projects(props) {
  // Chakra Color Mode
  const textColorPrimary = useColorModeValue("secondaryGray.900", "white");
  const textColorSecondary = "gray.400";
  const cardShadow = useColorModeValue(
    "0px 18px 40px rgba(112, 144, 176, 0.12)",
    "unset"
  );
  return (
    <Card mb={{ base: "0px", "2xl": "20px" }}>
      <Text
        color={textColorPrimary}
        fontWeight='bold'
        fontSize='2xl'
        mt='10px'
        mb='4px'>
        ESG Data Processing Pipeline
      </Text>
      <Text color={textColorSecondary} fontSize='md' me='26px' mb='40px'>
        Our comprehensive ESG data processing workflow ensures accurate and efficient analysis
      </Text>
      <Project
        boxShadow={cardShadow}
        mb='20px'
        ranking='1'
        link='#'
        title='PDF Document Processing'
        description='Upload and process PDF documents containing ESG-related information'
      />
      <Project
        boxShadow={cardShadow}
        mb='20px'
        ranking='2'
        link='#'
        title='Data Preprocessing & Extraction'
        description='Convert PDFs to structured text and tables, clean and normalize data'
      />
      <Project
        boxShadow={cardShadow}
        mb='20px'
        ranking='3'
        link='#'
        title='ESG Data Analysis'
        description='Extract relevant ESG metrics and indicators from processed data'
      />
      <Project
        boxShadow={cardShadow}
        mb='20px'
        ranking='4'
        link='#'
        title='ESG Rating Generation'
        description='Calculate and assign ESG ratings based on extracted metrics'
      />
      <Project
        boxShadow={cardShadow}
        ranking='5'
        link='#'
        title='Results Visualization'
        description='Present ESG ratings and analysis through interactive dashboards'
      />
    </Card>
  );
}
