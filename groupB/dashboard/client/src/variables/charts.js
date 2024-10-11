// Daily Traffic Dashboards Default

export const barChartDataDailyTraffic = [
  {
    name: "Daily Traffic",
    data: [20, 30, 40, 20, 45, 50, 30],
  },
];

export const createBarChartData = (data) => {
  if (!Array.isArray(data)) {
    console.error("Expected data to be an array, but got:", data);
    return { name: "Environmental Scores", data: [] }; // Return an empty array if not valid
  }

  return {
    name: "Environmental Scores",
    data: data.map(item => item.env_score_weighted || 0), // Default to 0 if property is missing
  };
};



export const e_barChartData = (data) => {
  // Group data by CompanyID and get the latest year for each company
  const latestDataByCompany = data.reduce((acc, curr) => {
    if (!acc[curr.CompanyID] || curr.ReportYear > acc[curr.CompanyID].ReportYear) {
      acc[curr.CompanyID] = curr;
    }
    return acc;
  }, {});

  // Convert the grouped data to an array and sort by Environmental_Score
  const sortedData = Object.values(latestDataByCompany)
    .sort((a, b) => b.Environmental_Score - a.Environmental_Score);

  return {
    labels: sortedData.map(item => item.CompanyName),
    data: sortedData.map(item => item.Environmental_Score)
  };
};

export const s_barChartData = (data) => {
  // Group data by CompanyID and get the latest year for each company
  const latestDataByCompany = data.reduce((acc, curr) => {
    if (!acc[curr.CompanyID] || curr.ReportYear > acc[curr.CompanyID].ReportYear) {
      acc[curr.CompanyID] = curr;
    }
    return acc;
  }, {});

  // Convert the grouped data to an array and sort by Environmental_Score
  const sortedData = Object.values(latestDataByCompany)
    .sort((a, b) => b.Social_Score - a.Social_Score);

  return {
    labels: sortedData.map(item => item.CompanyName),
    data: sortedData.map(item => item.Social_Score)
  };
};

export const g_barChartData = (data) => {
  // Group data by CompanyID and get the latest year for each company
  const latestDataByCompany = data.reduce((acc, curr) => {
    if (!acc[curr.CompanyID] || curr.ReportYear > acc[curr.CompanyID].ReportYear) {
      acc[curr.CompanyID] = curr;
    }
    return acc;
  }, {});

  // Convert the grouped data to an array and sort by Environmental_Score
  const sortedData = Object.values(latestDataByCompany)
    .sort((a, b) => b.Governance_Score - a.Governance_Score);
  console.log(sortedData);
  return {
    labels: sortedData.map(item => item.CompanyName),
    data: sortedData.map(item => item.Governance_Score)
  };
};


export const barChartOptionsDailyTraffic = {
  chart: {
    toolbar: {
      show: false,
    },
  },
  tooltip: {
    style: {
      fontSize: "12px",
      fontFamily: undefined,
    },
    onDatasetHover: {
      style: {
        fontSize: "12px",
        fontFamily: undefined,
      },
    },
    theme: "dark",
  },
  xaxis: {
    categories: [],
    show: false,
    labels: {
      show: true,
      style: {
        colors: "#A3AED0",
        fontSize: "14px",
        fontWeight: "500",
      },
    },
    axisBorder: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
  },
  yaxis: {
    show: false,
    color: "black",
    labels: {
      show: true,
      style: {
        colors: "#CBD5E0",
        fontSize: "14px",
      },
    },
  },
  grid: {
    show: false,
    strokeDashArray: 5,
    yaxis: {
      lines: {
        show: true,
      },
    },
    xaxis: {
      lines: {
        show: false,
      },
    },
  },
  fill: {
    type: "gradient",
    gradient: {
      type: "vertical",
      shadeIntensity: 1,
      opacityFrom: 0.7,
      opacityTo: 0.9,
      colorStops: [
        [
          {
            offset: 0,
            color: "#4318FF",
            opacity: 1,
          },
          {
            offset: 100,
            color: "rgba(67, 24, 255, 1)",
            opacity: 0.28,
          },
        ],
      ],
    },
  },
  dataLabels: {
    enabled: false,
  },
  plotOptions: {
    bar: {
      borderRadius: 10,
      columnWidth: "40px",
    },
  },
};

