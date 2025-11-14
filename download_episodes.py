#!/usr/bin/env python3
"""
BBC Podcast Episode Downloader
Downloads PDF and MP3 files and organizes them into subdirectories by episode name
"""

import os
import re
import requests
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Tuple


class EpisodeDownloader:
    def __init__(self, links_file: str, base_download_dir: str = "download"):
        """
        Initialize the downloader
        
        Args:
            links_file: Path to the file containing download links
            base_download_dir: Base directory for downloads
        """
        self.links_file = links_file
        self.base_download_dir = Path(base_download_dir)
        self.base_download_dir.mkdir(exist_ok=True)
        
        # Headers to mimic a browser request
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Accept': '*/*'
        }
    
    def extract_episode_name(self, url: str) -> str:
        """
        Extract episode name from URL
        
        Args:
            url: Download URL
            
        Returns:
            Episode name as a clean directory name
        """
        # Extract filename from URL
        filename = os.path.basename(urlparse(url).path)
        
        # Remove file extension
        name_without_ext = os.path.splitext(filename)[0]
        
        # Remove common suffixes like '_download', '_download_', and '_worksheet' (case-insensitive)
        name_without_ext = re.sub(r'_(download_?|worksheet)$', '', name_without_ext, flags=re.IGNORECASE)
        
        # Extract the episode name including date
        # Pattern: YYMMDD_(6min_english|6_minute_english)_episode_name
        match = re.search(r'(\d{6}_(?:6min_english|6_minute_english)_.+)', name_without_ext, flags=re.IGNORECASE)
        if match:
            episode_name = match.group(1)
            # Remove _6_minute_english or _6min_english from the folder name
            episode_name = re.sub(r'_6_?min(?:ute)?_english', '', episode_name, flags=re.IGNORECASE)
            # Remove apostrophes and other problematic characters
            episode_name = episode_name.replace("'", "")
            return episode_name
        
        # Fallback: return the cleaned name as-is
        return name_without_ext
    
    def parse_links_file(self) -> List[Tuple[str, str, List[str]]]:
        """
        Parse the links file and group PDF and MP3 by episode
        
        Returns:
            List of tuples (episode_name, episode_dir, [pdf_url, mp3_url])
        """
        with open(self.links_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        episodes = {}
        
        for url in lines:
            if not url.startswith('http'):
                continue
                
            episode_name = self.extract_episode_name(url)
            
            if episode_name not in episodes:
                episodes[episode_name] = {
                    'name': episode_name,
                    'pdf': None,
                    'mp3': None
                }
            
            if url.endswith('.pdf'):
                episodes[episode_name]['pdf'] = url
            elif url.endswith('.mp3'):
                episodes[episode_name]['mp3'] = url
        
        # Convert to list format
        result = []
        for ep_name, ep_data in episodes.items():
            urls = []
            if ep_data['pdf']:
                urls.append(ep_data['pdf'])
            if ep_data['mp3']:
                urls.append(ep_data['mp3'])
            
            if urls:
                # Create episode directory name (safe for filesystem)
                # Replace apostrophes and other problematic characters
                safe_dir_name = ep_name.replace("'", "").replace("`", "")
                safe_dir_name = re.sub(r'[<>:"/\\|?*]', '', safe_dir_name)
                result.append((ep_name, safe_dir_name, urls))
        
        return result
    
    def download_file(self, url: str, save_path: Path) -> bool:
        """
        Download a file from URL to save_path
        
        Args:
            url: URL to download
            save_path: Path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"  Downloading: {os.path.basename(save_path)}")
            response = requests.get(url, headers=self.headers, stream=True, timeout=30)
            response.raise_for_status()
            
            # Write file in chunks
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            file_size = os.path.getsize(save_path)
            print(f"    ✓ Downloaded successfully ({file_size:,} bytes)")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"    ✗ Failed to download: {e}")
            return False
        except Exception as e:
            print(f"    ✗ Error: {e}")
            return False
    
    def download_episodes(self) -> Tuple[int, int, int]:
        """
        Download all episodes
        
        Returns:
            Tuple of (total_episodes, successful_downloads, failed_downloads)
        """
        episodes = self.parse_links_file()
        total_episodes = len(episodes)
        successful = 0
        failed = 0
        
        print(f"Found {total_episodes} episodes to download\n")
        
        for i, (episode_name, dir_name, urls) in enumerate(episodes, 1):
            print(f"[{i}/{total_episodes}] {episode_name}")
            
            # Create episode directory
            episode_dir = self.base_download_dir / dir_name
            episode_dir.mkdir(exist_ok=True)
            
            # Download each file for this episode
            episode_success = True
            for url in urls:
                filename = os.path.basename(urlparse(url).path)
                
                # Clean filename by removing _download, _worksheet, and _6_minute_english
                # Also handle apostrophes and other special characters
                clean_filename = filename.replace('_download.mp3', '.mp3').replace('_worksheet.pdf', '.pdf')
                clean_filename = clean_filename.replace('_download_.mp3', '.mp3')  # Handle trailing underscore
                clean_filename = clean_filename.replace('_6_minute_english', '')
                clean_filename = clean_filename.replace("'", "")  # Remove apostrophes from filename
                save_path = episode_dir / clean_filename
                
                # Skip if file already exists
                if save_path.exists():
                    print(f"  Skipping: {clean_filename} (already exists)")
                    continue
                
                if not self.download_file(url, save_path):
                    episode_success = False
                    failed += 1
                else:
                    successful += 1
            
            if episode_success:
                print(f"  ✓ Episode complete\n")
            else:
                print(f"  ⚠ Episode completed with errors\n")
        
        return total_episodes, successful, failed
    
    def run(self):
        """Main execution method"""
        print("=" * 60)
        print("BBC Podcast Episode Downloader")
        print("=" * 60)
        print(f"Links file: {self.links_file}")
        print(f"Download directory: {self.base_download_dir.absolute()}")
        print("=" * 60 + "\n")
        
        total, successful, failed = self.download_episodes()
        
        print("=" * 60)
        print("Download Summary")
        print("=" * 60)
        print(f"Total episodes: {total}")
        print(f"Successful downloads: {successful}")
        print(f"Failed downloads: {failed}")
        print(f"Download directory: {self.base_download_dir.absolute()}")
        print("=" * 60)


def main():
    """Main entry point"""
    # Configuration
    LINKS_FILE = "6_minute_english-pdf_mp3_link-test.txt"
    DOWNLOAD_DIR = "download"
    
    # Check if links file exists
    if not os.path.exists(LINKS_FILE):
        print(f"Error: Links file '{LINKS_FILE}' not found!")
        print("Please ensure the file exists in the current directory.")
        return
    
    # Create downloader and run
    downloader = EpisodeDownloader(LINKS_FILE, DOWNLOAD_DIR)
    downloader.run()


if __name__ == "__main__":
    main()
