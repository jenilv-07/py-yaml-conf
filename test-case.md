Here's an example of how you can write unit tests for the `ActiveResponseManager` class using Python's `unittest` framework. These tests cover the main functionalities of the class, including reading the YAML, updating limits, and handling errors.

### Test Case Documentation

---

# 🧪 ActiveResponseManager Unit Tests

This section provides examples of unit tests for the `ActiveResponseManager` class using Python's `unittest` framework. These tests ensure that the class correctly manages the YAML and AR conf files, updates limits, and handles errors.

## 🛠️ Setup

To run the tests, you need the following:

- Python 3.x
- `unittest` module (part of the Python standard library)
- `mock` module for mocking file I/O operations (you can use `unittest.mock`)

```bash
pip install pyyaml
```

---

## 🧪 Unit Test Examples

### 1. **Test Initialization and File Reading**

```python
import unittest
from unittest.mock import mock_open, patch
from active_response_manager import ActiveResponseManager
import yaml

class TestActiveResponseManager(unittest.TestCase):
    
    @patch('builtins.open', new_callable=mock_open, read_data="active-response:\n  global-limit: 300\n  custom-limit: {}")
    @patch('os.path.exists', return_value=True)
    def test_init(self, mock_exists, mock_file):
        """
        Test that the initialization reads the YAML file correctly and sets the global limit.
        """
        manager = ActiveResponseManager()
        self.assertEqual(manager.global_limit, 300)
        mock_file.assert_called_once_with('ar_limit_conf.yaml', 'r')

    @patch('os.path.exists', return_value=False)
    def test_yaml_file_not_found(self, mock_exists):
        """
        Test that a FileNotFoundError is handled properly when the YAML file does not exist.
        """
        manager = ActiveResponseManager()
        self.assertEqual(manager.yaml_data, {})
        self.assertEqual(manager.global_limit, 200)  # Default global limit

```

### 2. **Test Command Limit Updates**

```python
    @patch('builtins.open', new_callable=mock_open, read_data="active-response:\n  global-limit: 300\n  custom-limit:\n    block-domain0: 100")
    @patch('os.path.exists', return_value=True)
    def test_update_command_limits(self, mock_exists, mock_file):
        """
        Test updating existing command limits.
        """
        manager = ActiveResponseManager()

        # Update command limit
        new_limits = {'block-domain0': 50}
        manager.update_command_limits(new_limits)

        # Check if the limit was updated
        updated_limits = manager.get_limits(['block-domain0'])
        self.assertEqual(updated_limits['block-domain0'], 50)
    
    @patch('builtins.open', new_callable=mock_open, read_data="active-response:\n  global-limit: 300\n  custom-limit:\n    block-domain0: 100")
    @patch('os.path.exists', return_value=True)
    def test_update_non_existing_command_limits(self, mock_exists, mock_file):
        """
        Test that non-existing commands are not added when updating limits.
        """
        manager = ActiveResponseManager()

        # Try updating a non-existing command
        new_limits = {'non-existing-command0': 50}
        manager.update_command_limits(new_limits)

        # The non-existing command should not be added
        updated_limits = manager.get_limits(['non-existing-command0'])
        self.assertNotIn('non-existing-command0', updated_limits)

```

### 3. **Test Global Limit Update**

```python
    @patch('builtins.open', new_callable=mock_open, read_data="active-response:\n  global-limit: 300\n  custom-limit: {}")
    @patch('os.path.exists', return_value=True)
    def test_update_global_limit(self, mock_exists, mock_file):
        """
        Test updating the global limit.
        """
        manager = ActiveResponseManager()

        # Update global limit
        manager.update_global_limit(400)

        # Check if the global limit was updated
        self.assertEqual(manager.global_limit, 400)

```

### 4. **Test Error Handling**

```python
    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('os.path.exists', return_value=True)
    def test_read_yaml_file_not_found(self, mock_exists, mock_file):
        """
        Test that a FileNotFoundError is handled properly during YAML file read.
        """
        manager = ActiveResponseManager()
        self.assertEqual(manager.yaml_data, {})  # YAML data should be empty
        self.assertEqual(manager.global_limit, 200)  # Default global limit

    @patch('builtins.open', new_callable=mock_open, read_data="invalid_yaml_content")
    @patch('os.path.exists', return_value=True)
    def test_invalid_yaml_parsing(self, mock_exists, mock_file):
        """
        Test that invalid YAML content raises a YAMLError and is handled properly.
        """
        manager = ActiveResponseManager()
        self.assertEqual(manager.yaml_data, {})  # YAML data should be empty due to parsing failure

```

---

## 📝 Test Cases Breakdown

1. **Test Initialization**: Ensure that YAML is properly loaded during initialization, and the default global limit is applied when the file is not found or data is missing.

2. **Test Command Limit Updates**: Check if existing commands' limits are correctly updated, and ensure non-existing commands are not added when trying to update their limits.

3. **Test Global Limit Update**: Validate that the global limit can be successfully updated and written to the YAML file.

4. **Test Error Handling**: Verify that file I/O errors, such as missing files and permission errors, are properly handled.

---

## 🧪 Running the Tests

To run the tests, navigate to the directory where your `test_active_response_manager.py` file is located and run the following command:

```bash
python -m unittest test_active_response_manager.py
```

You should see output indicating which tests passed or failed.

---

### 🏗️ Example File Structure

```plaintext
active-response-manager/
│
├── active_response_manager.py       # Main ActiveResponseManager class
├── ar_limit_conf.yaml               # YAML configuration file (example)
├── ar.conf                          # AR configuration file (example)
└── test_active_response_manager.py  # Unit tests for ActiveResponseManager
```

---

This is how you can set up and run unit tests for your `ActiveResponseManager` class using the `unittest` framework. It covers the primary functionalities such as file reading, updating command and global limits, and error handling.