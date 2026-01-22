import json
import logging
import os

logger = logging.getLogger(__name__)

class CreditsParser:
    SECTION_MAP = {
        "smwsprites": "Sprites",
        "uberasm": "UberASM",
        "smwblocks": "Blocks",
        "smwgraphics": "Graphics",
        "smwmusic": "Music",
        "patches": "Patches",
        "tools": "Tools"
    }

    @staticmethod
    def parse_file(filepath):
        """
        Parses a credits file (JSON or TXT).
        Returns a dict: { "Section Name": ["Author1", "Author2"], ... }
        For TXT, returns { "General": ["Author1", ...] }
        """
        if filepath.lower().endswith(".json"):
            return CreditsParser._parse_json(filepath)
        else:
            return CreditsParser._parse_txt(filepath)

    @staticmethod
    def parse_content(content, is_json=False):
        """Parses raw content string."""
        if is_json:
            if isinstance(content, str):
                try: content = json.loads(content)
                except: return {}
            return CreditsParser._parse_json_content(content)
        else:
            return CreditsParser._parse_txt_content(content)

    @staticmethod
    def _parse_txt_content(text):
        authors = set()
        for line in text.splitlines():
            name = line.strip()
            if name:
                authors.add(name)
        return {"General": sorted(list(authors), key=str.lower)}

    @staticmethod
    def _parse_txt(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return CreditsParser._parse_txt_content(f.read())
        except Exception as e:
            logger.error(f"Error parsing text credits: {e}")
            return {}

    @staticmethod
    def _parse_json(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = json.load(f)
            return CreditsParser._parse_json_content(content)
        except Exception as e:
            logger.error(f"Error parsing JSON credits file: {e}")
            return {}

    @staticmethod
    def _parse_json_content(content):
        data = {}
        try:
            # Content is list of objects
            if not isinstance(content, list):
                logger.error("JSON credits root must be a list")
                return {}

            for item in content:
                raw_section = item.get("section", "unknown")
                section_name = CreditsParser.SECTION_MAP.get(raw_section, raw_section.capitalize())
                
                if section_name not in data:
                    data[section_name] = set()

                item_authors = item.get("authors", [])
                for auth in item_authors:
                    name = auth.get("name")
                    if name:
                        data[section_name].add(name)
            
            # Convert sets to sorted lists
            final_data = {}
            for sec, names in data.items():
                if names:
                    final_data[sec] = sorted(list(names), key=str.lower)
            
            return final_data
        except Exception as e:
             logger.error(f"Error parsing JSON content: {e}")
             return {}

