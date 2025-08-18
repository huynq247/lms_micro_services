import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Chip,
  Tabs,
  Tab,
  Button,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
} from '@mui/material';
import {
  ArrowBack,
  School,
  PlayCircleOutline,
  Assignment,
  People,
  ExpandMore,
  Edit,
  Add,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { contentService } from '../../services/content.service';
import { assignmentService } from '../../services/assignment.service';
import { useAuth } from '../../context/AuthContext';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`course-tabpanel-${index}`}
      aria-labelledby={`course-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const CourseDetailPage: React.FC = () => {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);
  const { user } = useAuth();

  // Fetch course details
  const { data: course, isLoading: courseLoading } = useQuery({
    queryKey: ['course', courseId],
    queryFn: () => contentService.getCourse(courseId!),
    enabled: !!courseId,
  });

  // Fetch assignments for this course
  const { data: assignmentsData } = useQuery({
    queryKey: ['assignments', courseId],
    queryFn: () => assignmentService.getAssignments({ course_id: courseId }),
    enabled: !!courseId,
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (courseLoading) {
    return (
      <Container>
        <Typography>Loading course...</Typography>
      </Container>
    );
  }

  if (!course) {
    return (
      <Container>
        <Alert severity="error">Course not found</Alert>
      </Container>
    );
  }

  const isInstructor = user?.role === 'instructor' || user?.role === 'admin';

  return (
    <Container maxWidth="lg">
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Button
          startIcon={<ArrowBack />}
          onClick={() => navigate('/courses')}
          sx={{ mb: 2 }}
        >
          Back to Courses
        </Button>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <School sx={{ mr: 2, fontSize: 40, color: 'primary.main' }} />
              <Typography variant="h4" component="h1">
                {course.title}
              </Typography>
              {isInstructor && (
                <IconButton sx={{ ml: 2 }}>
                  <Edit />
                </IconButton>
              )}
            </Box>
            
            <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
              {course.description}
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <Chip 
                label={course.is_active ? 'Active' : 'Inactive'} 
                color={course.is_active ? 'success' : 'default'}
              />
              <Chip 
                label={`${course.lessons?.length || 0} Lessons`} 
                variant="outlined"
              />
              <Chip 
                label={`${assignmentsData?.assignments?.length || 0} Assignments`} 
                variant="outlined"
              />
            </Box>
            
            <Typography variant="caption" color="text.secondary">
              Created: {new Date(course.created_at).toLocaleDateString()}
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Course Stats */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
        gap: 3, 
        mb: 3 
      }}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <PlayCircleOutline sx={{ mr: 2, color: 'primary.main' }} />
              <Box>
                <Typography variant="h6">{course.lessons?.length || 0}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Lessons
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Assignment sx={{ mr: 2, color: 'warning.main' }} />
              <Box>
                <Typography variant="h6">{assignmentsData?.assignments?.length || 0}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Assignments
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <People sx={{ mr: 2, color: 'success.main' }} />
              <Box>
                <Typography variant="h6">0</Typography>
                <Typography variant="body2" color="text.secondary">
                  Students
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Lessons" />
          <Tab label="Assignments" />
          <Tab label="Students" />
        </Tabs>
      </Box>

      {/* Lessons Tab */}
      <TabPanel value={tabValue} index={0}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6">Course Lessons</Typography>
          {isInstructor && (
            <Button variant="contained" startIcon={<Add />}>
              Add Lesson
            </Button>
          )}
        </Box>
        
        {course.lessons && course.lessons.length > 0 ? (
          course.lessons.map((lesson, index) => (
            <Accordion key={lesson.id} sx={{ mb: 1 }}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                  <PlayCircleOutline sx={{ mr: 2, color: 'primary.main' }} />
                  <Box>
                    <Typography variant="subtitle1">
                      Lesson {index + 1}: {lesson.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {lesson.content?.substring(0, 100)}...
                    </Typography>
                  </Box>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2">
                  {lesson.content}
                </Typography>
                {isInstructor && (
                  <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                    <Button size="small" startIcon={<Edit />}>
                      Edit Lesson
                    </Button>
                  </Box>
                )}
              </AccordionDetails>
            </Accordion>
          ))
        ) : (
          <Typography color="text.secondary" align="center">
            No lessons available. {isInstructor && 'Add your first lesson!'}
          </Typography>
        )}
      </TabPanel>

      {/* Assignments Tab */}
      <TabPanel value={tabValue} index={1}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6">Course Assignments</Typography>
          {isInstructor && (
            <Button variant="contained" startIcon={<Add />}>
              Create Assignment
            </Button>
          )}
        </Box>
        
        {assignmentsData?.assignments && assignmentsData.assignments.length > 0 ? (
          <List>
            {assignmentsData.assignments.map((assignment) => (
              <ListItem 
                key={assignment.id} 
                sx={{ 
                  border: 1, 
                  borderColor: 'divider', 
                  borderRadius: 1, 
                  mb: 1,
                  cursor: 'pointer'
                }}
                onClick={() => navigate(`/assignments/${assignment.id}`)}
              >
                <ListItemIcon>
                  <Assignment color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary={assignment.title}
                  secondary={
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        {assignment.description}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Due: {assignment.due_date ? new Date(assignment.due_date).toLocaleDateString() : 'No due date'}
                      </Typography>
                    </Box>
                  }
                />
                <Chip 
                  label={assignment.max_points ? `${assignment.max_points} pts` : 'No points'} 
                  size="small" 
                  variant="outlined"
                />
              </ListItem>
            ))}
          </List>
        ) : (
          <Typography color="text.secondary" align="center">
            No assignments available. {isInstructor && 'Create your first assignment!'}
          </Typography>
        )}
      </TabPanel>

      {/* Students Tab */}
      <TabPanel value={tabValue} index={2}>
        <Typography variant="h6" sx={{ mb: 3 }}>Enrolled Students</Typography>
        <Typography color="text.secondary" align="center">
          Student enrollment feature coming soon...
        </Typography>
      </TabPanel>
    </Container>
  );
};

export default CourseDetailPage;
