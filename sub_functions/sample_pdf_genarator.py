def create_random_invoices(number):
    from fpdf import FPDF
    from faker import Faker
    import random
    import os

    # Initialize Faker
    fake = Faker()


    # Function to generate random items
    def generate_items():
        items = [
            {"item": "Laptop", "price": 1200},
            {"item": "Headphones", "price": 150},
            {"item": "Monitor", "price": 300},
            {"item": "Keyboard", "price": 100},
            {"item": "Smartphone", "price": 900},
            {"item": "Charger", "price": 25},
            {"item": "Mouse", "price": 40},
            {"item": "Tablet", "price": 500},
            {"item": "Webcam", "price": 80}
        ]
        # Randomly select a few items for the invoice
        return random.sample(items, random.randint(2, 5))


    # Function to generate random invoice data
    def generate_invoice_data(num_invoices):
        invoice_data = []
        for _ in range(num_invoices):
            invoice = {
                "name": fake.name(),
                "location": f"{fake.city()}, {fake.country()}",
                "items": [
                    {
                        "item": item["item"],
                        "quantity": random.randint(1, 3),
                        "price": item["price"]
                    } for item in generate_items()
                ]
            }
            invoice_data.append(invoice)
        return invoice_data


    # Generate sample invoice data
    invoice_data = generate_invoice_data(number)

    # Create a PDF document
    pdf = FPDF()


    # Function to add invoice to the PDF
    def add_invoice_page(pdf, invoice):
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add invoice header
        pdf.cell(200, 10, txt=f"Invoice for {invoice['name']}", ln=True, align="C")
        pdf.cell(200, 10, txt=f"Location: {invoice['location']}", ln=True, align="C")

        # Add table header
        pdf.ln(10)
        pdf.cell(80, 10, txt="Item", border=1, align="C")
        pdf.cell(30, 10, txt="Quantity", border=1, align="C")
        pdf.cell(30, 10, txt="Price", border=1, align="C")
        pdf.cell(30, 10, txt="Total", border=1, align="C")
        pdf.ln(10)

        # Add items to the invoice
        for item in invoice['items']:
            pdf.cell(80, 10, txt=item['item'], border=1)
            pdf.cell(30, 10, txt=str(item['quantity']), border=1, align="C")
            pdf.cell(30, 10, txt=f"${item['price']}", border=1, align="C")
            total_price = item['quantity'] * item['price']
            pdf.cell(30, 10, txt=f"${total_price}", border=1, align="C")
            pdf.ln(10)

        # Add footer
        pdf.ln(10)
        pdf.cell(200, 10, txt="Thank you for your business!", ln=True, align="C")


    # Add each invoice to the PDF
    for invoice in invoice_data:
        add_invoice_page(pdf, invoice)

    # Define the path to the folder
    folder_name = "uploads"
    folder_path = os.path.join(os.getcwd(), folder_name)

    # Check if the folder exists, if not, create it
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Output the PDF to a file
    pdf.output("uploads/invoices.pdf")

    print("PDF created successfully.")
