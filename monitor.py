import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
import json
from time import sleep

class AmazonBookMonitor:
    def __init__(self, config_path='config.json'):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def check_book_status(self, book_url):
        """Check availability and reviews for a single book"""
        try:
            response = requests.get(book_url, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get book title
            title = soup.find('span', {'id': 'productTitle'})
            title = title.text.strip() if title else 'Unknown Title'
            
            # Check availability
            availability = soup.find('div', {'id': 'availability'})
            in_stock = 'In Stock' in availability.text if availability else False
            
            # Check Kindle availability
            kindle_button = soup.find('a', {'id': 'kindle-button'})
            kindle_available = bool(kindle_button)
            
            # Get review score
            review_element = soup.find('span', {'class': 'a-icon-alt'})
            review_score = float(review_element.text.split(' ')[0]) if review_element else 0.0
            
            return {
                'title': title,
                'in_stock': in_stock,
                'kindle_available': kindle_available,
                'review_score': review_score,
                'url': book_url
            }
        except Exception as e:
            return {
                'title': 'Error checking book',
                'error': str(e),
                'url': book_url
            }

    def send_email(self, subject, body, recipients):
        """Send email using configured SMTP settings"""
        msg = MIMEMultipart()
        msg['From'] = self.config['smtp']['email']
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(self.config['smtp']['server'], self.config['smtp']['port']) as server:
            server.starttls()
            server.login(self.config['smtp']['email'], self.config['smtp']['password'])
            server.send_message(msg)

    def generate_report(self, results):
        """Generate email report from results"""
        report = f"Amazon Book Status Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        issues = []
        for book in results:
            report += f"Book: {book['title']}\n"
            report += f"URL: {book['url']}\n"
            
            if 'error' in book:
                report += f"Error: {book['error']}\n"
                issues.append(f"Error checking {book['title']}")
            else:
                report += f"In Stock: {'Yes' if book['in_stock'] else 'No'}\n"
                report += f"Kindle Available: {'Yes' if book['kindle_available'] else 'No'}\n"
                report += f"Review Score: {book['review_score']}\n"
                
                # Check for issues
                if not book['in_stock']:
                    issues.append(f"{book['title']} is out of stock")
                if not book['kindle_available']:
                    issues.append(f"{book['title']} Kindle version unavailable")
                if book['review_score'] < self.config['min_review_score']:
                    issues.append(f"{book['title']} review score below threshold ({book['review_score']})")
            
            report += "\n"
        
        return report, issues

    def run_monitoring(self):
        """Main monitoring function"""
        results = []
        for book_url in self.config['book_urls']:
            results.append(self.check_book_status(book_url))
            sleep(2)  # Delay to avoid rate limiting
        
        report, issues = self.generate_report(results)
        
        # Send email if there are issues or if daily report is enabled
        if issues or self.config['send_daily_report']:
            subject = "Amazon Book Status - Issues Found" if issues else "Amazon Book Status Report"
            self.send_email(subject, report, self.config['email_recipients'])

if __name__ == "__main__":
    monitor = AmazonBookMonitor()
    monitor.run_monitoring()
