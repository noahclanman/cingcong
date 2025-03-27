import random
from typing import List, Dict, Tuple
from datetime import datetime, timedelta

class CardGenerator:
    def __init__(self):
        self.card_patterns = {
            'visa': {'length': 16, 'cvv': 3, 'prefix': ['4']},
            'mastercard': {'length': 16, 'cvv': 3, 'prefix': ['51', '52', '53', '54', '55']},
            'amex': {'length': 15, 'cvv': 4, 'prefix': ['34', '37']},
            'discover': {'length': 16, 'cvv': 3, 'prefix': ['6011', '65', '64', '60']},
            'jcb': {'length': 16, 'cvv': 3, 'prefix': ['35']},
            'other': {'length': 16, 'cvv': 3, 'prefix': []}
        }

    def luhn_checksum(self, card_number: str) -> bool:
        """Validate card number using Luhn algorithm"""
        def digits_of(n: str) -> List[int]:
            return [int(d) for d in str(n)]

        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10 == 0

    def generate_card(self, pattern: str) -> str:
        """
        Generate a single valid card number based on the pattern
        Handles both 'x' markers and incomplete numbers
        """
        # If pattern contains |, extract just the card part
        if '|' in pattern:
            pattern = pattern.split('|')[0]
            
        # Detect brand and get target length
        brand = self.detect_brand(pattern)
        target_length = self.card_patterns.get(brand, {}).get('length', 16)
        
        # Pad with 'x' if number is incomplete
        if len(pattern) < target_length:
            pattern = pattern + 'x' * (target_length - len(pattern))
            
        card_number = list(pattern)
        
        # Generate random digits for 'x' or missing positions
        for i, char in enumerate(card_number):
            if char.lower() == 'x':
                card_number[i] = str(random.randint(0, 9))
        
        # Calculate Luhn checksum
        card_str = ''.join(card_number[:-1])
        for i in range(10):
            temp = card_str + str(i)
            if self.luhn_checksum(temp):
                card_number[-1] = str(i)
                break
                
        return ''.join(card_number)

    def generate_date(self) -> Tuple[str, str]:
        """Generate random future expiry date"""
        current_date = datetime.now()
        future_date = current_date + timedelta(days=random.randint(365, 1825))
        month = str(future_date.month).zfill(2)
        year = str(future_date.year)[-2:]
        return month, year

    def generate_cvv(self, brand: str) -> str:
        """Generate CVV based on card brand"""
        length = 4 if brand.lower() == 'amex' else 3
        return ''.join([str(random.randint(0, 9)) for _ in range(length)])

    def detect_brand(self, cc_pattern: str) -> str:
        """Detect card brand from the pattern"""
        for brand, info in self.card_patterns.items():
            if brand != 'other':
                for prefix in info['prefix']:
                    if cc_pattern.startswith(prefix):
                        return brand
        return 'other'

    def parse_extrap(self, extrap: str) -> Dict:
        """
        Parse the extrap pattern and validate
        Formats supported:
        - Full format with date/cvv: xxxxxxxxxxxxxxxx|xx|xx|xxx
        - Partial number with date: 650842507513|12|33
        - Partial number: 650842507513
        - Simple format with x: 424242x
        - Short BIN format: 424242
        """
        try:
            if '|' in extrap:
                parts = extrap.split('|')
                cc = parts[0].strip()
                
                # Validate basic BIN format (at least 6 digits)
                if not cc[:6].isdigit():
                    return None
                    
                # Handle date parts if provided
                mm = parts[1] if len(parts) > 1 else 'xx'
                yy = parts[2] if len(parts) > 2 else 'xx'
                cvv = parts[3] if len(parts) > 3 else 'xxx'
                
                # Use provided dates or generate random if 'xx'
                if mm == 'xx' or yy == 'xx':
                    mm, yy = self.generate_date()
                
                return {
                    'cc': cc,  # Will be completed in generate_card
                    'mm': mm,
                    'yy': yy,
                    'cvv': cvv
                }
            else:
                cc_pattern = extrap.strip()
                
                # Validate basic BIN format (at least 6 digits)
                if not cc_pattern[:6].isdigit():
                    return None
                
                return {
                    'cc': cc_pattern,  # Will be completed in generate_card
                    'mm': 'xx',
                    'yy': 'xx',
                    'cvv': 'xxx'
                }
        except Exception:
            return None

    def generate_cards(self, extrap: str, count: int = 10, mode: str = 'full') -> List[str]:
        """
        Generate multiple cards based on the extrap pattern
        mode: 'full' for complete card generation, 'datecvv' for only date and CVV
        """
        parsed = self.parse_extrap(extrap)
        if not parsed:
            return []

        cards = []
        brand = self.detect_brand(parsed['cc'])
        
        for _ in range(count):
            if mode == 'full':
                cc = self.generate_card(parsed['cc'])
                # Use provided dates if available, otherwise generate
                mm = parsed['mm'] if parsed['mm'] != 'xx' else self.generate_date()[0]
                yy = parsed['yy'] if parsed['yy'] != 'xx' else self.generate_date()[1]
                cvv = self.generate_cvv(brand) if parsed['cvv'] == 'xxx' else parsed['cvv']
                cards.append(f"{cc}|{mm}|{yy}|{cvv}")
            elif mode == 'datecvv':
                mm, yy = self.generate_date()
                cvv = self.generate_cvv(brand)
                cards.append(f"{mm}|{yy}|{cvv}")

        return cards

    def save_extrap(self, extrap: str) -> None:
        """Save extrap pattern to extrap.txt"""
        with open('extrap.txt', 'a') as f:
            f.write(f"{extrap}\n")

    def format_output(self, cards: List[str], bin_info: Dict, user_info: Dict) -> str:
        """Format the generated cards output with a minimal design"""
        
        # Define separator
        separator = "━━━━━━━━━━━━━━━━"
        
        # Header
        output = [
            separator,
            "│ 💳 CC GENERATOR RESULTS 💳",
            separator,
            "│ 📊 BIN INFORMATION",
            f"│ • BIN     : {bin_info.get('bin', 'Unknown')}",
            f"│ • BANK    : {bin_info.get('bank', 'Unknown')}",
            f"│ • BRAND   : {bin_info.get('brand', 'Unknown')}",
            f"│ • TYPE    : {bin_info.get('type', 'Unknown')}",
            f"│ • COUNTRY : {bin_info.get('country', 'Unknown')}",
            separator,
            "│ 🎲 GENERATED CARDS"
        ]
        
        # Format each card
        for i, card in enumerate(cards, 1):
            cc_data = card.split('|')
            if len(cc_data) >= 4:
                cc, mm, yy, cvv = cc_data
                output.append(f"│ {i}. `{cc}|{mm}|{yy}|{cvv}`")
            else:
                output.append(f"│ {i}. `{card}`")
        
        # Footer
        output.extend([
            separator,
            "│ 👤 USER INFORMATION",
            f"│ • ID      : {user_info.get('user_id', 'Unknown')}",
            f"│ • NAME    : {user_info.get('username', 'Unknown')}",
            separator,
            "│ ℹ️  Click 📋 to copy card details",
            separator
        ])
        
        return "\n".join(output)