export const e_barChartOptionsDailyTraffic = {
  chart: {
    toolbar: {
      show: false,
    },
  },
  tooltip: {
    style: {
      fontSize: "12px",
      fontFamily: undefined,
    },
    onDatasetHover: {
      style: {
        fontSize: "12px",
        fontFamily: undefined,
      },
    },
    theme: "dark",
  },
  xaxis: {
    categories: [],
    show: true,
    labels: {
      show: true,
      style: {
        colors: "#1B1B1B",
        fontSize: "14px",
        fontWeight: "500",
      },
    },
    axisBorder: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
  },
  yaxis: {
    show: false,
    color: "black",
    labels: {
      show: true,
      style: {
        colors: "#CBD5E0",
        fontSize: "14px",
      },
    },
  },
  grid: {
    show: true,
    strokeDashArray: 5,
    yaxis: {
      lines: {
        show: true,
      },
    },
    xaxis: {
      lines: {
        show: false,
      },
    },
  },
  fill: {
    type: "gradient",
    gradient: {
      type: "vertical",
      shadeIntensity: 1,
      opacityFrom: 0.7,
      opacityTo: 0.9,
      colorStops: [
        [
          {
            offset: 0,
            color: "#11998E",
            opacity: 1,
          },
          {
            offset: 100,
            color: "#38EF7D",
            opacity: 1,
          },
        ],
      ],
    },
  },
  dataLabels: {
    enabled: true,
  },
  plotOptions: {
    bar: {
      borderRadius: 10,
      columnWidth: "40px",
    },
  },
};

export const s_barChartOptionsDailyTraffic = {
  chart: {
    toolbar: {
      show: false,
    },
  },
  tooltip: {
    style: {
      fontSize: "12px",
      fontFamily: undefined,
    },
    onDatasetHover: {
      style: {
        fontSize: "12px",
        fontFamily: undefined,
      },
    },
    theme: "dark",
  },
  xaxis: {
    categories: [],
    show: true,
    labels: {
      show: true,
      style: {
        colors: "#1B1B1B",
        fontSize: "14px",
        fontWeight: "500",
      },
    },
    axisBorder: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
  },
  yaxis: {
    show: false,
    color: "black",
    labels: {
      show: true,
      style: {
        colors: "#CBD5E0",
        fontSize: "14px",
      },
    },
  },
  grid: {
    show: true,
    strokeDashArray: 5,
    yaxis: {
      lines: {
        show: true,
      },
    },
    xaxis: {
      lines: {
        show: false,
      },
    },
  },
  fill: {
    type: "gradient",
    gradient: {
      type: "vertical",
      shadeIntensity: 1,
      opacityFrom: 0.7,
      opacityTo: 0.9,
      colorStops: [
        [
          {
            offset: 0,
            color: "#2F80ED",
            opacity: 1,
          },
          {
            offset: 100,
            color: "#56CCF2",
            opacity: 1,
          },
        ],
      ],
    },
  },
  dataLabels: {
    enabled: true,
  },
  plotOptions: {
    bar: {
      borderRadius: 10,
      columnWidth: "40px",
    },
  },
};

