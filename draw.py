import random
import yaml
import json
from mail_utils import send_email, move_email_to_archive
import hashlib
import time

MAX_ATTEMPTS = 20
DEBUG = False
UNIQUE_ID = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]

def load_data(filename):
    with open(filename, 'r') as file:
        return yaml.safe_load(file)
    
def load_mail_contacts(filename): 
    with open(filename, 'r') as file:
        return json.load(file)
    

def draw(names, exclusions=None, previous_pairings=None):
    attempts =0
    if exclusions is None:
        exclusions = {}
    if previous_pairings is None:
        previous_pairings = {}
        
    receivers = names[:]
    givers = names[:]
    random.shuffle(receivers)
    pairs = {}
    
    for giver in givers:
        receiver = random.choice(receivers)
        while receiver == giver \
            or (giver in exclusions and receiver in exclusions[giver]) \
            or (previous_pairings.get(giver) == receiver) \
            or (previous_pairings.get(receiver) == giver):
            receiver = random.choice(receivers)
            if attempts > MAX_ATTEMPTS: #RECURSIVE DOOM
                return draw(names, exclusions, previous_pairings)
            else:
                attempts += 1 
        pairs[giver] = receiver
        receivers.remove(receiver)
    
    return pairs

def emails_for_pairings(pairings, stage):
    emails = []
    for giver, receiver in pairings.items():
        emails.append(
            (giver, receiver, f"Runde {stage}: {giver}, du hast {receiver} gezogen!")
        )
    return emails

def create_connections_dict(list_of_dicts):
    connections_dict = {}

    for i, d in enumerate(list_of_dicts):
        for key, value in d.items():
            if key not in connections_dict:
                connections_dict[key] = {}
            if i not in connections_dict[key]:
                connections_dict[key][i] = value

    return connections_dict

def create_body(key, connected_dict, data, unique_id=UNIQUE_ID):
    body = ('Hallo ' + key + ',\n')
    for i in range(len(data['draws'])):
        if i in connected_dict[key]:
            body+=('Runde '+ str(i+1) + ': Du hast ' + connected_dict[key][i] + ' gezogen. Das Budget beträgt ' + str(data['draws'][i]['budget']) + ' Euro.\n')
    body+=("Viel Spaß beim Schenken!\n\nBeste automatisierte Grüße\nSchatt\'scher Weihnachtswichtelbot 2024")
    body+=("\n\nDraw ID: " + unique_id)
    return body


def create_mail_dict(connections_dict, data, mail_contacts):
    mails = []
    for key in connections_dict:
        recipent = mail_contacts[key]
        body = create_body(key, connections_dict, data)
        mails.append((recipent, "Schatt'sches Weihnachtswichteln 2024", body))
    return mails


def main():
    data = load_data("secret_santa.yaml")
    mail_contacts = load_mail_contacts("mail_contacts.json")

    previous_pairings = {}
    final_pairings = []
    
    for i, draw_info in enumerate(data["draws"], start=1):
        participants = draw_info["participants"]
        exclusions = draw_info.get("exclusions", {})
        pairs = draw(participants, exclusions, previous_pairings)
        previous_pairings.update(pairs)
        final_pairings.append(pairs)

    connections_dict = create_connections_dict(final_pairings)
    mails = create_mail_dict(connections_dict, data, mail_contacts)

    if DEBUG:
        # create a debug file
        with open("debug_mails.json", "w") as file:
            json.dump(mails, file, indent=2)
        print("Debug file created.")
        
    else:
        print("Sending emails...")
        for receiver, title, body in mails:
            success_send, message_send = send_email(receiver, title, body)
            success_archive, message_archive = move_email_to_archive(message_send["id"])
            if success_send:
                print(f"Email sent to {receiver}")
            else:
                print(f"Failed to send email to {receiver}")
        print("All emails sent.")

if __name__ == "__main__":
    main()
