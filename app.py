from __future__ import annotations

import logging
from pathlib import Path

import streamlit as st

from config.settings import get_settings
from src.pdf.pdf_renderer import render_pdf_preview
from src.pdf.template_detector import suggest_template_from_pdf
from src.services.roster_service import RosterService
from src.utils.file_utils import ensure_temp_dir, write_uploaded_file
from src.utils.image_utils import preprocess_image_for_ai


def setup_logging() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def load_prompt() -> str:
    path = Path("prompts") / "roster_extraction_prompt.txt"
    return path.read_text(encoding="utf-8")


def template_choice_to_id(value: str) -> str | None:
    mapping = {
        "Auto Detect": None,
        "Nursing Officer": "nursing_officer",
        "Ward Boy / Aya": "ward_boy_aya",
        "Other": "other",
    }
    return mapping[value]


def main() -> None:
    setup_logging()

    st.set_page_config(
        page_title="Duty Roster Generator",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    st.title("🏥 Hospital Duty Roster Generator")
    st.markdown(
        "Convert handwritten duty rosters to clean, professional PDFs in seconds. "
        "Perfect for hospital staff scheduling."
    )

    # Initialize session state
    if "extracted_roster" not in st.session_state:
        st.session_state.extracted_roster = None
    if "reference_pdf_path" not in st.session_state:
        st.session_state.reference_pdf_path = None
    if "template_id" not in st.session_state:
        st.session_state.template_id = None

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 📋 Step 1: Reference Template")
        st.markdown("Choose the template type or let us auto-detect from your PDF")
        selected_template = st.selectbox(
            "Template Type",
            options=["Auto Detect", "Nursing Officer", "Ward Boy / Aya", "Other"],
            index=0,
            help="Select the roster template that matches your hospital's format",
        )

        st.markdown("### 📄 Step 2: Upload Reference PDF")
        st.markdown("Upload a clean reference PDF to use as the template base")
        reference_pdf = st.file_uploader(
            "Reference PDF",
            type=["pdf"],
            help="This PDF will be used as a template for the output",
        )

    with col2:
        st.markdown("### 📸 Step 3: Upload Handwritten Photo")
        st.markdown("Take a clear photo of the handwritten roster")
        images = st.file_uploader(
            "Handwritten Image(s)",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
            help="Clear, straight-on photos work best. Avoid shadows and glare.",
        )

    st.divider()

    # Main action button
    col_center1, col_center2, col_center3 = st.columns([1, 1, 1])
    with col_center2:
        extract_clicked = st.button(
            "🔍 Extract Roster Data",
            type="primary",
            use_container_width=True,
            key="extract_btn",
        )

    if extract_clicked:
        if reference_pdf is None:
            st.error("❌ Please upload a reference PDF first.")
            return

        if not images:
            st.error("❌ Please upload at least one handwritten roster image.")
            return

        service = RosterService()
        if not service.can_use_gemini():
            st.error(
                "❌ Gemini API key not configured. "
                "Please set up the GEMINI_API_KEY in your Streamlit secrets."
            )
            return

        temp_dir = ensure_temp_dir()

        with st.status("Processing roster...", expanded=True) as status:
            # Save reference PDF
            st.session_state.reference_pdf_path = write_uploaded_file(
                temp_dir, reference_pdf.name, reference_pdf.getvalue()
            )

            # Detect template if needed
            resolved_template_id = template_choice_to_id(selected_template)
            if resolved_template_id is None:
                status.write("🔎 Auto-detecting template from PDF...")
                detected = suggest_template_from_pdf(st.session_state.reference_pdf_path, Path("templates"))
                if detected:
                    resolved_template_id = detected
                    status.write(f"✅ Template detected: {detected}")
                else:
                    st.warning(
                        "⚠️ Could not auto-detect template. Please select the closest matching template "
                        "and try again."
                    )
                    status.update(label="Template detection failed", state="error")
                    return

            st.session_state.template_id = resolved_template_id

            # Process images
            status.write(f"📸 Processing {len(images)} image(s)...")
            saved_images: list[Path] = []
            settings = get_settings()

            for idx, upload in enumerate(images, start=1):
                raw_path = write_uploaded_file(
                    temp_dir, f"raw_{idx}_{upload.name}", upload.getvalue()
                )
                proc_path = temp_dir / f"proc_{idx}_{upload.name}"
                preprocess_image_for_ai(raw_path, proc_path, max_side=settings.max_image_side)
                saved_images.append(proc_path)

            # Extract roster using Gemini
            status.write("🤖 Extracting data with Gemini Vision...")
            result = service.read_handwritten_roster(saved_images, load_prompt())

            if not result.ok:
                st.error(f"❌ {result.message}")
                status.update(label="Extraction failed", state="error")
                return

            roster = result.roster_data
            assert roster is not None

            st.session_state.extracted_roster = roster
            status.update(label="✅ Roster extracted successfully!", state="complete")

        # Display extraction summary
        st.success(
            f"✅ Roster extracted successfully!\n\n"
            f"📅 **Month:** {roster.month}/{roster.year} | "
            f"**Days:** {roster.total_days} | "
            f"**Staff:** {len(roster.staff)}"
        )

        # Display uncertain cells warning if any
        if roster.uncertain_cells:
            with st.warning(f"⚠️ {len(roster.uncertain_cells)} uncertain cell(s) detected"):
                for cell in roster.uncertain_cells:
                    st.write(
                        f"- {cell.staff_name} (Day {cell.day}): "
                        f"'{cell.detected_value}' — {cell.reason}"
                    )

    # Show extraction results if available
    if st.session_state.extracted_roster:
        st.divider()
        st.markdown("### 👀 Preview Extracted Roster")

        roster = st.session_state.extracted_roster
        tab1, tab2 = st.tabs(["Staff Table", "Details"])

        with tab1:
            # Display roster table
            roster_data = []
            for staff in roster.staff:
                row = {
                    "S.N.": staff.serial_number,
                    "Name": staff.name,
                    "Post": staff.post,
                }
                for day in range(1, roster.total_days + 1):
                    row[f"D{day}"] = roster.staff[roster.staff.index(staff)].duties.get(day, "")
                roster_data.append(row)

            st.dataframe(roster_data, use_container_width=True, height=400)

        with tab2:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Hospital", roster.hospital_name or "—")
            col2.metric("Month/Year", f"{roster.month}/{roster.year}")
            col3.metric("Total Days", roster.total_days)
            col4.metric("Staff Count", len(roster.staff))

        st.divider()
        st.markdown("### 📄 Generate Final PDF")

        # Generate PDF button
        if st.button("✨ Generate PDF", type="primary", use_container_width=True, key="generate_pdf"):
            if not st.session_state.reference_pdf_path or not st.session_state.template_id:
                st.error("❌ Missing reference PDF or template ID. Please start over.")
                return

            with st.status("Generating PDF...", expanded=True) as status:
                try:
                    temp_dir = ensure_temp_dir()
                    output_pdf = temp_dir / "roster_output.pdf"

                    service = RosterService()
                    pdf_result = service.generate_pdf(
                        reference_pdf=st.session_state.reference_pdf_path,
                        roster_data=roster,
                        template_id=st.session_state.template_id,
                        output_pdf=output_pdf,
                    )

                    if not pdf_result.ok:
                        st.error(f"❌ {pdf_result.message}")
                        status.update(label="PDF generation failed", state="error")
                        return

                    status.write("📄 Rendering preview...")
                    preview_path = temp_dir / "preview.png"
                    render_pdf_preview(output_pdf, preview_path)

                    status.update(label="✅ PDF generated!", state="complete")

                    # Show preview
                    st.markdown("#### Preview")
                    preview_image = st.image(preview_path, use_column_width=True)

                    # Download button
                    with open(output_pdf, "rb") as f:
                        pdf_bytes = f.read()

                    st.download_button(
                        label="⬇️ Download PDF",
                        data=pdf_bytes,
                        file_name=f"roster_{roster.month}_{roster.year}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

                    st.success("✅ PDF ready for download!")

                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")
                    status.update(label="Error", state="error")
                    import logging

                    logging.exception("PDF generation error")


if __name__ == "__main__":
    main()