export const g_barChartOptionsDailyTraffic = {
  chart: {
    toolbar: {
      show: false,
    },
  },
  tooltip: {
    style: {
      fontSize: "12px",
      fontFamily: undefined,
    },
    onDatasetHover: {
      style: {
        fontSize: "12px",
        fontFamily: undefined,
      },
    },
    theme: "dark",
  },
  xaxis: {
    categories: [],
    show: true,
    labels: {
      show: true,
      style: {
        colors: "#1B1B1B",
        fontSize: "14px",
        fontWeight: "500",
      },
    },
    axisBorder: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
  },
  yaxis: {
    show: false,
    color: "black",
    labels: {
      show: true,
      style: {
        colors: "#CBD5E0",
        fontSize: "14px",
      },
    },
  },
  grid: {
    show: true,
    strokeDashArray: 5,
    yaxis: {
      lines: {
        show: true,
      },
    },
    xaxis: {
      lines: {
        show: false,
      },
    },
  },
  fill: {
    type: "gradient",
    gradient: {
      type: "vertical",
      shadeIntensity: 1,
      opacityFrom: 0.7,
      opacityTo: 0.9,
      colorStops: [
        [
          {
            offset: 0,
            color: "#F2994A",
            opacity: 1,
          },
          {
            offset: 100,
            color: "#F2C94C",
            opacity: 1,
          },
        ],
      ],
    },
  },
  dataLabels: {
    enabled: true,
  },
  plotOptions: {
    bar: {
      borderRadius: 10,
      columnWidth: "40px",
    },
  },
};

// Consumption Users Reports

export const barChartDataConsumption = [
  {
    name: "PRODUCT A",
    data: [400, 370, 330, 390, 320, 350, 360, 320, 380],
  },
  {
    name: "PRODUCT B",
    data: [400, 370, 330, 390, 320, 350, 360, 320, 380],
  },
  {
    name: "PRODUCT C",
    data: [400, 370, 330, 390, 320, 350, 360, 320, 380],
  },
];

export const barChartOptionsConsumption = {
  chart: {
    stacked: true,
    toolbar: {
      show: false,
    },
  },
  tooltip: {
    style: {
      fontSize: "12px",
      fontFamily: undefined,
    },
    onDatasetHover: {
      style: {
        fontSize: "12px",
        fontFamily: undefined,
      },
    },
    theme: "dark",
  },
  xaxis: {
    categories: ["17", "18", "19", "20", "21", "22", "23", "24", "25"],
    show: false,
    labels: {
      show: true,
      style: {
        colors: "#A3AED0",
        fontSize: "14px",
        fontWeight: "500",
      },
    },
    axisBorder: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
  },
  yaxis: {
    show: false,
    color: "black",
    labels: {
      show: false,
      style: {
        colors: "#A3AED0",
        fontSize: "14px",
        fontWeight: "500",
      },
    },
  },

  grid: {
    borderColor: "rgba(163, 174, 208, 0.3)",
    show: true,
    yaxis: {
      lines: {
        show: false,
        opacity: 0.5,
      },
    },
    row: {
      opacity: 0.5,
    },
    xaxis: {
      lines: {
        show: false,
      },
    },
  },
  fill: {
    type: "solid",
    colors: ["#5E37FF", "#6AD2FF", "#E1E9F8"],
  },
  legend: {
    show: false,
  },
  colors: ["#5E37FF", "#6AD2FF", "#E1E9F8"],
  dataLabels: {
    enabled: false,
  },
  plotOptions: {
    bar: {
      borderRadius: 10,
      columnWidth: "20px",
    },
  },
};

export const pieChartOptions = {
  labels: ["Your files", "System", "Empty"],
  colors: ["#4318FF", "#6AD2FF", "#EFF4FB"],
  chart: {
    width: "50px",
  },
  states: {
    hover: {
      filter: {
        type: "none",
      },
    },
  },
  legend: {
    show: false,
  },
  dataLabels: {
    enabled: false,
  },
  hover: { mode: null },
  plotOptions: {
    donut: {
      expandOnClick: false,
      donut: {
        labels: {
          show: false,
        },
      },
    },
  },
  fill: {
    colors: ["#4318FF", "#6AD2FF", "#EFF4FB"],
  },
  tooltip: {
    enabled: true,
    theme: "dark",
  },
};

