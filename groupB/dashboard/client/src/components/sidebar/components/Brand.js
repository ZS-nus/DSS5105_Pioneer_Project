import React from "react";
import { Flex, Text, useColorModeValue } from "@chakra-ui/react";
import { HSeparator } from "components/separator/Separator";

export function SidebarBrand() {
  let textColor = useColorModeValue("navy.700", "white");

  return (
    <Flex align='center' direction='column'>
      <Text
        fontSize="2xl"
        fontWeight="bold"
        color={textColor}
        my="32px"
      >
        Pioneer Project
      </Text>
      <HSeparator mb='20px' />
    </Flex>
  );
}

export default SidebarBrand;
