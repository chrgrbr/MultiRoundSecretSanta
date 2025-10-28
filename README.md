# 🎄 Multi-Round Secret Santa Draw 🎁

A Python tool to organize multi-round Secret Santa draws with customizable constraints, exclusions, and email notifications while preventing to drawing the same recipent twice in muliple gifting rounds.

---

## Features

- Supports multiple rounds with individual budgets.
- Handles exclusions and prevents participants from drawing themselves or excluded persons.
- Optionally avoids bidirectional draws (where two participants draw each other in different rounds).
- Generates personalized HTML email notifications with a unique draw ID.
- Supports English and German email templates.
- Debug mode to save emails and summary locally.
- Sends emails via SMTP (Gmail example included).

<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .container {
            max-width: 500px;
            margin: 20px auto;
            border: 2px solid #2e8b57;
            border-radius: 10px;
            padding: 20px;
            background: #f0fff0;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h2 { color: #000000; }
        ul { list-style-type: none; padding: 0; }
        li {
            background: #fff8dc;
            margin: 10px 0;
            padding: 10px;
            border-left: 5px solid #2e8b57;
            border-radius: 4px;
        }
        .draw-id {
            color: #888;
            font-style: italic;
            font-size: 0.9em;
            margin-top: 20px;
            display: block;
            text-align: right;
        }
        .footer {
            text-align: center;
            font-size: 0.95em;
            margin-top: 20px;
            color: #555;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Hello Alice!</h2>
        <p>Here are your Secret Santa assignments for 2025:</p>
        <ul>
            <li>🎁 Round 1: <strong>Bob</strong> (Budget: 50$)</li><li>🎁 Round 2: <strong>Emil</strong> (Budget: 30$)</li><li>🎁 Round 3: <strong>Florence</strong> (Budget: 10$)</li>
        </ul>
        <p>Festively compiled by your friendly neighborhood bot,</p>
        <p class="footer">✨ Your Secret Santa Bot ✨</p>
        <span class="draw-id">Draw ID: 306789b9</span>
    </div>
</body>
</html>


---

## Requirements

- Python 3.7+
- Packages:
  - `PyYAML` (`pip install pyyaml`)
  
---

## Setup

1. **Configuration**

   Edit `example_config/config.yaml` to define rounds, participants, budgets, exclusions, language and the option to exclude reciprocal pairs.

2. **Mail Contacts**

   Prepare `example_config/contact_information.json` with participant names and their email addresses.

3. **Email Credentials**

   Set environment variables for your email credentials or simply use the args `gmail_sender` and `gmail_password` when running `draw.py`. Plaes note that you might have to create an [app password](https://support.google.com/mail/answer/185833?hl=en) for your gmail account.



---

## Usage

Run the draw with:

`python draw.py --gmail_sender you@gmail.com --gmail_password your_app_password`

### Options

- `--config` `-cf`
  Path to folder with config files. Default is `example_config` 

- `--gmail_sender`  
   GMail account, default is environment variable `SECRET_SANTA_SENDER_MAIL`

- `--gmail_password`  
  GMail account password, default is environment variable `SECRET_SANTA_SENDER_PW`

- `--debug`  
Save generated emails and summary to the `debug/` folder instead of sending emails.

- `--debug_email_user USERNAME`  
  When in debug mode, send the email only to the specified user.

---

## Example Test Run / Debug

`python draw.py --debug --debug_email_user Alice`

This will generate emails which are saved in `debug/`, and send a test mail only to Alice (if user exists in contact list). It will also generate a summary:

```
Summary Draw [306789b9]:
Rounds: 3 | Participants: 8 | Prevent reciprocal pairs: True | Attempts needed: 3
Participant         Round 1 (50$)       Round 2 (30$)       Round 3 (10$)       
--------------------------------------------------------------------------------
Alice               Bob                 Emil                Florence            
Bob                 Casper              Florence            -                   
Casper              David               Alice               George              
David               Alice               Bob                 Hannah              
Emil                -                   David               -                   
Florence            -                   Casper              David               
George              -                   -                   Alice               
Hannah              -                   -                   Casper      
```

---

## Notes

- Ensure your SMTP credentials and permissions are set correctly.
- The draw ID helps track and verify each draw session.
- Avoid bidirectional draws by default; disable with code flag if desired.
- Want to change the style/language of your email? Just edit the files in `templates` and specify your chosen template in the `config.yaml`
- Next Feature: Backtracking with deterministic solution

---

## License

MIT License
