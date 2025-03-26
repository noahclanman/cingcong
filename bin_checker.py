import requests
import json
from typing import Dict, Optional

class BinChecker:
    def __init__(self):
        self.api_url = "https://lookup.binlist.net/"
        
    def check_bin(self, bin_number: str) -> Optional[Dict]:
        """
        Check BIN information using binlist.net API
        Returns None if the BIN is invalid or API request fails
        """
        if not bin_number.isdigit() or not (6 <= len(bin_number) <= 8):
            return None
            
        try:
            response = requests.get(f"{self.api_url}{bin_number}")
            if response.status_code == 200:
                data = response.json()
                return {
                    'bin': bin_number,
                    'brand': data.get('scheme', 'Unknown').title(),
                    'type': data.get('type', 'Unknown').title(),
                    'category': data.get('category', 'Unknown').title(),
                    'bank': data.get('bank', {}).get('name', 'Unknown'),
                    'country': data.get('country', {}).get('name', 'Unknown')
                }
        except (requests.RequestException, json.JSONDecodeError) as e:
            print(f"Error checking BIN: {e}")
        return None

    def format_bin_info(self, bin_info: Dict) -> str:
        """Format BIN information for display"""
        if not bin_info:
            return "❌ Invalid BIN or unable to fetch information"
            
        return (
            f"🔍 BIN Information:\n\n"
            f"BIN: {bin_info['bin']}\n"
            f"Brand: {bin_info['brand']}\n"
            f"Type: {bin_info['type']}\n"
            f"Category: {bin_info['category']}\n"
            f"Bank: {bin_info['bank']}\n"
            f"Country: {bin_info['country']}"
        )

    def save_bin(self, bin_number: str) -> None:
        """Save checked BIN to bins.txt"""
        with open('bins.txt', 'a') as f:
            f.write(f"{bin_number}\n")