export const ESG_metrics_pieChartOptions = {
  labels: ["Environmental", "Social", "Governance"],
  colors: ["#38ef7d", "#6AD2FF", "#f7b733"],
  chart: {
    width: "10=0%", // Change this to 100% to make it responsive
    height: "100%", // Add this to make it take full height
  },
  states: {
    hover: {
      filter: {
        type: "none",
      },
    },
  },
  legend: {
    show: false,
    position: 'bottom', // Move legend to bottom to give more space to the chart
  },
  dataLabels: {
    enabled: false,
    fontSize: "2px", // Adjust font size as needed
    fontWeight: "1000",
    fontFamily: 'Helvetica, Arial',
  },
  hover: { mode: null },
  plotOptions: {
    pie: { // Change from 'donut' to 'pie' if you want a full pie chart
      expandOnClick: false,
      donut: {
        size: '65%', // Adjust this to change the size of the donut hole (smaller percentage = bigger pie)
      },
    },
  },
  fill: {
    colors: ["#38ef7d", "#6AD2FF", "#f7b733"],
  },
  tooltip: {
    enabled: true,
    theme: "dark",
  },
  responsive: [{
    breakpoint: 480,
    options: {
      chart: {
        width: 300
      },
      legend: {
        position: 'bottom'
      }
    }
  }]
};

export const pieChartData = [63, 25, 12];
export const ESG_metrics_pieChartData = [40,30,30];

// Total Spent Default

export const lineChartDataTotalSpent = [
  {
    name: "Revenue",
    data: [50, 64, 48, 66, 49, 68],
  },
  {
    name: "Profit",
    data: [30, 40, 24, 46, 20, 46],
  },
];

export const lineChartOptionsTotalSpent = {
  chart: {
    toolbar: {
      show: false,
    },
    dropShadow: {
      enabled: true,
      top: 13,
      left: 0,
      blur: 10,
      opacity: 0.1,
      color: "#4318FF",
    },
  },
  colors: ["#4318FF", "#39B8FF"],
  markers: {
    size: 0,
    colors: "white",
    strokeColors: "#7551FF",
    strokeWidth: 3,
    strokeOpacity: 0.9,
    strokeDashArray: 0,
    fillOpacity: 1,
    discrete: [],
    shape: "circle",
    radius: 2,
    offsetX: 0,
    offsetY: 0,
    showNullDataPoints: true,
  },
  tooltip: {
    theme: "dark",
  },
  dataLabels: {
    enabled: false,
  },
  stroke: {
    curve: "smooth",
    type: "line",
  },
  xaxis: {
    type: "numeric",
    categories: ["SEP", "OCT", "NOV", "DEC", "JAN", "FEB"],
    labels: {
      style: {
        colors: "#A3AED0",
        fontSize: "12px",
        fontWeight: "500",
      },
    },
    axisBorder: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
  },
  yaxis: {
    show: false,
  },
  legend: {
    show: false,
  },
  grid: {
    show: false,
    column: {
      color: ["#7551FF", "#39B8FF"],
      opacity: 0.5,
    },
  },
  color: ["#7551FF", "#39B8FF"],
};


export const e_score_line = (data) => {
  // Group data by company
  const groupedData = data.reduce((acc, current) => {
    const { CompanyName, ReportYear, Environmental_Score } = current;
    if (!acc[CompanyName]) {
      acc[CompanyName] = {};
    }
    acc[CompanyName][ReportYear] = Environmental_Score; // Assign the score to the corresponding year
    return acc;
  }, {});

  // Prepare the final data structure for the chart
  const chartData = Object.keys(groupedData).map(company => {
    const years = Object.keys(groupedData[company]).sort(); // Get sorted years
    return {
      name: company,
      data: years.map(year => groupedData[company][year] || 0), // Fill in scores for each year
    };
  });

  return chartData;
};

export const s_score_line = (data) => {
  // Group data by company
  const groupedData = data.reduce((acc, current) => {
    const { CompanyName, ReportYear, Social_Score } = current;
    if (!acc[CompanyName]) {
      acc[CompanyName] = {};
    }
    acc[CompanyName][ReportYear] = Social_Score; // Assign the score to the corresponding year
    return acc;
  }, {});

  // Prepare the final data structure for the chart
  const chartData = Object.keys(groupedData).map(company => {
    const years = Object.keys(groupedData[company]).sort(); // Get sorted years
    return {
      name: company,
      data: years.map(year => groupedData[company][year] || 0), // Fill in scores for each year
    };
  });

  return chartData;
};

