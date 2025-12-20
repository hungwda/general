"""
PII (Personally Identifiable Information) redactor for medical documents.
Identifies and redacts sensitive information while maintaining document structure.
"""

import re
from typing import Dict, List, Optional, Tuple, Set
from pathlib import Path
from datetime import datetime


class PIIRedactor:
    """
    Redacts personally identifiable information from markdown documents.
    Supports various PII types with configurable redaction patterns.
    """

    def __init__(
        self,
        redaction_marker: str = "[REDACTED]",
        preserve_structure: bool = True,
        log_redactions: bool = True
    ):
        """
        Initialize PII redactor.

        Args:
            redaction_marker: Text to replace PII with (default: [REDACTED])
            preserve_structure: Keep document structure intact (default: True)
            log_redactions: Track what was redacted (default: True)
        """
        self.redaction_marker = redaction_marker
        self.preserve_structure = preserve_structure
        self.log_redactions = log_redactions
        self.redaction_log = []

    def _log_redaction(self, pii_type: str, original: str, context: str = ""):
        """Log a redaction event."""
        if self.log_redactions:
            self.redaction_log.append({
                'type': pii_type,
                'original': original,
                'context': context,
                'timestamp': datetime.now().isoformat()
            })

    def redact_names(self, text: str, patterns: Optional[List[str]] = None) -> str:
        """
        Redact person names from text.

        Args:
            text: Input text
            patterns: Optional custom name patterns to redact

        Returns:
            Text with names redacted
        """
        # Common patterns for name fields in medical documents
        name_patterns = [
            # Direct name labels
            r'(?:Name|Patient Name|Full Name|Legal Name):\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'(?:Name|Patient Name|Full Name|Legal Name)\s*-\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',

            # Table format
            r'\|\s*(?:Name|Patient Name)\s*\|\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s*\|',

            # List format
            r'-\s*(?:Name|Patient Name):\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        ]

        if patterns:
            name_patterns.extend(patterns)

        for pattern in name_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                name = match.group(1)
                self._log_redaction('NAME', name)
                text = text.replace(name, self.redaction_marker)

        return text

    def redact_dates_of_birth(self, text: str) -> str:
        """
        Redact dates of birth from text.

        Args:
            text: Input text

        Returns:
            Text with DOBs redacted
        """
        dob_patterns = [
            # DOB with various formats
            r'(?:DOB|Date of Birth|Birth Date|Born):\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(?:DOB|Date of Birth|Birth Date|Born)\s*-\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'\|\s*(?:DOB|Date of Birth)\s*\|\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\s*\|',

            # Written format
            r'(?:DOB|Date of Birth|Born):\s*([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})',
            r'(?:DOB|Date of Birth|Born)\s*-\s*([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})',
        ]

        for pattern in dob_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                dob = match.group(1)
                self._log_redaction('DATE_OF_BIRTH', dob)
                text = text.replace(dob, self.redaction_marker)

        return text

    def redact_ids(self, text: str) -> str:
        """
        Redact various ID numbers (patient ID, MRN, SSN, etc.).

        Args:
            text: Input text

        Returns:
            Text with IDs redacted
        """
        id_patterns = [
            # Patient ID / MRN
            (r'(?:Patient\s+)?(?:ID|MRN|Medical Record Number):\s*([A-Z0-9-]+)', 'PATIENT_ID'),
            (r'\|\s*(?:Patient\s+)?(?:ID|MRN)\s*\|\s*([A-Z0-9-]+)\s*\|', 'PATIENT_ID'),

            # SSN (Social Security Number)
            (r'(?:SSN|Social Security(?:\s+Number)?):\s*(\d{3}-\d{2}-\d{4})', 'SSN'),
            (r'(?:SSN|Social Security(?:\s+Number)?):\s*(\d{9})', 'SSN'),

            # Driver's License
            (r'(?:Driver\'?s?\s+License|DL)(?:\s+Number)?:\s*([A-Z0-9-]+)', 'DRIVERS_LICENSE'),

            # Insurance ID
            (r'(?:Insurance|Policy)\s+(?:ID|Number):\s*([A-Z0-9-]+)', 'INSURANCE_ID'),
        ]

        for pattern, id_type in id_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                id_value = match.group(1)
                self._log_redaction(id_type, id_value)
                text = text.replace(id_value, self.redaction_marker)

        return text

    def redact_contact_info(self, text: str) -> str:
        """
        Redact contact information (phone, email, address).

        Args:
            text: Input text

        Returns:
            Text with contact info redacted
        """
        # Phone numbers
        phone_patterns = [
            (r'(?:Phone|Tel|Telephone|Mobile|Cell):\s*(\+?1?\s*\(?[0-9]{3}\)?[\s.-]?[0-9]{3}[\s.-]?[0-9]{4})', 'PHONE'),
            (r'\|\s*(?:Phone|Tel|Contact)\s*\|\s*(\+?1?\s*\(?[0-9]{3}\)?[\s.-]?[0-9]{3}[\s.-]?[0-9]{4})\s*\|', 'PHONE'),
        ]

        for pattern, contact_type in phone_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                phone = match.group(1)
                self._log_redaction(contact_type, phone)
                text = text.replace(phone, self.redaction_marker)

        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.finditer(email_pattern, text)
        for match in matches:
            email = match.group(0)
            self._log_redaction('EMAIL', email)
            text = text.replace(email, self.redaction_marker)

        # Street addresses (basic pattern)
        address_patterns = [
            r'(?:Address|Street|Residence):\s*(\d+\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)[A-Za-z0-9\s,]*)',
        ]

        for pattern in address_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                address = match.group(1)
                self._log_redaction('ADDRESS', address)
                text = text.replace(address, self.redaction_marker)

        return text

    def redact_age_over_89(self, text: str) -> str:
        """
        Redact ages over 89 per HIPAA requirements.

        Args:
            text: Input text

        Returns:
            Text with ages >89 redacted
        """
        age_pattern = r'(?:Age|age):\s*(\d+)'

        matches = re.finditer(age_pattern, text)
        for match in matches:
            age_str = match.group(1)
            age = int(age_str)
            if age > 89:
                self._log_redaction('AGE_OVER_89', age_str)
                text = text.replace(f'Age: {age_str}', f'Age: {self.redaction_marker}')
                text = text.replace(f'age: {age_str}', f'age: {self.redaction_marker}')

        return text

    def redact_custom_patterns(self, text: str, patterns: Dict[str, str]) -> str:
        """
        Redact custom patterns provided by user.

        Args:
            text: Input text
            patterns: Dictionary of {pattern_name: regex_pattern}

        Returns:
            Text with custom patterns redacted
        """
        for pattern_name, pattern in patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value = match.group(0)
                self._log_redaction(f'CUSTOM_{pattern_name}', value)
                text = text.replace(value, self.redaction_marker)

        return text

    def redact_all(
        self,
        text: str,
        include: Optional[Set[str]] = None,
        exclude: Optional[Set[str]] = None,
        custom_patterns: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Redact all PII types from text.

        Args:
            text: Input text
            include: Set of PII types to include (None = all)
            exclude: Set of PII types to exclude
            custom_patterns: Custom redaction patterns

        Returns:
            Text with all specified PII redacted
        """
        # Reset redaction log for new document
        self.redaction_log = []

        # Available redaction types
        redaction_methods = {
            'names': self.redact_names,
            'dob': self.redact_dates_of_birth,
            'ids': self.redact_ids,
            'contact': self.redact_contact_info,
            'age_over_89': self.redact_age_over_89,
        }

        # Determine which methods to apply
        if include:
            methods_to_apply = {k: v for k, v in redaction_methods.items() if k in include}
        else:
            methods_to_apply = redaction_methods.copy()

        if exclude:
            methods_to_apply = {k: v for k, v in methods_to_apply.items() if k not in exclude}

        # Apply each redaction method
        for method_name, method in methods_to_apply.items():
            text = method(text)

        # Apply custom patterns if provided
        if custom_patterns:
            text = self.redact_custom_patterns(text, custom_patterns)

        return text

    def redact_file(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        include: Optional[Set[str]] = None,
        exclude: Optional[Set[str]] = None,
        custom_patterns: Optional[Dict[str, str]] = None
    ) -> Tuple[Path, int]:
        """
        Redact PII from a markdown file.

        Args:
            input_path: Path to input markdown file
            output_path: Path for output file (None = overwrite)
            include: Set of PII types to include
            exclude: Set of PII types to exclude
            custom_patterns: Custom redaction patterns

        Returns:
            Tuple of (output_path, redaction_count)
        """
        # Read input file
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Redact PII
        redacted_content = self.redact_all(
            content,
            include=include,
            exclude=exclude,
            custom_patterns=custom_patterns
        )

        # Add redaction notice to document
        redaction_notice = self._generate_redaction_notice()
        redacted_content = redaction_notice + "\n\n" + redacted_content

        # Determine output path
        if output_path is None:
            output_path = input_path
        else:
            output_path = Path(output_path)

        # Write redacted content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(redacted_content)

        redaction_count = len(self.redaction_log)
        return output_path, redaction_count

    def redact_directory(
        self,
        directory: Path,
        output_dir: Optional[Path] = None,
        include: Optional[Set[str]] = None,
        exclude: Optional[Set[str]] = None,
        custom_patterns: Optional[Dict[str, str]] = None
    ) -> Dict[str, Tuple[Path, int]]:
        """
        Redact PII from all markdown files in a directory.

        Args:
            directory: Input directory
            output_dir: Output directory (None = overwrite in place)
            include: Set of PII types to include
            exclude: Set of PII types to exclude
            custom_patterns: Custom redaction patterns

        Returns:
            Dictionary mapping input files to (output_path, redaction_count)
        """
        directory = Path(directory)
        results = {}

        # Find all markdown files
        md_files = list(directory.glob('*.md'))

        for md_file in md_files:
            # Skip README and other documentation files
            if md_file.name in ['README.md', 'INSTALL.md', 'LICENSE.md']:
                continue

            # Determine output path
            if output_dir:
                output_path = Path(output_dir) / md_file.name
            else:
                output_path = None

            # Redact file
            try:
                output_path, count = self.redact_file(
                    md_file,
                    output_path,
                    include=include,
                    exclude=exclude,
                    custom_patterns=custom_patterns
                )
                results[str(md_file)] = (output_path, count)
                print(f"Redacted {count} items from {md_file.name}")

            except Exception as e:
                print(f"Error redacting {md_file}: {e}")
                results[str(md_file)] = (None, 0)

        return results

    def _generate_redaction_notice(self) -> str:
        """Generate a notice about redactions made."""
        notice = "<!--\nPII REDACTION NOTICE:\n"
        notice += f"This document has been processed to redact personally identifiable information.\n"
        notice += f"Redaction Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        notice += f"Total Redactions: {len(self.redaction_log)}\n"

        if self.redaction_log:
            # Count by type
            type_counts = {}
            for entry in self.redaction_log:
                pii_type = entry['type']
                type_counts[pii_type] = type_counts.get(pii_type, 0) + 1

            notice += "\nRedactions by Type:\n"
            for pii_type, count in sorted(type_counts.items()):
                notice += f"  - {pii_type}: {count}\n"

        notice += "-->"

        return notice

    def get_redaction_summary(self) -> Dict:
        """
        Get summary of redactions made.

        Returns:
            Dictionary with redaction statistics
        """
        summary = {
            'total_redactions': len(self.redaction_log),
            'by_type': {},
            'redaction_log': self.redaction_log if self.log_redactions else []
        }

        # Count by type
        for entry in self.redaction_log:
            pii_type = entry['type']
            summary['by_type'][pii_type] = summary['by_type'].get(pii_type, 0) + 1

        return summary

    def save_redaction_log(self, output_path: Path):
        """
        Save detailed redaction log to file.

        Args:
            output_path: Path for log file
        """
        import json

        summary = self.get_redaction_summary()

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        print(f"Redaction log saved to: {output_path}")
