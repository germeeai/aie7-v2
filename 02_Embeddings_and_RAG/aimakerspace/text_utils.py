import os
from typing import List
import PyPDF2


class TextFileLoader:
    def __init__(self, path: str, encoding: str = "utf-8"):
        self.documents = []
        self.path = path
        self.encoding = encoding

    def load(self):
        if os.path.isdir(self.path):
            self.load_directory()
        elif os.path.isfile(self.path):
            if self.path.endswith(".txt"):
                self.load_file()
            elif self.path.endswith(".pdf"):
                self.load_pdf_file()
            else:
                raise ValueError(
                    "Provided file is neither a .txt nor .pdf file."
                )
        else:
            raise ValueError(
                "Provided path is neither a valid directory nor a supported file."
            )

    def load_file(self):
        with open(self.path, "r", encoding=self.encoding) as f:
            self.documents.append(f.read())

    def load_pdf_file(self):
        """Load text content from a PDF file using PyPDF2."""
        try:
            with open(self.path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                
                # Extract text from all pages
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text_content += page.extract_text() + "\n"
                
                if text_content.strip():  # Only add if we extracted meaningful text
                    self.documents.append(text_content)
                else:
                    print(f"Warning: No text content extracted from {self.path}")
                    
        except Exception as e:
            print(f"Error reading PDF file {self.path}: {str(e)}")
            raise

    def load_directory(self):
        for root, _, files in os.walk(self.path):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith(".txt"):
                    with open(file_path, "r", encoding=self.encoding) as f:
                        self.documents.append(f.read())
                elif file.endswith(".pdf"):
                    # Create a temporary loader for this PDF file
                    pdf_loader = TextFileLoader(file_path, self.encoding)
                    pdf_loader.load_pdf_file()
                    self.documents.extend(pdf_loader.documents)

    def load_documents(self):
        self.load()
        return self.documents


class PDFFileLoader:
    """Specialized loader for PDF files with additional metadata extraction."""
    
    def __init__(self, path: str):
        self.documents = []
        self.metadata = []
        self.path = path

    def load_pdf_with_metadata(self):
        """Load PDF content with metadata for each page."""
        try:
            with open(self.path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract document-level metadata
                doc_info = pdf_reader.metadata
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text_content = page.extract_text()
                    
                    if text_content.strip():
                        # Create metadata for this page
                        page_metadata = {
                            "source_file": self.path,
                            "page_number": page_num + 1,
                            "total_pages": len(pdf_reader.pages),
                            "document_title": doc_info.get('/Title', 'Unknown'),
                            "document_author": doc_info.get('/Author', 'Unknown'),
                            "document_subject": doc_info.get('/Subject', ''),
                            "document_creator": doc_info.get('/Creator', ''),
                            "document_producer": doc_info.get('/Producer', ''),
                            "creation_date": doc_info.get('/CreationDate', ''),
                            "modification_date": doc_info.get('/ModDate', '')
                        }
                        
                        self.documents.append(text_content)
                        self.metadata.append(page_metadata)
                        
        except Exception as e:
            print(f"Error reading PDF file {self.path}: {str(e)}")
            raise

    def load_documents(self):
        """Load documents and return them with metadata."""
        self.load_pdf_with_metadata()
        return self.documents, self.metadata


class CharacterTextSplitter:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        assert (
            chunk_size > chunk_overlap
        ), "Chunk size must be greater than chunk overlap"

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> List[str]:
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunks.append(text[i : i + self.chunk_size])
        return chunks

    def split_texts(self, texts: List[str]) -> List[str]:
        chunks = []
        for text in texts:
            chunks.extend(self.split(text))
        return chunks


if __name__ == "__main__":
    loader = TextFileLoader("data/KingLear.txt")
    loader.load()
    splitter = CharacterTextSplitter()
    chunks = splitter.split_texts(loader.documents)
    print(len(chunks))
    print(chunks[0])
    print("--------")
    print(chunks[1])
    print("--------")
    print(chunks[-2])
    print("--------")
    print(chunks[-1])
