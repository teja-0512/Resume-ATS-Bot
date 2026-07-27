import os
import fitz  # PyMuPDF
from docx import Document


class ResumeParser:
    """
    Resume Parser
    Supports:
        - PDF
        - DOCX
    """

    @staticmethod
    def extract_pdf(file_path: str) -> str:
        """
        Extract text from a PDF file.
        """

        try:
            document = fitz.open(file_path)

            text = ""

            for page in document:
                text += page.get_text()

            document.close()

            return text.strip()

        except Exception as e:
            raise Exception(f"Failed to extract PDF text.\n{e}")

    @staticmethod
    def extract_docx(file_path: str) -> str:
        """
        Extract text from a DOCX file.
        """

        try:
            document = Document(file_path)

            text = ""

            for paragraph in document.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"

            return text.strip()

        except Exception as e:
            raise Exception(f"Failed to extract DOCX text.\n{e}")

    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Detect file type and extract text.
        """

        extension = os.path.splitext(file_path)[1].lower()

        if extension == ".pdf":
            return ResumeParser.extract_pdf(file_path)

        elif extension == ".docx":
            return ResumeParser.extract_docx(file_path)

        else:
            raise Exception("Unsupported file format. Please upload PDF or DOCX.")

    @staticmethod
    def get_resume_sections(text: str) -> dict:
        """
        Extract common resume sections.
        """

        sections = {
            "summary": "",
            "education": "",
            "skills": "",
            "experience": "",
            "projects": "",
            "certifications": "",
            "others": ""
        }

        current_section = "others"

        headings = {
            "summary": "summary",
            "professional summary": "summary",
            "profile": "summary",

            "education": "education",
            "academic": "education",

            "skills": "skills",
            "technical skills": "skills",

            "experience": "experience",
            "work experience": "experience",
            "employment": "experience",

            "projects": "projects",
            "project": "projects",

            "certifications": "certifications",
            "certification": "certifications"
        }

        lines = text.splitlines()

        for line in lines:

            clean = line.strip().lower()

            if clean in headings:
                current_section = headings[clean]
                continue

            sections[current_section] += line + "\n"

        return sections

    @staticmethod
    def parse_resume(file_path: str) -> dict:
        """
        Returns structured resume data.
        """

        text = ResumeParser.extract_text(file_path)

        sections = ResumeParser.get_resume_sections(text)

        return {
            "text": text,
            "sections": sections
        }