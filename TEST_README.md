# Test Suite for BBC Podcast Downloader

## Overview
This test suite (`test_download_episodes.py`) validates the functionality of the BBC Podcast Episode Downloader, with a focus on verifying folder naming conventions and file naming patterns for downloaded MP3 and PDF files.

## Running Tests

### Prerequisites
Make sure you have the virtual environment activated and dependencies installed:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Execute Tests
Run the complete test suite:

```bash
python test_download_episodes.py
```

Or use unittest directly:

```bash
python -m unittest test_download_episodes.py -v
```

## Test Cases

### TestEpisodeDownloader Class

#### 1. `test_extract_episode_name`
- **Purpose**: Validates that episode names are correctly extracted from URLs
- **Checks**: 
  - Removes `_download` and `_worksheet` suffixes
  - Extracts the core episode identifier (date + title)
  - Works with both PDF and MP3 URLs

#### 2. `test_parse_links_file`
- **Purpose**: Verifies correct parsing of the links file
- **Checks**:
  - Correct number of episodes parsed
  - Each episode has both PDF and MP3 files
  - Files are properly grouped by episode

#### 3. `test_folder_names_exist`
- **Purpose**: Confirms that episode folders are created
- **Checks**:
  - Download directory exists
  - Contains at least one episode folder

#### 4. `test_mp3_files_exist`
- **Purpose**: Validates MP3 file presence and naming
- **Checks**:
  - At least 3 MP3 files exist
  - Files are not empty (size > 0)
  - Filenames end with `_download.mp3`

#### 5. `test_pdf_files_exist`
- **Purpose**: Validates PDF file presence and naming
- **Checks**:
  - At least 3 PDF files exist
  - Files are not empty (size > 0)
  - Filenames end with `_worksheet.pdf`

#### 6. `test_folder_name_sanitization`
- **Purpose**: Ensures folder names are filesystem-safe
- **Checks**:
  - No forbidden characters: `< > : " / \ | ? *`
  - Folder names are valid for all operating systems

#### 7. `test_file_count_per_episode`
- **Purpose**: Verifies each episode has exactly 2 files
- **Checks**:
  - Each folder contains exactly 2 files
  - One PDF and one MP3 per episode

#### 8. `test_filename_consistency`
- **Purpose**: Validates filename patterns within folders
- **Checks**:
  - All files in a folder share the same base name
  - MP3 files contain `_download.mp3`
  - PDF files contain `_worksheet.pdf`

#### 9. `test_folder_file_correspondence`
- **Purpose**: Verifies logical correspondence between folder names and file contents
- **Checks**:
  - Files in "Do You Like Garlic" start with `251106_6_minute_english_do_you_like_garlic`
  - Files in "How Important Is Play" start with `251113_6_minute_english_how_important_is_play`
  - Files in "Is Breakfast The Most Important Meal Of The Day" start with `251030_6_minute_english_is_breakfast_the_most_important_meal_of_the_day`

### TestDownloadIntegrity Class

#### 1. `test_no_empty_folders`
- **Purpose**: Ensures no empty episode folders exist
- **Checks**: Every folder in the download directory contains at least one file

#### 2. `test_no_corrupted_files`
- **Purpose**: Detects potentially corrupted downloads
- **Checks**: All files have size greater than 0 bytes

## File Naming Conventions

### Expected Patterns

**Episode Folders:**
- Format: Human-readable title case (e.g., "Do You Like Garlic")
- Characters: Alphanumeric, spaces allowed, no special characters

**MP3 Files:**
- Format: `YYMMDD_6_minute_english_episode_title_download.mp3`
- Example: `251106_6_minute_english_do_you_like_garlic_download.mp3`

**PDF Files:**
- Format: `YYMMDD_6_minute_english_episode_title_worksheet.pdf`
- Example: `251106_6_minute_english_do_you_like_garlic_worksheet.pdf`

### File Structure Example
```
download/
├── Do You Like Garlic/
│   ├── 251106_6_minute_english_do_you_like_garlic_download.mp3
│   └── 251106_6_minute_english_do_you_like_garlic_worksheet.pdf
├── How Important Is Play/
│   ├── 251113_6_minute_english_how_important_is_play_download.mp3
│   └── 251113_6_minute_english_how_important_is_play_worksheet.pdf
└── Is Breakfast The Most Important Meal Of The Day/
    ├── 251030_6_minute_english_is_breakfast_the_most_important_meal_of_the_day_download.mp3
    └── 251030_6_minute_english_is_breakfast_the_most_important_meal_of_the_day_worksheet.pdf
```

## Troubleshooting

### Test Failures

**"ModuleNotFoundError: No module named 'requests'"**
- Solution: Activate virtual environment and install dependencies
  ```bash
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

**"Download directory does not exist"**
- Solution: Run the downloader first to create test data
  ```bash
  python download_episodes.py
  ```

**File count or naming mismatches**
- Check that `6_minute_english-pdf_mp3_link-test.txt` exists and contains valid URLs
- Verify the download completed successfully
- Ensure folder and file names match the expected patterns

## Continuous Integration

These tests can be integrated into CI/CD pipelines to automatically validate:
- Correct episode parsing
- Proper file organization
- Download integrity
- Naming convention compliance

## Contributing

When adding new test cases:
1. Use descriptive test names following the pattern `test_<what_is_being_tested>`
2. Include docstrings explaining the test purpose
3. Use `self.subTest()` for parameterized tests
4. Provide clear assertion messages for debugging
