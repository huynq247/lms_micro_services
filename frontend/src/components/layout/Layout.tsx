import React from 'react';
import { Outlet } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
} from '@mui/material';
import {
  Dashboard,
  School,
  Assignment,
  Quiz,
  ExitToApp,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { GradientText } from '../common/GlassContainer';

const drawerWidth = 240;

const Layout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    { text: 'Dashboard', icon: <Dashboard />, path: '/dashboard', roles: ['ADMIN', 'TEACHER', 'STUDENT'] },
    { text: 'Courses', icon: <School />, path: '/courses', roles: ['ADMIN', 'TEACHER', 'STUDENT'] },
    { text: 'Assignments', icon: <Assignment />, path: '/assignments', roles: ['ADMIN', 'TEACHER', 'STUDENT'] },
    { text: 'Flashcards', icon: <Quiz />, path: '/decks', roles: ['ADMIN', 'TEACHER', 'STUDENT'] },
    { text: 'User Management', icon: <Dashboard />, path: '/users', roles: ['ADMIN'] },
    { text: 'Analytics', icon: <Dashboard />, path: '/analytics', roles: ['ADMIN', 'TEACHER'] },
  ];

  // Filter menu items based on user role
  const filteredMenuItems = menuItems.filter(item => 
    item.roles.includes(user?.role?.toUpperCase() || '')
  );

  return (
    <Box sx={{ display: 'flex' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{ 
          zIndex: (theme) => theme.zIndex.drawer + 1,
          background: 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(168, 184, 240, 0.2)',
          boxShadow: '0 4px 16px 0 rgba(168, 184, 240, 0.15)',
          color: '#1a202c',
        }}
      >
        <Toolbar>
          <GradientText variant="primary" component={Typography} sx={{ variant: 'h6', component: 'div', flexGrow: 1, fontWeight: 800 }}>
            Learning Management System
          </GradientText>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="body2" sx={{ fontWeight: 600, color: '#2d3748' }}>
              Welcome, {user?.full_name || user?.username} ({user?.role})
            </Typography>
            <Button 
              color="inherit" 
              onClick={handleLogout} 
              startIcon={<ExitToApp />}
              sx={{ 
                color: '#1a202c',
                fontWeight: 600,
                borderRadius: '12px',
                '&:hover': {
                  backgroundColor: 'rgba(168, 184, 240, 0.1)',
                }
              }}
            >
              Logout
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            background: 'rgba(255, 255, 255, 0.9)',
            backdropFilter: 'blur(20px)',
            borderRight: '1px solid rgba(168, 184, 240, 0.2)',
          },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto' }}>
          <List>
            {filteredMenuItems.map((item) => (
              <ListItem key={item.text} disablePadding>
                <ListItemButton
                  selected={location.pathname === item.path}
                  onClick={() => navigate(item.path)}
                  sx={{
                    margin: 1,
                    borderRadius: '12px',
                    fontWeight: 600,
                    '&.Mui-selected': {
                      background: 'linear-gradient(135deg, rgba(168, 184, 240, 0.15) 0%, rgba(177, 156, 217, 0.15) 100%)',
                      border: '1px solid rgba(168, 184, 240, 0.3)',
                      '&:hover': {
                        background: 'linear-gradient(135deg, rgba(168, 184, 240, 0.2) 0%, rgba(177, 156, 217, 0.2) 100%)',
                      }
                    },
                    '&:hover': {
                      background: 'rgba(168, 184, 240, 0.1)',
                    }
                  }}
                >
                  <ListItemIcon sx={{ color: location.pathname === item.path ? '#a8b8f0' : '#4a5568' }}>
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText 
                    primary={item.text} 
                    sx={{ 
                      '& .MuiListItemText-primary': { 
                        fontWeight: 600,
                        color: location.pathname === item.path ? '#1a202c' : '#4a5568'
                      } 
                    }} 
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          bgcolor: 'background.default',
          p: 3,
        }}
      >
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
};

export default Layout;
