import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Container, Box, Typography } from '@mui/material';
import ChatInterface from './components/ChatInterface';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="md">
        <Box sx={{ my: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom align="center">
            Legislator Chatbot (Updated 2024)
          </Typography>
          <Typography variant="subtitle1" align="center" color="text.secondary" paragraph>
            Ask questions regarding current Senate legislature and receive up-to-date answers based on real documents
          </Typography>
          <ChatInterface />
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;
