import React, { useState } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Chip,
  IconButton,
  Paper,
  Divider,
} from '@mui/material';
import { 
  Add, 
  Edit, 
  Delete, 
  School, 
  ArrowBack,
  FlipToFront,
  Quiz
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { useParams, useNavigate } from 'react-router-dom';
import { contentService, Flashcard, CreateFlashcardRequest } from '../../services/content.service';
import { RoleBasedComponent } from '../../components/common/RoleBasedComponent';

const DeckDetailPage: React.FC = () => {
  const { deckId } = useParams<{ deckId: string }>();
  const navigate = useNavigate();
  const [openCreateDialog, setOpenCreateDialog] = useState(false);
  const [editingCard, setEditingCard] = useState<Flashcard | null>(null);
  const [error, setError] = useState<string>('');
  const [flippedCards, setFlippedCards] = useState<Set<string>>(new Set());
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors },
  } = useForm<CreateFlashcardRequest>();

  // Fetch deck details
  const { data: deck, isLoading } = useQuery({
    queryKey: ['deck', deckId],
    queryFn: () => contentService.getDeck(deckId!),
    enabled: !!deckId,
  });

  // Create flashcard mutation
  const createFlashcardMutation = useMutation({
    mutationFn: contentService.createFlashcard,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deck', deckId] });
      setOpenCreateDialog(false);
      setEditingCard(null);
      reset();
      setError('');
    },
    onError: (err: any) => {
      setError(err.message || 'Failed to save flashcard');
    },
  });

  // Delete flashcard mutation
  const deleteFlashcardMutation = useMutation({
    mutationFn: (cardId: string) => contentService.deleteFlashcard(cardId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deck', deckId] });
    },
  });

  const handleCreateFlashcard = (data: CreateFlashcardRequest) => {
    const flashcardData = {
      ...data,
      deck_id: deckId!,
    };
    createFlashcardMutation.mutate(flashcardData);
  };

  const handleEditFlashcard = (card: Flashcard) => {
    setEditingCard(card);
    setValue('front_content', card.front_content);
    setValue('back_content', card.back_content);
    setValue('difficulty', card.difficulty);
    setValue('deck_id', card.deck_id);
    setOpenCreateDialog(true);
  };

  const handleDeleteFlashcard = (cardId: string) => {
    if (window.confirm('Are you sure you want to delete this flashcard?')) {
      deleteFlashcardMutation.mutate(cardId);
    }
  };

  const handleFlipCard = (cardId: string) => {
    const newFlipped = new Set(flippedCards);
    if (newFlipped.has(cardId)) {
      newFlipped.delete(cardId);
    } else {
      newFlipped.add(cardId);
    }
    setFlippedCards(newFlipped);
  };

  const handleStartStudy = () => {
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

  const closeDialog = () => {
    setOpenCreateDialog(false);
    setEditingCard(null);
    reset();
    setError('');
  };

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Loading Deck...
        </Typography>
      </Container>
    );
  }

  if (!deck) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Deck Not Found
        </Typography>
        <Button startIcon={<ArrowBack />} onClick={() => navigate('/decks')}>
          Back to Decks
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={4}>
        <Box>
          <Button 
            startIcon={<ArrowBack />} 
            onClick={() => navigate('/decks')}
            sx={{ mb: 2 }}
          >
            Back to Decks
          </Button>
          <Typography variant="h4" component="h1" gutterBottom>
            📚 {deck.title}
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            {deck.description}
          </Typography>
          <Box display="flex" gap={1} mb={2}>
            <Chip
              label={deck.difficulty || 'No difficulty'}
              color={getDifficultyColor(deck.difficulty)}
              size="small"
            />
            <Chip
              label={`${deck.total_flashcards || 0} cards`}
              variant="outlined"
              size="small"
            />
            {deck.is_public && (
              <Chip
                label="Public"
                color="info"
                variant="outlined"
                size="small"
              />
            )}
          </Box>
        </Box>
        <Box display="flex" gap={2}>
          <Button
            variant="contained"
            startIcon={<School />}
            onClick={handleStartStudy}
            disabled={!deck.flashcards || deck.flashcards.length === 0}
          >
            Study Deck
          </Button>
          <RoleBasedComponent allowedRoles={['TEACHER', 'ADMIN']}>
            <Button
              variant="outlined"
              startIcon={<Add />}
              onClick={() => setOpenCreateDialog(true)}
            >
              Add Card
            </Button>
          </RoleBasedComponent>
        </Box>
      </Box>

      {/* Deck Stats */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: 'repeat(4, 1fr)' },
          gap: 3,
          mb: 4
        }}
      >
        <Paper sx={{ p: 2, textAlign: 'center' }}>
          <Typography variant="h4" color="primary">
            {deck.total_flashcards || 0}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Total Cards
          </Typography>
        </Paper>
        <Paper sx={{ p: 2, textAlign: 'center' }}>
          <Typography variant="h4" color="success.main">
            {/* Cannot calculate by difficulty without flashcards data */}
            0
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Easy Cards
          </Typography>
        </Paper>
        <Paper sx={{ p: 2, textAlign: 'center' }}>
          <Typography variant="h4" color="warning.main">
            {/* Cannot calculate by difficulty without flashcards data */}
            0
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Medium Cards
          </Typography>
        </Paper>
        <Paper sx={{ p: 2, textAlign: 'center' }}>
          <Typography variant="h4" color="error.main">
            {/* Cannot calculate by difficulty without flashcards data */}
            0
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Hard Cards
          </Typography>
        </Paper>
      </Box>

      {/* Flashcards Grid */}
      <Typography variant="h5" component="h2" gutterBottom>
        Flashcards
      </Typography>
      
      {/* Flashcards Grid - Currently API doesn't return flashcards data */}
      {/* TODO: Implement flashcards API endpoint to display actual flashcards */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: 'repeat(3, 1fr)' },
          gap: 3
        }}
      >
        {/* No flashcards data from API - show empty state */}
      </Box>

      {/* Empty State - Always show since API doesn't return flashcards */}
      <Box textAlign="center" mt={6}>
        <Quiz sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          Flashcards Feature Coming Soon
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          The flashcards API is not yet implemented. You can create and manage decks, but individual flashcards will be available in a future update.
        </Typography>
      </Box>

      {/* Create/Edit Flashcard Dialog - Disabled since API not implemented */}
      <Dialog open={openCreateDialog} onClose={closeDialog} maxWidth="md" fullWidth>
        <form onSubmit={handleSubmit(handleCreateFlashcard)}>
          <DialogTitle>
            {editingCard ? 'Edit Flashcard' : 'Create New Flashcard'}
          </DialogTitle>
          <DialogContent>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}
            
            <TextField
              autoFocus
              margin="dense"
              label="Front Content"
              fullWidth
              multiline
              rows={3}
              variant="outlined"
              {...register('front_content', { required: 'Front content is required' })}
              error={!!errors.front_content}
              helperText={errors.front_content?.message}
              sx={{ mb: 2 }}
            />
            
            <TextField
              margin="dense"
              label="Back Content"
              fullWidth
              multiline
              rows={3}
              variant="outlined"
              {...register('back_content', { required: 'Back content is required' })}
              error={!!errors.back_content}
              helperText={errors.back_content?.message}
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
            >
              <option value="">Select difficulty</option>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </TextField>
          </DialogContent>
          <DialogActions>
            <Button onClick={closeDialog}>Cancel</Button>
            <Button type="submit" variant="contained" disabled={createFlashcardMutation.isPending}>
              {createFlashcardMutation.isPending ? 'Saving...' : (editingCard ? 'Update' : 'Create')}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Container>
  );
};

export default DeckDetailPage;
