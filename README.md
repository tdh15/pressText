# nytext_v00

**Before running:**
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Note: you can skip the first two lines if the venv is already running.

**For Twilio and Redis connection (in development):**

Ngrok lets us expose localhost publicly so that Twilio can use port 5000 as a Webhook URL.
1) In Twilio, go to the Phone Number settings and add `thomastwilio.ngrok.app` as the Webhook URL for incoming messages.
2) Run:
```
ngrok http --domain=thomastwilio.ngrok.app 5000
```
3) In a separate terminal window:
```
python3 app.py
```
4) In a separate terminal window, run Redis like so:
```
brew services start redis
```
This runs Redis on your computer. For production, you'll host this somewhere 
not on your computer.
When you're done for the day, turn off Redis by running
```
brew services stop redis
```

**Initial Twilio Setup (only check these if the above is broken for some reason):**
1) Created API Key and stored the secret in Config. See: https://www.twilio.com/console/runtime/api-keys/
2) twilio-cli configuration saved to "/Users/thomashughes/.twilio-cli/config.json"
3) Saved dev (shorthand identifier for this profile).

**If you're getting SSL: CERTIFICATE_VERIFY_FAIL ERROR:**
This is related to trying to connect to the database. You need to run:
```
cd '/Applications/Python 3.11'
```
or whatever version of Python you're using, then run
```
./Install\ Certificates.command
```

**For running individual scripts:**
```
python3 -m [script name without the .py]
```
Run this from the main repository. If you need to specify in a sub-folder, use
dot notation. e.g. `python3 -m ap.add_articles_to_db`
