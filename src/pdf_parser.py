import PyPDF2
import re

KEYWORDS = ["D’APPROUVER", "D’ATTRIBUER", "D’AUTORISER", "DE PRENDRE", "D’AFFECTER"]
class PdfParser:
    def __init__(self) -> None:
        self.upload_file = "src/uploads/"
        pass
    
    def parse_document(self, filename:str) -> str:
        
        with open(self.upload_file+filename, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

        return (text)
    
    def extract_date(self, text:str)->str:  
        pattern = r"Réunion du (\d{1,2}\s+[a-zéû]+\s+\d{4})"

        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            date = match.group(1)
            return date
        else:
            return ''

    def extract_decisions(self, text:str) -> list[str]:
        decisions =  []
        words = text.split()
        first_keyword = self.find_first_keyword_index(words)
        if(first_keyword>0):
            significant_text = words[first_keyword:]
            text = " ".join(significant_text)
            parts = re.split(r"\b(?:D'[A-Z]{5,}|[A-Z]{5,})\b", text)
            decisions = [part for part in parts if part!="D’"]
            
        return decisions

    
    def find_first_keyword_index(self, words: list[str]) -> int:
        for i, word in enumerate(words):
            if word in KEYWORDS:  # Check if word is in keyword list
                return i  # Return index of first match
        return -1
