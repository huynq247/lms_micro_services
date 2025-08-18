import React, { useState } from 'react';
import {
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  Box,
  Chip,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Alert,
  LinearProgress,
} from '@mui/material';
import { Add, Assignment, Schedule, CheckCircle, RadioButtonUnchecked } from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { assignmentService, CreateAssignmentRequest } from '../../services/assignment.service';
import { contentService } from '../../services/content.service';
import { useAuth } from '../../context/AuthContext';
import { RoleBasedComponent, useRolePermission } from '../../components/common/RoleBasedComponent';

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
      id={`assignments-tabpanel-${index}`}
      aria-labelledby={`assignments-tab-${index}`}
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

const AssignmentsPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [open, setOpen] = useState(false);
  const [error, setError] = useState<string>('');
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const { isTeacherOrAdmin, isStudent, isAdmin } = useRolePermission();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CreateAssignmentRequest>();

  // Fetch assignments
  const { data: assignmentsData, isLoading } = useQuery({
    queryKey: ['assignments'],
    queryFn: () => assignmentService.getAssignments(),
  });

  // Fetch courses for dropdown
  const { data: coursesData } = useQuery({
    queryKey: ['courses'],
    queryFn: contentService.getCourses,
    enabled: open,
  });

  // Create assignment mutation
  const createAssignmentMutation = useMutation({
    mutationFn: assignmentService.createAssignment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assignments'] });
      setOpen(false);
      reset();
      setError('');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to create assignment');
    },
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleCreateAssignment = (data: CreateAssignmentRequest) => {
    createAssignmentMutation.mutate({
      ...data,
      instructor_id: user?.id || 1,
      student_id: 1, // This should be selected from UI
      content_type: 'course',
    });
  };

  const handleViewAssignment = (assignmentId: number) => {
    navigate(`/assignments/${assignmentId}`);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle color="success" />;
      case 'in_progress':
        return <Schedule color="warning" />;
      default:
        return <RadioButtonUnchecked color="disabled" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'warning';
      default:
        return 'default';
    }
  };

  // Filter assignments based on tab
  const filteredAssignments = assignmentsData?.assignments?.filter(assignment => {
    if (tabValue === 0) return true; // All
    if (tabValue === 1) return assignment.status === 'not_started';
    if (tabValue === 2) return assignment.status === 'in_progress';
    if (tabValue === 3) return assignment.status === 'completed';
    return true;
  }) || [];

  if (isLoading) {
    return (
      <Container>
        <Typography>Loading assignments...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Assignments
        </Typography>
        <RoleBasedComponent allowedRoles={['TEACHER', 'ADMIN']}>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setOpen(true)}
          >
            Create Assignment
          </Button>
        </RoleBasedComponent>
      </Box>

      {/* Assignment Statistics */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 3, mb: 3 }}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Assignment sx={{ mr: 2, color: 'primary.main' }} />
              <Box>
                <Typography variant="h6">{assignmentsData?.total || 0}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Assignments
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <RadioButtonUnchecked sx={{ mr: 2, color: 'grey.500' }} />
              <Box>
                <Typography variant="h6">
                  {assignmentsData?.assignments?.filter(a => a.status === 'not_started').length || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Not Started
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Schedule sx={{ mr: 2, color: 'warning.main' }} />
              <Box>
                <Typography variant="h6">
                  {assignmentsData?.assignments?.filter(a => a.status === 'in_progress').length || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  In Progress
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <CheckCircle sx={{ mr: 2, color: 'success.main' }} />
              <Box>
                <Typography variant="h6">
                  {assignmentsData?.assignments?.filter(a => a.status === 'completed').length || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Completed
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="All Assignments" />
          <Tab label="Not Started" />
          <Tab label="In Progress" />
          <Tab label="Completed" />
        </Tabs>
      </Box>

      {/* Assignments List */}
      <TabPanel value={tabValue} index={tabValue}>
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: 3 }}>
          {filteredAssignments.map((assignment) => (
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }} key={assignment.id}>
              <CardContent sx={{ flexGrow: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  {getStatusIcon(assignment.status)}
                  <Typography variant="h6" component="h3" sx={{ ml: 1 }}>
                    {assignment.title}
                  </Typography>
                </Box>
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {assignment.description}
                </Typography>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Course: {assignment.content_title}
                  </Typography>
                  {assignment.due_date && (
                    <Typography variant="body2" color="text.secondary">
                      Due: {new Date(assignment.due_date).toLocaleDateString()}
                    </Typography>
                  )}
                </Box>
                
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <Chip 
                    label={assignment.status.replace('_', ' ')} 
                    color={getStatusColor(assignment.status) as any}
                    size="small"
                  />
                  {assignment.max_points && (
                    <Chip 
                      label={`${assignment.max_points} pts`} 
                      variant="outlined"
                      size="small"
                    />
                  )}
                </Box>
                
                {assignment.status === 'in_progress' && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      Progress: 50%
                    </Typography>
                    <LinearProgress variant="determinate" value={50} />
                  </Box>
                )}
              </CardContent>
              
              <CardActions>
                <Button 
                  size="small" 
                  onClick={() => handleViewAssignment(assignment.id)}
                >
                  View Details
                </Button>
                {assignment.status === 'not_started' && (
                  <Button size="small" variant="contained">
                    Start
                  </Button>
                )}
                {assignment.status === 'in_progress' && (
                  <Button size="small" variant="contained">
                    Continue
                  </Button>
                )}
              </CardActions>
            </Card>
          ))}
          
          {filteredAssignments.length === 0 && (
            <Box sx={{ gridColumn: '1 / -1', textAlign: 'center', py: 4 }}>
              <Typography color="text.secondary">
                No assignments found.
              </Typography>
            </Box>
          )}
        </Box>
      </TabPanel>

      {/* Create Assignment Dialog */}
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Assignment</DialogTitle>
        <DialogContent>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          
          <TextField
            autoFocus
            margin="dense"
            label="Assignment Title"
            fullWidth
            variant="outlined"
            {...register('title', { required: 'Assignment title is required' })}
            error={!!errors.title}
            helperText={errors.title?.message}
            sx={{ mb: 2 }}
          />
          
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            {...register('description', { required: 'Description is required' })}
            error={!!errors.description}
            helperText={errors.description?.message}
            sx={{ mb: 2 }}
          />
          
          <TextField
            margin="dense"
            label="Instructions"
            fullWidth
            multiline
            rows={4}
            variant="outlined"
            {...register('instructions', { required: 'Instructions are required' })}
            error={!!errors.instructions}
            helperText={errors.instructions?.message}
            sx={{ mb: 2 }}
          />
          
          <TextField
            select
            margin="dense"
            label="Course"
            fullWidth
            variant="outlined"
            {...register('content_id', { required: 'Course selection is required' })}
            error={!!errors.content_id}
            helperText={errors.content_id?.message}
          >
            {coursesData?.courses?.map((course) => (
              <MenuItem key={course.id} value={course.id}>
                {course.title}
              </MenuItem>
            ))}
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleSubmit(handleCreateAssignment)}
            variant="contained"
            disabled={createAssignmentMutation.isPending}
          >
            {createAssignmentMutation.isPending ? 'Creating...' : 'Create Assignment'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default AssignmentsPage;
