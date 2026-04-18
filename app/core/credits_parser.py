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
                try:
                    content = json.loads(content)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON syntax: {e}")
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
        except FileNotFoundError:
            raise ValueError(f"File not found: {filepath}")
        except Exception as e:
            raise ValueError(f"Error reading text file: {e}")

    @staticmethod
    def _parse_json(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = json.load(f)
            return CreditsParser._parse_json_content(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON syntax: {e}")
        except FileNotFoundError:
            raise ValueError(f"File not found: {filepath}")
        except Exception as e:
            raise ValueError(f"Error reading JSON file: {e}")

    @staticmethod
    def _parse_json_content(content):
        data = {}
        # Content is list of objects
        if not isinstance(content, list):
            raise ValueError(
                f"JSON root must be a list (got {type(content).__name__}). "
                "Expected format: [{\"section\": \"...\", \"authors\": [...]}]"
            )

        for i, item in enumerate(content):
            if not isinstance(item, dict):
                raise ValueError(
                    f"Item {i} must be an object/dict (got {type(item).__name__}). "
                    "Expected: {\"section\": \"...\", \"authors\": [...]}"
                )
            raw_section = item.get("section", "unknown")
            section_name = CreditsParser.SECTION_MAP.get(raw_section, raw_section.capitalize())

            if section_name not in data:
                data[section_name] = set()

            item_authors = item.get("authors", [])
            if not isinstance(item_authors, list):
                raise ValueError(
                    f"'authors' in section '{raw_section}' must be a list (got {type(item_authors).__name__})"
                )
            for auth in item_authors:
                if isinstance(auth, dict):
                    name = auth.get("name")
                elif isinstance(auth, str):
                    name = auth
                else:
                    continue
                if name:
                    data[section_name].add(name)

        # Convert sets to sorted lists
        final_data = {}
        for sec, names in data.items():
            if names:
                final_data[sec] = sorted(list(names), key=str.lower)

        return final_data

