"""Read-only retrieval from a curated evidence corpus. Never fetch document URLs."""
import json
from pathlib import Path
from urllib.parse import urlsplit
from .schema import Evidence


class EvidenceStore:
    def __init__(self, path=None):
        self.records = []
        self.available = False
        # Explicit configuration only: neighboring demo files are not verified sources.
        target_path = path
        if target_path:
            try:
                records = json.loads(Path(target_path).read_text(encoding='utf-8-sig'))
                for row in records:
                    evidence = Evidence.model_validate(row['evidence'])
                    if urlsplit(evidence.source_url).scheme != 'https' or not evidence.excerpt.strip():
                        raise ValueError('Evidence requires an HTTPS source and excerpt')
                    self.records.append((row['claim_text'].casefold().strip(), evidence))
                self.available = True
            except (OSError, ValueError, KeyError, TypeError):
                self.records = []

    def verify(self, claim):
        if not self.available or not claim.extracted_entity:
            return claim
        matches = [e for text, e in self.records if text == claim.text.casefold().strip()
                   and e.entity.casefold().strip() == claim.extracted_entity.casefold().strip()]
        matches.sort(key=lambda e: {'authoritative': 0, 'public': 1, 'unassessed': 2}[e.source_quality])
        claim.evidence = matches
        if matches:
            relations = {e.relation for e in matches}
            claim.verification_status = next(iter(relations)) if len(relations) == 1 else 'unable_to_verify'
        else:
            claim.verification_status = 'not_corroborated'
        return claim
