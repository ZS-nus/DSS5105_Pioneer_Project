import React, { useEffect, useState } from "react";
import {
  Avatar,
  Box,
  Flex,
  FormLabel,
  Icon,
  Select,
  SimpleGrid,
  useColorModeValue,
} from "@chakra-ui/react";
// Assets
import MiniCalendar from "components/calendar/MiniCalendar";

import CheckTable from "views/admin/default/components/CheckTable";
import ComplexTable from "views/admin/default/components/ComplexTable";
import DailyTraffic from "views/admin/default/components/DailyTraffic";
import PieCard from "views/admin/default/components/PieCard";
import Tasks from "views/admin/default/components/Tasks";
import ELineChart from "views/admin/default/components/e_line_chart";
import WeeklyRevenue from "views/admin/default/components/WeeklyRevenue";
import EBarChart from "views/admin/default/components/e_bar_chart";
import {
  columnsDataCheck,
  columnsDataComplex,
} from "views/admin/default/variables/columnsData";
import tableDataCheck from "views/admin/default/variables/tableDataCheck.json";
import tableDataComplex from "views/admin/default/variables/tableDataComplex.json";
import { fetchEScoreData } from '../../../api'; // Import your API function
import tableDataTopCreators from "views/admin/marketplace/variables/tableDataTopCreators.json";
import { tableColumnsTopCreators } from "views/admin/marketplace/variables/tableColumnsTopCreators";
import OverallRanking from "views/admin/default/components/Overall_ranking";
import Card from "components/card/Card.js";

export default function UserReports() {

  const [e_score, setEScore] = useState([]); // State to store all fetched data
  const [e_score_latest, setERateLatest] = useState([]); // State to store latest scores

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetchEScoreData(); // Call the API function
        const data = response.data; // Access the data property of the response
        console.log("Fetched Data:", data); // Log the fetched data

        // Check if data is an array
        if (!Array.isArray(data)) {
          throw new Error("Fetched data is not an array");
        }

        setEScore(data); // Store the fetched data

        // Process the data to get the latest scores
        const latestScores = data.reduce((acc, current) => {
          const existing = acc.find(item => item.CompanyName === current.CompanyName);
          if (!existing || existing.ReportYear < current.ReportYear) {
            // If no existing entry or current year is greater, update the entry
            acc = acc.filter(item => item.CompanyName !== current.CompanyName); // Remove older entries
            acc.push(current); // Add the current entry
          }
          return acc;
        }, []);

        // Sort the latest scores by env_score_weighted in ascending order
        latestScores.sort((a, b) => a.env_score_weighted - b.env_score_weighted);

        setERateLatest(latestScores); // Store the sorted latest scores

      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, []);


  // Chakra Color Mode
  const brandColor = useColorModeValue("brand.500", "white");
  const boxBg = useColorModeValue("secondaryGray.300", "whiteAlpha.100");
  return (
    <Box pt={{ base: "130px", md: "80px", xl: "80px" }}>


      <SimpleGrid columns={{ base: 1, md: 2, xl: 2 }} gap='20px' mb='20px'>
        <Card px='0px' mb='20px'>
            <OverallRanking
              tableData={tableDataTopCreators}
              columnsData={tableColumnsTopCreators}
            />
          </Card>
          <Card px='0px' mb='20px'>
          <SimpleGrid columns={{ base: 1, md: 2, xl: 2 }} gap='20px'>
            {/* <DailyTraffic />
            <PieCard />
            <DailyTraffic />
            <PieCard /> `` */}
        </SimpleGrid>
          </Card>

      </SimpleGrid>


      <SimpleGrid columns={{ base: 1, md: 2, xl: 2 }} gap='20px' mb='20px'>
          <EBarChart data={e_score_latest} />
          <ELineChart />
      </SimpleGrid>


      <SimpleGrid columns={{ base: 1, md: 2, xl: 2 }} gap='20px' mb='20px'>
        <ELineChart />
        <ELineChart />
      </SimpleGrid>



      <SimpleGrid columns={{ base: 1, md: 1, xl: 2 }} gap='20px' mb='20px'>
        <CheckTable columnsData={columnsDataCheck} tableData={tableDataCheck} />
        <SimpleGrid columns={{ base: 1, md: 2, xl: 2 }} gap='20px'>
          <DailyTraffic />
          <PieCard />
        </SimpleGrid>
      </SimpleGrid>
      <SimpleGrid columns={{ base: 1, md: 1, xl: 2 }} gap='20px' mb='20px'>
        <ComplexTable
          columnsData={columnsDataComplex}
          tableData={tableDataComplex}
        />
        <SimpleGrid columns={{ base: 1, md: 2, xl: 2 }} gap='20px'>
          <Tasks />
          <MiniCalendar h='100%' minW='100%' selectRange={false} />
        </SimpleGrid>
      </SimpleGrid>
    </Box>
  );
}
