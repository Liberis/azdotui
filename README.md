
# azdotui
A terminal-based Azure DevOps manager that allows you to interact with projects, pipelines, and builds from the command line.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Install from Source](#install-from-source)
- [Configuration](#configuration)
  - [Authentication](#authentication)
- [Usage](#usage)
  - [Navigation Instructions](#navigation-instructions)
  - [Key Features](#key-features)
    - [Selecting Projects and Pipelines](#selecting-projects-and-pipelines)
    - [Triggering Pipelines](#triggering-pipelines)
    - [Cancelling Builds](#cancelling-builds)
- [Building and Packaging](#building-and-packaging)
  - [Project Structure](#project-structure)
  - [Building the Package](#building-the-package)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features
- **Browse Azure DevOps Projects and Pipelines:** Navigate through your Azure DevOps projects and pipelines directly from the terminal.
- **Trigger Pipelines:** Trigger selected pipelines on specific branches or tags.
- **View Builds Categorized by Status:** Builds are displayed in categories such as Succeeded, Failed, Warning, Queued, and Running.
- **Cancel Builds:** Cancel all running and queued builds with a simple command.
- **Keyboard Navigation:** Efficiently navigate the interface using keyboard shortcuts.

## Installation

### Prerequisites
- Python 3.10 or higher.
- pip package manager.

### Install from Source

1. Clone the Repository
    ```bash
    git clone https://github.com/yourusername/azdotui.git
    cd azdotui
    ```

2. Install Dependencies
    ```bash
    pip install -r requirements.txt
    ```

3. Build and Install the Package
    ```bash
    python setup.py sdist bdist_wheel
    pip install dist/azdotui-1.0.0-py3-none-any.whl
    ```
   Replace `azdotui-1.0.0-py3-none-any.whl` with the actual filename generated in the `dist/` directory.

## Configuration

### Authentication
Before running the application, you need to configure authentication with Azure DevOps.

#### Set Environment Variables
Set the following environment variables in your shell:

- `AZDO_ORGANIZATION`: Your Azure DevOps organization name.
- `AZDO_PAT`: Your Azure DevOps Personal Access Token with appropriate permissions.

Example:
```bash
export AZDO_ORGANIZATION="your_organization"
export AZDO_PAT="your_personal_access_token"
```

*Note:* It's recommended to set these variables in your shell profile (e.g., `.bashrc`, `.zshrc`) or use a secure method to store secrets.

#### Personal Access Token (PAT) Permissions
Ensure your PAT has the following scopes:
- Build (Read & Execute)
- Pipelines (Read & Execute)
- Project and Team (Read)

## Usage
Run the application from the command line:
```bash
azdotui
```

### Navigation Instructions
- **Switch Panes:** Press `Tab` to cycle through the panes (Projects, Pipelines, Builds).
- **Navigate Lists:** Use the `Up` and `Down` arrow keys to move through lists.
- **Select Items:** Press `Enter` to select projects or expand/collapse folders in the Pipelines pane.
- **Select/Deselect Pipelines:** Press `Spacebar` to select or deselect pipelines.
- **Expand/Collapse Folders:** Use `Left` and `Right` arrow keys or `Enter` to collapse or expand folders in the Pipelines pane.
- **Trigger Pipelines:** Press `t` to trigger selected pipelines.
- **Cancel Builds:** Press `c` in the Builds pane to cancel all running and queued builds.
- **Quit Application:** Press `q` to exit the application.

### Key Features

#### Selecting Projects and Pipelines
1. **Select a Project:**
   - Navigate to the Projects Pane using `Tab` if necessary.
   - Use the `Up` and `Down` arrow keys to select a project.
   - Press `Enter` to select the project and load its pipelines.

2. **Navigate Pipelines:**
   - Switch to the Pipelines Pane.
   - Use the arrow keys to navigate through pipelines and folders.
   - Press `Enter` or `Right Arrow` to expand a folder.
   - Press `Enter` or `Left Arrow` to collapse a folder.

3. **Select Pipelines:**
   - Press `Spacebar` to select or deselect a pipeline.
   - When a folder is selected, all pipelines within it are selected or deselected.

#### Triggering Pipelines
1. **Select Pipelines:**
   - Use `Spacebar` to select one or more pipelines.

2. **Initiate Trigger:**
   - Press `t` to start the trigger process.

3. **Enter Branch or Tag:**
   - When prompted, enter the branch or tag name (e.g., `main`, `develop`, `v1.0.0`).

4. **Confirm Action:**
   - Press `Enter` to proceed.
   - Confirm the action by pressing `y` when prompted.

5. **View Status:**
   - The status bar will display messages indicating the progress.
   - Triggered pipelines will start appearing in the Builds Pane.

#### Cancelling Builds
1. **Switch to Builds Pane:**
   - Press `Tab` to navigate to the Builds Pane.

2. **Initiate Cancellation:**
   - Press `c` to cancel all running and queued builds.

3. **Confirm Action:**
   - Press `y` to confirm the cancellation.

4. **View Updates:**
   - The Builds Pane will refresh, and cancelled builds will be updated accordingly.

## Building and Packaging

### Project Structure
The project is organized as follows:
```arduino
azdotui/
├── src/
│   ├── api/
│   │   └── azdo.py
│   ├── config/
│   │   ├── logger.py
│   │   └── settings.py
│   ├── events/
│   │   └── keybindings.py
│   ├── main.py
│   ├── ui/
│   │   ├── layout.py
│   │   ├── panes/
│   │   │   ├── base_pane.py
│   │   │   ├── builds_pane.py
│   │   │   ├── pipelines_pane.py
│   │   │   └── projects_pane.py
│   │   └── status_bar.py
│   └── utils/
│       ├── cursed.py
│       └── tree.py
├── setup.py
├── README.md
└── requirements.txt
```

### Building the Package

1. **Navigate to Project Root:**
   ```bash
   cd azdotui
   ```

2. **Build the Package:**
   ```bash
   python -m build
   ```
   This command generates distribution archives in the `dist/` directory.

3. **Install the Package:**
   ```bash
   pip install . --upgrade   ```

4. **Run the Application:**
   ```bash
   azdotui
   ```

## Dependencies
The application requires the following Python packages:
- `aiohttp`: Asynchronous HTTP client for Python.

These are listed in `requirements.txt`:
```txt
aiohttp>=3.7.4
```

Install dependencies using:
```bash
pip install -r requirements.txt
```

## Contributing
Contributions are welcome! Please follow these steps:

1. **Fork the Repository:** Click on the 'Fork' button at the top right of the repository page.

2. **Clone Your Fork:**
    ```bash
    git clone https://github.com/yourusername/azdotui.git
    ```

3. **Create a Branch:**
    ```bash
    git checkout -b feature/your-feature-name
    ```

4. **Make Changes:** Implement your feature or fix.

5. **Commit Changes:**
    ```bash
    git commit -am 'Add new feature'
    ```

6. **Push to GitHub:**
    ```bash
    git push origin feature/your-feature-name
    ```

7. **Submit a Pull Request:** Open a pull request on GitHub to merge your changes into the main repository.

## License
This project is licensed under the MIT License.

## Contact
**Author:** Liberis Patoucheas 
**Email:** libpatouch@gmail.com  
**GitHub:** liberis  

### Additional Information
- **Logging Configuration:** Logs are written to `app.log` in the application directory. Configure logging in `src/config/logger.py`.
- **Error Handling:** The application includes error handling to provide messages and assist with debugging.
- **Python Version:** The application requires Python 3.10 or higher.

### Quick Start

1. **Set Environment Variables:**
    ```bash
    export AZDO_ORGANIZATION="your_organization"
    export AZDO_PAT="your_personal_access_token"
    ```

2. **Run the Application:**
    ```bash
    azdotui
    ```

3. **Navigate and Enjoy:** Use the keyboard shortcuts to navigate and manage your Azure DevOps resources.

