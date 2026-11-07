"""Interchangeable export strategies with no shared base class requirement."""

import csv
import io
import json
from collections.abc import Sequence

from book_domain.dto import BookPayload


class JsonExporter:
    def export(self, records: Sequence[BookPayload]) -> str:
        return json.dumps(list(records), ensure_ascii=False, indent=2)


class CsvExporter:
    def export(self, records: Sequence[BookPayload]) -> str:
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(
            ("id", "title", "author", "year", "pages", "publisher", "format")
        )
        for row in records:
            writer.writerow(
                (
                    row["id"],
                    row["title"],
                    row["author_name"],
                    row["year"],
                    row["pages"],
                    row["publisher"],
                    row.get("file_format", ""),
                )
            )
        return output.getvalue()
