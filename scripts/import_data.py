import argparse
import csv
import typing
import uuid
from pathlib import Path
from typing import Dict, Optional

import requests
from chromadb import ClientAPI

import chroma
from chroma import FloraTextDAO, FloraImageDAO
from models import Flower


class FloraImporter:
    """Import flora data from CSV, download associated images and save the data to ChromaDB."""

    def __init__(self, csv_file_path: str, chromadb_client: ClientAPI, img_directory: str = "img",
                 download_images: bool = True):
        self.csv_file_path = csv_file_path
        self.img_directory = Path(img_directory)
        self.img_directory.mkdir(exist_ok=True)
        self.chromadb_client = chromadb_client
        self.download_images = download_images

    def _download_image(self, url: str, filename: str) -> Optional[str]:
        if not url or url.strip() == "":
            return None

        try:
            file_path = self.img_directory / f"{filename}{'.jpg'}"
            if not Path(file_path).is_file():
                print(f"Downloading image with URL: {url}")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                with open(file_path, 'wb') as f:
                    f.write(response.content)
            return str(file_path)
        except Exception as e:
            print(f"Failed to download image from {url}: {e}")
            return None

    @staticmethod
    def _create_safe_filename(name: str, image_num: int) -> str:
        # Remove special characters and spaces, convert to lowercase
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_').lower()
        return f"{safe_name}_img{image_num}"

    def _process_row(self, row: Dict[str, str]) -> tuple[Flower, dict[str, str]]:
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

    def _download_images(self, flower) -> dict[str, str]:
        image_paths = {}
        for i, image_url in enumerate(
                [flower.image1_url, flower.image2_url, flower.image3_url, flower.image4_url], 1
        ):
            if image_url:
                filename = self._create_safe_filename(flower.common_name, i)
                downloaded_path = self._download_image(image_url, filename)
                if downloaded_path:
                    image_paths[f"image{i}_local_uri"] = downloaded_path
        return image_paths

    @staticmethod
    def _slice_rows(reader: typing.Iterable, start: int, end: int) -> list:
        rows = list(reader)
        # Apply start/end slicing
        if end is not None:
            rows = rows[start:end]
        else:
            rows = rows[start:]
        return rows

    @staticmethod
    def _join_text_fields(flower):
        document_text = f"Botanical name: {flower.botanical_name} " \
                        f"Common name: {flower.common_name} " \
                        f"Family: {flower.family} " \
                        f"Description: {flower.description}"
        return document_text

    def _process_rows(self, rows, start):
        for i, row in enumerate(rows):
            flower, local_image_paths = self._process_row(row)
            document_text = self._join_text_fields(flower)
            flower_id = str(uuid.uuid4())
            metadata = vars(flower)
            metadata.update(local_image_paths)
            # Write to the expected collections for tests
            self._save_to_text_collection(flower_id, document_text, metadata)
            self._save_images(flower_id, local_image_paths)
            print(f"Processed {start + i}: {flower.common_name}")

    def _save_to_new_text_collection(self, document_id, document, metadata):
        from chroma import FloraTextOnlyDAO
        text_collection = FloraTextOnlyDAO(self.chromadb_client)
        text_collection.add_document(document_id, document, metadata)

    def _save_to_text_collection(self, document_id, document, metadata):
        text_collection = FloraTextDAO(self.chromadb_client)
        text_collection.add_document(document_id, document, metadata)

    def _save_images(self, flower_id, image_paths: Dict[str, str]):
        """Save all images paths for a flower in the DB"""

        document_ids, uris, metadata_list = [], [], []
        for path in image_paths.values():
            document_ids.append(str(uuid.uuid4()))
            uris.append(path)
            metadata_list.append({"flora_id": flower_id})
        self._save_to_image_collection(document_ids, uris, metadata_list)

    def _save_to_image_collection(self, document_ids, image_uris, metadata_list):
        image_collection = FloraImageDAO(self.chromadb_client)
        image_collection.add_documents_batch(
            document_ids=document_ids,
            uris=image_uris,
            metadata_list=metadata_list
        )

    def import_data(self, start: int = 0, end: Optional[int] = None) -> int:
        """ Reads the CSV file and processes each row into a flower and its images """

        print(f"Starting import from {self.csv_file_path}")
        with open(self.csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = self._slice_rows(reader, start, end)
            self._process_rows(rows, start)
            return len(rows)


def main():
    parser = argparse.ArgumentParser(description='Imports flower data from a CSV file to ChromaDB')
    parser.add_argument('csv_file', nargs='?', default='foi_himalayan_flowers.csv',
                        help='Path to the CSV file (default: foi_himalayan_flowers.csv)')
    parser.add_argument('--start', type=int, default=0, help='Start row index (default: 0)')
    parser.add_argument('--end', type=int, help='End row index (optional)')
    parser.add_argument('--no-download', action='store_true',
                        help='Skip downloading images that already exist locally')

    args = parser.parse_args()

    chromadb_client = chroma.client(persistent=True, path="../src/chroma")
    importer = FloraImporter(args.csv_file, chromadb_client, download_images=not args.no_download)
    num_imported = importer.import_data(start=args.start, end=args.end)
    print(f"Import complete! {num_imported} entries added to DB.")


if __name__ == "__main__":
    main()
