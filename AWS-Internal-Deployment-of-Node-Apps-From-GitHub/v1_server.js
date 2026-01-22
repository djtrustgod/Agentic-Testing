const express = require('express');
const app = express();

// Health check endpoint for ALB
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy', timestamp: new Date().toISOString() });
});

app.get('/', (req, res) => {
  res.json({ message: 'Hello from ECS Fargate!' });
});

const PORT = process.env. PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});