export const g_score_line = (data) => {
  // Group data by company
  const groupedData = data.reduce((acc, current) => {
    const { CompanyName, ReportYear, Governance_Score } = current;
    if (!acc[CompanyName]) {
      acc[CompanyName] = {};
    }
    acc[CompanyName][ReportYear] = Governance_Score; // Assign the score to the corresponding year
    return acc;
  }, {});

  // Prepare the final data structure for the chart
  const chartData = Object.keys(groupedData).map(company => {
    const years = Object.keys(groupedData[company]).sort(); // Get sorted years
    return {
      name: company,
      data: years.map(year => groupedData[company][year] || 0), // Fill in scores for each year
    };
  });

  return chartData;
};

export const esg_score_line = (data) => {
  // Group data by company
  // console.log(data);
  const groupedData = data.reduce((acc, current) => {
    const { CompanyName, ReportYear, Final_ESG_score } = current;
    if (!acc[CompanyName]) {
      acc[CompanyName] = {};
    }
    acc[CompanyName][ReportYear] = Final_ESG_score; // Assign the score to the corresponding year
    return acc;
  }, {});

  // Prepare the final data structure for the chart
  const chartData = Object.keys(groupedData).map(company => {
    const years = Object.keys(groupedData[company]).sort(); // Get sorted years
    return {
      name: company,
      data: years.map(year => groupedData[company][year] || 0), // Fill in scores for each year
    };
  });
  // console.log(chartData);
  return chartData;
};


export const E_score_line_option = {
  chart: {
    toolbar: {
      show: false,
    },
    dropShadow: {
      enabled: true,
      top: 13,
      left: 0,
      blur: 10,
      opacity: 0.1,
      color: "#4318FF",
    },
  },
  colors: ["#11998e","#38ef7d","#1D976C", "#93F9B9" , "#56ab2f", "#4318FF"],
  markers: {
    size: 0,
    colors: "white",
    strokeColors: "#7551FF",
    strokeWidth: 3,
    strokeOpacity: 0.9,
    strokeDashArray: 0,
    fillOpacity: 1,
    discrete: [],
    shape: "circle",
    radius: 2,
    offsetX: 0,
    offsetY: 0,
    showNullDataPoints: true,
  },
  tooltip: {
    theme: "dark",
  },
  dataLabels: {
    enabled: true,
  },
  stroke: {
    curve: "smooth",
    type: "line",
  },
  xaxis: {
    type: "numeric",
    categories: [],
    labels: {
      style: {
        colors: "#A3AED0",
        fontSize: "12px",
        fontWeight: "500",
      },
    },
    axisBorder: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
  },
  yaxis: {
    show: true,
  },
  legend: {
    show: true,
    showForSingleSeries: true,
    position: 'bottom',
    horizontalAlign: 'center',
    floating: false,
    fontSize: '14px',
    fontFamily: 'Helvetica, Arial',
    fontWeight: 400,
  },
  grid: {
    show: true,
    column: {
      color: ["#7551FF", "#39B8FF"],
      opacity: 0.5,
    },
  },
  color: ["#11998e", "#39B8FF"],
};

export const S_score_line_option = {
  chart: {
    toolbar: {
      show: false,
    },
    dropShadow: {
      enabled: true,
      top: 13,
      left: 0,
      blur: 10,
      opacity: 0.1,
      color: "#4318FF",
    },
  },
  colors: ["#2F80ED"],
  markers: {
    size: 0,
    colors: "white",
    strokeColors: "#7551FF",
    strokeWidth: 3,
    strokeOpacity: 0.9,
    strokeDashArray: 0,
    fillOpacity: 1,
    discrete: [],
    shape: "circle",
    radius: 2,
    offsetX: 0,
    offsetY: 0,
    showNullDataPoints: true,
  },
  tooltip: {
    theme: "dark",
  },
  dataLabels: {
    enabled: true,
  },
  stroke: {
    curve: "smooth",
    type: "line",
  },
  xaxis: {
    type: "numeric",
    categories: [],
    labels: {
      style: {
        colors: "#A3AED0",
        fontSize: "12px",
        fontWeight: "500",
      },
    },
    axisBorder: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
  },
  yaxis: {
    show: true,
    min: 0,
    max: 10,
    tickAmount: 5,
  },
  legend: {
    show: true,
    showForSingleSeries: true,
    position: 'bottom',
    horizontalAlign: 'center',
    floating: false,
    fontSize: '14px',
    fontFamily: 'Helvetica, Arial',
    fontWeight: 400,
  },
  grid: {
    show: true,
    column: {
      color: ["#7551FF", "#39B8FF"],
      opacity: 0.5,
    },
  },
  color: ["#2F80ED", "#39B8FF"],
};

