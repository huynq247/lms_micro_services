import React from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Box,
  Chip,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  School,
  Assignment,
  Person,
} from '@mui/icons-material';
import { useAuth } from '../../context/AuthContext';
import { useQuery } from '@tanstack/react-query';
import { contentService } from '../../services/content.service';
import { assignmentService } from '../../services/assignment.service';
import { GlassContainer, GradientText } from '../../components/common/GlassContainer';

const DashboardPage: React.FC = () => {
  const { user } = useAuth();

  // Fetch dashboard data
  const { data: coursesData } = useQuery({
    queryKey: ['courses'],
    queryFn: contentService.getCourses,
  });

  const { data: assignmentsData } = useQuery({
    queryKey: ['assignments'],
    queryFn: () => assignmentService.getAssignments({ page: 1, size: 10 }),
  });

  const { data: analyticsData } = useQuery({
    queryKey: ['analytics'],
    queryFn: assignmentService.getAnalyticsSummary,
  });

  // Role-based stats
  const getStatsForRole = () => {
    const baseStats = [
      {
        title: 'Total Courses',
        value: coursesData?.courses?.length || 0,
        icon: <School />,
        color: 'primary',
      },
      {
        title: 'Total Assignments',
        value: assignmentsData?.assignments?.length || 0,
        icon: <Assignment />,
        color: 'secondary',
      },
    ];

    if (user?.role?.toUpperCase() === 'ADMIN') {
      return [
        ...baseStats,
        {
          title: 'Total Students',
          value: analyticsData?.total_students || 0,
          icon: <Person />,
          color: 'info',
        },
        {
          title: 'Total Teachers',
          value: 3, // Hardcoded for now, will implement user service later
          icon: <Person />,
          color: 'warning',
        },
      ];
    } else if (user?.role?.toUpperCase() === 'TEACHER') {
      return [
        ...baseStats,
        {
          title: 'My Students',
          value: analyticsData?.total_students || 0,
          icon: <Person />,
          color: 'info',
        },
        {
          title: 'Completion Rate',
          value: `${analyticsData?.completion_rate || 0}%`,
          icon: <DashboardIcon />,
          color: 'success',
        },
      ];
    } else {
      // STUDENT
      return [
        ...baseStats,
        {
          title: 'Completed',
          value: `${analyticsData?.completion_rate || 0}%`,
          icon: <DashboardIcon />,
          color: 'success',
        },
        {
          title: 'In Progress',
          value: assignmentsData?.assignments?.filter((a: any) => a.status === 'in_progress')?.length || 0,
          icon: <Assignment />,
          color: 'warning',
        },
      ];
    }
  };

  const stats = getStatsForRole();

  return (
    <Container maxWidth="lg">
      <GlassContainer sx={{ mb: 4 }}>
        <GradientText variant="primary" component={Typography} sx={{ variant: 'h4', component: 'h1', gutterBottom: true }}>
          Dashboard
        </GradientText>

        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: '#1a202c' }}>
            Welcome back, {user?.full_name || user?.username}!
          </Typography>
          <Chip 
            label={user?.role?.toUpperCase()} 
            color="primary" 
            variant="filled"
            sx={{ fontWeight: 600 }}
          />
        </Box>
      </GlassContainer>

      {/* Stats Cards */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
        gap: 3, 
        mb: 4 
      }}>
        {stats.map((stat, index) => (
          <GlassContainer key={index} sx={{ height: '100%' }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <Box>
                <Typography color="textSecondary" gutterBottom sx={{ fontWeight: 500 }}>
                  {stat.title}
                </Typography>
                <GradientText variant={stat.color as any} component={Typography} 
                  sx={{ fontSize: '2.5rem', fontWeight: 800, lineHeight: 1 }}>
                  {stat.value}
                </GradientText>
              </Box>
              <Box sx={{ 
                color: `${stat.color}.main`, 
                opacity: 0.7,
                fontSize: '2.5rem'
              }}>
                {stat.icon}
              </Box>
            </Box>
          </GlassContainer>
        ))}
      </Box>

      {/* Recent Activity */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, 
        gap: 3 
      }}>
        <GlassContainer>
          <GradientText variant="primary" component={Typography} sx={{ variant: 'h6', gutterBottom: true, mb: 3 }}>
            Recent Courses
          </GradientText>
          {coursesData?.courses?.slice(0, 5).map((course) => (
            <Box key={course.id} sx={{ mb: 2, p: 2, borderRadius: 2, backgroundColor: 'rgba(168, 184, 240, 0.1)' }}>
              <Typography variant="body1" sx={{ fontWeight: 600, color: '#1a202c' }}>
                {course.title}
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ fontWeight: 500 }}>
                {course.description}
              </Typography>
            </Box>
          )) || <Typography sx={{ fontWeight: 500 }}>No courses available</Typography>}
        </GlassContainer>

        <GlassContainer>
          <GradientText variant="secondary" component={Typography} sx={{ variant: 'h6', gutterBottom: true, mb: 3 }}>
            Recent Assignments
          </GradientText>
          {assignmentsData?.assignments?.slice(0, 5).map((assignment) => (
            <Box key={assignment.id} sx={{ mb: 2, p: 2, borderRadius: 2, backgroundColor: 'rgba(245, 194, 231, 0.1)' }}>
              <Typography variant="body1" sx={{ fontWeight: 600, color: '#1a202c' }}>
                {assignment.title}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                <Chip 
                  label={assignment.status} 
                  size="small" 
                  color={assignment.status === 'completed' ? 'success' : 'warning'}
                  sx={{ fontWeight: 600 }}
                />
                <Chip 
                  label={assignment.content_type} 
                  size="small" 
                  variant="outlined"
                  sx={{ fontWeight: 600 }}
                />
              </Box>
            </Box>
          )) || <Typography sx={{ fontWeight: 500 }}>No assignments available</Typography>}
        </GlassContainer>
      </Box>
    </Container>
  );
};

export default DashboardPage;
