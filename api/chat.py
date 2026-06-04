from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read the user's message from the request
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body) if body else {}

            user_message = data.get('message', '')
            mode = data.get('mode', 'cook')

            if not user_message:
                self.send_error_response(400, 'No message provided')
                return

            region = data.get('region', 'general')

            # Region-specific cooking guidance
            cook_note = 'The user wants to know what to cook.'
            if region == 'south':
                cook_note = 'The user wants to cook South Indian food. Focus on Tamil, Telugu, Kannada, and Malayali dishes — sambar, rasam, dosas, idlis, rice dishes, kootu, avial, coconut-based curries, fish curries. Pantry staples to draw from: curry leaves, mustard seeds, tamarind, coconut, urad dal, asafoetida, dried red chillies.'
            elif region == 'north':
                cook_note = 'The user wants to cook North Indian food. Focus on Punjabi, UP, and Delhi-style dishes — rotis, parathas, sabzis, dal, chole, rajma, paneer dishes, tomato-onion gravies. Pantry staples to draw from: ghee, cumin, coriander, garam masala, amchur, kasuri methi.'

            # Mode-specific instructions
            mode_instructions = {
                'cook': cook_note,
                'store': 'The user wants to know how to store ingredients properly.',
                'nourish': 'The user wants to know how to eat what they made — what to pair, when, how much.'
            }

            mode_note = mode_instructions.get(mode, mode_instructions['cook'])

            # The system prompt — Gharelu's voice
            system_prompt = f"""You are Gharelu — a warm, knowing kitchen companion built on the real wisdom of two Indian mothers. You adapt to the user's language — if they write in English, reply in plain English; if they write in Hinglish, reply in Hinglish. Match their tone. You are warm but not gushing. You are specific and practical. You give one good answer, not five options. You never lecture about nutrition or calories. You treat the person as capable and intelligent. You assume they are tired and on their side.

{mode_note}

Your response should feel like advice from a mother who has cooked for decades — grounded, caring, and specific. If the user wrote in Hinglish, use Hindi phrases naturally (like "beta," "thoda," "bas," "achcha") mixed with English. If they wrote in English, stay warm but reply in English. Keep it conversational, not formal. Maximum 150 words. One clear, warm, actionable reply.

Important: Never count calories. Never mention weight loss unless specifically asked about a health condition like diabetes. If someone mentions a health condition like diabetes or acidity, offer real traditional wisdom (jeera, methi, cinnamon etc.) but in a warm, non-clinical way."""

            # Get the API key from Vercel environment variables
            api_key = os.environ.get('ANTHROPIC_API_KEY')

            if not api_key:
                self.send_error_response(500, 'API key not configured')
                return

            # Call the Anthropic API
            anthropic_request = {
                'model': 'claude-sonnet-4-6',
                'max_tokens': 1000,
                'system': system_prompt,
                'messages': [
                    {'role': 'user', 'content': user_message}
                ]
            }

            req = urllib.request.Request(
                'https://api.anthropic.com/v1/messages',
                data=json.dumps(anthropic_request).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'x-api-key': api_key,
                    'anthropic-version': '2023-06-01'
                },
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                anthropic_response = json.loads(response.read().decode('utf-8'))

            reply_text = anthropic_response['content'][0]['text']

            # Send the reply back to the browser
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'reply': reply_text}).encode('utf-8'))

        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            self.send_error_response(e.code, f'Anthropic API error: {error_body}')

        except Exception as e:
            self.send_error_response(500, f'Server error: {str(e)}')

    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode('utf-8'))
