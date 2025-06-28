#!/bin/bash

nvm install 22.15.1
nvm use 22.15.1

npm install -g @openai/codex
codex --model gpt-4o