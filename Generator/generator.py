import random
import numpy as np

def generate_frequency_dict(N, n, distribution="uniform", alpha=1.0):
    """
    Generate a frequency dictionary with distinct values as keys
    and their occurrences as values.
    
    Args:
        N (int): Total size of the stream (number of elements).
        n (int): Number of distinct elements in the stream.
        distribution (str): "uniform" or "zipf".
        alpha (float): Parameter for the Zipf distribution (used if distribution == "zipf").
        
    Returns:
        dict: A dictionary where keys are distinct values and values are their occurrences.
    """
    if distribution == "uniform":
        # Uniform distribution: each value has an equal probability
        stream = [random.randint(1, n) for _ in range(N)]
    elif distribution == "zipf":
        # Zipf distribution: some values appear much more frequently
        stream = np.random.zipf(alpha, N)
        # Map values to the range 1 to n
        stream = [x % n + 1 for x in stream]
    else:
        raise ValueError("Invalid distribution. Choose 'uniform' or 'zipf'.")
    
    # Generate frequency dictionary
    frequency_dict = {}
    for value in stream:
        if value in frequency_dict:
            frequency_dict[value] += 1
        else:
            frequency_dict[value] = 1
    
    return frequency_dict

def dict_to_random_list(frequency_dict):
    """
    Convert a frequency dictionary into a randomized list.
    
    Args:
        frequency_dict (dict): A dictionary where keys are distinct values
                               and values are their frequencies.
                               
    Returns:
        list: A randomized list where each value appears according to its frequency.
    """
    # Create a list with occurrences of each key
    result_list = []
    for value, frequency in frequency_dict.items():
        result_list.extend([value] * frequency)
    
    # Shuffle the list
    random.shuffle(result_list)
    
    return result_list

def generate_list(N, n, distribution="uniform", alpha=1.0):
    """
    Generate a randomized list based on a frequency dictionary.
    
    Args:
        N (int): Total size of the stream (number of elements).
        n (int): Number of distinct elements in the stream.
        distribution (str): "uniform" or "zipf".
        alpha (float): Parameter for the Zipf distribution (used if distribution == "zipf").
        
    Returns:
        tuple: A tuple containing:
            - list: Randomized list of elements.
            - int: True cardinality (number of distinct keys in the frequency dictionary).
            - dict: Frequency dictionary with distinct values and their occurrences.
    """
    frequency_dict = generate_frequency_dict(N, n, distribution, alpha)
    random_list = dict_to_random_list(frequency_dict)
    true_cardinality = len(frequency_dict)  # Cardinality is the number of distinct keys
    return random_list, true_cardinality, frequency_dict
