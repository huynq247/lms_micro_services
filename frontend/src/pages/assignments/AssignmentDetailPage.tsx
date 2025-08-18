import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Paper,
  LinearProgress,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
} from '@mui/material';
import {
  ArrowBack,
  Assignment,
  Schedule,
  CheckCircle,
  PlayArrow,
  Pause,
  Edit,
  Timer,
  Person,
  School,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { assignmentService } from '../../services/assignment.service';
import { useAuth } from '../../context/AuthContext';

const AssignmentDetailPage: React.FC = () => {
  const { assignmentId } = useParams<{ assignmentId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [isWorking, setIsWorking] = useState(false);

  // Fetch assignment details
  const { data: assignment, isLoading } = useQuery({
    queryKey: ['assignment', assignmentId],
    queryFn: () => assignmentService.getAssignment(Number(assignmentId)),
    enabled: !!assignmentId,
  });

  // Fetch progress
  const { data: progress } = useQuery({
    queryKey: ['progress', assignmentId],
    queryFn: () => assignmentService.getProgress(Number(assignmentId)),
    enabled: !!assignmentId,
  });

  // Update progress mutation
  const updateProgressMutation = useMutation({
    mutationFn: (data: { completion_percentage: number; time_spent: number; status: 'not_started' | 'in_progress' | 'completed' }) =>
      assignmentService.updateProgress(Number(assignmentId), data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['progress', assignmentId] });
      queryClient.invalidateQueries({ queryKey: ['assignment', assignmentId] });
    },
  });

  const handleStartWork = () => {
    setIsWorking(true);
    // Start timer logic here
  };

  const handlePauseWork = () => {
    setIsWorking(false);
    // Pause timer and save progress
    updateProgressMutation.mutate({
      completion_percentage: progress?.completion_percentage || 0,
      time_spent: progress?.time_spent || 0,
      status: 'in_progress',
    });
  };

  const handleCompleteAssignment = () => {
    updateProgressMutation.mutate({
      completion_percentage: 100,
      time_spent: progress?.time_spent || 0,
      status: 'completed',
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle color="success" />;
      case 'in_progress':
        return <Schedule color="warning" />;
      default:
        return <Assignment color="disabled" />;
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

  if (isLoading) {
    return (
      <Container>
        <Typography>Loading assignment...</Typography>
      </Container>
    );
  }

  if (!assignment) {
    return (
      <Container>
        <Alert severity="error">Assignment not found</Alert>
      </Container>
    );
  }

  const isInstructor = user?.role === 'instructor' || user?.role === 'admin';
  const progressPercentage = progress?.completion_percentage || 0;
  const currentStatus = assignment.status;

  return (
    <Container maxWidth="lg">
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Button
          startIcon={<ArrowBack />}
          onClick={() => navigate('/assignments')}
          sx={{ mb: 2 }}
        >
          Back to Assignments
        </Button>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
          <Box sx={{ flex: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              {getStatusIcon(currentStatus)}
              <Typography variant="h4" component="h1" sx={{ ml: 2 }}>
                {assignment.title}
              </Typography>
              {isInstructor && (
                <IconButton sx={{ ml: 2 }}>
                  <Edit />
                </IconButton>
              )}
            </Box>

            <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
              {assignment.description}
            </Typography>

            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <Chip 
                label={currentStatus.replace('_', ' ')} 
                color={getStatusColor(currentStatus) as any}
              />
              {assignment.max_points && (
                <Chip 
                  label={`${assignment.max_points} points`} 
                  variant="outlined"
                />
              )}
              <Chip 
                label={assignment.content_title} 
                variant="outlined"
                icon={<School />}
              />
            </Box>

            <Typography variant="caption" color="text.secondary">
              Created: {new Date(assignment.created_at).toLocaleDateString()}
              {assignment.due_date && (
                <> • Due: {new Date(assignment.due_date).toLocaleDateString()}</>
              )}
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Progress Section */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Progress Overview
          </Typography>
          
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2">Completion</Typography>
              <Typography variant="body2">{progressPercentage}%</Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={progressPercentage} 
              sx={{ height: 8, borderRadius: 4 }}
            />
          </Box>

          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
            <Box>
              <Typography variant="body2" color="text.secondary">Time Spent</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Timer sx={{ mr: 1, fontSize: 20 }} />
                <Typography variant="h6">{Math.floor((progress?.time_spent || 0) / 60)} min</Typography>
              </Box>
            </Box>
            
            <Box>
              <Typography variant="body2" color="text.secondary">Status</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                {getStatusIcon(currentStatus)}
                <Typography variant="h6" sx={{ ml: 1, textTransform: 'capitalize' }}>
                  {currentStatus.replace('_', ' ')}
                </Typography>
              </Box>
            </Box>
            
            <Box>
              <Typography variant="body2" color="text.secondary">Last Accessed</Typography>
              <Typography variant="h6">
                {progress?.last_accessed 
                  ? new Date(progress.last_accessed).toLocaleDateString()
                  : 'Never'
                }
              </Typography>
            </Box>
          </Box>

          {/* Action Buttons */}
          <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
            {currentStatus === 'not_started' && (
              <Button
                variant="contained"
                startIcon={<PlayArrow />}
                onClick={handleStartWork}
              >
                Start Assignment
              </Button>
            )}
            
            {currentStatus === 'in_progress' && (
              <>
                {!isWorking ? (
                  <Button
                    variant="contained"
                    startIcon={<PlayArrow />}
                    onClick={handleStartWork}
                  >
                    Continue Working
                  </Button>
                ) : (
                  <Button
                    variant="outlined"
                    startIcon={<Pause />}
                    onClick={handlePauseWork}
                  >
                    Pause Work
                  </Button>
                )}
                
                <Button
                  variant="contained"
                  color="success"
                  startIcon={<CheckCircle />}
                  onClick={handleCompleteAssignment}
                >
                  Mark Complete
                </Button>
              </>
            )}
            
            {currentStatus === 'completed' && (
              <Chip 
                label="Completed" 
                color="success" 
                icon={<CheckCircle />}
                sx={{ fontSize: '1rem', py: 2, px: 3 }}
              />
            )}
          </Box>
        </CardContent>
      </Card>

      {/* Instructions Section */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Instructions
          </Typography>
          <Paper variant="outlined" sx={{ p: 2, backgroundColor: 'grey.50' }}>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
              {assignment.instructions}
            </Typography>
          </Paper>
        </CardContent>
      </Card>

      {/* Assignment Details */}
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Assignment Details
          </Typography>
          
          <List>
            <ListItem>
              <ListItemIcon>
                <Person />
              </ListItemIcon>
              <ListItemText
                primary="Instructor"
                secondary={`Instructor ID: ${assignment.instructor_id}`}
              />
            </ListItem>
            
            <Divider variant="inset" component="li" />
            
            <ListItem>
              <ListItemIcon>
                <School />
              </ListItemIcon>
              <ListItemText
                primary="Course"
                secondary={assignment.content_title}
              />
            </ListItem>
            
            <Divider variant="inset" component="li" />
            
            <ListItem>
              <ListItemIcon>
                <Assignment />
              </ListItemIcon>
              <ListItemText
                primary="Content Type"
                secondary={assignment.content_type}
              />
            </ListItem>
            
            {assignment.due_date && (
              <>
                <Divider variant="inset" component="li" />
                <ListItem>
                  <ListItemIcon>
                    <Schedule />
                  </ListItemIcon>
                  <ListItemText
                    primary="Due Date"
                    secondary={new Date(assignment.due_date).toLocaleString()}
                  />
                </ListItem>
              </>
            )}
          </List>
        </CardContent>
      </Card>
    </Container>
  );
};

export default AssignmentDetailPage;
