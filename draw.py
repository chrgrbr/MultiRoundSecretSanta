import yaml
import random
from itertools import permutations
from collections import defaultdict
import os
from email.mime.text import MIMEText
import smtplib
import hashlib
import time
import json
import argparse



def load_config(yaml_path):
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    return data

def load_mail_contacts(filename): 
    with open(filename, 'r') as file:
        return json.load(file)
    
def load_mail_template(template_path):
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

def send_email_smtp(sender_email, app_password, recipient_email, config, html_body):
    msg = MIMEText(html_body, 'html')
    msg['Subject'] = config['email']['subject']
    msg['From'] = config['email']['sender']
    msg['To'] = recipient_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, app_password)
        server.send_message(msg)
        print(f"Email sent to {recipient_email}")

def validate_round(round_config, history, pair_history, avoid_bidirectional=False):
    participants = round_config['participants']
    exclusions = defaultdict(set)
    
    if round_config.get('exclusions'):
        for giver, excluded in round_config.get('exclusions', {}).items():
            for receiver in excluded:
                exclusions[giver].add(receiver)
                exclusions[receiver].add(giver)
    
    valid = []
    
    for perm in permutations(participants):
        valid_pairing = True
        pairing = list(zip(participants, perm))
        
        for giver, receiver in pairing:
            if (
                giver == receiver or 
                receiver in exclusions[giver] or 
                receiver in history[giver] or
                (avoid_bidirectional and (receiver, giver) in pair_history)
            ):
                valid_pairing = False
                break
        
        if valid_pairing:
            valid.append(pairing)
    
    return valid

def generate_all_pairings(config, avoid_bidirectional=False):
    history = defaultdict(set)
    pair_history = set()
    all_pairings = []
    rounds = config['rounds']
    
    for round_num, round_config in enumerate(rounds, 1):
        valid = validate_round(round_config, history, pair_history, avoid_bidirectional)
        
        if not valid:
            raise ValueError(f"No valid pairings for round {round_num}")
        # else:  # Can be interesting 
        #     print(f"Valid pairings for round {round_num}: {len(valid)}")
        
        chosen = random.choice(valid)
        all_pairings.append({
            'pairing': dict(chosen),
            'budget': round_config['budget']
        })

        for giver, receiver in chosen:
            history[giver].add(receiver)
            pair_history.add((giver, receiver))

    return all_pairings

def generate_emails(all_pairings, config, draw_id):

    def load_template(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
        
    emails = defaultdict(list)
    
    template_path = f"templates/{config['email'].get('language', 'en')}.tmpl"
    
    #To be fixed in next version (if ever)
    silly_round_string = "Round" if config['email'].get('language', 'en') else "Runde"
    

    for round_num, round_data in enumerate(all_pairings, 1):
        pairing = round_data['pairing']
        budget = round_data['budget']
        
        for giver in pairing:
            emails[giver].append(
                f"{silly_round_string} {round_num}: <strong>{pairing[giver]}</strong> (Budget: {budget})"
            )
    
    html_emails = {}
    for name, assignments in emails.items():
        template = load_template(template_path)
        assignments_html = ''.join(f'<li>🎁 {assignment}</li>' for assignment in assignments)
        html_emails[name] = template.format(
            name=name,
            year=config['year'],
            assignments=assignments_html,
            sender=config['email']['sender'],
            draw_id=draw_id
        )
    return html_emails

def generate_summary(all_pairings):
    """Thank you perplexity for the help"""
    participants = set()
    for round_data in all_pairings:
        participants.update(round_data['pairing'].keys())
    participants = sorted(participants)
    
    col_width = 20 
    
    header = f"{'Participant':<{col_width}}"
    for round_num, round_data in enumerate(all_pairings, 1):
        budget = round_data['budget']
        header += f"Round {round_num} ({budget})".ljust(col_width)
    lines = [header]
    lines.append("-" * len(header))
    
    # Prepare rows
    for name in participants:
        row = f"{name:<{col_width}}"
        for round_num, round_data in enumerate(all_pairings, 1):
            pairing = round_data['pairing']
            if name in pairing:
                val = pairing[name]
            else:
                val = "-"
            row += f"{val:<{col_width}}"
        lines.append(row)
    
    return "\n".join(lines)


def run_draw():

    DRAW_ID = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
    SENDER_MAIL = args.gmail_sender
    SENDER_PW = args.gmail_password  #might have to be an "app password" for Gmail
    config = load_config('data/config.yaml')
    mail_adresses = load_mail_contacts('data/contact_information.json')


    all_pairings = generate_all_pairings(config, avoid_bidirectional=True)
    emails = generate_emails(all_pairings, config, DRAW_ID)
    
    if args.debug:
        # Save all mails as HTML files in "debug" folder
        for name, content in emails.items():
            with open(f"debug/{name}.html", "w") as f:
                f.write(content)
        if args.debug_email_user and args.debug_email_user in mail_adresses:
            send_email_smtp(SENDER_MAIL, SENDER_PW, mail_adresses[args.debug_email_user], config, emails[args.debug_email_user])
        #save summary as text file
        summary = generate_summary(all_pairings)
        with open("debug/summary.txt", "w") as f:
            f.write(summary)
        print(f"Summary Draw [{DRAW_ID}]:\n{summary}")
        print("\nDebug files created.")
    else:
        print("Draw ID:", DRAW_ID)
        # Send all mails
        for name, content in emails.items():
            send_email_smtp(SENDER_MAIL, SENDER_PW, mail_adresses[name], config, content)

    print("Draw completed.")
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Secret Santa draw.")
    parser.add_argument('--debug', action='store_true', help="Run in debug mode.")
    parser.add_argument('--debug_email_user', type=str, help="Debug Mail. Enter User Mail shall be sent to.", default=None)
    parser.add_argument('--gmail_sender', type=str, help="Gmail Sender Mail.", default=os.getenv("SENDER_MAIL"))
    parser.add_argument('--gmail_password', type=str, help="Gmail Sender Password.", default=os.getenv("SENDER_PW"))
    args = parser.parse_args()

    run_draw()
