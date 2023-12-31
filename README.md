
# IPTV Playlist Generator

This is a Flask-based IPTV Playlist Generator that fetches video URLs from YouTube and other sources and generates an M3U playlist file. It allows users to add, update, and delete channels, as well as manage external M3U links. The generated playlist can be downloaded and used with media players that support IPTV.

## Prerequisites

- Python 3.6 or higher
- yt_dlp library
- Flask library
- SQLite3

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/SriramTalasila/YTtoM3U.git
   ```

2. Install the required dependencies:
   ```
   pip install yt_dlp Flask
   ```

3. Initialize the SQLite database:
   ```
   sqlite3 database.sqlite < schema.sql
   ```

## Usage

1. Run the Flask application:
   ```
   python app.py
   ```

2. Access the application in your web browser:
   ```
   http://localhost:5000/
   ```

3. Use the web interface to add, update, or delete channels. Channels can be either YouTube videos or direct video URLs.

4. The generated M3U playlist can be downloaded by accessing the following URLs:
   ```
   http://localhost:5000/all_channels.m3u
   http://localhost:5000/playlist/allchannels.m3u
   ```

5. The application also supports external M3U links. You can add, update, or delete them using the provided endpoints.

## License


