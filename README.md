# Dysarthric Phone Recognition

This repository contains code and resources for recognizing phones (phonemes) in speech data, with a focus on dysarthric speech analysis. The project leverages various data sources, processing scripts, and domain-driven diagrams to facilitate research and experimentation.

## Project Structure

- **Diagram/**
	- `Domain Driven Diagram.png`: Visual representation of the project's domain and workflow.
- **Output/**
	- Contains processed data files (CSV, JSON) and graph outputs for acoustic, EMA, and phone data.
- **Praat_Scripts-master/**
	- Collection of Praat scripts and Python utilities for audio processing, annotation, and feature extraction.
- **RQ1/**
	- Python and MATLAB scripts for data analysis, DTW, k-means clustering, and feature extraction.
- **tapadm/**
	- MATLAB scripts and data for advanced signal processing and calibration.
- **Utils/**
	- Utility scripts for data conversion and preprocessing.

## Key Features

- **Speech Data Processing:**
	- Scripts for cleaning prompts, counting phones, converting CSV to JSON, and extracting features (MFCC, EMA).
- **Dynamic Time Warping (DTW):**
	- DTW-based analysis for phone and word recognition.
- **Clustering:**
	- K-means clustering for feature grouping and analysis.
- **Praat Integration:**
	- Extensive use of Praat scripts for annotation, segmentation, and feature extraction.
- **MATLAB Signal Processing:**
	- Advanced calibration and analysis scripts for EMA and acoustic data.

## Getting Started

1. **Clone the Repository:**
	 ```bash
	 git clone https://github.com/srinisam139/Dysarthric-Phone-Recognition.git
	 ```
2. **Install Dependencies:**
	 - Python: See individual script requirements (e.g., `requirements.txt` if available).
	 - MATLAB: Required for scripts in `tapadm/` and some in `RQ1/`.
	 - Praat: Required for running Praat scripts in `Praat_Scripts-master/`.
3. **Explore the Diagrams:**
	 - Refer to `Diagram/Domain Driven Diagram.png` for an overview of the workflow.
4. **Run Scripts:**
	 - See script headers and comments for usage instructions.

## Example Workflow

![Domain Driven Diagram](Diagram/Domain%20Driven%20Diagram.png)

1. **Prepare Data:**
	 - Use scripts in `Utils/` and `Praat_Scripts-master/00-Python/` to preprocess and format data.
2. **Feature Extraction:**
	 - Extract MFCC, EMA, and other features using scripts in `RQ1/` and Praat scripts.
3. **Analysis:**
	 - Perform DTW, clustering, and statistical analysis using Python and MATLAB scripts.
4. **Output Results:**
	 - Results are saved in the `Output/` directory for further review and visualization.

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements, bug fixes, or new features.

## License

See `tapadm/gpl.txt` for GPL license details.

## Contact

For questions or collaboration, contact the repository owner via GitHub.
