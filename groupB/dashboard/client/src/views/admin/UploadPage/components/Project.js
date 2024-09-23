// Chakra imports
import {
  Box,
  Icon,
  Flex,
  Link,
  Text,
  useColorModeValue,
} from "@chakra-ui/react";
// Custom components
import Card from "components/card/Card.js";
import React from "react";
// Assets
import {MdDownload} from "react-icons/md";

export default function Project(props) {
  const { title, ranking, link, ...rest } = props;
  // Chakra Color Mode
  const textColorPrimary = useColorModeValue("secondaryGray.900", "white");
  const textColorSecondary = "gray.400";
  const brandColor = useColorModeValue("brand.500", "white");
  const bg = useColorModeValue("white", "navy.700");
  return (
    <Link href={link} isExternal style={{ textDecoration: 'none' }}>
      <Card bg={bg} {...rest} p='14px'>
        <Flex align='center' direction={{ base: "column", md: "row" }}>
          <Box mt={{ base: "10px", md: "0" }} display="flex" alignItems="center">
            <Icon as={MdDownload} mr={2} width="20px" height="20px" /> {/* Add margin to the right of the icon */}
            <Text
              fontWeight='500'
              color={textColorSecondary}
              fontSize='sm'
              me='4px'>
              Report #{ranking} &nbsp; &nbsp; &nbsp;
            </Text>
            <Text
              color={textColorPrimary}
              fontWeight='500'
              fontSize='md'
              mb='4px'>
              {title}
            </Text>
          </Box>
        </Flex>
      </Card>
    </Link>
  );
}
