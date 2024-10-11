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
import ESG_metrics_pie from "views/admin/default/components/ESG_metrics_pie";
import Tasks from "views/admin/default/components/Tasks";
import ELineChart from "views/admin/default/components/e_line_chart";
import SLineChart from "views/admin/default/components/s_line_chart";
import GLineChart from "views/admin/default/components/g_line_chart";
import ESGLineChart from "views/admin/default/components/esg_line_chart";
import WeeklyRevenue from "views/admin/default/components/WeeklyRevenue";
import EBarChart from "views/admin/default/components/e_bar_chart";
import SBarChart from "views/admin/default/components/s_bar_chart";
import GBarChart from "views/admin/default/components/g_bar_chart";
import {
  columnsDataCheck,
  columnsDataComplex,
} from "views/admin/default/variables/columnsData";
import tableDataCheck from "views/admin/default/variables/tableDataCheck.json";
import tableDataComplex from "views/admin/default/variables/tableDataComplex.json";
import { fetchEScoreData,fetchESGScoreData} from '../../../api'; // Import your API function
import tableDataTopCreators from "views/admin/marketplace/variables/tableDataTopCreators.json";
import { tableColumnsTopCreators } from "views/admin/marketplace/variables/tableColumnsTopCreators";
import OverallRanking from "views/admin/default/components/Overall_ranking";
import Card from "components/card/Card.js";
import {
  e_score_line,
  lineChartOptionsTotalSpent,
} from "variables/charts";

export default function UserReports() {

  const [esg_score, setESGScore] = useState([]);
  const [e_score, setEScore] = useState([]);
  const [s_score, setSScore] = useState([]);
  const [g_score, setGScore] = useState([]);
  const [latestScores, setLatestScores] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetchESGScoreData();
        const data = response.data;

        if (!Array.isArray(data)) {
          throw new Error("Fetched data is not an array");
        }

        // Separate the scores
        const esgScores = data.map(item => ({ ...item, score: item.Final_ESG_score }));
        const eScores = data.map(item => ({ ...item, score: item.Environmental_Score }));
        const sScores = data.map(item => ({ ...item, score: item.Social_Score }));
        const gScores = data.map(item => ({ ...item, score: item.Governance_Score }));

        console.log("Final_esg_score",esgScores)
        console.log("eScores",eScores)

        setESGScore(esgScores);
        setEScore(eScores);
        setSScore(sScores);
        setGScore(gScores);

        // Process the data to get the latest scores
        const latest = data.reduce((acc, current) => {
          const existing = acc.find(item => item.CompanyID === current.CompanyID);
          if (!existing || existing.ReportYear > existing.ReportYear) {
            acc = acc.filter(item => item.CompanyID !== current.CompanyID);
            acc.push(current);
          }
          return acc;
        }, []);

        // Sort the latest scores by Final_ESG_score in descending order
        latest.sort((a, b) => b.Final_ESG_score - a.Final_ESG_score);

        setLatestScores(latest);

      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, []);

  // Get the company name from the first entry in esg_score
  const companyName = esg_score.length > 0 ? esg_score[0].CompanyName : "Unknown Company";

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
          <Flex direction="column" h="100%"> {/* Add this Flex container */}
            <Box pl='20px' pr='20px' flex="1"> {/* Modify this Box */}
              <ESG_metrics_pie h="100%" /> {/* Add h="100%" to PieCard */}
            </Box>
          </Flex>
        </Card>

      </SimpleGrid>

      <SimpleGrid columns={{ base: 1, md: 1, xl: 1 }} gap='20px' mb='20px'>
      <ESGLineChart data={esg_score} company={companyName} /> 
      </SimpleGrid>


      <SimpleGrid columns={{ base: 1, md: 2, xl: 2 }} gap='20px' mb='20px'>
          <EBarChart data={e_score} />
          <ELineChart data={e_score} company={companyName} /> 
      </SimpleGrid>

      <SimpleGrid columns={{ base: 1, md: 2, xl: 2 }} gap='20px' mb='20px'>
          <SBarChart data={e_score} />
          <SLineChart data={e_score} company={companyName} /> 
      </SimpleGrid>

      <SimpleGrid columns={{ base: 1, md: 2, xl: 2 }} gap='20px' mb='20px'>
          <GBarChart data={e_score} />
          <GLineChart data={e_score} company={companyName} /> 
      </SimpleGrid>


      <SimpleGrid columns={{ base: 1, md: 2, xl: 2 }} gap='20px' mb='20px'>

      </SimpleGrid>



      {/* <SimpleGrid columns={{ base: 1, md: 1, xl: 2 }} gap='20px' mb='20px'>
        <ComplexTable
          columnsData={columnsDataComplex}
          tableData={tableDataComplex}
        />
        <SimpleGrid columns={{ base: 1, md: 2, xl: 2 }} gap='20px'>
          <Tasks />
          <MiniCalendar h='100%' minW='100%' selectRange={false} />
        </SimpleGrid>
      </SimpleGrid> */}
    </Box>
  );
}
