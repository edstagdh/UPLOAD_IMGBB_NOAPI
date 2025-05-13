# UPLOAD_IMGBB_NOAPI

A Python script that automates the process of uploading images to [IMGBB](https://imgbb.com/) using Selenium, eliminating the need to use their API.
<br>
It is recommended to use on less than 10 files per run.

## 📌 Features

- Automated image uploads to IMGBB via browser automation.
- No requirement for IMGBB API keys.
- Configurable settings through `Config.json_Example` and `creds.secret_Example`.
- Supports batch image uploads.
- Saves uploaded image URLs for easy access.


## 🛣️ Roadmap

- [ ] Add support for smart file matching for better filename matching in output file

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Google Chrome browser
- ChromeDriver compatible with your Chrome version
- IMGBB Account
- IMGBB Album ID(get from URL)

### Installation

1. **Clone the repository:**

   ```
   git clone https://github.com/edstagdh/UPLOAD_IMGBB_NOAPI.git
   cd UPLOAD_IMGBB_NOAPI
   ```

2. **Install the required Python packages:**

   ```
   pip install -r Requirements.txt
   ```

3. **Set up configuration files:**

   - Rename `Config.json_Example` to `Config.json` and update the settings as needed.
   - Rename `creds.secret_Example` to `creds.secret` and add your credentials and album id

## ⚙️ Usage

1. Ensure ChromeDriver is installed and added to your system's PATH.

2. Modify the Config.json and the creds.secret files accordingly.

3. Run the script:

   ```
   python Main.py
   ```

5. Upon completion, the script will save the URLs for the uploaded images in a text file(json format) in the working path.

## 📝 Configuration

- **Config.json:**

   ```
   {
     "working_path": "path/to/your/images",
     "allowed_formats": [""],
     "ignored_files": [""],
     "link_export_types": "Direct links",
     "headless_mode": true,
   }
   ```

   - `working_path`: Directory containing images to upload.
   - `allowed_formats`: List of supported image formats on IMGBB. 
   - `ignored_files`: List of files names to ignore for upload process.
   - `link_export_types`: Type of links to export for each image, only direct links supported.
   - `headless_mode`: Flag to run Chrome in headless mode.


- **creds.secret:**

   ```
   {
     "imgbb_username": "your_username",
     "imgbb_password": "your_password"
     "imgbb_album_id": "album_id"
   }
   ```

   - `imgbb_username`: Username to use for login
   - `imgbb_password`: Password to use for login 
   - `imgbb_album_id`: ID of Album to use(get from URL)


## 📄 License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/edstagdh/UPLOAD_IMGBB_NOAPI/blob/main/LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## 📧 Contact

For any questions or suggestions, please open an issue in the repository.
