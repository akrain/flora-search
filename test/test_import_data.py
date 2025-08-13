from unittest.mock import MagicMock, mock_open, patch

from import_data import FloraImporter
from models import Flower


class TestFloraImporter:
    """Test suite for FloraImporter class."""

    def setup_method(self):
        self.mock_chromadb_client = MagicMock()
        self.csv_file_path = "/test/path/flowers.csv"
        self.img_directory = "test_img"

    @patch("import_data.Path")
    def test_init_creates_image_directory(self, mock_path_class):
        """Test that __init__ properly initializes FloraImporter and creates image directory."""
        # Arrange
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance

        # Act
        importer = FloraImporter(
            csv_file_path=self.csv_file_path,
            chromadb_client=self.mock_chromadb_client,
            img_directory=self.img_directory,
            download_images=True
        )

        # Assert
        assert importer.csv_file_path == self.csv_file_path
        assert importer.chromadb_client == self.mock_chromadb_client
        assert importer.download_images is True
        mock_path_class.assert_called_once_with(self.img_directory)
        mock_path_instance.mkdir.assert_called_once_with(exist_ok=True)

    @patch("import_data.Path")
    def test_init_with_default_parameters(self, mock_path_class):
        """Test __init__ with default parameters."""
        # Arrange
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance

        # Act
        importer = FloraImporter(
            csv_file_path=self.csv_file_path,
            chromadb_client=self.mock_chromadb_client
        )

        # Assert
        assert importer.download_images is True
        mock_path_class.assert_called_once_with("img")

    @patch("import_data.open", new_callable=mock_open)
    @patch("import_data.requests.get")
    @patch("import_data.Path")
    def test_download_image_successful_download(self, mock_path_class, mock_requests_get, mock_file_open):
        """Test _download_image successfully downloads and saves an image."""
        # Arrange
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance

        # Setup file path mocking
        mock_file_path = MagicMock()
        mock_path_instance.__truediv__.return_value = mock_file_path
        mock_path_class.return_value.is_file.return_value = False

        # Setup requests mock
        mock_response = MagicMock()
        mock_response.content = b"fake_image_content"
        mock_requests_get.return_value = mock_response

        importer = FloraImporter(
            csv_file_path=self.csv_file_path,
            chromadb_client=self.mock_chromadb_client,
            img_directory=self.img_directory
        )

        url = "https://example.com/flower.jpg"
        filename = "test_flower_img1"

        # Act
        result = importer._download_image(url, filename)

        # Assert
        assert result == str(mock_file_path)
        mock_requests_get.assert_called_once_with(url, timeout=30)
        mock_response.raise_for_status.assert_called_once()
        mock_file_open.assert_called_once_with(mock_file_path, "wb")

    @patch("import_data.Path")
    def test_download_image_file_already_exists(self, mock_path_class):
        """Test _download_image when file already exists locally."""
        # Arrange
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance

        mock_file_path = MagicMock()
        mock_path_instance.__truediv__.return_value = mock_file_path
        mock_path_class.return_value.is_file.return_value = True

        importer = FloraImporter(
            csv_file_path=self.csv_file_path,
            chromadb_client=self.mock_chromadb_client,
            img_directory=self.img_directory
        )

        url = "https://example.com/flower.jpg"
        filename = "test_flower_img1"

        # Act
        result = importer._download_image(url, filename)

        # Assert
        assert result == str(mock_file_path)

    @patch("import_data.Path")
    def test_download_image_empty_url(self, mock_path_class):
        """Test _download_image with empty URL returns None."""
        # Arrange
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance

        importer = FloraImporter(
            csv_file_path=self.csv_file_path,
            chromadb_client=self.mock_chromadb_client,
            img_directory=self.img_directory
        )

        # Act & Assert
        assert importer._download_image("", "filename") is None
        assert importer._download_image("   ", "filename") is None
        assert importer._download_image(None, "filename") is None

    def test_create_safe_filename(self):
        """Test _create_safe_filename creates proper safe filenames."""
        # Test cases with expected results
        test_cases = [
            ("Blue Trumpet Bush", 1, "blue_trumpet_bush_img1"),
            ("Chinese Fold-wing", 2, "chinese_fold-wing_img2"),
            ("Plant with Special @#$% Characters!", 3, "plant_with_special__characters_img3"),
            ("Multiple   Spaces", 4, "multiple___spaces_img4"),
            ("UPPERCASE NAME", 1, "uppercase_name_img1"),
            ("Name_with_underscores", 2, "name_with_underscores_img2")
        ]

        for plant_name, img_num, expected in test_cases:
            result = FloraImporter._create_safe_filename(plant_name, img_num)
            assert result == expected, f"Failed for {plant_name}: expected {expected}, got {result}"

    @patch.object(FloraImporter, "_download_images")
    def test_process_row_creates_flower_and_downloads_images(self, mock_download_images):
        """Test _process_row creates Flower object and calls image download."""
        # Arrange
        importer = FloraImporter(
            csv_file_path=self.csv_file_path,
            chromadb_client=self.mock_chromadb_client
        )

        row_data = {
            "botanical_name": "Rosa damascena",
            "family": "Rosaceae",
            "url": "https://example.com/rosa",
            "common_name": "Damask Rose",
            "description": "Beautiful fragrant rose",
            "image1_url": "https://example.com/rose1.jpg",
            "image2_url": "https://example.com/rose2.jpg",
            "image3_url": "",
            "image4_url": ""
        }

        mock_image_paths = {"image1_local_uri": "/path/to/rose1.jpg"}
        mock_download_images.return_value = mock_image_paths

        # Act
        flower, image_paths = importer._process_row(row_data)

        # Assert
        assert isinstance(flower, Flower)
        assert flower.botanical_name == "Rosa damascena"
        assert flower.family == "Rosaceae"
        assert flower.common_name == "Damask Rose"
        assert flower.description == "Beautiful fragrant rose"
        assert flower.image1_url == "https://example.com/rose1.jpg"
        assert flower.image2_url == "https://example.com/rose2.jpg"

        assert image_paths == mock_image_paths
        mock_download_images.assert_called_once_with(flower)

    @patch.object(FloraImporter, "_download_image")
    @patch.object(FloraImporter, "_create_safe_filename")
    def test_download_images_processes_all_image_urls(self, mock_create_filename, mock_download_image):
        """Test _download_images processes all image URLs for a flower."""
        # Arrange
        importer = FloraImporter(
            csv_file_path=self.csv_file_path,
            chromadb_client=self.mock_chromadb_client
        )

        flower = Flower(
            botanical_name="Test Plant",
            family="Test Family",
            url="https://example.com",
            common_name="Test Flower",
            image1_url="https://example.com/img1.jpg",
            image2_url="https://example.com/img2.jpg",
            image3_url="https://example.com/img3.jpg",
            image4_url="https://example.com/img4.jpg"
        )

        mock_create_filename.side_effect = ["test_flower_img1", "test_flower_img2", "test_flower_img3",
                                            "test_flower_img4"]
        mock_download_image.side_effect = ["/path/img1.jpg", "/path/img2.jpg", "/path/img3.jpg", "/path/img4.jpg"]

        # Act
        result = importer._download_images(flower)

        # Assert
        expected_result = {
            "image1_local_uri": "/path/img1.jpg",
            "image2_local_uri": "/path/img2.jpg",
            "image3_local_uri": "/path/img3.jpg",
            "image4_local_uri": "/path/img4.jpg"
        }
        assert result == expected_result

        # Verify all image URLs were processed
        assert mock_create_filename.call_count == 4
        assert mock_download_image.call_count == 4

    def test_slice_rows_with_start_and_end(self):
        """Test _slice_rows correctly slices iterator with start and end parameters."""
        # Arrange
        test_data = [{"id": i, "name": f"flower_{i}"} for i in range(10)]

        # Test cases
        test_cases = [
            (0, 5, test_data[0:5]),
            (2, 7, test_data[2:7]),
            (5, None, test_data[5:]),
            (0, None, test_data)
        ]

        for start, end, expected in test_cases:
            result = FloraImporter._slice_rows(iter(test_data), start, end)
            assert result == expected, f"Failed for start={start}, end={end}"

    def test_join_text_fields_creates_proper_document_text(self):
        """Test _join_text_fields creates proper document text from flower data."""
        # Arrange
        flower = Flower(
            botanical_name="Rosa damascena",
            family="Rosaceae",
            url="https://example.com",
            common_name="Damask Rose",
            description="A beautiful and fragrant rose species"
        )

        # Act
        result = FloraImporter._join_text_fields(flower)

        # Assert
        expected = ("Botanical name: Rosa damascena "
                    "Common name: Damask Rose "
                    "Family: Rosaceae "
                    "Description: A beautiful and fragrant rose species")
        assert result == expected

    @patch("uuid.uuid4")
    @patch.object(FloraImporter, "_save_images")
    @patch.object(FloraImporter, "_save_to_text_collection")
    @patch.object(FloraImporter, "_join_text_fields")
    @patch.object(FloraImporter, "_process_row")
    def test_process_rows_processes_all_rows(self, mock_process_row, mock_join_text,
                                             mock_save_text, mock_save_images, mock_uuid):
        """Test _process_rows processes all rows and saves data correctly."""
        # Arrange
        importer = FloraImporter(
            csv_file_path=self.csv_file_path,
            chromadb_client=self.mock_chromadb_client
        )

        # Setup test data
        rows = [
            {"common_name": "Rose 1"},
            {"common_name": "Rose 2"}
        ]

        mock_flower1 = Flower(botanical_name="Rosa 1", family="Rosaceae",
                              url="https://test1.com", common_name="Rose 1")
        mock_flower2 = Flower(botanical_name="Rosa 2", family="Rosaceae",
                              url="https://test2.com", common_name="Rose 2")

        mock_process_row.side_effect = [
            (mock_flower1, {"image1_local_uri": "/path1.jpg"}),
            (mock_flower2, {"image1_local_uri": "/path2.jpg"})
        ]

        mock_join_text.side_effect = ["Document text 1", "Document text 2"]
        mock_uuid.side_effect = ["id1", "id2"]

        # Act
        importer._process_rows(rows, start=0)

        # Assert
        assert mock_process_row.call_count == 2
        assert mock_join_text.call_count == 2
        assert mock_save_text.call_count == 2
        assert mock_save_images.call_count == 2

    @patch("import_data.FloraTextDAO")
    def test_save_to_text_collection(self, mock_text_dao_class):
        """Test _save_to_text_collection creates DAO and adds document."""
        # Arrange
        mock_text_dao = MagicMock()
        mock_text_dao_class.return_value = mock_text_dao

        importer = FloraImporter(
            csv_file_path=self.csv_file_path,
            chromadb_client=self.mock_chromadb_client
        )

        document_id = "test-id"
        document = "Test document text"
        metadata = {"botanical_name": "Test Plant"}

        # Act
        importer._save_to_text_collection(document_id, document, metadata)

        # Assert
        mock_text_dao_class.assert_called_once_with(self.mock_chromadb_client)
        mock_text_dao.add_document.assert_called_once_with(document_id, document, metadata)

    @patch("uuid.uuid4")
    @patch.object(FloraImporter, "_save_to_image_collection")
    def test_save_images_processes_image_paths(self, mock_save_to_collection, mock_uuid):
        """Test _save_images processes image paths and calls batch save."""
        # Arrange
        importer = FloraImporter(
            csv_file_path=self.csv_file_path,
            chromadb_client=self.mock_chromadb_client
        )

        flower_id = "flower-123"
        image_paths = {
            "image1_local_uri": "/path/to/img1.jpg",
            "image2_local_uri": "/path/to/img2.jpg"
        }

        mock_uuid.side_effect = ["img-id-1", "img-id-2"]

        # Act
        importer._save_images(flower_id, image_paths)

        # Assert
        expected_document_ids = ["img-id-1", "img-id-2"]
        expected_uris = ["/path/to/img1.jpg", "/path/to/img2.jpg"]
        expected_metadata = [{"flora_id": flower_id}, {"flora_id": flower_id}]

        mock_save_to_collection.assert_called_once_with(
            expected_document_ids, expected_uris, expected_metadata
        )

    @patch("import_data.FloraImageDAO")
    def test_save_to_image_collection(self, mock_image_dao_class):
        """Test _save_to_image_collection creates DAO and adds documents in batch."""
        # Arrange
        mock_image_dao = MagicMock()
        mock_image_dao_class.return_value = mock_image_dao

        importer = FloraImporter(
            csv_file_path=self.csv_file_path,
            chromadb_client=self.mock_chromadb_client
        )

        document_ids = ["img-1", "img-2"]
        image_uris = ["/path/img1.jpg", "/path/img2.jpg"]
        metadata_list = [{"flora_id": "flower-1"}, {"flora_id": "flower-1"}]

        # Act
        importer._save_to_image_collection(document_ids, image_uris, metadata_list)

        # Assert
        mock_image_dao_class.assert_called_once_with(self.mock_chromadb_client)
        mock_image_dao.add_documents_batch.assert_called_once_with(
            document_ids=document_ids,
            uris=image_uris,
            metadata_list=metadata_list
        )

    @patch("import_data.open", new_callable=mock_open)
    @patch("import_data.csv.DictReader")
    @patch.object(FloraImporter, "_process_rows")
    @patch.object(FloraImporter, "_slice_rows")
    def test_import_data_processes_csv_file(self, mock_slice_rows, mock_process_rows,
                                            mock_dict_reader, mock_file_open):
        """Test import_data opens CSV file and processes rows correctly."""
        # Arrange
        importer = FloraImporter(
            csv_file_path=self.csv_file_path,
            chromadb_client=self.mock_chromadb_client
        )

        # Mock CSV data
        mock_reader = MagicMock()
        mock_dict_reader.return_value = mock_reader

        mock_rows = [{"name": "flower1"}, {"name": "flower2"}]
        mock_slice_rows.return_value = mock_rows

        start, end = 0, 10

        # Act
        result = importer.import_data(start=start, end=end)

        # Assert
        assert result == len(mock_rows)

        mock_file_open.assert_called_once_with(self.csv_file_path, "r", encoding="utf-8")
        mock_dict_reader.assert_called_once()
        mock_slice_rows.assert_called_once_with(mock_reader, start, end)
        mock_process_rows.assert_called_once_with(mock_rows, start)

    @patch("import_data.open", new_callable=mock_open)
    @patch("import_data.csv.DictReader")
    @patch.object(FloraImporter, "_process_rows")
    @patch.object(FloraImporter, "_slice_rows")
    def test_import_data_with_default_parameters(self, mock_slice_rows, mock_process_rows,
                                                 mock_dict_reader, mock_file_open):
        """Test import_data with default start=0 and end=None parameters."""
        # Arrange
        importer = FloraImporter(
            csv_file_path=self.csv_file_path,
            chromadb_client=self.mock_chromadb_client
        )

        mock_reader = MagicMock()
        mock_dict_reader.return_value = mock_reader

        mock_rows = [{"name": "flower1"}]
        mock_slice_rows.return_value = mock_rows

        # Act
        result = importer.import_data()

        # Assert
        assert result == 1
        mock_slice_rows.assert_called_once_with(mock_reader, 0, None)
        mock_process_rows.assert_called_once_with(mock_rows, 0)
