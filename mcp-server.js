// MCP server that wraps OpenAI Codex CLI
const express = require('express');
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');
const { spawn, exec } = require('child_process');

const app = express();
app.use(bodyParser.json());

// Check if Codex CLI is working
let isCodexAvailable = false;

function checkCodexAvailability() {
  exec('codex --version', (error, stdout, stderr) => {
    if (error) {
      console.error('Codex CLI is not available:', error.message);
      console.error('Using simulated responses instead');
      isCodexAvailable = false;
    } else {
      console.log('Codex CLI is available:', stdout.trim());
      isCodexAvailable = true;
    }
  });
}

// Check initially and then every 5 minutes
checkCodexAvailability();
setInterval(checkCodexAvailability, 5 * 60 * 1000);

// Basic health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// MCP: POST /v1/chat/completions
app.post('/v1/chat/completions', async (req, res) => {
  console.log('Received request:', JSON.stringify(req.body, null, 2));
  
  const { messages, ...rest } = req.body;
  if (!messages || !Array.isArray(messages)) {
    return res.status(400).json({ error: 'Missing messages array' });
  }

  // Prepare prompt for Codex CLI
  const prompt = messages.map(m => `${m.role}: ${m.content}`).join('\n');
  console.log('Processing prompt:', prompt);

  // If Codex is available, use it, otherwise simulate responses
  if (isCodexAvailable) {
    try {
      // Call Codex CLI
      const codex = spawn('codex', ['chat', '--json'], { stdio: ['pipe', 'pipe', 'pipe'] });
      let output = '';
      let errorOutput = '';
      
      codex.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      codex.stderr.on('data', (data) => {
        errorOutput += data.toString();
        console.error('Codex CLI error:', data.toString());
      });
      
      codex.stdin.write(prompt + '\n');
      codex.stdin.end();

      codex.on('close', (code) => {
        console.log('Codex CLI exited with code:', code);
        console.log('Codex CLI output:', output);
        
        if (code !== 0) {
          console.error('Codex CLI failed, switching to simulated response');
          sendSimulatedResponse(prompt, res);
          return;
        }
        
        try {
          let response;
          try {
            response = JSON.parse(output);
          } catch (parseError) {
            // If not valid JSON, use raw output as text
            response = { text: output.trim() };
          }
          
          // MCP response format
          res.json({
            id: uuidv4(),
            object: 'chat.completion',
            created: Math.floor(Date.now() / 1000),
            model: 'codex-cli',
            choices: [
              {
                index: 0,
                message: {
                  role: 'assistant',
                  content: response.choices?.[0]?.message?.content || 
                           response.choices?.[0]?.text || 
                           response.text || 
                           output.trim()
                },
                finish_reason: 'stop'
              }
            ],
            usage: response.usage || {}
          });
        } catch (e) {
          console.error('Error processing Codex response:', e);
          sendSimulatedResponse(prompt, res);
        }
      });
    } catch (e) {
      console.error('Error spawning Codex CLI:', e);
      sendSimulatedResponse(prompt, res);
    }
  } else {
    // Codex not available, send simulated response
    sendSimulatedResponse(prompt, res);
  }

  function sendSimulatedResponse(prompt, res) {
    console.log('Sending simulated response for prompt:', prompt);
    
    // Create a simulated response
    const simulatedContent = `This is a simulated response from the MCP server. Codex CLI is not available (requires Node.js v22+).
    
Your prompt was:
${prompt}

In a real implementation, this would be handled by the Codex CLI.`;
    
    // Return in MCP format
    res.json({
      id: uuidv4(),
      object: 'chat.completion',
      created: Math.floor(Date.now() / 1000),
      model: 'codex-cli-simulation',
      choices: [
        {
          index: 0,
          message: {
            role: 'assistant',
            content: simulatedContent
          },
          finish_reason: 'stop'
        }
      ],
      usage: {
        prompt_tokens: prompt.length,
        completion_tokens: simulatedContent.length,
        total_tokens: prompt.length + simulatedContent.length
      }
    });
  }
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`Codex MCP wrapper listening on port ${PORT}`);
  console.log('Server started at:', new Date().toISOString());
  console.log('Visit http://localhost:' + PORT + '/health to check server status');
});