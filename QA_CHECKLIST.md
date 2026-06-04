# Gharelu — Pre-Release QA Checklist

Run through this before every major update. Grounded in Gharelu's purpose
(a warm, Hinglish, mother's-wisdom kitchen companion with three modes) plus
the features built on top.

## 1. Technical sanity (do these first)
- [ ] `index.html` `<script>` parses with no syntax errors (a single missing comma kills the whole page)
- [ ] `api/chat.py` compiles — no indentation/syntax errors
- [ ] Page loads with no errors in the browser console
- [ ] Model ID in `chat.py` is a current, non-retired model
- [ ] `ANTHROPIC_API_KEY` is set in Vercel env (a real request returns a reply, not "API key not configured")
- [ ] After deploy, hard-refresh and confirm the *new* version is actually live (not a cached old build)

## 2. Voice & persona (the heart of the product)
- [ ] Replies feel **warm, specific, and practical** — like a mother, not a chatbot
- [ ] Gives **one good answer, not five options**
- [ ] **Language matches the user**: English in → English out; Hinglish in → Hinglish out
- [ ] **No calorie counting**, no weight-loss lecturing
- [ ] Health conditions (diabetes, acidity) get **traditional wisdom** (jeera, methi, etc.), warmly — not clinically
- [ ] Replies stay reasonably short (~150 words), not essay-length

## 3. The three modes
- [ ] **Cook** — suggests one real dish from the ingredients given
- [ ] **Store** — gives proper freshness/storage advice
- [ ] **Nourish** — answers pairing / when / how much
- [ ] Switching tabs updates the hint text, placeholder, and the response tag correctly
- [ ] The mode tag on the response card matches the mode that was used

## 4. Sub-features
- [ ] **Cook → South Indian** biases toward South Indian dishes (sambar, dosa, coconut, curry leaves)
- [ ] **Cook → North Indian** biases toward North Indian dishes (dal, paneer, garam masala)
- [ ] **Cook → Any** gives general suggestions
- [ ] **Nourish chips** (Feeling heavy, Acidity, Low energy, Cold/cough, Period, Can't sleep, After workout) each shift the advice appropriately
- [ ] Sub-tabs/chips **only show for their mode** (region under Cook, chips under Nourish) and are hidden elsewhere
- [ ] Sub-tabs are **visible on first load** (not just after switching tabs and back)
- [ ] **Time-of-day**: a late-night query nudges toward lighter food; advice feels time-appropriate

## 5. Input methods
- [ ] **Typing** works; Enter submits, Shift+Enter makes a newline
- [ ] **🎤 Voice** — button shows listening state, fills the text box, appends to existing text, stops on second tap
- [ ] Voice fails *gracefully* on unsupported browsers / blocked mic (friendly alert, no crash)
- [ ] **📷 Photo** — uploads, shows thumbnail preview, ✕ removes it
- [ ] Photo reaches the vision model — it describes what's *actually* in the image
- [ ] Can submit with **photo alone, text alone, or both**
- [ ] Photo clears after a successful reply
- [ ] Photo + voice + chips all work **in every mode/sub-mode**

## 6. Error handling & edge cases
- [ ] Empty submit (no text, no photo) does nothing / focuses input — no error spam
- [ ] API/network failure shows the friendly error message, not a blank screen
- [ ] Submit button re-enables and loading spinner stops after every request (success *and* failure)
- [ ] Very long input doesn't break layout
- [ ] A non-food photo is handled kindly (redirects to ingredients, doesn't crash)

## 7. Cross-device
- [ ] Looks right on **mobile** (most users will be on a phone in front of the fridge)
- [ ] Mode tabs, chips, and the photo/voice buttons wrap cleanly on a narrow screen
- [ ] Works in **Chrome and Safari** (voice especially — it's the most browser-sensitive feature)
