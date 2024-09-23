// Chakra imports
import { Text, useColorModeValue, Link } from "@chakra-ui/react";
// Custom components
import Card from "components/card/Card.js";
import React, { useEffect, useState } from "react";
import Project from "views/admin/UploadPage/components/Project";
import { fetchFirebaseStorageFiles } from '../../../../api'; // Import your API function

export default function Projects(props) {
  // Chakra Color Mode
  const textColorPrimary = useColorModeValue("secondaryGray.900", "white");
  const textColorSecondary = "gray.400";
  const cardShadow = useColorModeValue(
    "0px 18px 40px rgba(112, 144, 176, 0.12)",
    "unset"
  );

  const [files, setFiles] = useState([]);

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const response = await fetchFirebaseStorageFiles();
        setFiles(response.data);
      } catch (error) {
        console.error('Error fetching files:', error);
      }
    };

    fetchFiles();
  }, []);


  return (
    <Card mb={{ base: "0px", "2xl": "20px" }}>
      <Text
        color={textColorPrimary}
        fontWeight='bold'
        fontSize='2xl'
        mt='10px'
        mb='4px'>
        Download Reports
      </Text>
      <Text color={textColorSecondary} fontSize='md' me='26px' mb='40px'>
      Select a company from the list to download their latest ESG reports. The reports contain detailed information on the company's environmental, social, and governance performance. 
      </Text>
      {files.map((file, index) => (
        // Check if the file name is not empty before rendering the Project component
        file.name ? (
          <Project
            key={`${file.name}-${index}`} // Ensure a unique key
            boxShadow={cardShadow}
            mb='20px'
            ranking={index} // Ranking starts from 1
            link={file.downloadUrl} // Link to the file
            title={file.name} // Title is the file name
          />
        ) : null // Do not render anything if the name is empty
      ))}
    </Card>
  );
}
