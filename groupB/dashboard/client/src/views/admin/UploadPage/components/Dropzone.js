import React from "react";
import { Flex, Input, useColorModeValue, Text } from "@chakra-ui/react";
import { useDropzone } from "react-dropzone";

function Dropzone(props) {
  const { content, onDrop, ...rest } = props;
  const bg = useColorModeValue("gray.100", "navy.700");
  const borderColor = useColorModeValue("secondaryGray.100", "whiteAlpha.100");

  const { getRootProps, getInputProps, fileRejections } = useDropzone({
    onDrop: (acceptedFiles) => {
      if (onDrop) {
        onDrop(acceptedFiles);
      }
    },
    accept: {
      'application/pdf': ['.pdf'],
      'text/html': ['.html', '.htm'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1
  });

  return (
    <Flex
      align='center'
      justify='center'
      bg={bg}
      border='1px dashed'
      borderColor={borderColor}
      borderRadius='16px'
      w='100%'
      h='max-content'
      minH='100%'
      cursor='pointer'
      flexDirection="column"
      {...getRootProps({ className: "dropzone" })}
      {...rest}>
      <Input variant='main' {...getInputProps()} />
      {content}
      {fileRejections.length > 0 && (
        <Text color="red.500" mt={2}>
          File type not accepted. Please upload a PDF, HTML, or DOCX file.
        </Text>
      )}
    </Flex>
  );
}

export default Dropzone;
