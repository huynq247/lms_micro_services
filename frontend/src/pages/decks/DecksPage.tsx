import React, { useState } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Box,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Chip,
  Stack,
  FormControlLabel,
  Checkbox,
} from '@mui/material';
import { Add, Style, School, Visibility, Edit, Delete } from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { contentService, Deck, CreateDeckRequest } from '../../services/content.service';
import { RoleBasedComponent } from '../../components/common/RoleBasedComponent';
import { useAuth } from '../../context/AuthContext';
import { GlassContainer, GradientText } from '../../components/common/GlassContainer';

const DecksPage: React.FC = () => {
  const [openCreateDialog, setOpenCreateDialog] = useState(false);
  const [error, setError] = useState<string>('');
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CreateDeckRequest>();

  // Fetch decks
  const { data: decksData, isLoading } = useQuery({
    queryKey: ['decks'],
    queryFn: contentService.getDecks,
  });

  // Create deck mutation
  const createDeckMutation = useMutation({
    mutationFn: contentService.createDeck,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['decks'] });
      setOpenCreateDialog(false);
      reset();
      setError('');
    },
    onError: (err: any) => {
      setError(err.message || 'Failed to create deck');
    },
  });

  // Delete deck mutation
  const deleteDeckMutation = useMutation({
    mutationFn: (deckId: string) => contentService.deleteDeck(deckId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['decks'] });
    },
  });

  const handleCreateDeck = (data: CreateDeckRequest) => {
    const deckData = {
      ...data,
      instructor_id: String(user?.id || '')
    };
    createDeckMutation.mutate(deckData);
  };

  const handleDeleteDeck = (deckId: string) => {
    if (window.confirm('Are you sure you want to delete this deck?')) {
      deleteDeckMutation.mutate(deckId);
    }
  };

  const handleViewDeck = (deckId: string) => {
    navigate(`/decks/${deckId}`);
  };

  const handleStudyDeck = (deckId: string) => {
    navigate(`/decks/${deckId}/study`);
  };

  const getDifficultyColor = (difficulty: string | undefined | null) => {
    if (!difficulty) return 'default';
    switch (difficulty.toLowerCase()) {
      case 'easy': return 'success';
      case 'medium': return 'warning';
      case 'hard': return 'error';
      default: return 'default';
    }
  };

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <GlassContainer>
          <GradientText variant="primary" component="h1" sx={{ fontSize: '2rem', mb: 2 }}>
            Loading Your Decks...
          </GradientText>
        </GlassContainer>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <GlassContainer sx={{ mb: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <GradientText variant="primary" component="h1" sx={{ fontSize: '2.5rem', mb: 1 }}>
              🃏 Flashcard Decks
            </GradientText>
            <Typography variant="body1" color="text.secondary">
              Create, manage, and study your flashcard collections
            </Typography>
          </Box>
          <RoleBasedComponent allowedRoles={['TEACHER', 'ADMIN']}>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setOpenCreateDialog(true)}
              size="large"
              sx={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
                  transform: 'translateY(-2px)',
                },
              }}
            >
              Create Deck
            </Button>
          </RoleBasedComponent>
        </Box>
      </GlassContainer>

      {/* Stats */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: 'repeat(3, 1fr)' },
          gap: 3,
          mb: 4
        }}
      >
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center">
              <Style color="primary" sx={{ mr: 2 }} />
              <Box>
                <Typography variant="h6">
                  {decksData?.decks?.length || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Decks
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center">
              <School color="success" sx={{ mr: 2 }} />
              <Box>
                <Typography variant="h6">
                  {decksData?.decks?.reduce((acc, deck) => acc + (deck.total_flashcards || 0), 0) || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Cards
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center">
              <Visibility color="info" sx={{ mr: 2 }} />
              <Box>
                <Typography variant="h6">
                  {decksData?.decks?.filter(deck => deck.is_published || deck.is_public).length || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Public Decks
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Decks Grid */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: 'repeat(3, 1fr)' },
          gap: 3
        }}
      >
        {decksData?.decks?.map((deck: Deck) => (
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1 }}>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                  <Typography variant="h6" component="h2" gutterBottom>
                    {deck.title}
                  </Typography>
                  <Chip
                    label={deck.difficulty || 'No difficulty'}
                    color={getDifficultyColor(deck.difficulty)}
                    size="small"
                  />
                </Box>
                
                <Typography variant="body2" color="text.secondary" paragraph>
                  {deck.description}
                </Typography>

                <Stack direction="row" spacing={1} mb={2}>
                  <Chip
                    label={`${deck.total_flashcards || 0} cards`}
                    variant="outlined"
                    size="small"
                  />
                  {(deck.is_published || deck.is_public) && (
                    <Chip
                      label="Public"
                      color="info"
                      variant="outlined"
                      size="small"
                    />
                  )}
                </Stack>

                <Typography variant="caption" display="block" color="text.secondary">
                  Created: {new Date(deck.created_at).toLocaleDateString()}
                </Typography>
              </CardContent>

              <CardActions>
                <Button
                  size="small"
                  startIcon={<Visibility />}
                  onClick={() => handleViewDeck(deck.id)}
                >
                  View
                </Button>
                <Button
                  size="small"
                  startIcon={<School />}
                  onClick={() => handleStudyDeck(deck.id)}
                  color="primary"
                >
                  Study
                </Button>
                <RoleBasedComponent allowedRoles={['TEACHER', 'ADMIN']}>
                  <Button
                    size="small"
                    startIcon={<Delete />}
                    onClick={() => handleDeleteDeck(deck.id)}
                    color="error"
                  >
                    Delete
                  </Button>
                </RoleBasedComponent>
              </CardActions>
            </Card>
        ))}
      </Box>

      {/* Empty State */}
      {(!decksData?.decks || decksData.decks.length === 0) && (
        <Box textAlign="center" mt={6}>
          <Style sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            No Decks Available
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Create your first flashcard deck to start studying!
          </Typography>
          <RoleBasedComponent allowedRoles={['TEACHER', 'ADMIN']}>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setOpenCreateDialog(true)}
            >
              Create Your First Deck
            </Button>
          </RoleBasedComponent>
        </Box>
      )}

      {/* Create Deck Dialog */}
      <Dialog open={openCreateDialog} onClose={() => setOpenCreateDialog(false)} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmit(handleCreateDeck)}>
          <DialogTitle>Create New Deck</DialogTitle>
          <DialogContent>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}
            
            <TextField
              autoFocus
              margin="dense"
              label="Deck Title"
              fullWidth
              variant="outlined"
              {...register('title', { required: 'Title is required' })}
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
              {...register('description')}
              sx={{ mb: 2 }}
            />
            
            <TextField
              select
              margin="dense"
              label="Difficulty"
              fullWidth
              variant="outlined"
              {...register('difficulty', { required: 'Difficulty is required' })}
              error={!!errors.difficulty}
              helperText={errors.difficulty?.message}
              SelectProps={{
                native: true,
              }}
              sx={{ mb: 2 }}
            >
              <option value="">Select difficulty</option>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </TextField>
            
            <FormControlLabel
              control={
                <Checkbox
                  {...register('is_public')}
                  defaultChecked={false}
                />
              }
              label="Make this deck public"
              sx={{ mt: 1 }}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenCreateDialog(false)}>Cancel</Button>
            <Button type="submit" variant="contained" disabled={createDeckMutation.isPending}>
              {createDeckMutation.isPending ? 'Creating...' : 'Create Deck'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Container>
  );
};

export default DecksPage;
