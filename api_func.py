import yaml
import os

class ActiveResponseManager:
    """
    This class manages the 'active-response' configuration by reading and updating YAML files based on commands 
    found in the AR (active response) configuration file. It supports reading limits, updating limits, and 
    automatically synchronizing the YAML file with the AR conf commands.
    """

    def __init__(self):
        """
        Initializes the ActiveResponseManager class by loading the YAML configuration file, reading the AR conf file, 
        and updating the YAML file with any new or removed commands.
        """
        self.yaml_file = 'ar_limit_conf.yaml'
        self.ar_conf_file = 'ar.conf'
        
        self.yaml_data = self.read_yaml()
        self.global_limit = self.yaml_data.get('active-response', {}).get('global-limit', 200)

        self.update_yaml_with_new_and_removed_commands()

    def read_yaml(self):
        """
        Reads the YAML configuration file and returns the parsed data.

        Returns:
            dict: Parsed YAML data.
        """
        try:
            if not os.path.exists(self.yaml_file):
                raise FileNotFoundError(f"YAML file '{self.yaml_file}' not found.")
            with open(self.yaml_file, 'r') as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError as e:
            print(f"Error: {e}")
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while reading the YAML file: {e}")
        return {}

    def write_yaml(self):
        """
        Writes the current state of `yaml_data` back to the YAML file. Ensures any changes in the limits 
        are saved without disrupting the structure.
        """
        try:
            with open(self.yaml_file, 'w') as file:
                yaml.dump(self.yaml_data, file, default_flow_style=False)
        except PermissionError as e:
            print(f"Error: Permission denied when writing to the file '{self.yaml_file}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred while writing to the YAML file: {e}")

    def read_ar_conf(self):
        """
        Reads the AR conf file and extracts unique commands ending with '0'. These commands are the ones
        that will be used for updating the YAML file.

        Returns:
            set: A set of unique commands from the AR conf file.
        """
        ar_conf_commands = set()
        try:
            if not os.path.exists(self.ar_conf_file):
                raise FileNotFoundError(f"AR conf file '{self.ar_conf_file}' not found.")
            with open(self.ar_conf_file, 'r') as file:
                for line in file:
                    parts = line.strip().split(' - ')
                    if len(parts) >= 3:
                        command = parts[0].strip()
                        if command.endswith('0'):
                            ar_conf_commands.add(command)
        except FileNotFoundError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while reading the AR conf file: {e}")
        return ar_conf_commands

    def update_yaml_with_new_and_removed_commands(self):
        """
        Updates the YAML file by adding new commands from the AR conf file and keeping existing commands intact. 
        New commands will be added with the global limit, and no existing commands will be removed.
        """
        try:
            ar_conf_commands = self.read_ar_conf()

            custom_limits = self.yaml_data.get('active-response', {}).get('custom-limit', {})

            for command in ar_conf_commands:
                if command not in custom_limits:
                    custom_limits[command] = self.global_limit

            self.yaml_data['active-response']['custom-limit'] = custom_limits
            self.write_yaml()
        except Exception as e:
            print(f"An error occurred while updating the YAML file: {e}")

    def get_limits(self, command_list=None):
        """
        Retrieves limits for specific commands or all commands if no list is provided.

        Args:
            command_list (list, optional): A list of commands for which limits are to be retrieved.

        Returns:
            dict: A dictionary of command limits.
        """
        try:
            custom_limits = self.yaml_data.get('active-response', {}).get('custom-limit', {})

            if command_list:
                return {command: custom_limits.get(command) for command in command_list if command in custom_limits}
            return custom_limits
        except Exception as e:
            print(f"An error occurred while retrieving the limits: {e}")
            return {}

    def update_command_limits(self, new_limits_dict):
        """
        Updates the command limits for existing commands in the YAML file. Only modifies existing commands and does not
        add new ones.

        Args:
            new_limits_dict (dict): A dictionary with command names as keys and new limits as values.
        """
        try:
            custom_limits = self.yaml_data.get('active-response', {}).get('custom-limit', {})

            for command, new_limit in new_limits_dict.items():
                if command in custom_limits:
                    custom_limits[command] = new_limit
                    print(f"Updated '{command}' to limit: {new_limit}")
                else:
                    print(f"Command '{command}' does not exist in custom limits. Skipping update.")

            self.yaml_data['active-response']['custom-limit'] = custom_limits
            self.write_yaml()
        except Exception as e:
            print(f"An error occurred while updating the command limits: {e}")

    def update_global_limit(self, new_global_limit):
        """
        Updates the global limit in the YAML file.

        Args:
            new_global_limit (int): The new global limit to be set.
        """
        try:
            self.yaml_data['active-response']['global-limit'] = new_global_limit
            self.global_limit = new_global_limit
            print(f"Global limit updated to {new_global_limit}")

            self.write_yaml()
        except Exception as e:
            print(f"An error occurred while updating the global limit: {e}")

try:
    manager = ActiveResponseManager()

    manager.update_global_limit(300)

    new_limits = {
        'block-domain0': 50,
        'quick-scan0': 15,
        'new-command0': 100
    }
    manager.update_command_limits(new_limits)

    updated_limits = manager.get_limits()
    print("Updated Limits:", updated_limits)

except Exception as e:
    print(f"An unexpected error occurred in the main execution: {e}")
