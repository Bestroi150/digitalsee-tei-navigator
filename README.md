# DigitalSEE: TEI Navigator

**DigitalSEE: TEI Navigator** is an interactive web application built with [Streamlit](https://streamlit.io/) that allows you to view, search, and analyze TEI (Text Encoding Initiative) XML files with ease. With its intuitive interface, you can filter XML documents by author, place, or keyword, view detailed metadata (including TEI headers, commentary sections, and editions), and download matched XML files for further analysis.

## Table of Contents

1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Folder Structure](#folder-structure)
6. [Customization](#customization)
   - [Modifying config.toml](#modifying-config.toml)
   - [Changing XML Folder Path](#changing-xml-folder-path)
7. [License](#license)
8. [Funding Statement](#funding-statement)

## Features

- **Interactive Search:** Filter and search TEI XML files by author, place name, or keyword.
- **Rich Metadata Display:** Automatically extract and display metadata from TEI headers, including title, author, publication details, and date.
- **Content Extraction:** View commentary and edition sections with syntax-highlighted XML code.
- **Downloadable Entries:** Easily download XML files that match your search criteria.
- **User-Friendly Interface:** Designed with a clean and responsive UI using Streamlit for a smooth user experience.

## Prerequisites

Before running the application, ensure you have the following installed:

- [Python 3.7+](https://www.python.org/downloads/)
- [Streamlit](https://streamlit.io/)
- [lxml](https://lxml.de/)
- (Optional) Other standard libraries: `pathlib`, `io`, and `collections` (*included with Python*)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/digitalsee-tei-lens.git
cd digitalsee-tei-lens
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install the Dependencies

```bash
pip install streamlit lxml
```

Alternatively, if a `requirements.txt` file is available, run:

```bash
pip install -r requirements.txt
```

## Usage

### 1. Prepare Your XML Files
Ensure that your TEI XML files are located in the folder `./xmls` relative to the project’s root. If your XML files are stored elsewhere, update the `xml_folder` path in the code accordingly.

### 2. Run the Application

Launch the **Streamlit** app with the following command:

```bash
streamlit run app.py
```

Replace `app.py` with the name of the Python file containing the app code.

### 3. Interact with the App

- **Search Panel:** Use the dropdown menus in the sidebar to filter XML files by author, place, or keyword.
- **View Details:** Click on an XML file entry to expand and view its TEI header, commentary, and edition sections.
- **Download Files:** Download the XML file of any matched entry using the provided download button.

## Folder Structure

An example structure for the project might look like:

```python
digitalsee-tei-lens/
│
├── xmls/                     # Folder containing TEI XML files
│   ├── file1.xml
│   ├── file2.xml
│   └── ...
│
├── app.py                     # Main Streamlit application file
└── README.md                  # This file
```

## Customization

### Modifying `config.toml`

Streamlit allows customization via a configuration file named `config.toml`. You can modify the layout, theming, and other parameters by editing or creating this file.

#### **1. Locate or Create `config.toml`**
- If it does not exist, create a new file inside `~/.streamlit/` (Linux/Mac) or `%userprofile%\.streamlit\` (Windows).

#### **2. Customize Settings**
Here’s an example `config.toml` file:

```python
[theme]
primaryColor = "#1E88E5"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

#### **3. Available Customization Options**
- **Colors:** Change `primaryColor`, `backgroundColor`, and `textColor`.
- **Sidebar:** Toggle `showSidebarNavigation`.
- **Server Settings:** Change `port` or set `headless = false` to run with a GUI.

#### **4. Apply Changes**
Restart the application for changes to take effect:

```python
streamlit run app.py
```
### Changing XML Folder Path:
If your TEI XML files are in a different directory, modify the `xml_folder` variable in the code:
    
```python
xml_folder = Path("./xmls")    
```

## License

This project is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/).

## Funding Statement

This study is financed by the European Union-NextGenerationEU, through the National Recovery and Resilience Plan of the Republic of Bulgaria, project No BG-RRP-2.004-0008.

