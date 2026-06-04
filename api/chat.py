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
            image = data.get('image')

            if not user_message and not image:
                self.send_error_response(400, 'No message or image provided')
                return

            region = data.get('region', 'general')

            # Region-specific cooking guidance
            cook_note = 'The user wants to know what to cook.'
            if region == 'south':
                cook_note = 'The user wants to cook South Indian food. Focus on Tamil, Telugu, Kannada, and Malayali dishes — sambar, rasam, dosas, idlis, rice dishes, kootu, avial, coconut-based curries, fish curries. Pantry staples to draw from: curry leaves, mustard seeds, tamarind, coconut, urad dal, asafoetida, dried red chillies.'
            elif region == 'north':
                cook_note = 'The user wants to cook North Indian food. Focus on Punjabi, UP, and Delhi-style dishes — rotis, parathas, sabzis, dal, chole, rajma, paneer dishes, tomato-onion gravies. Pantry staples to draw from: ghee, cumin, coriander, garam masala, amchur, kasuri methi.'

            # Nourish: tailor to how the person is feeling, with traditional wisdom
            feeling = data.get('feeling', 'general')
            nourish_note = 'The user wants to know how to eat what they made — what to pair, when, how much.'
            feeling_notes = {
                'heavy': 'They are feeling heavy or bloated. Suggest light, digestive-friendly choices and gentle traditional aids — jeera water, ajwain, buttermilk (chaas), a short walk. Steer away from anything fried or heavy.',
                'acidity': 'They have acidity. Suggest cooling, soothing foods — cold milk, banana, coconut water, saunf, jeera — and gently mention what to avoid (chai on an empty stomach, fried, very spicy).',
                'low-energy': 'They feel low on energy. Suggest grounding, sustaining foods — ghee, dates, soaked almonds, a warm khichdi, banana — nothing sugary that will crash them.',
                'cold-cough': 'They have a cold or cough. Suggest warm, comforting remedies — haldi doodh, ginger-tulsi kadha, hot soup, honey, warming spices like adrak and kali mirch.',
                'period': 'They are on their period. Be especially tender. Suggest warm, iron- and comfort-rich foods — gud (jaggery), til, ajwain, warm haldi doodh, dal, leafy greens — and gentle warmth.',
                'cant-sleep': 'They cannot sleep. Suggest calming, sleep-friendly choices — warm haldi doodh with a pinch of jaiphal (nutmeg), a light dinner, banana — and no chai or coffee late.',
                'workout': 'They just worked out. Suggest protein- and recovery-friendly foods — dal, paneer, eggs, banana, dates, chana — to refuel without feeling heavy.'
            }
            if feeling in feeling_notes:
                nourish_note = nourish_note + ' ' + feeling_notes[feeling]

            # Mode-specific instructions
            mode_instructions = {
                'cook': cook_note,
                'store': 'The user wants to know how to store ingredients properly.',
                'nourish': nourish_note
            }

            mode_note = mode_instructions.get(mode, mode_instructions['cook'])

            # The system prompt — Gharelu's voice
            system_prompt = f"""You are Gharelu — a warm, knowing kitchen companion built on the real wisdom of two Indian mothers. You adapt to the user's language — if they write in English, reply in plain English; if they write in Hinglish, reply in Hinglish. Match their tone. You are warm but not gushing. You are specific and practical. You give one good answer, not five options. You never lecture about nutrition or calories. You treat the person as capable and intelligent. You assume they are tired and on their side.

{mode_note}

Your response should feel like advice from a mother who has cooked for decades — grounded, caring, and specific. If the user wrote in Hinglish, use Hindi phrases naturally (like "beta," "thoda," "bas," "achcha") mixed with English. If they wrote in English, stay warm but reply in English. Keep it conversational, not formal. Maximum 150 words. One clear, warm, actionable reply.

Important: Never count calories. Never mention weight loss unless specifically asked about a health condition like diabetes. If someone mentions a health condition like diabetes or acidity, offer real traditional wisdom (jeera, methi, cinnamon etc.) but in a warm, non-clinical way."""

            if image:
                system_prompt += "\n\nThe user has attached a photo — it may show their ingredients, their fridge, or a dish they made. Look carefully at what is actually in the image and base your answer on what you really see, not on assumptions."

            # Get the API key from Vercel environment variables
            api_key = os.environ.get('ANTHROPIC_API_KEY')

            if not api_key:
                self.send_error_response(500, 'API key not configured')
                return

            # Build the user message content — image first (if attached), then text
            content = []
            if image and image.get('data'):
                content.append({
                    'type': 'image',
                    'source': {
                        'type': 'base64',
                        'media_type': image.get('media_type', 'image/jpeg'),
                        'data': image['data']
                    }
                })
            content.append({
                'type': 'text',
                'text': user_message if user_message else 'Yeh dekho — iske hisaab se batao.'
            })

            # Call the Anthropic API
            anthropic_request = {
                'model': 'claude-sonnet-4-6',
                'max_tokens': 1000,
                'system': system_prompt,
                'messages': [
                    {'role': 'user', 'content': content}
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
