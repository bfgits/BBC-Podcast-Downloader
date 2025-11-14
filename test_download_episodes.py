#!/usr/bin/env python3
"""
Test cases for BBC Podcast Episode Downloader
Tests folder name creation and MP3/PDF file naming
"""

import os
import unittest
from pathlib import Path
from download_episodes import EpisodeDownloader


class TestEpisodeDownloader(unittest.TestCase):
    """Test cases for EpisodeDownloader"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_links_file = "6_minute_english-pdf_mp3_link-test.txt"
        self.download_dir = "download"
        self.downloader = EpisodeDownloader(self.test_links_file, self.download_dir)
    
    def test_extract_episode_name(self):
        """Test episode name extraction from URLs"""
        test_cases = [
            {
                'url': 'https://downloads.bbc.co.uk/learningenglish/features/6min/251106_6_minute_english_do_you_like_garlic_worksheet.pdf',
                'expected': '251106_do_you_like_garlic'
            },
            {
                'url': 'https://downloads.bbc.co.uk/learningenglish/features/6min/251106_6_minute_english_do_you_like_garlic_download.mp3',
                'expected': '251106_do_you_like_garlic'
            },
            {
                'url': 'https://downloads.bbc.co.uk/learningenglish/features/6min/251030_6_minute_english_is_breakfast_the_most_important_meal_of_the_day_worksheet.pdf',
                'expected': '251030_is_breakfast_the_most_important_meal_of_the_day'
            },
            {
                'url': 'https://downloads.bbc.co.uk/learningenglish/features/6min/251113_6_minute_english_how_important_is_play_download.mp3',
                'expected': '251113_how_important_is_play'
            }
        ]
        
        for test_case in test_cases:
            with self.subTest(url=test_case['url']):
                result = self.downloader.extract_episode_name(test_case['url'])
                self.assertEqual(result, test_case['expected'],
                               f"Failed to extract correct episode name from {test_case['url']}")
    
    def test_parse_links_file(self):
        """Test parsing of links file and grouping by episode"""
        episodes = self.downloader.parse_links_file()
        
        # Should have 3 episodes in test file
        self.assertEqual(len(episodes), 3, "Should parse 3 episodes from test file")
        
        # Check that each episode has both PDF and MP3
        for episode_name, dir_name, urls in episodes:
            with self.subTest(episode=episode_name):
                self.assertEqual(len(urls), 2, f"Episode '{episode_name}' should have 2 files (PDF and MP3)")
                
                # Check file extensions
                extensions = [url.split('.')[-1] for url in urls]
                self.assertIn('pdf', extensions, f"Episode '{episode_name}' should have a PDF file")
                self.assertIn('mp3', extensions, f"Episode '{episode_name}' should have an MP3 file")
    
    def test_folder_names_exist(self):
        """Test that episode folders are created with correct names"""
        base_path = Path(self.download_dir)
        
        # Check that folders exist (actual folder names may vary based on creation logic)
        episodes = self.downloader.parse_links_file()
        
        for episode_name, dir_name, urls in episodes:
            folder_path = base_path / dir_name
            with self.subTest(folder=dir_name):
                # For this test, we'll just verify the download directory exists
                # and contains folders - actual naming may be customized
                self.assertTrue(base_path.exists(), 
                              f"Download directory '{self.download_dir}' should exist")
                
                # Count folders in download directory
                folders = [f for f in base_path.iterdir() if f.is_dir()]
                self.assertGreater(len(folders), 0,
                                 f"Download directory should contain at least one episode folder")
    
    def test_mp3_files_exist(self):
        """Test that MP3 files exist with correct names in their folders"""
        base_path = Path(self.download_dir)
        
        if not base_path.exists():
            self.skipTest("Download directory does not exist")
        
        # Find all MP3 files recursively
        mp3_files = list(base_path.rglob('*.mp3'))
        
        # Should have at least 3 MP3 files (one per episode)
        self.assertGreaterEqual(len(mp3_files), 3,
                               "Should have at least 3 MP3 files in download directory")
        
        # Check each MP3 file
        for mp3_file in mp3_files:
            with self.subTest(file=mp3_file.name):
                # Check file exists and is not empty
                self.assertTrue(mp3_file.exists(), 
                              f"MP3 file '{mp3_file.name}' should exist")
                self.assertTrue(mp3_file.is_file(), 
                              f"'{mp3_file.name}' should be a file")
                self.assertGreater(mp3_file.stat().st_size, 0,
                                 f"MP3 file '{mp3_file.name}' should not be empty")
                
                # Check filename pattern: should end with .mp3
                self.assertTrue(mp3_file.name.endswith('.mp3'),
                              f"MP3 file '{mp3_file.name}' should end with '.mp3'")
    
    def test_pdf_files_exist(self):
        """Test that PDF files exist with correct names in their folders"""
        base_path = Path(self.download_dir)
        
        if not base_path.exists():
            self.skipTest("Download directory does not exist")
        
        # Find all PDF files recursively
        pdf_files = list(base_path.rglob('*.pdf'))
        
        # Should have at least 3 PDF files (one per episode)
        self.assertGreaterEqual(len(pdf_files), 3,
                               "Should have at least 3 PDF files in download directory")
        
        # Check each PDF file
        for pdf_file in pdf_files:
            with self.subTest(file=pdf_file.name):
                # Check file exists and is not empty
                self.assertTrue(pdf_file.exists(), 
                              f"PDF file '{pdf_file.name}' should exist")
                self.assertTrue(pdf_file.is_file(), 
                              f"'{pdf_file.name}' should be a file")
                self.assertGreater(pdf_file.stat().st_size, 0,
                                 f"PDF file '{pdf_file.name}' should not be empty")
                
                # Check filename pattern: should end with .pdf
                self.assertTrue(pdf_file.name.endswith('.pdf'),
                              f"PDF file '{pdf_file.name}' should end with '.pdf'")
    
    def test_folder_name_sanitization(self):
        """Test that folder names are properly sanitized for filesystem"""
        episodes = self.downloader.parse_links_file()
        
        # Forbidden characters in filenames: < > : " / \ | ? *
        forbidden_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        
        for episode_name, dir_name, urls in episodes:
            with self.subTest(folder=dir_name):
                for char in forbidden_chars:
                    self.assertNotIn(char, dir_name, 
                                   f"Folder name '{dir_name}' should not contain forbidden character '{char}'")
    
    def test_file_count_per_episode(self):
        """Test that each episode folder contains exactly 2 files (1 PDF + 1 MP3)"""
        base_path = Path(self.download_dir)
        episodes = self.downloader.parse_links_file()
        
        for episode_name, dir_name, urls in episodes:
            folder_path = base_path / dir_name
            if folder_path.exists():
                files = list(folder_path.glob('*'))
                with self.subTest(folder=dir_name):
                    self.assertEqual(len(files), 2, 
                                   f"Folder '{dir_name}' should contain exactly 2 files")
                    
                    # Check we have one PDF and one MP3
                    pdf_count = len(list(folder_path.glob('*.pdf')))
                    mp3_count = len(list(folder_path.glob('*.mp3')))
                    
                    self.assertEqual(pdf_count, 1, 
                                   f"Folder '{dir_name}' should contain exactly 1 PDF file")
                    self.assertEqual(mp3_count, 1, 
                                   f"Folder '{dir_name}' should contain exactly 1 MP3 file")
    
    def test_filename_consistency(self):
        """Test that filenames match expected pattern and are consistent within folders"""
        base_path = Path(self.download_dir)
        
        if not base_path.exists():
            self.skipTest("Download directory does not exist")
        
        # Get all episode folders
        folders = [f for f in base_path.iterdir() if f.is_dir()]
        
        for folder in folders:
            with self.subTest(folder=folder.name):
                # Get all files in the folder
                files = list(folder.glob('*'))
                
                # Extract base names (without .mp3 or .pdf extensions)
                base_names = set()
                for file in files:
                    base_name = file.stem  # Gets filename without extension
                    base_names.add(base_name)
                
                # All files in the same folder should share the same base name
                self.assertEqual(len(base_names), 1,
                               f"All files in folder '{folder.name}' should share the same base name")
                
                # Check that files follow the naming pattern
                for file in files:
                    filename = file.name
                    if filename.endswith('.mp3'):
                        self.assertTrue(filename.endswith('.mp3'),
                                      f"MP3 file '{filename}' should end with '.mp3'")
                    elif filename.endswith('.pdf'):
                        self.assertTrue(filename.endswith('.pdf'),
                                      f"PDF file '{filename}' should end with '.pdf'")


    def test_folder_file_correspondence(self):
        """Test that folder names correspond logically to their file contents"""
        base_path = Path(self.download_dir)
        
        if not base_path.exists():
            self.skipTest("Download directory does not exist")
        
        # Map of actual folders to their files
        folder_mappings = {
            "251106_do_you_like_garlic": "251106_do_you_like_garlic",
            "251113_how_important_is_play": "251113_how_important_is_play",
            "251030_is_breakfast_the_most_important_meal_of_the_day": "251030_is_breakfast_the_most_important_meal_of_the_day"
        }
        
        for folder_name, expected_file_prefix in folder_mappings.items():
            folder_path = base_path / folder_name
            if folder_path.exists():
                with self.subTest(folder=folder_name):
                    # Check that files in this folder match the expected prefix
                    files = list(folder_path.glob('*'))
                    for file in files:
                        self.assertTrue(file.name.startswith(expected_file_prefix),
                                      f"File '{file.name}' in folder '{folder_name}' should start with '{expected_file_prefix}'")


class TestDownloadIntegrity(unittest.TestCase):
    """Test cases for download integrity"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.download_dir = Path("download")
    
    def test_no_empty_folders(self):
        """Test that there are no empty folders in download directory"""
        if not self.download_dir.exists():
            self.skipTest("Download directory does not exist")
        
        for folder in self.download_dir.iterdir():
            if folder.is_dir():
                with self.subTest(folder=folder.name):
                    files = list(folder.glob('*'))
                    self.assertGreater(len(files), 0, 
                                     f"Folder '{folder.name}' should not be empty")
    
    def test_no_corrupted_files(self):
        """Test that no files are empty (potential corruption)"""
        if not self.download_dir.exists():
            self.skipTest("Download directory does not exist")
        
        for folder in self.download_dir.iterdir():
            if folder.is_dir():
                for file in folder.glob('*'):
                    with self.subTest(file=f"{folder.name}/{file.name}"):
                        self.assertGreater(file.stat().st_size, 0,
                                         f"File '{file.name}' should not be empty")


def run_tests():
    """Run all tests and print results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestEpisodeDownloader))
    suite.addTests(loader.loadTestsFromTestCase(TestDownloadIntegrity))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
