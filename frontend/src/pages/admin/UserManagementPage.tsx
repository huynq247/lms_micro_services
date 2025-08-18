import React, { useState } from 'react';
import {
  Container,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Alert,
} from '@mui/material';
import { Add, Edit, Delete, Person } from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { RoleBasedComponent } from '../../components/common/RoleBasedComponent';

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

interface CreateUserRequest {
  username: string;
  email: string;
  password: string;
  full_name: string;
  role: 'STUDENT' | 'TEACHER' | 'ADMIN';
}

// Updated service with proper API Gateway URLs and authentication
const userService = {
  getUsers: async (): Promise<{ users: User[] }> => {
    const token = localStorage.getItem('authToken');
    console.log('🔑 Token for users request:', token ? 'Present' : 'Missing');
    console.log('🌐 API URL:', `${process.env.REACT_APP_API_GATEWAY_URL}/api/v1/users`);
    
    const response = await fetch(`${process.env.REACT_APP_API_GATEWAY_URL}/api/v1/users`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('📡 Users API Response status:', response.status);
    console.log('📡 Users API Response headers:', response.headers);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Users API Error:', errorText);
      throw new Error(`Failed to fetch users: ${response.statusText} - ${errorText}`);
    }
    
    const data = await response.json();
    console.log('✅ Users API Data:', data);
    return data;
  },
  
  createUser: async (userData: CreateUserRequest) => {
    const token = localStorage.getItem('authToken');
    const response = await fetch(`${process.env.REACT_APP_API_GATEWAY_URL}/api/v1/users`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(userData)
    });
    
    if (!response.ok) {
      throw new Error(`Failed to create user: ${response.statusText}`);
    }
    
    return response.json();
  },
  
  deleteUser: async (userId: number) => {
    const token = localStorage.getItem('authToken');
    const response = await fetch(`${process.env.REACT_APP_API_GATEWAY_URL}/api/v1/users/${userId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`Failed to delete user: ${response.statusText}`);
    }
    
    return response.json();
  }
};

const UserManagementPage: React.FC = () => {
  const [openCreateDialog, setOpenCreateDialog] = useState(false);
  const [error, setError] = useState<string>('');
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CreateUserRequest>();

  // Fetch users
  const { data: usersData, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: userService.getUsers,
  });

  // Create user mutation
  const createUserMutation = useMutation({
    mutationFn: userService.createUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setOpenCreateDialog(false);
      reset();
      setError('');
    },
    onError: (err: any) => {
      setError(err.message || 'Failed to create user');
    },
  });

  // Delete user mutation
  const deleteUserMutation = useMutation({
    mutationFn: userService.deleteUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });

  const handleCreateUser = (data: CreateUserRequest) => {
    createUserMutation.mutate(data);
  };

  const handleDeleteUser = (userId: number) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      deleteUserMutation.mutate(userId);
    }
  };

  const getRoleColor = (role: string) => {
    switch (role.toUpperCase()) {
      case 'ADMIN':
        return 'error';
      case 'TEACHER':
        return 'warning';
      case 'STUDENT':
        return 'primary';
      default:
        return 'default';
    }
  };

  if (isLoading) {
    return (
      <Container maxWidth="lg">
        <Typography>Loading users...</Typography>
      </Container>
    );
  }

  return (
    <RoleBasedComponent 
      allowedRoles={['ADMIN']} 
      fallback={
        <Container maxWidth="lg">
          <Alert severity="error">Access denied. Admin privileges required.</Alert>
        </Container>
      }
    >
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            User Management
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setOpenCreateDialog(true)}
          >
            Create User
          </Button>
        </Box>

        {/* Users Table */}
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Username</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Full Name</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {usersData?.users?.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>{user.id}</TableCell>
                  <TableCell>{user.username}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>{user.full_name}</TableCell>
                  <TableCell>
                    <Chip 
                      label={user.role} 
                      color={getRoleColor(user.role)} 
                      size="small" 
                    />
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={user.is_active ? 'Active' : 'Inactive'} 
                      color={user.is_active ? 'success' : 'default'}
                      size="small" 
                    />
                  </TableCell>
                  <TableCell>
                    <Button
                      size="small"
                      startIcon={<Edit />}
                      sx={{ mr: 1 }}
                    >
                      Edit
                    </Button>
                    <Button
                      size="small"
                      color="error"
                      startIcon={<Delete />}
                      onClick={() => handleDeleteUser(user.id)}
                    >
                      Delete
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Create User Dialog */}
        <Dialog open={openCreateDialog} onClose={() => setOpenCreateDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Create New User</DialogTitle>
          <DialogContent>
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            
            <TextField
              {...register('username', { required: 'Username is required' })}
              label="Username"
              fullWidth
              margin="normal"
              error={!!errors.username}
              helperText={errors.username?.message}
            />
            
            <TextField
              {...register('email', { required: 'Email is required' })}
              label="Email"
              type="email"
              fullWidth
              margin="normal"
              error={!!errors.email}
              helperText={errors.email?.message}
            />
            
            <TextField
              {...register('password', { required: 'Password is required', minLength: 8 })}
              label="Password"
              type="password"
              fullWidth
              margin="normal"
              error={!!errors.password}
              helperText={errors.password?.message}
            />
            
            <TextField
              {...register('full_name', { required: 'Full name is required' })}
              label="Full Name"
              fullWidth
              margin="normal"
              error={!!errors.full_name}
              helperText={errors.full_name?.message}
            />
            
            <TextField
              {...register('role', { required: 'Role is required' })}
              label="Role"
              select
              fullWidth
              margin="normal"
              error={!!errors.role}
              helperText={errors.role?.message}
            >
              <MenuItem value="STUDENT">Student</MenuItem>
              <MenuItem value="TEACHER">Teacher</MenuItem>
              <MenuItem value="ADMIN">Admin</MenuItem>
            </TextField>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenCreateDialog(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleSubmit(handleCreateUser)}
              variant="contained"
              disabled={createUserMutation.isPending}
            >
              {createUserMutation.isPending ? 'Creating...' : 'Create User'}
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </RoleBasedComponent>
  );
};

export default UserManagementPage;
