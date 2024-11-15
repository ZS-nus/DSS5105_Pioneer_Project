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
import E_hue_bar from "views/admin/default/components/e_hue_bar";
import EBarChart from "views/admin/default/components/e_bar_chart";
import SBarChart from "views/admin/default/components/s_bar_chart";
import GBarChart from "views/admin/default/components/g_bar_chart";
import ESGLinePredict from "views/admin/default/components/esg_predict_line";
import FinancialCorr from "views/admin/default/components/financialCorr";
import EnvMetrics from "views/admin/default/components/EnvTable";
import EnvAnalysis from "views/admin/default/components/Env_analysis";

import {
  columnsDataCheck,
  columnsDataComplex,
} from "views/admin/default/variables/columnsData";
import tableDataCheck from "views/admin/default/variables/tableDataCheck.json";
import tableDataComplex from "views/admin/default/variables/tableDataComplex.json";
import { fetchDashboardESGData,fetchESGScoreData,fetchESGPredict} from '../../../api'; // Import your API function
import tableDataTopCreators from "views/admin/marketplace/variables/tableDataTopCreators.json";
import { tableColumnsTopCreators } from "views/admin/marketplace/variables/tableColumnsTopCreators";
import OverallRanking from "views/admin/default/components/Overall_ranking";
import Card from "components/card/Card.js";
import ESG_analysis from "views/admin/default/components/esg_analysis";
import {
  e_score_line,
  lineChartOptionsTotalSpent,
} from "variables/charts";

export default function UserReports() {
  const [esg_score, setESGScore] = useState([]);
  const [latestScores, setLatestScores] = useState([]);
  const [predictData, setPredictData] = useState([]); // Add new state for prediction data
  const [selectedCompany, setSelectedCompany] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch both regular ESG data and prediction data
        const [esgResponse, predictResponse] = await Promise.all([
          fetchDashboardESGData(),
          fetchESGPredict()
        ]);

        const esgData = esgResponse.data;
        const predictData = predictResponse.data;

        if (!Array.isArray(esgData)) {
          throw new Error("Fetched ESG data is not an array");
        }

        setESGScore(esgData);
        setLatestScores(esgData);
        setPredictData(predictData);

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

  const handleCompanySelect = (company) => {
    console.log('Company selected:', company);
    setSelectedCompany(company);
  };

  return (
    <Box pt={{ base: "130px", md: "80px", xl: "80px" }}>

      <SimpleGrid columns={{ base: 1, md: 2, xl: 2 }} gap='20px' mb='20px'>

        <SimpleGrid columns={{ base: 1, md: 1, xl: 1 }} gap='20px' mb='20px'>
          <Card px='0px' mb='20px'>
            <OverallRanking
              tableData={tableDataTopCreators}
              columnsData={tableColumnsTopCreators}
            />
          </Card>
        </SimpleGrid>

        <SimpleGrid columns={{ base: 1, md: 2, xl: 2 }} gap='20px' mb='20px'>
        <ESG_analysis gap='20px' mb='20px'company={companyName} data={esg_score}/>
        <Card px='0px' mb='20px'>
          <Flex direction="column" h="100%"> {/* Add this Flex container */}
            <Box pl='10px' pr='10px' flex="1"> {/* Modify this Box */}
              <ESG_metrics_pie h="100%" /> {/* Add h="100%" to PieCard */}
            </Box>
          </Flex>
        </Card>
        </SimpleGrid>

    
      </SimpleGrid>

      <SimpleGrid columns={{ base: 1, md: 1, xl: 1 }} gap='20px' mb='20px'>
      <ESGLineChart data={esg_score} company={companyName} /> 
      </SimpleGrid>


      <SimpleGrid columns={{ base: 1, md: 2, xl: 2 }} gap='20px' mb='20px'>
          <EBarChart data={esg_score} />
          <ELineChart data={predictData} company={companyName} /> 
      </SimpleGrid>

      <SimpleGrid columns={{ base: 1, md: 2, xl: 2 }} gap='20px' mb='20px'>
          <EnvMetrics 
            company={companyName} 
            data={esg_score} 
            onCompanySelect={handleCompanySelect}
          />
          <EnvAnalysis 
            company={selectedCompany || companyName} 
            data={esg_score}
          />
      </SimpleGrid>


      <SimpleGrid columns={{ base: 1, md: 2, xl: 2 }} gap='20px' mb='20px'>
          <SBarChart data={esg_score} />
          <SLineChart data={predictData} company={companyName} /> 
      </SimpleGrid>

      <SimpleGrid columns={{ base: 1, md: 2, xl: 2 }} gap='20px' mb='20px'>
          <GBarChart data={esg_score} />
          <GLineChart data={predictData} company={companyName} /> 
      </SimpleGrid>


      <SimpleGrid columns={{ base: 1, md: 1, xl: 1 }} gap='20px' mb='20px'>
      <ESGLinePredict company={companyName} /> 
      </SimpleGrid>

      <SimpleGrid columns={{ base: 1, md: 1, xl: 1 }} gap='20px' mb='20px'>
      <FinancialCorr />
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
