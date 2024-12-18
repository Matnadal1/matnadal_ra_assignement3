def read_txt_as_list(file_path):
    """
    Read a local .txt file and return its content as a list of words.

    Args:
        file_path (str): The path to the .txt file on the local computer.

    Returns:
        list: A list of words from the text file.
    """
    try:
        # Open the file and read its content
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Split the content into words
        words = content.split()
        
        return words

    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return []
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return []

def get_cardinality_and_dict_from_dat(file_path):
    """
    Read a .dat file and calculate the cardinality and return the dictionary.

    Args:
        file_path (str): The path to the .dat file on the local computer.

    Returns:
        tuple: A tuple containing:
            - int: The cardinality (number of unique keys).
            - dict: A dictionary where keys are words and values are their counts.
    """
    try:
        # Read the file and construct the dictionary
        word_dict = {}
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                # Split each line into key-value pairs
                key, value = line.strip().split(": ")
                word_dict[key] = int(value)
        
        # Calculate the cardinality (number of unique keys)
        cardinality = len(word_dict)
        
        return cardinality, word_dict

    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return 0, {}
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")
        return 0, {}
