from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from src.ai.gemini_client import GeminiClient
from src.ai.roster_extractor import RosterExtractor
from src.models.roster import RosterData
from src.pdf.pdf_editor import PdfEditor

logger = logging.getLogger(__name__)


@dataclass
class ServiceResult:
    ok: bool
    message: str
    roster_data: RosterData | None = None
    output_pdf: Path | None = None


class RosterService:
    def __init__(self, extractor: RosterExtractor | None = None, editor: PdfEditor | None = None) -> None:
        self.extractor = extractor or RosterExtractor()
        self.editor = editor or PdfEditor()
        self.client = GeminiClient.from_settings()

    def can_use_gemini(self) -> bool:
        return self.client.is_configured()

    def read_handwritten_roster(
        self,
        image_paths: list[Path],
        prompt_text: str,
    ) -> ServiceResult:
        if not self.can_use_gemini():
            return ServiceResult(ok=False, message="Gemini API key not configured.")

        try:
            logger.info("Starting handwritten roster extraction for %d image(s)", len(image_paths))
            roster_data = self.extractor.extract(image_paths=image_paths, prompt_text=prompt_text)
            logger.info("Gemini extraction complete with %d staff rows", len(roster_data.staff))
            return ServiceResult(ok=True, message="Roster extracted successfully.", roster_data=roster_data)
        except NotImplementedError as exc:
            return ServiceResult(ok=False, message=str(exc))
        except Exception:
            logger.exception("Unexpected extraction failure")
            return ServiceResult(
                ok=False,
                message="Could not read handwritten roster. Please retry with a clearer image.",
            )

    def generate_pdf(
        self,
        reference_pdf: Path,
        roster_data: RosterData,
        template_id: str,
        output_pdf: Path,
    ) -> ServiceResult:
        """Generate final PDF with roster data."""
        if not template_id:
            return ServiceResult(ok=False, message="Template ID not specified.")

        try:
            logger.info("Generating PDF with template=%s", template_id)
            result_pdf = self.editor.generate_roster_pdf(
                reference_pdf=reference_pdf,
                roster_data=roster_data,
                template_id=template_id,
                output_pdf=output_pdf,
            )
            logger.info("PDF generated successfully: %s", result_pdf)
            return ServiceResult(
                ok=True,
                message="PDF generated successfully.",
                roster_data=roster_data,
                output_pdf=result_pdf,
            )
        except Exception:
            logger.exception("PDF generation failed")
            return ServiceResult(
                ok=False,
                message="Failed to generate PDF. Please check template configuration.",
            )
