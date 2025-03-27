import json
import os
from typing import List, Dict, Optional

class NotesManager:
    def __init__(self, file_path: str = 'notes.json'):
        self.file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create notes file if it doesn't exist"""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump({}, f)
    
    def _load_notes(self) -> Dict:
        """Load notes from file"""
        with open(self.file_path, 'r') as f:
            return json.load(f)
    
    def _save_notes(self, notes: Dict):
        """Save notes to file"""
        with open(self.file_path, 'w') as f:
            json.dump(notes, f, indent=4)
    
    def save_note(self, title: str, content: str) -> bool:
        """Save a new note"""
        notes = self._load_notes()
        notes[title] = content
        self._save_notes(notes)
        return True
    
    def get_note(self, title: str) -> Optional[str]:
        """Get a specific note by title"""
        notes = self._load_notes()
        return notes.get(title)
    
    def remove_note(self, title: str) -> bool:
        """Remove a note by title"""
        notes = self._load_notes()
        if title in notes:
            del notes[title]
            self._save_notes(notes)
            return True
        return False
    
    def list_notes(self) -> List[str]:
        """Get list of all note titles"""
        notes = self._load_notes()
        return list(notes.keys())