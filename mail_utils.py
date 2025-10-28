from email.mime.text import MIMEText
import smtplib
from localization import Translations

class EmailHandler:
    def __init__(self, config):
        self.config = config
        self.translator = Translations(config['email'].get('language', 'en'))
        
    def load_template(self, template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    
    def format_assignment(self, recipient, round_num, total_rounds, budget):
        """Formats a single assignment line"""
        if total_rounds == 1:
            text = f"<strong>{recipient}</strong>"
        else:
            text = f"{self.translator.format_round(round_num)}: <strong>{recipient}</strong>"
            
        if budget:
            text += f" {self.translator.format_budget(budget)}"
        return text
    
    def generate_email(self, name, assignments, draw_id):
        """Generates complete email HTML for a participant"""
        template_path = f"templates/{self.translator.language}.tmpl"
        template = self.load_template(template_path)
        assignments_html = ''.join(f'<li>🎁 {assignment}</li>' for assignment in assignments)
        
        return template.format(
            name=name,
            year=self.config['year'],
            assignments=assignments_html,
            sender=self.config['email']['sender'],
            draw_id=draw_id,
            assignment_text=self.translator.get_assignment_text(len(assignments) == 1)
        )
    
    def send_email(self, sender_email, app_password, recipient_email, html_body):
        """Sends an email using SMTP"""
        msg = MIMEText(html_body, 'html')
        msg['Subject'] = self.config['email']['subject']
        msg['From'] = self.config['email']['sender']
        msg['To'] = recipient_email

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, app_password)
            server.send_message(msg)
            print(f"Email sent to {recipient_email}")