import pdfplumber
import re
import uuid
import os

class PdfPlumberUtils:
    """Extraction of text and table data"""

    def __init__(self, file_path):
        """Intialize the file path"""
        self.file_path = file_path
        self.source = os.path.basename(file_path)

    def parse_specs(self, specs_text: str):
        specs = {}

        lines = specs_text.split("\n")

        for line in lines:
            line = line.strip()

            if not line or "Specification" in line:
                continue

            parts = line.split(" ", 1)

            if len(parts) == 2:
                key, value = parts
                specs[key.strip()] = value.strip()

        return specs

    def extract_sections(self, content: str):
        """Extract product about, description and specification from content"""
        about = ""
        description = ""
        specs_text = ""

        about_match = re.search(
            r'ABOUT THIS PRODUCT\n(.*?)\nPRODUCT DESCRIPTION',
            content,
            re.DOTALL
        )
        if about_match:
            about = about_match.group(1).strip()

        desc_match = re.search(
            r'PRODUCT DESCRIPTION\n(.*?)\nPRODUCT SPECIFICATIONS',
            content,
            re.DOTALL
        )
        if desc_match:
            description = desc_match.group(1).strip()

        specs_match = re.search(
            r'PRODUCT SPECIFICATIONS\n(.*)',
            content,
            re.DOTALL
        )
        if specs_match:
            specs_text = specs_match.group(1).strip()

        return about, description, specs_text

    def extract_text_from_pdf(self) -> list:

        all_products = []

        current_product = None

        with pdfplumber.open(self.file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                
                if not text:
                    continue

                text = re.sub(r'\(cid:\d+\)', '', text)
                text = re.sub(r'\n+', '\n', text)
                lines = text.split("\n")

                i = 0
                while i < len(lines):
                    line = lines[i].strip()

                    if "thank you for exploring" in line.lower():
                        break

                    if( i + 2 < len(lines)
                       and lines[i+1].strip() == "n"
                       and re.match(r'[\d,]+', lines[i+2].strip())
                    ):
                        if current_product:
                            all_products.append(current_product)

                        current_product = {
                            "id": str(uuid.uuid4()),
                            "page": page_num,
                            "name": line,
                            "price": lines[i+2].strip(),
                            "content": "",
                            "source": self.source
                        }
                        i += 3
                        continue
                    if current_product:
                        current_product["content"] += line + "\n"

                    i += 1

                if current_product:
                    current_product["content"] += line + "\n"


        return all_products
    

    def process(self):
        """Step by step process to extract data from pdf"""
        result = []
        all_products = self.extract_text_from_pdf()

        for product in all_products:
            about, description, specs_text = self.extract_sections(product['content'])
            specification = self.parse_specs(specs_text)
            result.append(
                { **product, "about": about, "description": description, "specification": specification}
            )

        return result