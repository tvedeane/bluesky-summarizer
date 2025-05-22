1. User inputs a word (e.g. company name)
2. Collect data from Bluesky using their API, specifically using (ATProto?) search 
3. Run once a day collecting data for the last 24h.
4. Summarize using `genai` library (https://ai.google.dev/gemini-api/docs/quickstart?hl=pl&lang=python)
5. Store the data and send email

# How to start on windows:

`$env:GENAIKEY="...";  $env:BSKYPASS="..."; $env:BSKYLOGIN="..." ;py -m flask --app app run`