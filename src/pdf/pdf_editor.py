from __future__ import annotations

import logging
from pathlib import Path

import fitz  # PyMuPDF
import yaml
from PIL import Image

from src.models.roster import RosterData
from src.pdf.coordinate_mapper import Rect

logger = logging.getLogger(__name__)


class PdfEditor:
    """Template-aware PDF editor for roster generation."""

    def __init__(self) -> None:
        self.templates_dir = Path("templates")

    def generate_roster_pdf(
        self,
        reference_pdf: Path,
        roster_data: RosterData,
        template_id: str,
        output_pdf: Path,
    ) -> Path:
        """Generate roster PDF by filling template with extracted data."""
        logger.info("Generating PDF with template=%s", template_id)

        # Load template configuration
        template = self._load_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")

        # Open reference PDF and extract as image
        with fitz.open(reference_pdf) as ref_doc:
            if ref_doc.page_count < 1:
                raise ValueError("Reference PDF is empty")
            page = ref_doc[0]

            # Render to image for overlay drawing
            zoom = 2.0  # High quality
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
            img_data = pix.tobytes("ppm")
            base_image = Image.open(fitz.Pixmap(pix).tobytes("ppm"))

        # Clear table area and fill with new data
        edited_pdf = self._edit_pdf_with_roster(
            reference_pdf,
            roster_data,
            template,
            zoom=zoom,
        )

        # Save output
        edited_pdf.save(output_pdf)
        logger.info("Generated PDF saved to %s", output_pdf)
        return output_pdf

    def _load_template(self, template_id: str) -> dict | None:
        """Load template YAML configuration."""
        template_path = self.templates_dir / f"{template_id}.yaml"
        if not template_path.exists():
            logger.warning("Template file not found: %s", template_path)
            return None

        with template_path.open("r", encoding="utf-8") as f:
            template = yaml.safe_load(f) or {}
        return template

    def _edit_pdf_with_roster(
        self,
        reference_pdf: Path,
        roster_data: RosterData,
        template: dict,
        zoom: float = 1.0,
    ) -> fitz.Document:
        """Edit PDF by clearing old data and filling new roster data."""
        doc = fitz.open(reference_pdf)
        page = doc[0]

        table_config = template.get("table", {})
        row_start_y = table_config.get("row_start_y", 170) / zoom
        row_height = table_config.get("row_height", 22) / zoom
        max_staff_rows = table_config.get("max_staff_rows", 20)

        # Clear the table area (white fill)
        table_height = row_height * max_staff_rows
        table_area = Rect(
            x0=0,
            y0=row_start_y,
            x1=page.rect.width,
            y1=row_start_y + table_height,
        )

        # Draw white rectangle to clear old entries
        white_rect = fitz.Rect(table_area.x0, table_area.y0, table_area.x1, table_area.y1)
        page.draw_rect(white_rect, color=None, fill=fitz.sRGB_white)

        # Fill in new roster data
        columns = table_config.get("columns", {})
        first_day_x = columns.get("first_day_x", 250) / zoom
        day_col_width = columns.get("day_col_width", 12) / zoom

        for row_idx, staff in enumerate(roster_data.staff[:max_staff_rows]):
            y = row_start_y + (row_idx * row_height)

            # Serial number
            self._insert_text(
                page,
                str(staff.serial_number),
                Rect(
                    columns["serial"]["x0"] / zoom,
                    y,
                    columns["serial"]["x1"] / zoom,
                    y + row_height,
                ),
            )

            # Name
            self._insert_text(
                page,
                staff.name,
                Rect(
                    columns["name"]["x0"] / zoom,
                    y,
                    columns["name"]["x1"] / zoom,
                    y + row_height,
                ),
            )

            # Post
            self._insert_text(
                page,
                staff.post,
                Rect(
                    columns["post"]["x0"] / zoom,
                    y,
                    columns["post"]["x1"] / zoom,
                    y + row_height,
                ),
            )

            # Duties for each day
            for day, duty_code in staff.duties.items():
                if day > roster_data.total_days:
                    continue
                x = first_day_x + ((day - 1) * day_col_width)
                self._insert_text(
                    page,
                    duty_code,
                    Rect(x, y, x + day_col_width, y + row_height),
                )

        logger.info("Filled %d staff rows in PDF", len(roster_data.staff))
        return doc

    @staticmethod
    def _insert_text(
        page: fitz.Page,
        text: str,
        rect: Rect,
        font_size: int = 9,
        align: int = fitz.TEXT_ALIGN_CENTER,
    ) -> None:
        """Insert text in cell with proper alignment and sizing."""
        if not text or not text.strip():
            return

        cell_rect = fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y1)

        # Try to fit text in cell
        text_rect = page.insert_textbox(
            cell_rect,
            text,
            fontsize=font_size,
            color=fitz.sRGB_black,
            align=align,
            overflow=fitz.TEXT_OVERFLOW_HIDDEN,
        )

        if text_rect == 0:
            # If text doesn't fit, reduce font size
            page.insert_textbox(
                cell_rect,
                text,
                fontsize=max(6, font_size - 2),
                color=fitz.sRGB_black,
                align=align,
                overflow=fitz.TEXT_OVERFLOW_HIDDEN,
            )
