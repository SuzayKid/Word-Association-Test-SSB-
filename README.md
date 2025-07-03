# SSB Word Association Test (WAT)

A fullscreen Word Association Test (WAT) application built with Python and Pygame to help candidates prepare for the SSB psychological tests. This tool displays a series of words for a fixed duration, allowing users to practice forming sentences under time constraints.

## Features

- **Fullscreen Display**: Provides an immersive, distraction-free experience.
- **Timed Word Sessions**: Displays 60 words per session, each for a configurable amount of time (defaults to 15-20 seconds).
- **Progress Tracking**: Automatically tracks which words have been shown and ensures all words are eventually displayed.
- **Customizable Word Lists**: Easily add, remove, or modify words by editing the `wat.csv` file.
- **Audio Cues**: Plays a bell sound at the start of each word and session, with a fallback beep if the sound file is missing.
- **Pause and Resume**: Allows pausing the test at any time.
- **Multiple Difficulty Levels**: Includes different Python scripts (`wat.py`, `easy.py`, etc.) with varying time limits per word.

## Requirements

- Python 3.x
- Pygame library

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repository-name.git
    cd your-repository-name
    ```

2.  **Install Pygame:**
    ```bash
    pip install pygame
    ```

## Usage

To run the application, execute one of the Python scripts. `wat.py` is the standard version.

```bash
python wat.py
```

### Other Versions

-   `easy.py`: A version with a longer duration per word (20 seconds).
-   `tab.py`: A version with robust path handling for assets.
-   `.time.py`: A version with a slightly different duration per word (18 seconds).

## Configuration

You can customize the word list by editing the `wat.csv` file. The file has three columns: `word`, `best_response`, and `shown`.

-   `word`: The word to be displayed.
-   `best_response`: An example sentence for the word (not used in the application but useful for reference).
-   `shown`: A flag (`true` or `false`) to track if the word has been displayed. You can reset the progress by changing all `true` values to `false`.

## Controls

-   **ENTER**: Start a session.
-   **SPACEBAR**: Pause or resume the current session.
-   **ESC**: Exit the application.

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
