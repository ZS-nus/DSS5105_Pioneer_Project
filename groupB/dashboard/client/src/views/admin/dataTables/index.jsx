
// Chakra imports
import { Box, SimpleGrid } from "@chakra-ui/react";
import CompanyTable from "views/admin/dataTables/components/CompanyTable";
import EnvTable from "views/admin/dataTables/components/EnvTable";
import SocialTable from "views/admin/dataTables/components/SocialTable";
import GovTable from "views/admin/dataTables/components/GovTable";
import Financial from "views/admin/dataTables/components/financial";
import {
  columnsDataDevelopment,
  columnsDataCheck,
  columnsDataColumns,
  columnsDataComplex,
} from "views/admin/dataTables/variables/columnsData";
import React from "react";

export default function Settings() {
  // Chakra Color Mode
  return (
    <Box pt={{ base: "130px", md: "80px", xl: "80px" }}>
      <SimpleGrid
        mb='20px'
        columns={{ sm: 1, md: 2 }}
        spacing={{ base: "20px", xl: "20px" }}>
        <CompanyTable
        />
        <EnvTable />
        <SocialTable />
        <GovTable />
        <Financial />
        {/* <ColumnsTable
          columnsData={columnsDataColumns}
          tableData={tableDataColumns}
        /> */}
        {/* <ComplexTable
          columnsData={columnsDataComplex}
          tableData={tableDataComplex}
        /> */}
      </SimpleGrid>
    </Box>
  );
}
