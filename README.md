# 🛠️ ActiveResponseManager

## 🚀 Overview

`ActiveResponseManager` is a Python class that helps manage the **Active Response** configurations in YAML format based on the commands found in an AR configuration file (`ar.conf`). It provides functionality to:

- 📖 Read and update YAML files.
- 🔄 Automatically synchronize YAML commands with the commands in the AR configuration file.
- ⚙️ Retrieve, update, and set limits for commands.
- 📊 Handle global and custom limits for active responses.
- 🛡️ Robust error handling for file operations and YAML parsing.

## 📋 Requirements

Make sure you have the following installed:

- Python 3.x
- `pyyaml` for YAML file parsing:

    ```bash
    pip install pyyaml
    ```

## ⚙️ Setup

1. 🌀 Clone the repository to your local machine:

    ```bash
    git clone https://github.com/yourusername/active-response-manager.git
    ```

2. 📁 Navigate to the project directory:

    ```bash
    cd active-response-manager
    ```

3. 📝 Make sure you have the YAML configuration file (`ar_limit_conf.yaml`) and AR configuration file (`ar.conf`) in your project directory or update the file paths in the code accordingly.

4. ▶️ Run the script to execute the functionality.

## 📦 Usage

### 🛠️ Initializing the ActiveResponseManager

The `ActiveResponseManager` class is initialized by loading the configuration files. Once initialized, it automatically updates the YAML file with any new or removed commands found in the AR conf file.

```python
manager = ActiveResponseManager()
```

### 🔧 Updating Global Limit

You can update the global limit by calling the `update_global_limit()` method.

```python
manager.update_global_limit(300)
```

### 📝 Updating Command Limits

To update the limits for specific commands, use the `update_command_limits()` method. This method will only update existing commands; new commands will not be added.

```python
new_limits = {
    'block-domain0': 50,  # Example of an update to an existing command
    'quick-scan0': 15,    # Another example
}
manager.update_command_limits(new_limits)
```

### 📊 Retrieving Command Limits

You can retrieve the limits for specific commands by passing a list of command names to the `get_limits()` method. If no list is provided, it returns all command limits.

```python
# Get all command limits
all_limits = manager.get_limits()

# Get specific command limits
specific_limits = manager.get_limits(['block-domain0', 'quick-scan0'])
```

### 🔄 Example Execution

Below is a basic usage example to show how to use the `ActiveResponseManager` class:

```python
# Initialize manager
manager = ActiveResponseManager()

# Update global limit
manager.update_global_limit(300)

# Update command limits for existing commands
new_limits = {
    'block-domain0': 50,
    'quick-scan0': 15
}
manager.update_command_limits(new_limits)

# Print updated limits
updated_limits = manager.get_limits()
print("Updated Limits:", updated_limits)
```

### 🛡️ Error Handling

The class has robust error handling for the following:

- **FileNotFoundError** 🗂️: If the YAML or AR conf file is missing.
- **YAMLError** 📄: If there is an issue while parsing the YAML file.
- **PermissionError** 🛑: If there are insufficient permissions to read/write files.
- **General Exception Handling** ⚠️: To catch any unexpected issues.

## 🗂️ File Structure

```plaintext
active-response-manager/
│
├── ActiveResponseManager.py        # Main Python script with the ActiveResponseManager class
├── ar_limit_conf.yaml              # YAML configuration file for active response limits (example, update path in code)
└── ar.conf                         # AR configuration file with commands (example, update path in code)
```

## 🤝 Contributing

Feel free to submit issues, fork the repository, and make pull requests to improve the codebase.

### 📑 Steps to Contribute:

1. 🍴 Fork the repository.
2. 🌱 Create a new branch for your feature or bug fix.
3. 📝 Commit your changes with proper commit messages.
4. 📤 Push your changes to your fork.
5. 🔁 Submit a pull request.

## 📜 License

This project is licensed under the MIT License.