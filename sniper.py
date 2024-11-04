import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import re


# Suppress Selenium logs
logging.getLogger('selenium').setLevel(logging.WARNING)

# Email configuration
EMAIL_ADDRESS = 'tiagopinto188@gmail.com'  # Replace with your sender email
recipient_email = 'zarkin2005@gmail.com'  # Replace with your recipient email


smtp_port = 587  # For TLS


def time_to_minutes(time_str):
    # Expressão regular para capturar "horas" ou "minutos"
    match = re.search(r'(\d+)\s*(hora|minuto)', time_str, re.IGNORECASE)
    if match:
        quantity = int(match.group(1))
        unit = match.group(2).lower()
        
        # Converte para minutos
        if 'hora' in unit:
            return quantity * 60
        elif 'minuto' in unit:
            return quantity
    return None



def send_email(subject, product):
    # Prepare HTML content for the email
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #007BFF;">New Product Alert!</h2>
            <p>We have found a new product that matches your search criteria:</p>
            <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0;">
                <img src="{product['img']}" alt="Product Image" style="max-width: 200px; height: auto; border: 1px solid #ddd; margin-bottom: 10px;">
                <p><strong>Brand:</strong> {product['brand']}</p>
                <p><strong>Price:</strong> {product['price']}</p>
                <p><strong>Upload Date:</strong> {product.get('upload_date', 'Unknown')}</p>
                <p><strong>Link:</strong> <a href="{product['link']}">View Product</a></p>
            </div>
            <p>Check it out now before it's gone!</p>
            <p>Best regards,<br>Your Automated Product Notifier</p>
        </body>
    </html>
    """
    
    # Set up the email message
    message = MIMEMultipart("alternative")
    message["From"] = EMAIL_ADDRESS
    message["To"] = recipient_email
    message["Subject"] = subject

    # Attach both plain text and HTML content
    message.attach(MIMEText(html_content, "html"))

    # Send the email
    server = smtplib.SMTP("smtp.gmail.com", smtp_port)
    server.starttls()
    server.login(EMAIL_ADDRESS, "yjyc aczq zkun qtns")  # Be sure to keep your credentials secure
    server.sendmail(EMAIL_ADDRESS, recipient_email, message.as_string())
    server.quit()
    print("Email sent successfully.")

def fetch_product(url):
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    service = Service(r"C:\Users\Tiago Pinto\projetos\pessoais\2024\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        print(f'Sniping [{count}]') # Placeholder for the count of fetches
        driver.get(url)
        time.sleep(3)  # Wait for the page to load

        # Step 1: Get the first product element
        product = {}
        item = driver.find_element(By.CSS_SELECTOR, '.feed-grid__item')  # Select the first product item
        
        img = item.find_element(By.CSS_SELECTOR, '[data-testid$="--image--img"]').get_attribute('src')
        price = item.find_element(By.CSS_SELECTOR, '.new-item-box__title').text
        brand = item.find_element(By.CSS_SELECTOR, '.new-item-box__description').text
        link = item.find_element(By.CSS_SELECTOR, '.new-item-box__overlay.new-item-box__overlay--clickable').get_attribute('href')

        product['img'] = img
        product['price'] = price
        product['brand'] = brand
        product['link'] = link

        # Step 2: Navigate to the product link to get the upload date
        driver.get(product['link'])
        time.sleep(3)  # Wait for the product page to load

        # Extract upload date
        upload_date_element = driver.find_element(By.CSS_SELECTOR, '[data-testid="item-attributes-upload_date"] .details-list__item-value')
        upload_date = upload_date_element.text if upload_date_element else 'Unknown'

        # Check for existing latest upload date
        try:
            with open('latest_upload_date.txt', 'r') as f:
                latest_upload_date = f.read().strip()
        except FileNotFoundError:
            latest_upload_date = None

        # Logic for comparing and updating upload dates as strings
        if latest_upload_date is None or time_to_minutes(upload_date) < time_to_minutes(latest_upload_date):
            with open('latest_upload_date.txt', 'w') as f:
                f.write(upload_date)  # Store the new upload date
            # Send email notification
            print("Email to be sent")
            send_email("New Product Found!", product)

        # Print the product details
        print("\nProduct Details:")
        print(f"  Image URL: {product['img']}")
        print(f"  Price: {product['price']}")
        print(f"  Brand: {product['brand']}")
        print(f"  Link: {product['link']}")
        print(f"  Upload Date: {upload_date}\n")

    except Exception as e:
        print(f"Error fetching product: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    url = input("Please enter a Vinted search URL: ").strip()
    print("Press any key to stop the program.")

    count = 0
    try:
        while True:
            count += 1
            fetch_product(url)  # Fetch the product
            time.sleep(10)  # Wait for 10 seconds before the next fetch
    except KeyboardInterrupt:
        print("Exiting the program due to keyboard interrupt.")
