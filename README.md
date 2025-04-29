# 🎄 Multi-Round Secret Santa Draw 🎁

A Python tool to organize multi-round Secret Santa draws with customizable constraints, exclusions, and email notifications.

---

## Features

- Supports multiple rounds with individual budgets.
- Handles exclusions and prevents participants from drawing themselves or excluded persons.
- Optionally avoids bidirectional draws (where two participants draw each other in different rounds).
- Generates personalized HTML email notifications with a unique draw ID.
- Supports English and German email templates.
- Debug mode to save emails and summary locally.
- Sends emails via SMTP (Gmail example included).

---

## Requirements

- Python 3.7+
- Packages:
  - `PyYAML` (`pip install pyyaml`)
  
---

## Setup

1. **Configuration**

   Edit `data/config.yaml` to define rounds, participants, budgets, exclusions, and language.

2. **Mail Contacts**

   Prepare `data/contact_information.json` with participant names and their email addresses.

3. **Email Credentials**

   Set environment variables for your email credentials or simply use the args `gmail_sender` and `gmail_password` when running `draw.py`. Plaes note that you might have to create an [app password](https://support.google.com/mail/answer/185833?hl=en) for your gmail account.



---

## Usage

Run the draw with:

`python secret_santa.py --gmail_sender you@gmail.com --gmail_password your_app_password`

### Options

- `--gmail_sender`  
   GMail account, default is environment variable `SENDER_MAIL`

- `--gmail_password`  
  GMail account password, default is environment variable `SENDER_PW`

- `--debug`  
Save generated emails and summary to the `debug/` folder instead of sending emails.

- `--debug_email_user USERNAME`  
  When in debug mode, send the email only to the specified user.

---

## Example Test Run / Debug

`python secret_santa.py --debug --debug_email_user Alice`


This will generate emails which are saved in `debug/`, and send a test mail only to Alice (if user exists in contact list). It will also generate a summary:
```
Summary Draw [677a590c]:
Participant         Round 1 (50$)       Round 2 (30$)       
------------------------------------------------------------
Alice               Casper              David               
Bob                 Alice               Casper              
Casper              David               Bob                 
David               Bob                 Alice               
Emil                -                   Florence            
Florence            -                   Emil      
```

---

## Notes

- Ensure your SMTP credentials and permissions are set correctly.
- The draw ID helps track and verify each draw session.
- Avoid bidirectional draws by default; disable with code flag if desired.
- Want to change the style/language of your email? Just edit the files in `templates` and specify your chosen template in the `config.yaml`

---

## License

MIT License
