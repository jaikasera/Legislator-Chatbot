import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import axios from 'axios';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const API_BASE_URL = 'http://127.0.0.1:8000';  // Using 127.0.0.1 instead of localhost

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([{
    role: 'assistant',
    content: 'Currently indexing documents and initializing backend. This may take up to a few minutes depending on the number of documents.'
  }]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isBackendReady, setIsBackendReady] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  useEffect(() => {
    const checkBackendHealth = async () => {
      try {
        console.log('Checking backend health...');
        const response = await axios.get(`${API_BASE_URL}/api/health`);
        console.log('Backend health check response:', response.data);
        if (!isBackendReady) {
          setIsBackendReady(true);
          setMessages(prev => {
            // Only add the message if it doesn't already exist
            if (!prev.some(m => m.content === 'All documents have been indexed. Ask me anything about current legislation!')) {
              return [...prev, {
                role: 'assistant',
                content: 'All documents have been indexed. Ask me anything about current legislation!'
              }];
            }
            return prev;
          });
        }
      } catch (error: any) {
        console.error('Backend health check failed:', {
          message: error.message,
          response: error.response?.data,
          status: error.response?.status
        });
        if (isBackendReady) {
          setIsBackendReady(false);
        }
      }
    };

    // Initial check
    checkBackendHealth();

    // Set up polling every 5 seconds
    const intervalId = setInterval(checkBackendHealth, 5000);

    // Cleanup interval on component unmount
    return () => clearInterval(intervalId);
  }, [isBackendReady]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user' as const, content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    if (!isBackendReady) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Currently indexing documents. This may take up to a few minutes.'
      }]);
      setIsLoading(false);
      return;
    }

    try {
      console.log('Sending request to backend...');
      const response = await axios.post(`${API_BASE_URL}/api/chat`, {
        message: input
      });
      console.log('Received response:', response.data);

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.response
      }]);
    } catch (error: any) {
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${error.response?.data?.detail || error.message || 'Unknown error occurred'}`
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box sx={{ 
      height: '100vh', 
      display: 'flex', 
      flexDirection: 'column',
      backgroundColor: '#f0f2f5',
      padding: '20px'
    }}>
      <Paper
        elevation={3}
        sx={{
          flex: 1,
          mb: 2,
          p: 2,
          overflow: 'auto',
          backgroundColor: '#ffffff',
          borderRadius: '12px',
          boxShadow: '0 2px 12px rgba(0,0,0,0.1)',
          maxHeight: 'calc(100vh - 300px)' // Increased space for title
        }}
      >
        <List>
          {messages.map((message, index) => (
            <ListItem
              key={index}
              sx={{
                justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                mb: 2
              }}
            >
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  maxWidth: '70%',
                  backgroundColor: message.role === 'user' ? '#1a73e8' : '#f8f9fa',
                  color: message.role === 'user' ? '#ffffff' : '#000000',
                  borderRadius: '12px',
                  boxShadow: '0 1px 2px rgba(0,0,0,0.1)'
                }}
              >
                <ListItemText
                  primary={message.content}
                  sx={{
                    '& .MuiListItemText-primary': {
                      whiteSpace: 'pre-wrap',
                      fontSize: '1rem',
                      lineHeight: 1.5
                    }
                  }}
                />
              </Paper>
            </ListItem>
          ))}
          <div ref={messagesEndRef} />
        </List>
      </Paper>

      <Box
        component="form"
        onSubmit={handleSubmit}
        sx={{
          display: 'flex',
          gap: 1,
          backgroundColor: '#ffffff',
          padding: '16px',
          borderRadius: '12px',
          boxShadow: '0 2px 12px rgba(0,0,0,0.1)'
        }}
      >
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type your question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: '8px',
              '&:hover fieldset': {
                borderColor: '#1a73e8',
              },
            },
          }}
        />
        <Button
          type="submit"
          variant="contained"
          endIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : <SendIcon />}
          disabled={isLoading || !input.trim()}
          sx={{
            backgroundColor: '#1a73e8',
            borderRadius: '8px',
            '&:hover': {
              backgroundColor: '#1557b0',
            },
            minWidth: '100px'
          }}
        >
          Send
        </Button>
      </Box>
    </Box>
  );
};

export default ChatInterface; 