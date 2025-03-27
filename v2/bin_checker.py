import requests
import json
from typing import Dict, Optional

class BinChecker:
    def __init__(self):
        self.api_url = "https://lookup.binlist.net/"
        self.backup_url = "https://bincheck.io/bin/"
        
    def check_bin(self, bin_number: str) -> Optional[Dict]:
        """
        Check BIN information using reliable BIN lookup APIs
        Returns None if the BIN is invalid
        """
        if not bin_number.isdigit() or not (6 <= len(bin_number) <= 8):
            return None

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json'
        }
            
        # Try primary API first (binlist.net)
        try:
            response = requests.get(f"{self.api_url}{bin_number}", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'bin': bin_number,
                    'brand': data.get('scheme', self.detect_brand(bin_number)).title(),
                    'type': data.get('type', 'Credit').title(),
                    'category': data.get('brand', 'Classic').title(),
                    'bank': data.get('bank', {}).get('name', data.get('bank', 'Unknown')),
                    'country': data.get('country', {}).get('name', data.get('country', 'Unknown'))
                }
        except:
            pass

        # Try backup API (bincheck.io)
        try:
            response = requests.get(f"{self.backup_url}{bin_number}", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'bin': bin_number,
                    'brand': data.get('brand', self.detect_brand(bin_number)).title(),
                    'type': data.get('card_type', 'Credit').title(),
                    'category': data.get('level', 'Classic').title(),
                    'bank': data.get('issuing_bank', 'Unknown'),
                    'country': data.get('country', 'Unknown')
                }
        except:
            pass

        # If both APIs fail, use local detection with basic info
        brand = self.detect_brand(bin_number)
        if brand != 'Unknown':
            return {
                'bin': bin_number,
                'brand': brand,
                'type': 'Credit',
                'category': 'Classic',
                'bank': 'Unknown',
                'country': 'Unknown'
            }
        return None

    def detect_brand(self, bin_number: str) -> str:
        """Detect card brand from BIN"""
        if bin_number.startswith('4'):
            return 'Visa'
        elif bin_number.startswith(('51', '52', '53', '54', '55')):
            return 'Mastercard'
        elif bin_number.startswith(('34', '37')):
            return 'American Express'
        elif bin_number.startswith(('60', '64', '65')):
            return 'Discover'
        elif bin_number.startswith('35'):
            return 'JCB'
        return 'Unknown'

    def format_bin_info(self, bin_info: Dict) -> str:
        """Format BIN information for display"""
        if not bin_info:
            return "\n".join([
                "━━━━━━━━━━━━━━━━",
                "│ ❌ INVALID BIN",
                "│ • Unable to fetch information",
                "━━━━━━━━━━━━━━━━"
            ])
        
        separator = "━━━━━━━━━━━━━━━━"
        
        output = [
            separator,
            "│ 💳 BIN CHECKER",
            separator,
            "│ 📊 BIN INFORMATION",
            f"│ • BIN      : {bin_info['bin']}",
            f"│ • BRAND    : {bin_info['brand']}",
            f"│ • TYPE     : {bin_info['type']}",
            f"│ • CATEGORY : {bin_info['category']}",
            f"│ • BANK     : {bin_info['bank']}",
            f"│ • COUNTRY  : {bin_info['country']}",
            separator,
            "│ ℹ️  BIN Lookup Service",
            separator
        ]
        
        return "\n".join(output)

    def save_bin(self, bin_number: str) -> None:
        """Save checked BIN to bins.txt"""
        with open('bins.txt', 'a') as f:
            f.write(f"{bin_number}\n")