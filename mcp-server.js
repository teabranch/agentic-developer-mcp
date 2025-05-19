// MCP server that wraps OpenAI Codex CLI
const express = require('express');
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');
const { spawn } = require('child_process');

const app = express();
app.use(bodyParser.json());

// MCP: POST /v1/chat/completions
app.post('/v1/chat/completions', async (req, res) => {
  const { messages, ...rest } = req.body;
  if (!messages || !Array.isArray(messages)) {
    return res.status(400).json({ error: 'Missing messages array' });
  }

  // Prepare prompt for Codex CLI
  const prompt = messages.map(m => `${m.role}: ${m.content}`).join('\n');

  // Call Codex CLI
  const codex = spawn('npx', ['codex', 'chat', '--json'], { stdio: ['pipe', 'pipe', 'inherit'] });
  let output = '';
  codex.stdout.on('data', (data) => {
    output += data.toString();
  });
  codex.stdin.write(prompt + '\n');
  codex.stdin.end();

  codex.on('close', (code) => {
    try {
      const codexResp = JSON.parse(output);
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
              content: codexResp.choices?.[0]?.message || codexResp.choices?.[0]?.text || codexResp.text || output
            },
            finish_reason: 'stop'
          }
        ],
        usage: codexResp.usage || {}
      });
    } catch (e) {
      res.status(500).json({ error: 'Failed to parse Codex response', details: e.message, raw: output });
    }
  });
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`Codex MCP wrapper listening on port ${PORT}`);
});
