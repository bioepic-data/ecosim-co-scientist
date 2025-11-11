#!/usr/bin/env python
"""
Tests for the FAO HWSD fetcher.

This module provides comprehensive tests for the fetch_fao_soil_database module,
including unit tests and integration tests.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
import sys
import os

# Add scripts directory to path for importing
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from fetch_fao_soil_database import HWSDFetcher, HWSD_DATABASE_URL, HWSD_RASTER_URL


class TestHWSDFetcher(unittest.TestCase):
    """Test cases for the HWSDFetcher class."""
    
    def setUp(self):
        """Set up test fixtures with a temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.fetcher = HWSDFetcher(data_dir=self.temp_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """Test fetcher initialization."""
        # Test default initialization
        with tempfile.TemporaryDirectory() as temp_dir:
            fetcher = HWSDFetcher(data_dir=temp_dir)
            self.assertTrue(fetcher.data_dir.exists())
            self.assertEqual(str(fetcher.data_dir), temp_dir)
        
        # Test that directory is created if it doesn't exist
        non_existent = Path(self.temp_dir) / "new_dir"
        fetcher = HWSDFetcher(data_dir=str(non_existent))
        self.assertTrue(non_existent.exists())
    
    def test_url_constants(self):
        """Test that required URL constants are defined."""
        self.assertTrue(HWSD_DATABASE_URL.startswith("https://"))
        self.assertTrue(HWSD_RASTER_URL.startswith("https://"))
        self.assertTrue("HWSD" in HWSD_DATABASE_URL)
        self.assertTrue("HWSD" in HWSD_RASTER_URL)
    
    @patch('fetch_fao_soil_database.urlretrieve')
    def test_download_file(self, mock_urlretrieve):
        """Test file download functionality."""
        # Mock successful download
        mock_urlretrieve.return_value = None
        
        # Create a mock file to simulate download
        test_file = Path(self.temp_dir) / "test_file.zip"
        test_file.write_text("test content")
        
        # Patch the file size calculation
        with patch.object(Path, 'stat') as mock_stat:
            mock_stat.return_value.st_size = 1024 * 1024  # 1MB
            
            result = self.fetcher.download_file("https://example.com/test.zip", "test_file.zip")
            
            self.assertEqual(result, test_file)
            self.assertTrue(result.exists())
    
    def test_download_file_existing(self):
        """Test that existing files are not re-downloaded."""
        # Create an existing file
        test_file = Path(self.temp_dir) / "existing_file.zip"
        test_file.write_text("existing content")
        
        with patch('fetch_fao_soil_database.urlretrieve') as mock_urlretrieve:
            result = self.fetcher.download_file("https://example.com/test.zip", "existing_file.zip")
            
            # Should return existing file without downloading
            self.assertEqual(result, test_file)
            mock_urlretrieve.assert_not_called()
    
    def test_verify_checksum(self):
        """Test checksum verification."""
        # Create a test file with known content
        test_file = Path(self.temp_dir) / "test.txt"
        test_content = "test content for checksum"
        test_file.write_text(test_content)
        
        # Calculate expected SHA256 (echo -n "test content for checksum" | sha256sum)
        import hashlib
        expected = hashlib.sha256(test_content.encode()).hexdigest()
        
        # Test with correct checksum
        self.assertTrue(self.fetcher.verify_checksum(test_file, expected))
        
        # Test with incorrect checksum
        self.assertFalse(self.fetcher.verify_checksum(test_file, "incorrect_hash"))
        
        # Test with no expected checksum (should always return True)
        self.assertTrue(self.fetcher.verify_checksum(test_file))
    
    def test_find_mdb_files(self):
        """Test finding .mdb files."""
        # Create some test files
        mdb_file1 = Path(self.temp_dir) / "test1.mdb"
        mdb_file2 = Path(self.temp_dir) / "subdir" / "test2.mdb"
        other_file = Path(self.temp_dir) / "test.txt"
        
        mdb_file1.touch()
        mdb_file2.parent.mkdir(exist_ok=True)
        mdb_file2.touch()
        other_file.touch()
        
        found_files = self.fetcher.find_mdb_files()
        
        # Should find both .mdb files but not the .txt file
        self.assertEqual(len(found_files), 2)
        self.assertIn(mdb_file1, found_files)
        self.assertIn(mdb_file2, found_files)
    
    @patch('fetch_fao_soil_database.subprocess.run')
    def test_check_mdb_tools_available(self, mock_run):
        """Test checking for mdb-tools when available."""
        # Mock successful mdb-ver command
        mock_run.return_value.returncode = 0
        
        result = self.fetcher.check_mdb_tools()
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    @patch('fetch_fao_soil_database.subprocess.run')
    def test_check_mdb_tools_unavailable(self, mock_run):
        """Test checking for mdb-tools when unavailable."""
        # Mock FileNotFoundError for missing command
        mock_run.side_effect = FileNotFoundError()
        
        result = self.fetcher.check_mdb_tools()
        self.assertFalse(result)
    
    def test_extract_zip(self):
        """Test ZIP file extraction."""
        import zipfile
        
        # Create a test ZIP file
        zip_path = Path(self.temp_dir) / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("file1.txt", "content1")
            zf.writestr("subdir/file2.txt", "content2")
        
        # Extract the ZIP
        extract_dir = self.fetcher.extract_zip(zip_path)
        
        # Check extracted files
        self.assertTrue(extract_dir.exists())
        self.assertTrue((extract_dir / "file1.txt").exists())
        self.assertTrue((extract_dir / "subdir" / "file2.txt").exists())
        
        # Check file contents
        self.assertEqual((extract_dir / "file1.txt").read_text(), "content1")
        self.assertEqual((extract_dir / "subdir" / "file2.txt").read_text(), "content2")
    
    def test_get_database_info(self):
        """Test getting database information."""
        # Create some test files to simulate a populated data directory
        zip_file = Path(self.temp_dir) / "test.zip"
        pdf_file = Path(self.temp_dir) / "doc.pdf"
        mdb_file = Path(self.temp_dir) / "test.mdb"
        db_file = Path(self.temp_dir) / "test.db"
        csv_dir = Path(self.temp_dir) / "test_csv"
        
        zip_file.touch()
        pdf_file.touch()
        mdb_file.touch()
        db_file.touch()
        csv_dir.mkdir()
        
        info = self.fetcher.get_database_info()
        
        self.assertIsInstance(info, dict)
        self.assertEqual(info["data_directory"], str(Path(self.temp_dir).absolute()))
        self.assertIn(str(zip_file), info["downloaded_files"])
        self.assertIn(str(pdf_file), info["downloaded_files"])
        self.assertIn(str(mdb_file), info["mdb_files"])
        self.assertIn(str(db_file), info["sqlite_files"])
        self.assertIn(str(csv_dir), info["csv_directories"])
    
    def test_find_bil_files(self):
        """Test finding BIL files in the data directory."""
        # Create mock BIL files
        bil_file1 = Path(self.temp_dir) / "test1.bil"
        bil_file2 = Path(self.temp_dir) / "subdir" / "test2.bil"
        
        bil_file1.write_text("mock bil content")
        bil_file2.parent.mkdir(exist_ok=True)
        bil_file2.write_text("mock bil content")
        
        # Test find_bil_files method
        bil_files = self.fetcher.find_bil_files()
        
        self.assertEqual(len(bil_files), 2)
        self.assertIn(bil_file1, bil_files)
        self.assertIn(bil_file2, bil_files)
    
    def test_find_bil_files_empty(self):
        """Test finding BIL files when none exist."""
        bil_files = self.fetcher.find_bil_files()
        self.assertEqual(len(bil_files), 0)
    
    @patch('fetch_fao_soil_database.rasterio')
    def test_process_bil_to_csv_mock(self, mock_rasterio):
        """Test BIL to CSV conversion with mocked rasterio."""
        # Create mock BIL file
        bil_file = Path(self.temp_dir) / "test.bil"
        bil_file.write_text("mock bil")
        
        # Mock rasterio open context manager
        mock_src = Mock()
        mock_src.width = 3
        mock_src.height = 3
        mock_src.transform = Mock()
        mock_src.crs = "EPSG:4326"
        mock_src.nodata = -9999
        mock_src.read.return_value = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        
        mock_rasterio.open.return_value.__enter__.return_value = mock_src
        mock_rasterio.transform.xy.side_effect = lambda t, r, c: (c, r)  # Simple coordinate transform
        
        # Test processing
        csv_file = self.fetcher.process_bil_to_csv(bil_file, sample_rate=1.0)
        
        self.assertTrue(csv_file.exists())
        self.assertEqual(csv_file.suffix, ".csv")
        
        # Verify CSV content
        import pandas as pd
        df = pd.read_csv(csv_file)
        
        self.assertIn('longitude', df.columns)
        self.assertIn('latitude', df.columns)
        self.assertIn('soil_mapping_unit', df.columns)
        self.assertEqual(len(df), 9)  # 3x3 grid
    
    @patch('fetch_fao_soil_database.rasterio')
    @patch('fetch_fao_soil_database.sqlite3')
    def test_process_bil_with_soil_variables(self, mock_sqlite3, mock_rasterio):
        """Test BIL to CSV conversion with soil variable joining."""
        # Create mock BIL file
        bil_file = Path(self.temp_dir) / "test.bil"
        bil_file.write_text("mock bil")
        
        # Create mock SQLite database file
        db_file = Path(self.temp_dir) / "test.db"
        db_file.write_text("mock db")
        
        # Mock rasterio behavior
        mock_src = Mock()
        mock_src.width = 2
        mock_src.height = 2
        mock_src.transform = Mock()
        mock_src.crs = "EPSG:4326"
        mock_src.nodata = -9999
        mock_src.read.return_value = [[101, 102], [103, 104]]
        
        mock_rasterio.open.return_value.__enter__.return_value = mock_src
        mock_rasterio.transform.xy.side_effect = lambda t, r, c: (c * 0.1, r * 0.1)
        
        # Mock SQLite database behavior
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock table listing
        mock_cursor.execute.side_effect = [
            None,  # SELECT name FROM sqlite_master 
            None,  # PRAGMA table_info
            None   # SELECT query
        ]
        mock_cursor.fetchall.side_effect = [
            [('D_SOIL',), ('HWSD_META',)],  # Available tables
            [('cid', 'MU_GLOBAL', 'INTEGER'), ('cid', 'SOC', 'REAL')],  # Column info
            []  # Query result
        ]
        
        mock_sqlite3.connect.return_value = mock_conn
        
        # Mock pandas read_sql_query to return soil data for multiple tables
        import pandas as pd
        with patch('fetch_fao_soil_database.pd.read_sql_query') as mock_read_sql:
            # Mock multiple table responses for the new multi-table approach
            def mock_query_response(query, conn):
                if 'D_AWC' in query:
                    return pd.DataFrame({
                        'MU_GLOBAL': [101, 102, 103],
                        'd_awc_awc_t_percent': [15.2, 18.5, 16.1]
                    })
                elif 'D_TEXTURE' in query:
                    return pd.DataFrame({
                        'MU_GLOBAL': [101, 102, 104],
                        'd_texture_sand_percent': [45.0, 52.3, 38.7],
                        'd_texture_clay_percent': [25.5, 20.1, 32.8]
                    })
                else:
                    return pd.DataFrame()  # Empty for other tables
            
            mock_read_sql.side_effect = mock_query_response
            
            # Test conversion with database join
            csv_file = self.fetcher.process_bil_to_csv(bil_file, sample_rate=1.0, sqlite_db_path=db_file)
            
            self.assertTrue(csv_file.exists())
            self.assertEqual(csv_file.suffix, ".csv")
            
            # Verify the method was called with database path
            mock_sqlite3.connect.assert_called_with(db_file)


class TestIntegration(unittest.TestCase):
    """Integration tests for HWSD fetcher (requiring internet and mdb-tools)."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.fetcher = HWSDFetcher(data_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up integration test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @unittest.skip("Integration test - requires internet connection")
    def test_download_documentation(self):
        """Test downloading documentation (requires internet)."""
        doc_file = self.fetcher.download_documentation()
        
        self.assertTrue(doc_file.exists())
        self.assertTrue(doc_file.name.endswith(".pdf"))
        self.assertGreater(doc_file.stat().st_size, 1000)  # Should be substantial file
    
    @unittest.skip("Integration test - requires internet connection")
    def test_full_download_workflow(self):
        """Test complete download workflow (requires internet and time)."""
        # This test downloads actual files and may take several minutes
        components = self.fetcher.download_all()
        
        self.assertIn("database", components)
        self.assertIn("raster", components)
        self.assertIn("documentation", components)
        
        for component, file_path in components.items():
            self.assertTrue(file_path.exists())
            self.assertGreater(file_path.stat().st_size, 1000)


def create_mock_mdb_file():
    """
    Create a mock .mdb file for testing (obviously not a real Access database).
    
    Returns:
        Path to created mock file
    """
    import tempfile
    
    # Create a temporary file with .mdb extension
    fd, path = tempfile.mkstemp(suffix=".mdb")
    with os.fdopen(fd, 'w') as f:
        f.write("Mock MDB file content")
    
    return Path(path)


def run_basic_tests():
    """Run basic tests that don't require external dependencies."""
    # Create a test suite with only basic tests
    suite = unittest.TestSuite()
    
    # Add unit tests (no external dependencies)
    suite.addTest(unittest.makeSuite(TestHWSDFetcher))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_all_tests():
    """Run all tests including integration tests."""
    # Discover and run all tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run FAO HWSD fetcher tests")
    parser.add_argument("--integration", action="store_true", 
                       help="Run integration tests (requires internet)")
    parser.add_argument("--basic", action="store_true", default=True,
                       help="Run basic unit tests only (default)")
    
    args = parser.parse_args()
    
    if args.integration:
        print("Running all tests including integration tests...")
        success = run_all_tests()
    else:
        print("Running basic unit tests only...")
        success = run_basic_tests()
    
    if success:
        print("\n✓ All tests passed!")
        exit(0)
    else:
        print("\n✗ Some tests failed!")
        exit(1)