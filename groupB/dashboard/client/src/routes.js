import React from 'react';

import { Icon } from '@chakra-ui/react';
import {
  MdBarChart,
  MdPerson,
  MdHome,
  MdLock,
  MdOutlineShoppingCart,
} from 'react-icons/md';

// Admin Imports
import MainDashboard from 'views/admin/default';
import UploadPage from 'views/admin/UploadPage';
import Profile from 'views/admin/profile';
import DataTables from 'views/admin/dataTables';
import { MdUpload } from "react-icons/md";
import NFTMarketplace from 'views/admin/marketplace';


// Auth Imports
import SignInCentered from 'views/auth/signIn';

const routes = [
  {
    name: 'Dashboard',
    layout: '/admin',
    path: '/default',
    icon: <Icon as={MdHome} width="20px" height="20px" color="inherit" />,
    component: <MainDashboard />,
  },
  {
    name: 'ESG Report Upload',
    layout: '/admin',
    path: '/upload',
    icon: (
      <Icon
        as={MdUpload}
        width="20px"
        height="20px"
        color="inherit"
      />
    ),
    component: <UploadPage />,
    secondary: true,
  },
  {
    name: 'Data Tables',
    layout: '/admin',
    icon: <Icon as={MdBarChart} width="20px" height="20px" color="inherit" />,
    path: '/data-tables',
    component: <DataTables />,
  },
  {
    name: 'Profile',
    layout: '/admin',
    path: '/profile',
    icon: <Icon as={MdPerson} width="20px" height="20px" color="inherit" />,
    component: <Profile />,
  },

  {
    name: 'Logout',
    layout: '/auth',
    path: '/sign-in',
    icon: <Icon as={MdLock} width="20px" height="20px" color="inherit" />,
    component: <SignInCentered />,
  },
//   {
//     name: 'RTL Admin',
//     layout: '/rtl',
//     path: '/rtl-default',
//     icon: <Icon as={MdHome} width="20px" height="20px" color="inherit" />,
//     component: <RTL />,
//   },
];

export default routes;
