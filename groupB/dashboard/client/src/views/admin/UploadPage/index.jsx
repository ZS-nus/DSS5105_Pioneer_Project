
// Chakra imports
import { Box, Grid ,  SimpleGrid,} from "@chakra-ui/react";


import UploadedReports from "views/admin/UploadPage/components/Uploaded_reports";
import Upload from "views/admin/UploadPage/components/Upload";
import Storage from "views/admin/UploadPage/components/Storage";
import General from "views/admin/UploadPage/components/General";

import React from "react";

export default function Overview() {
  return (
    <Box pt={{ base: "130px", md: "80px", xl: "80px" }}>
      {/* Main Fields */}
      <Grid
        templateColumns={{
          base: "1fr",
          lg: "1.5fr 1.5fr 1fr",
        }}
        templateRows={{
          base: "repeat(3, 1fr)",
          lg: "1fr",
        }}
        gap={{ base: "20px", xl: "20px" }}>
        <Upload
          minH={{ base: "auto", lg: "420px", "2xl": "365px" }}
          pe='20px'
          pb={{ base: "100px", lg: "20px" }}
        />
        <General
          
        />
        <Storage
          
          used={75.3}
          total={100}
        />
      </Grid>
      <br></br>
      <br></br>

      <SimpleGrid columns={{ base: 1, md: 2, xl: 2 }} gap='20px' mb='20px'>
        <UploadedReports
            gridArea='1 / 1 / 2 / 2'
          />
          {/* <Upload /> */}
      </SimpleGrid>


    </Box>
  );
}
