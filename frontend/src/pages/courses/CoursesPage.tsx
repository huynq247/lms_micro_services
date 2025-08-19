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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
} from '@mui/material';
import { Add, School, Edit, Delete } from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { contentService, CreateCourseRequest } from '../../services/content.service';
import { useAuth } from '../../context/AuthContext';
import { GlassContainer, GradientText } from '../../components/common/GlassContainer';

const CoursesPage: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [error, setError] = useState<string>('');
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CreateCourseRequest>();

  // Fetch courses
  const { data: coursesData, isLoading } = useQuery({
    queryKey: ['courses'],
    queryFn: contentService.getCourses,
  });

  // Create course mutation
  const createCourseMutation = useMutation({
    mutationFn: contentService.createCourse,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] });
      setOpen(false);
      reset();
      setError('');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to create course');
    },
  });

  const handleCreateCourse = (data: CreateCourseRequest) => {
    createCourseMutation.mutate({
      ...data,
      instructor_id: user?.id?.toString() || '1',
    });
  };

  const handleViewCourse = (courseId: string) => {
    navigate(`/courses/${courseId}`);
  };

  if (isLoading) {
    return (
      <Container>
        <Typography>Loading courses...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <GlassContainer sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <GradientText variant="primary" component={Typography} sx={{ variant: 'h4', component: 'h1' }}>
            Courses
          </GradientText>
          {(user?.role === 'instructor' || user?.role === 'admin') && (
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setOpen(true)}
              sx={{ 
                fontWeight: 700,
                borderRadius: '14px',
                px: 3,
                py: 1.5
              }}
            >
              Create Course
            </Button>
          )}
        </Box>
      </GlassContainer>

      {/* Courses Grid */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', 
        gap: 3 
      }}>
        {coursesData?.courses?.map((course) => (
          <GlassContainer key={course.id} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ flexGrow: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <School sx={{ mr: 1.5, color: 'primary.main', fontSize: '1.5rem' }} />
                <GradientText variant="primary" component={Typography} sx={{ variant: 'h6', component: 'h2', fontWeight: 700 }}>
                  {course.title}
                </GradientText>
              </Box>
              <Typography variant="body1" color="text.primary" sx={{ mb: 3, fontWeight: 500, lineHeight: 1.6 }}>
                {course.description}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1.5, mb: 3 }}>
                <Chip 
                  label={course.is_active ? 'Active' : 'Inactive'} 
                  color={course.is_active ? 'success' : 'warning'}
                  size="medium"
                  sx={{ fontWeight: 600 }}
                />
                <Chip 
                  label={`${course.lessons?.length || 0} Lessons`} 
                  variant="outlined"
                  size="medium"
                  sx={{ fontWeight: 600 }}
                />
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
                Created: {new Date(course.created_at).toLocaleDateString()}
              </Typography>
            </Box>
            <Box sx={{ mt: 3, display: 'flex', gap: 1.5 }}>
              <Button
                variant="contained"
                onClick={() => navigate(`/courses/${course.id}`)}
                sx={{ flex: 1, fontWeight: 600, borderRadius: '12px' }}
              >
                View Details
              </Button>
              {(user?.role === 'instructor' || user?.role === 'admin') && (
                <Button
                  variant="outlined"
                  startIcon={<Edit />}
                  onClick={() => navigate(`/courses/${course.id}/edit`)}
                  sx={{ fontWeight: 600, borderRadius: '12px' }}
                >
                  Edit
                </Button>
              )}
            </Box>
          </GlassContainer>
        ))}
      </Box>

      {coursesData?.courses?.length === 0 && (
        <GlassContainer sx={{ textAlign: 'center', py: 4, mt: 4 }}>
          <Typography color="text.secondary" sx={{ fontWeight: 500 }}>
            No courses available. Create your first course!
          </Typography>
        </GlassContainer>
      )}

      {/* Create Course Dialog */}
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Course</DialogTitle>
        <DialogContent>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          
          <TextField
            autoFocus
            margin="dense"
            label="Course Title"
            fullWidth
            variant="outlined"
            {...register('title', { required: 'Course title is required' })}
            error={!!errors.title}
            helperText={errors.title?.message}
            sx={{ mb: 2 }}
          />
          
          <TextField
            margin="dense"
            label="Course Description"
            fullWidth
            multiline
            rows={4}
            variant="outlined"
            {...register('description', { required: 'Course description is required' })}
            error={!!errors.description}
            helperText={errors.description?.message}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleSubmit(handleCreateCourse)}
            variant="contained"
            disabled={createCourseMutation.isPending}
          >
            {createCourseMutation.isPending ? 'Creating...' : 'Create Course'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default CoursesPage;
