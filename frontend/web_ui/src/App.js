import React, { useState } from 'react';
import { 
  Container, 
  Box, 
  TextField, 
  Button, 
  Paper, 
  Typography,
  CircularProgress,
  Card,
  CardContent
} from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import SendIcon from '@mui/icons-material/Send';
import axios from 'axios';

const BRIDGE_API = process.env.REACT_APP_BRIDGE_API || 'http://localhost:8000';

function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${BRIDGE_API}/command`, {
        user_id: 'web-user-001',
        text: input,
        context: []
      });

      const assistantMessage = {
        role: 'assistant',
        text: response.data.response_text,
        actions: response.data.actions
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        role: 'error',
        text: `Erreur: ${error.message}`
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleVoiceInput = () => {
    // TODO: Implémenter enregistrement audio et envoi au bridge
    setIsRecording(!isRecording);
    alert('Enregistrement vocal en cours d\'implémentation');
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          🤖 JARVIS
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Assistant Personnel IA - Local & Sécurisé
        </Typography>
      </Box>

      <Paper elevation={3} sx={{ p: 2, mb: 2, maxHeight: '500px', overflowY: 'auto' }}>
        {messages.length === 0 ? (
          <Typography color="text.secondary" align="center">
            Envoyez un message pour commencer...
          </Typography>
        ) : (
          messages.map((msg, idx) => (
            <Card 
              key={idx} 
              sx={{ 
                mb: 2, 
                bgcolor: msg.role === 'user' ? '#e3f2fd' : msg.role === 'error' ? '#ffebee' : '#f5f5f5'
              }}
            >
              <CardContent>
                <Typography variant="caption" color="text.secondary">
                  {msg.role === 'user' ? 'Vous' : msg.role === 'error' ? 'Erreur' : 'JARVIS'}
                </Typography>
                <Typography variant="body1">
                  {msg.text}
                </Typography>
                {msg.actions && msg.actions.length > 0 && (
                  <Typography variant="caption" sx={{ mt: 1, display: 'block' }}>
                    Actions: {msg.actions.length}
                  </Typography>
                )}
              </CardContent>
            </Card>
          ))
        )}
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
            <CircularProgress />
          </Box>
        )}
      </Paper>

      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Demandez quelque chose à JARVIS..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          disabled={loading}
        />
        <Button
          variant="contained"
          color="primary"
          onClick={handleVoiceInput}
          disabled={loading}
          sx={{ minWidth: '56px' }}
        >
          <MicIcon color={isRecording ? 'error' : 'inherit'} />
        </Button>
        <Button
          variant="contained"
          color="primary"
          onClick={handleSendMessage}
          disabled={loading || !input.trim()}
          sx={{ minWidth: '56px' }}
        >
          <SendIcon />
        </Button>
      </Box>

      <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block', textAlign: 'center' }}>
        JARVIS v0.1.0 - Local First AI Assistant
      </Typography>
    </Container>
  );
}

export default App;