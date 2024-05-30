
# Node Log Reader

Node Log Reader is a PyQt6-based GUI tool for executing remote commands and collecting logs from a RIG via SSH.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/Rajindra/Node-Log-Reader.git
    ```

2. Install the required Python packages:
    ```sh
    pip install PyQt6 paramiko scp
    ```

## Build

1. Install PyInstaller:
    ```sh
    pip install pyinstaller
    ```

2. Build the executable using the `.spec` file:
    ```sh
    pyinstaller NodeLogReader.spec
    ```

## Run

1. Navigate to the `dist` directory and run the executable:
    ```sh
    dist\Ikman\Ikman.exe
    ```