export const G_score_line_option = {
  chart: {
    toolbar: {
      show: false,
    },
    dropShadow: {
      enabled: true,
      top: 13,
      left: 0,
      blur: 10,
      opacity: 0.1,
      color: "#4318FF",
    },
  },
  colors: ["#F2994A","#38ef7d","#1D976C", "#93F9B9" , "#56ab2f", "#4318FF"],
  markers: {
    size: 0,
    colors: "white",
    strokeColors: "#7551FF",
    strokeWidth: 3,
    strokeOpacity: 0.9,
    strokeDashArray: 0,
    fillOpacity: 1,
    discrete: [],
    shape: "circle",
    radius: 2,
    offsetX: 0,
    offsetY: 0,
    showNullDataPoints: true,
  },
  tooltip: {
    theme: "dark",
  },
  dataLabels: {
    enabled: true,
  },
  stroke: {
    curve: "smooth",
    type: "line",
  },
  xaxis: {
    type: "numeric",
    categories: [],
    labels: {
      style: {
        colors: "#A3AED0",
        fontSize: "12px",
        fontWeight: "500",
      },
    },
    axisBorder: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
  },
  yaxis: {
    show: true,
  },
  legend: {
    show: true,
    showForSingleSeries: true,
    position: 'bottom',
    horizontalAlign: 'center',
    floating: false,
    fontSize: '14px',
    fontFamily: 'Helvetica, Arial',
    fontWeight: 400,
  },
  grid: {
    show: true,
    column: {
      color: ["#7551FF", "#39B8FF"],
      opacity: 0.5,
    },
  },
  color: ["#F2994A", "#39B8FF"],
};


export const ESG_score_line_option = {
  chart: {
    toolbar: {
      show: false,
    },
    dropShadow: {
      enabled: true,
      top: 13,
      left: 0,
      blur: 10,
      opacity: 0.1,
      color: "#4318FF",
    },
  },
  colors: ["#7551FF", "#39B8FF"],
  markers: {
    size: 0,
    colors: "white",
    strokeColors: "#7551FF",
    strokeWidth: 3,
    strokeOpacity: 0.9,
    strokeDashArray: 0,
    fillOpacity: 1,
    discrete: [],
    shape: "circle",
    radius: 2,
    offsetX: 0,
    offsetY: 0,
    showNullDataPoints: true,
  },
  tooltip: {
    theme: "dark",
  },
  dataLabels: {
    enabled: true,
  },
  stroke: {
    curve: "smooth",
    type: "line",
  },
  xaxis: {
    type: "numeric",
    categories: [],
    labels: {
      style: {
        colors: "#A3AED0",
        fontSize: "12px",
        fontWeight: "500",
      },
    },
    axisBorder: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
  },
  yaxis: {
    show: true,
    min: 0,
    max: 10,
    tickAmount: 10, // This will create 5 ticks on the y-axis (0, 2.5, 5, 7.5, 10)
    labels: {
      formatter: function(val) {
        return val.toFixed(1); // This will format the labels to one decimal place
      }
    },
  },
  legend: {
    show: true,
    showForSingleSeries: true,
    position: 'bottom',
    horizontalAlign: 'center',
    floating: false,
    fontSize: '14px',
    fontFamily: 'Helvetica, Arial',
    fontWeight: 400,
  },
  grid: {
    show: true,
    column: {
      color: ["#7551FF", "#39B8FF"],
      opacity: 0.5,
    },
  },
  color: ["#7551FF", "#39B8FF"],
};

