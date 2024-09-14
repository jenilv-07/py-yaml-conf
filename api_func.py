import yaml
import os
import logging

logger = logging.getLogger('wazuh-api')
logger.setLevel(logging.DEBUG)



class ActiveResponseLimit:
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
            logger.error(e)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while reading the YAML file: {e}")
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
            logger.error(f"Error: Permission denied when writing to the file '{self.yaml_file}': {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while writing to the YAML file: {e}")

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
            logger.error(f"Error: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while reading the AR conf file: {e}")
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
            logger.error(f"An error occurred while updating the YAML file: {e}")

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
            logger.error(f"An error occurred while retrieving the limits: {e}")
            return {}


    def update_command_limits(self, new_limits_dict):
        """
        Updates the command limits for existing commands in the YAML file. Only modifies existing commands and does not
        add new ones. If the limit exceeds the global limit, it raises an error. Handles `None` values by storing `null` 
        in the YAML file.

        Args:
            new_limits_dict (dict): A dictionary with command names as keys and new limits as values.
        
        Returns:
            bool: True if the update is successful, False otherwise.
        """
        try:
            custom_limits = self.yaml_data.get('active-response', {}).get('custom-limit', {})

            for command, new_limit in new_limits_dict.items():
                if new_limit is not None and new_limit > self.global_limit:
                    raise ValueError(f"Limit for command '{command}' exceeds the global limit ({self.global_limit}).")

                if command in custom_limits:
                    if new_limit is None:
                        custom_limits[command] = None  # Store as null in YAML
                        logger.debug(f"Updated '{command}' to limit: null")
                    else:
                        custom_limits[command] = new_limit
                        logger.debug(f"Updated '{command}' to limit: {new_limit}")
                else:
                    logger.debug(f"Command '{command}' does not exist in custom limits. Skipping update.")

            self.yaml_data['active-response']['custom-limit'] = custom_limits
            self.write_yaml()
            return True
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return False
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
            logger.debug(f"Global limit updated to {new_global_limit}")

            self.write_yaml()
            return True
        except Exception as e:
            logger.error(f"An error occurred while updating the global limit: {e}")
            return False
            
    def get_global_limit(self):
        """
        Retrieves the global limit from the YAML file.

        Returns:
            int: The global limit value.
        """
        try:
            return self.yaml_data['active-response']['global-limit']
        except KeyError:
            logger.error("Global limit not found in YAML file.")
            return None
        
    def get_custom_limits_with_global(self):
        """
        Retrieves the custom limits and the global limit from the YAML file in the required format.
        This method constructs a dictionary containing both the custom limits for specific commands
        and the global limit that applies to all commands.

        Returns:
            dict: A dictionary containing:
                - "Custom-limit" (dict): The custom limits for each command where keys are command names 
                and values are the respective limits. Commands with no set limit are represented as `None`.
                - "global-limit" (dict): A dictionary with a single key "global-limit" representing the overall 
                global limit applied across all commands.
                
        Raises:
            Exception: If there is an issue retrieving the custom limits or the global limit, an exception is caught, 
            logged, and an empty dictionary is returned.

        Example:
            >>> ar_manager = ActiveResponseLimit()
            >>> limits = ar_manager.get_custom_limits_with_global()
            >>> print(limits)
        """
        try:
            # Retrieve custom limits from YAML file
            custom_limits = self.yaml_data.get('active-response', {}).get('custom-limit', {})
            # Retrieve the global limit using the existing function
            global_limit = self.get_global_limit()

            # Construct the formatted data with custom limits and global limit
            formatted_data = {
                "Custom-limit": custom_limits,
                "global-limit": {
                    "global-limit": global_limit
                }
            }

            # Return the formatted data
            return formatted_data

        except Exception as e:
            # Log any error encountered and return an empty dictionary
            logger.error(f"An error occurred while retrieving custom limits and global limit: {e}")
            return {}

    def update_custom_limits_and_global(self, limits_dict):
        """
        Updates the custom limits and the global limit in the YAML file. This method allows you to provide a 
        dictionary that contains both the custom limits and the global limit.

        Args:
            limits_dict (dict): A dictionary that should have the following structure:
                {
                    'Custom-limit': {
                        'ar-trigger0': 150,
                        'block-domain0': None,
                        ...
                    },
                    'global-limit': {
                        'global-limit': 150
                    }
                }

        Returns:
            bool: True if the update was successful, False otherwise.

        Raises:
            Exception: If there is an issue updating the limits, it logs the error and returns False.

        Example:
            >>> ar_manager = ActiveResponseLimit()
            >>> limits = {
            >>>     'Custom-limit': {
            >>>         'ar-trigger0': 150,
            >>>         'block-domain0': None,
            >>>         ...
            >>>     },
            >>>     'global-limit': {
            >>>         'global-limit': 150
            >>>     }
            >>> }
            >>> success = ar_manager.update_custom_limits_and_global(limits)
            >>> if success:
            >>>     print("Limits updated successfully")
        """
        try:
            # Retrieve current custom limits from YAML file
            custom_limits = self.yaml_data.get('active-response', {}).get('custom-limit', {})

            old_global_limit = self.get_global_limit()
            
            # Get new custom limits from the passed limits_dict
            new_custom_limits = limits_dict.get('Custom-limit', {})
            new_global_limit = limits_dict.get('global-limit', {}).get('global-limit')

            # Update custom limits
            for command, limit in new_custom_limits.items():
                if limit is not None:
                    if limit < new_global_limit:
                        custom_limits[command] = limit
                    else:
                        custom_limits[command] = new_global_limit
                else:
                    custom_limits[command] = None  # Store None as null in YAML

            # Set updated custom limits in the YAML structure
            self.yaml_data['active-response']['custom-limit'] = custom_limits

            # Update the global limit if provided
            if new_global_limit is not None and new_global_limit > 0:
                self.yaml_data['active-response']['global-limit'] = new_global_limit
                logger.debug(f"Updated global limit to: {new_global_limit}")

            # Write the updated YAML data back to the file
            self.write_yaml()
            return True

        except Exception as e:
            logger.error(f"An error occurred while updating the custom limits and global limit: {e}")
            return False

        
ar_manager = ActiveResponseLimit()

# The input dictionary to update limits
limits = {
    'Custom-limit': {
        'ar-trigger0': None,
        'block-domain0': None,
        'blockusb0': None,
        'full-scan0': None,
        'isolation0': 234,
        'offboard0': None,
        'quick-scan0': None,
        'remove-threat0': None,
        'restart-ossec0': None,
        'restart-wazuh0': None,
        'run-livequery0': None,
        'unblock-domain0': None,
        'unblockusb0': None,
        'unisolation0': None
    },
    'global-limit': {
        'global-limit': 100
    }
}

# Update the limits
success = ar_manager.update_custom_limits_and_global(limits)

# Check if the update was successful
if success:
    print("Limits updated successfully")
else:
    print("Failed to update limits")