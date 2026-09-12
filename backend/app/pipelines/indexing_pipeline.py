from pathlib import Path
import re

import fitz

from haystack import Document

from backend.app.components.embedding_service import (
    embed_documents,
)

from backend.app.haystack_store import (
    document_store,
)


TARGET_CHUNK_SIZE = 1200
MAX_CHUNK_SIZE = 1600
MIN_CHUNK_SIZE = 300
OVERLAP = 150


def clean_text(
    text: str,
) -> str:

    text = text.replace(
        "\r\n",
        "\n",
    )

    text = text.replace(
        "\r",
        "\n",
    )

    # Remove standalone page numbers
    text = re.sub(
        r"(?m)^\s*\d+\s*$",
        "",
        text,
    )

    # Normalize bullets
    text = re.sub(
        r"[•●▪◦]",
        "-",
        text,
    )

    # Normalize spaces
    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    # Normalize excessive newlines
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


def split_long_text(
    text: str,
    max_size: int = MAX_CHUNK_SIZE,
) -> list[str]:

    if len(text) <= max_size:
        return [
            text.strip()
        ]

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    pieces = []

    current = ""

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        if len(sentence) > max_size:

            if current:

                pieces.append(
                    current.strip()
                )

                current = ""

            start = 0

            while start < len(sentence):

                end = min(
                    start + max_size,
                    len(sentence),
                )

                pieces.append(
                    sentence[
                        start:end
                    ].strip()
                )

                if end >= len(sentence):
                    break

                start = end - OVERLAP

        elif (
            len(current)
            + len(sentence)
            + 1
            <= max_size
        ):

            current = (
                f"{current} {sentence}"
                if current
                else sentence
            )

        else:

            pieces.append(
                current.strip()
            )

            current = sentence

    if current:

        pieces.append(
            current.strip()
        )

    return pieces


def build_chunks(
    text: str,
) -> list[str]:

    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(
            r"\n\s*\n",
            text,
        )
        if paragraph.strip()
    ]

    expanded = []

    for paragraph in paragraphs:

        expanded.extend(
            split_long_text(
                paragraph
            )
        )

    chunks = []

    current = ""

    for paragraph in expanded:

        if (
            current
            and len(current)
            + len(paragraph)
            + 2
            <= TARGET_CHUNK_SIZE
        ):

            current += (
                "\n\n"
                + paragraph
            )

            continue

        if current:

            chunks.append(
                current.strip()
            )

        current = paragraph

    if current:

        chunks.append(
            current.strip()
        )

    final_chunks = []

    for index, chunk in enumerate(
        chunks
    ):

        if index == 0:

            final_chunks.append(
                chunk
            )

            continue

        previous = chunks[
            index - 1
        ]

        overlap_text = previous[
            -OVERLAP:
        ].strip()

        combined = (
            f"{overlap_text}\n\n{chunk}"
        )

        if len(combined) <= MAX_CHUNK_SIZE:

            final_chunks.append(
                combined
            )

        else:

            final_chunks.append(
                chunk
            )

    return [
        chunk.strip()
        for chunk in final_chunks
        if len(chunk.strip())
        >= MIN_CHUNK_SIZE
    ]


def ingest_pdf(
    file_path: str,
    subject="Not Specified",
    course="Not Specified",
    document_type="Academic Document",
) -> int:

    pdf = fitz.open(
        file_path
    )

    documents = []

    for page_number, page in enumerate(
        pdf,
        start=1,
    ):

        raw_text = page.get_text()

        if not raw_text.strip():
            continue

        cleaned_text = clean_text(
            raw_text
        )

        if not cleaned_text:
            continue

        chunks = build_chunks(
            cleaned_text
        )

        for chunk_number, chunk in enumerate(
            chunks,
            start=1,
        ):

            documents.append(
                Document(
                    content=chunk,
                    meta={
                        "source": Path(
                            file_path
                        ).name,

                        "page_number":
                            page_number,

                        "chunk_number":
                            chunk_number,

                        "subject":
                            subject,

                        "course":
                            course,

                        "document_type":
                            document_type,
                    },
                )
            )

    pdf.close()

    if not documents:
        return 0

    embeddings = embed_documents(
        [
            document.content
            for document in documents
        ]
    )

    for document, embedding in zip(
        documents,
        embeddings,
    ):

        document.embedding = embedding

    document_store.write_documents(
        documents
    )

    return len(documents)