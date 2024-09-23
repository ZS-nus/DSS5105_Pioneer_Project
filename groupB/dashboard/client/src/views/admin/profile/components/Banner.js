// Chakra imports
import { Avatar, Box, Flex, Text, useColorModeValue, SimpleGrid } from "@chakra-ui/react";
import Card from "components/card/Card.js";
import React from "react";
import Information from "views/admin/profile/components/Information";

export default function Banner(props) {
  const { banner, avatar, name, job, posts, followers, following } = props;
  // Chakra Color Mode
  const textColorPrimary = useColorModeValue("secondaryGray.900", "white");
  const textColorSecondary = "gray.400";
  const cardShadow = useColorModeValue(
    "0px 18px 40px rgba(112, 144, 176, 0.12)",
    "unset"
  );
  const borderColor = useColorModeValue(
    "white !important",
    "#111C44 !important"
  );

  // Get the current date and time formatted as dd/month/year hh:mm:ss AM/PM
  const currentDateTime = new Date().toLocaleString('en-GB', {
    day: '2-digit',
    month: 'short', // Use 'short' for abbreviated month names
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true, // Use 12-hour format
  });

  return (
    <Card mb={{ base: "0px", lg: "20px" }} align='center'>
      <Box
        bg={`url(${banner})`}
        bgSize='cover'
        borderRadius='16px'
        h='131px'
        w='100%'
      />
      <Avatar
        mx='auto'
        src={avatar}
        h='87px'
        w='87px'
        mt='-43px'
        border='4px solid'
        borderColor={borderColor}
      />
      <Text color={textColorPrimary} fontWeight='bold' fontSize='xl' mt='10px'>
        {name}
      </Text>
      <Text color={textColorSecondary} fontSize='sm'>
        {job}
      </Text>
      <Flex w='max-content' mx='auto' mt='26px'>
        <SimpleGrid columns='1' gap='20px'>
          <Information
            boxShadow={cardShadow}
            title='Last login'
            value={currentDateTime} // Display the formatted current date and time
          />
        </SimpleGrid>
      </Flex>
    </Card>
  );
}
