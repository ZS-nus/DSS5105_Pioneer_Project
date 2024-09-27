import React, { useState } from "react";
import {
  Box,
  Button,
  Flex,
  Icon,
  Text,
  useColorModeValue,
} from "@chakra-ui/react";
// Custom components
import Card from "components/card/Card.js";
import { MdUpload } from "react-icons/md";
import Dropzone from "views/admin/UploadPage/components/Dropzone";

export default function Upload(props) {
  const { used, total, ...rest } = props;
  const [selectedFile, setSelectedFile] = useState(null);

  // Chakra Color Mode
  const textColorPrimary = useColorModeValue("secondaryGray.900", "white");
  const brandColor = useColorModeValue("brand.500", "white");
  const textColorSecondary = "gray.400";

  const handleFileChange = (files) => {
    if (files && files.length > 0) {
      const file = files[0];
      setSelectedFile(file);
      console.log("Selected File:", {
        name: file.name,
        type: file.type,
        size: file.size,
        lastModified: new Date(file.lastModified).toLocaleString(),
      });
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const dropzoneContent = selectedFile ? (
    <Box textAlign="center">
      <Text fontSize='xl' fontWeight='700' color={brandColor} mb='12px'>File Selected:</Text>
      <Box textAlign="left" pl="20px" pr="20px" >
      <Text color={textColorSecondary}>File Name: {selectedFile.name}</Text>
      <Text color={textColorSecondary}>File Type: {selectedFile.type}</Text>
      <Text color={textColorSecondary}>File Size: {formatFileSize(selectedFile.size)}</Text>
      </Box>
    </Box>
  ) : (
    <Box>
      <Icon as={MdUpload} w='80px' h='80px' color={brandColor} />
      <Flex justify='center' mx='auto' mb='12px'>
        <Text fontSize='xl' fontWeight='700' color={brandColor}>
          Upload Report
        </Text>
      </Flex>
      <Text fontSize='sm' fontWeight='500' color='secondaryGray.500'>
        PDF, Html, and Docx files are allowed
      </Text>
    </Box>
  );

  return (
    <Card {...rest} mb='20px' align='center' p='20px'>
      <Flex h='100%' direction={{ base: "column", "2xl": "row" }}>
        <Dropzone
          w={{ base: "100%", "2xl": "268px" }}
          me='36px'
          maxH={{ base: "60%", lg: "50%", "2xl": "100%" }}
          minH={{ base: "60%", lg: "50%", "2xl": "100%" }}
          onDrop={handleFileChange}
          content={dropzoneContent}
        />
        <Flex direction='column' pe='44px'>
          <Text
            color={textColorPrimary}
            fontWeight='bold'
            textAlign='start'
            fontSize='2xl'
            mt={{ base: "20px", "2xl": "50px" }}>
            Analyze your report
          </Text>
          <Text
            color={textColorSecondary}
            fontSize='md'
            my={{ base: "auto", "2xl": "10px" }}
            mx='auto'
            textAlign='start'>
            Stay on the pulse of distributed projects with an online whiteboard
            to plan, coordinate and discuss
          </Text>
          <Flex w='100%'>
            <Button
              me='100%'
              mb='50px'
              w='140px'
              minW='140px'
              mt={{ base: "20px", "2xl": "auto" }}
              variant='brand'
              fontWeight='500'>
              Upload now
            </Button>
          </Flex>
        </Flex>
      </Flex>
    </Card>
  );
}
