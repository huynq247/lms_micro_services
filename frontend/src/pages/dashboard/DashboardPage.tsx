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
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>

      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Welcome back, {user?.full_name || user?.username}!
        </Typography>
        <Chip 
          label={user?.role?.toUpperCase()} 
          color="primary" 
          variant="outlined"
        />
      </Box>

      {/* Stats Cards */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
        gap: 3, 
        mb: 4 
      }}>
        {stats.map((stat, index) => (
          <Card key={index}>
            <CardContent>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    {stat.title}
                  </Typography>
                  <Typography variant="h4" component="div">
                    {stat.value}
                  </Typography>
                </Box>
                <Box sx={{ color: `${stat.color}.main` }}>
                  {stat.icon}
                </Box>
              </Box>
            </CardContent>
          </Card>
        ))}
      </Box>

      {/* Recent Activity */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, 
        gap: 3 
      }}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Courses
            </Typography>
            {coursesData?.courses?.slice(0, 5).map((course) => (
              <Box key={course.id} sx={{ mb: 1 }}>
                <Typography variant="body1">{course.title}</Typography>
                <Typography variant="body2" color="textSecondary">
                  {course.description}
                </Typography>
              </Box>
            )) || <Typography>No courses available</Typography>}
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Assignments
            </Typography>
            {assignmentsData?.assignments?.slice(0, 5).map((assignment) => (
              <Box key={assignment.id} sx={{ mb: 1 }}>
                <Typography variant="body1">{assignment.title}</Typography>
                <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                  <Chip 
                    label={assignment.status} 
                    size="small" 
                    color={assignment.status === 'completed' ? 'success' : 'default'}
                  />
                  <Chip 
                    label={assignment.content_type} 
                    size="small" 
                    variant="outlined"
                  />
                </Box>
              </Box>
            )) || <Typography>No assignments available</Typography>}
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};

export default DashboardPage;
