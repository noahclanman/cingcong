import requests
import json
from typing import Dict, Optional

class BinChecker:
    def __init__(self):
        self.api_url = "https://lookup.binlist.net/"
        self.backup_url = "https://api.bintable.com/v1/"
        self.backup_key = "4d08a1ffdd1845c9b62d65d65c8be7ad"
        
    def check_bin(self, bin_number: str) -> Optional[Dict]:
        """
        Check BIN information using local detection
        Returns None if the BIN is invalid
        """
        if not bin_number.isdigit() or not (6 <= len(bin_number) <= 8):
            return None
            
        brand = self.detect_brand(bin_number)
        if brand != 'Unknown':
            return {
                'bin': bin_number,
                'brand': brand,
                'type': 'Credit',
                'category': 'Classic',
                'bank': 'Test Bank',
                'country': 'United States'
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