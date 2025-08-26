import React from 'react';
import { Box, Paper, Typography, Button } from '@mui/material';
import { styled } from '@mui/material/styles';
import { currentTheme } from '../../theme/colors.config';
import { ThemeUtils } from '../../theme/utils';

// Glass Background Wrapper
export const GlassBackground: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <Box
    sx={{
      minHeight: '100vh',
      background: currentTheme.background.primary,
      py: 4
    }}
  >
    {children}
  </Box>
);

// Glass Header Component
export const GlassHeader: React.FC<{ 
  icon: string;
  title: string; 
  subtitle: string;
  children?: React.ReactNode;
}> = ({ icon, title, subtitle, children }) => (
  <Paper 
    elevation={8}
    sx={{ 
      mb: 4,
      background: 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%)',
      backdropFilter: 'blur(10px)',
      borderRadius: 3,
      border: '1px solid rgba(255,255,255,0.3)',
      p: 3
    }}
  >
    <Box display="flex" justifyContent="space-between" alignItems="center">
      <Box>
        <Typography 
          variant="h3" 
          component="h1" 
          sx={{ 
            fontSize: '2.5rem', 
            mb: 1,
            background: 'linear-gradient(45deg, #1e3c72, #2a5298, #19547b, #1e3c72)',
            backgroundSize: '300% 300%',
            animation: 'gradient 3s ease infinite',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            '@keyframes gradient': {
              '0%': { backgroundPosition: '0% 50%' },
              '50%': { backgroundPosition: '100% 50%' },
              '100%': { backgroundPosition: '0% 50%' }
            }
          }}
        >
          {icon} {title}
        </Typography>
        <Typography variant="body1" sx={{ color: '#5A5A5A', fontWeight: 500 }}>
          {subtitle}
        </Typography>
      </Box>
      {children}
    </Box>
  </Paper>
);

// Glass Card/Paper Component
export const GlassPaper: React.FC<{ 
  children: React.ReactNode;
  elevation?: number;
}> = ({ children, elevation = 8 }) => (
  <Paper 
    elevation={elevation}
    sx={ThemeUtils.getGlass.styles()}
  >
    {children}
  </Paper>
);

// Glass Stats Card
export const GlassStatsCard: React.FC<{
  icon: React.ReactNode;
  iconColor: string;
  value: string | number;
  label: string;
}> = ({ icon, iconColor, value, label }) => (
  <Paper 
    elevation={6}
    sx={{
      ...ThemeUtils.getGlass.styles(),
      p: 2,
      boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
    }}
  >
    <Box display="flex" alignItems="center">
      <Box 
        sx={ThemeUtils.getIcon.withShadow(iconColor)}
      >
        {icon}
      </Box>
      <Box>
        <Typography variant="h6" sx={{ 
          ...ThemeUtils.getText.withShadow(),
          fontSize: '1.5rem'
        }}>
          {value}
        </Typography>
        <Typography variant="body2" sx={{ 
          ...ThemeUtils.getText.styles().secondary,
        }}>
          {label}
        </Typography>
      </Box>
    </Box>
  </Paper>
);

// Glass Button
export const GlassButton = styled(Button)(({ theme }) => ({
  ...ThemeUtils.getButton.primary(),
}));

// Glass List Item Styles
export const getGlassListItemStyles = (index: number) => ThemeUtils.getListItem(index);

// Glass Avatar Styles
export const getGlassAvatarStyles = (gradientColors: string[]) => ThemeUtils.getAvatar(gradientColors);

// Glass Typography for light backgrounds
export const getGlassTextStyles = (index: number) => ThemeUtils.getText.withShadow();
