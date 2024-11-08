# Intronomicon DB

This is the database dev repo for Project Intronomicon from The Korf Lab. Developed by Henry Li in collaboration with Ian Korf and Lilith Marinho-Davis.

## Background

To facilitate intron splicing research in C. elegans (and potentially other model species in the future), having a comprehensive database detailing all possible product introns would be handy. This database houses all existing C. elegans experiments published and with RUN files submitted to the SRA database on NCBI. The database is supported by SQLite. Users of this code can create the database following the steps in the [Usage](#usage) section.

## Schema

The schema of this database was designed on paper and visualized on [QuickDBD](https://app.quickdatabasediagrams.com/).

<p align="center">
  <img src="https://github.com/Vanishborn/intronomicon-db/blob/main/db_schema.png?raw=true" alt="Schema Overview by QuickDBD"/>
</p>

## Features

The following features are available:
- Error handling and logs
- Server errors handled during eSearch requests
- Avoids IP ban from repetitive eUtils pings
- Auto update each time the scripts are run
- Updates only increment new entries compared to last run
- eFetch returned SraExperimentPackage XML files are saved locally in bulk
- All downloaded SraExperimentPackage XML files are bundled and compressed into a single tar.gz
- Easily customizable for other organisms

## Dependencies

The `requests` package for Python is used to work with the E-Utilities, handling returned XML infoamation from eSearch URLs.

## Installation

### Install the requests Package

Assuming any version of Python 3 is installed, use the following command to install `requests`:

```
pip install requests
```

### Check SQLite Availability

SQLite is most likely built in on a Mac or recent Linux installations.

The following command returns the version of your SQLite installation:

```
sqlite3 --version
```

For users having trouble with `sudo`, `conda` is a great alternative. Once any type of `conda` is installed, use the following to install all dependencies:

```
conda create -n intronomicon -c conda-forge --solver libmamba python=3.12 requests sqlite
```

Once the installation is done,

```
conda activate intronomicon
```

Read more about `conda` on the [Anaconda Documentation](https://docs.anaconda.com/anaconda/).

### Clone this Repository

```
git clone https://github.com/Vanishborn/intronomicon-db.git
```

## Usage

Edit XML file download path in efetch.py to your desired directory.

Adjust other paths if necessary. Omit the '/' at the end for all paths.

**Coming soon**: Support for YAML config file

Navigate to the repo clone directory and dive into bin,

```
cd bin
```

To create the db, 

```
python3 dbgen.py
```

To perform eSearch to retrieve all PMIDs from the SRA database of NCBI and save new additions of PMIDs to additions.txt,

```
python3 esearch.py
```

To perform eFetch to download all SraExperimentPackage XML files in the additions.txt and get the bundled tar.gz file,

```
python3 efetch.py
```

To insert and update info from the XML files in additions.txt to the db,

```
python3 parsexml.py
```

The intronomicon.db is populated and any failed attempts are logged.

**Coming soon**: Realignment of SRA Run files and populating the intron table.

## License

This project is licensed under the MIT License.
