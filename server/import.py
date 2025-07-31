import csv
import os
import typing

import requests
import argparse
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import hashlib
from pathlib import Path
from models import Flower


class FloraImporter:
    """Import flora data from CSV, download associated images and save the data to ChromaDB."""
    
    def __init__(self, csv_file_path: str, img_directory: str = "img", download_images: bool = True):
        self.csv_file_path = csv_file_path
        self.img_directory = Path(img_directory)
        self.img_directory.mkdir(exist_ok=True)
        self.chroma_handler = None
        self.download_images = download_images


    def _download_image(self, url: str, filename: str) -> Optional[str]:
        if not url or url.strip() == "":
            return None

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            file_path = self.img_directory / f"{filename}{'.jpg'}"
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return str(file_path)
        except Exception as e:
            print(f"Failed to download image from {url}: {e}")
            return None

    @staticmethod
    def _create_filename_from_name(name: str, image_num: int) -> str:
        # Remove special characters and spaces, convert to lowercase
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_').lower()
        return f"{safe_name}_img{image_num}"

    def _process_row(self, row: Dict[str, str]) -> tuple[Flower, List[str]]:
        """Process a single CSV row and download images."""

        # Create Flower object from CSV row
        flower = Flower(
            botanical_name=row.get('botanical_name'),
            family=row.get('family'),
            url=row.get('url'),
            common_name=row.get('common_name'),
            description=row.get('description'),
            image1_url=row.get('image1_url'),
            image2_url=row.get('image2_url', ""),
            image3_url=row.get('image3_url', ""),
            image4_url=row.get('image4_url', "")
        )
        # Download images if enabled
        image_paths = self._download_images(flower)
        return flower, image_paths

    def _download_images(self, flower):
        image_paths = []
        if self.download_images:
            for i, image_url in enumerate(
                    [flower.image1_url, flower.image2_url, flower.image3_url, flower.image4_url], 1
            ):
                if image_url:
                    filename = self. _create_filename_from_name(flower.common_name, i)
                    downloaded_path = self._download_image(image_url, filename)
                    if downloaded_path:
                        image_paths.append(downloaded_path)
        return image_paths

    def import_data(self, start: int = 0, end: Optional[int] = None) -> None:

        print(f"Starting import from {self.csv_file_path}")
        documents, document_ids, metadata_list = [], [], []

        with open(self.csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = self._slice_rows(reader, start, end)

            print(f"Processing rows {start} to {start + len(rows)} (total: {len(rows)} rows)")
            for i, row in rows:
                flower, image_paths = self._process_row(row)
                document_text = f"{flower.botanical_name} {flower.common_name} {flower.description}"
                # Create unique document ID
                document_id = hashlib.md5((flower.botanical_name + flower.common_name).encode()).hexdigest()
                metadata = vars(flower)
                documents.append(document_text)
                document_ids.append(document_id)
                metadata_list.append(metadata)

                print(f"Processed {start + i + 1}: {flower.botanical_name}")

        self._save_to_db(document_ids, documents, metadata_list)
        print(f"Import completed! {len(documents)} flora entries added to ChromaDB.")

    def _save_to_db(self, document_ids, documents, metadata_list):
        if self.chroma_handler is None:
            print("ChromaDB not configured yet")
            return
        print(f"Adding {len(documents)} documents to ChromaDB...")
        self.chroma_handler.add_documents_batch(
            document_ids=document_ids,
            texts=documents,
            metadatas=metadata_list
        )

    @staticmethod
    def _slice_rows(reader: typing.Iterable, start: int, end: int) -> list:
        rows = list(reader)
        # Apply start/end slicing
        if end is not None:
            rows = rows[start:end]
        else:
            rows = rows[start:]
        return rows


def main():
    parser = argparse.ArgumentParser(description='Imports flower data from a CSV file to ChromaDB')
    parser.add_argument('csv_file', nargs='?', default='foi_himalayan_flowers.csv', help='Path to the CSV file (default: foi_himalayan_flowers.csv)')
    parser.add_argument('--start', type=int, default=0, help='Start row index (default: 0)')
    parser.add_argument('--end', type=int, help='End row index (optional)')
    parser.add_argument('--no-download', action='store_true', help='Skip downloading images')
    
    args = parser.parse_args()

    importer = FloraImporter(args.csv_file, download_images=not args.no_download)
    importer.import_data(start=args.start, end=args.end)


if __name__ == "__main__":
    main()