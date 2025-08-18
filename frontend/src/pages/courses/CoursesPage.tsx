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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Courses
        </Typography>
        {(user?.role === 'instructor' || user?.role === 'admin') && (
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setOpen(true)}
          >
            Create Course
          </Button>
        )}
      </Box>

      {/* Courses Grid */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', 
        gap: 3 
      }}>
        {coursesData?.courses?.map((course) => (
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }} key={course.id}>
            <CardContent sx={{ flexGrow: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <School sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6" component="h2">
                  {course.title}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {course.description}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <Chip 
                  label={course.is_active ? 'Active' : 'Inactive'} 
                  color={course.is_active ? 'success' : 'default'}
                  size="small"
                />
                <Chip 
                  label={`${course.lessons?.length || 0} Lessons`} 
                  variant="outlined"
                  size="small"
                />
              </Box>
              <Typography variant="caption" color="text.secondary">
                Created: {new Date(course.created_at).toLocaleDateString()}
              </Typography>
            </CardContent>
            <CardActions>
              <Button 
                size="small" 
                onClick={() => handleViewCourse(course.id)}
              >
                View Course
              </Button>
              {(user?.role === 'instructor' || user?.role === 'admin') && (
                <>
                  <Button size="small" startIcon={<Edit />}>
                    Edit
                  </Button>
                  <Button size="small" color="error" startIcon={<Delete />}>
                    Delete
                  </Button>
                </>
              )}
            </CardActions>
          </Card>
        )) || (
          <Box sx={{ gridColumn: '1 / -1', textAlign: 'center', py: 4 }}>
            <Typography color="text.secondary">
              No courses available. Create your first course!
            </Typography>
          </Box>
        )}
      </Box>

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
