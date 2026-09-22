from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader
)

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)


class DocumentService:

    ALLOWED_EXTENSIONS = {
        ".pdf",
        ".txt"
    }

    def __init__(self):

        self.upload_directory = Path(
            "data/uploads"
        )

        self.upload_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        self.text_splitter = (
            RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=150
            )
        )

    def save_file(
        self,
        filename: str,
        content: bytes
    ) -> Path:

        file_path = (
            self.upload_directory /
            filename
        )

        with open(
            file_path,
            "wb"
        ) as file:

            file.write(content)

        return file_path

    def load_document(
        self,
        file_path: Path
    ):

        extension = (
            file_path.suffix.lower()
        )

        if extension == ".pdf":

            loader = PyPDFLoader(
                str(file_path)
            )

        elif extension == ".txt":

            loader = TextLoader(
                str(file_path),
                encoding="utf-8"
            )

        else:

            raise ValueError(
                "Only PDF and TXT files are supported."
            )

        documents = loader.load()

        chunks = self.text_splitter.split_documents(
            documents
        )

        return chunks


document_service = DocumentService()