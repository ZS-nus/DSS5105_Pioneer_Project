import React, { useState } from "react";
import {
  Box,
  Button,
  Flex,
  Icon,
  Text,
  useColorModeValue,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  useToast
} from "@chakra-ui/react";
// Custom components
import Card from "components/card/Card.js";
import { MdUpload } from "react-icons/md";
import Dropzone from "views/admin/UploadPage/components/Dropzone";
import { reportUploadToFirebase } from "api.js";

export default function Upload(props) {
  const { used, total, ...rest } = props;
  const [selectedFile, setSelectedFile] = useState(null);
  const [showAlert, setShowAlert] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const toast = useToast();

  // Chakra Color Mode
  const textColorPrimary = useColorModeValue("secondaryGray.900", "white");
  const brandColor = useColorModeValue("brand.500", "white");
  const textColorSecondary = "gray.400";

  const handleFileChange = (files) => {
    if (files && files.length > 0) {
      const file = files[0];
      setSelectedFile(file);
      setShowAlert(false);
      console.log("Selected File:", {
        name: file.name,
        type: file.type,
        size: file.size,
        lastModified: new Date(file.lastModified).toLocaleString(),
      });
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setShowAlert(true);
    } else {
      setIsUploading(true);
      setShowAlert(false);
      try {
        const formData = new FormData();
        formData.append('file', selectedFile);

        const result = await reportUploadToFirebase(formData);
        console.log("Upload response:", result);
        toast({
          title: "File uploaded successfully",
          description: `File is available at: ${result.url}`,
          status: "success",
          duration: 5000,
          isClosable: true,
        });
        setSelectedFile(null);
      } catch (error) {
        console.error("Upload error:", error);
        toast({
          title: "Upload failed",
          description: "There was an error uploading your file.",
          status: "error",
          duration: 3000,
          isClosable: true,
        });
      } finally {
        setIsUploading(false);
      }
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
            Our system utilizes advanced Artificial Intelligence technologies to extract and analyze ESG data from unstructured reports.
          </Text>
          <Flex w='100%' direction="column">
            <Button
              me='100%'
              mb='10px'
              w='140px'
              minW='140px'
              mt={{ base: "20px", "2xl": "auto" }}
              variant='brand'
              fontWeight='500'
              onClick={handleUpload}
              isLoading={isUploading}
              loadingText="Uploading">
              Upload now
            </Button>
            {showAlert && (
              <Alert status="error" mt={2}>
                <AlertIcon />
                <AlertTitle mr={2}>Error!</AlertTitle>
                <AlertDescription>Please select a file before uploading.</AlertDescription>
              </Alert>
            )}
          </Flex>
        </Flex>
      </Flex>
    </Card>
  );
}
