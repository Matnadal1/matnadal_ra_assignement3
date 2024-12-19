import csv
import time
import random
import hashlib
import xxhash
import os
from randomhash import RandomHashFamily
from REC.rec import Recordinality
from HLL.hll import HyperLogLog 
from Generator.generator import generate_list
from Tools.file_reader import read_txt_as_list, get_cardinality_and_dict_from_dat

configurations = [
    {"N": 1000, "n": 100, "alpha": 1.2},
    {"N": 10000, "n": 1000, "alpha": 1.2},
    {"N": 100000, "n": 100000, "alpha": 1.2},
    {"N": 100000, "n": 1000, "alpha": 1.2},
    {"N": 500000, "n": 5000, "alpha": 1.5},
    {"N": 1000000, "n": 100000, "alpha": 1.8},
    {"N": 2000000, "n": 200000, "alpha": 2.0},
    {"N": 20000, "n": 20000, "alpha": 2.0},
]

book_directory = "./datasets"

def get_book_pairs(directory):
    """
    Get pairs of .txt and .dat files in the directory.
    Args:
        directory (str): Path to the directory containing books.
    Returns:
        dict: Dictionary with book names as keys and paths to .txt and .dat files as values.
    """
    files = os.listdir(directory)
    book_pairs = {}
    
    # Group files by name without extensions
    for file in files:
        name, ext = os.path.splitext(file)
        if ext == ".txt" or ext == ".dat":
            if name not in book_pairs:
                book_pairs[name] = {}
            book_pairs[name][ext[1:]] = os.path.join(directory, file)
    
    # Filter out incomplete pairs
    return {name: paths for name, paths in book_pairs.items() if "txt" in paths and "dat" in paths}

def sha256_hash_int(element):
    return int(hashlib.sha256(str(element).encode()).hexdigest(), 16) & 0xFFFFFFFF 

def xxhash32_int(element):
    return xxhash.xxh32(str(element).encode()).intdigest() 

def python_hash_int(element):
    return hash(element) & 0xFFFFFFFF 

def sha256_hash(element):
    return int(hashlib.sha256(str(element).encode()).hexdigest(), 16) / (2**256 - 1)

def xxhash32(element):
    return xxhash.xxh32(str(element).encode()).intdigest() / (2**32 - 1)

def python_hash(element):
    return (hash(element) & 0xFFFFFFFF) / (2**32 - 1)

def test_recordinality(k_values, hash_functions, algorithm, data_stream, cardinality, runs=1000, output_file="results.csv", source="unknown"):
    """
    Test different configurations of Recordinality or HLL multiple times and save results to CSV.
    Args:
        k_values (list): List of subset sizes (for REC) or precision values (for HLL).
        hash_functions (dict): Dictionary of hash function names and callables.
        algorithm (string): The name of the algorithm to test ("HLL" or "REC").
        data_stream (list): The list of data to evaluate.
        cardinality (int): Number of distinct elements in the stream.
        runs (int): Number of runs to average results.
        output_file (str): Path to the CSV file for storing results.
        source (str): The source of the data ("book name" or "generator").
    """
    results = []
    print(f"\nTesting {algorithm} configurations with average error over multiple runs...\n")

    for k in k_values:
        for hash_name, hash_func in hash_functions.items():
            total_error = 0.0
            total_time = 0.0
            total_estimated_cardinality = 0.0

            for _ in range(runs):
                start_time = time.time()

                if algorithm == "REC":
                    recordinality = Recordinality(k=k, hashfunc=hash_func)
                    recordinality.run_rec(data_stream)
                    estimated_cardinality = recordinality.estimate_cardinality()
                elif algorithm == "HLL":
                    hll = HyperLogLog(p=k, hashfunc=hash_func)
                    hll.add_elements_to_hll(data_stream)
                    estimated_cardinality = hll.count()

                elapsed_time = time.time() - start_time
                error = abs(estimated_cardinality - cardinality) / cardinality

                total_time += elapsed_time
                total_error += error
                total_estimated_cardinality += estimated_cardinality

            memory = k
            if algorithm == "HLL":
                memory = 2**k
            average_error = total_error / runs
            average_time = total_time / runs
            average_estimated_cardinality = total_estimated_cardinality / runs

            results.append({
                "source": source,  # Ajout de la colonne source
                "memory": memory,
                "cardinality": cardinality,
                "total_elements": len(data_stream),
                "average_time": average_time,
                "algorithm": algorithm,
                "hash_function": hash_name,
                "average_error": average_error,
                "average_estimated_cardinality": average_estimated_cardinality,
                "nb_of_run": runs
            })

            print(f"Source={source}, k={k}, Hash={hash_name}, Avg. Error={average_error:.6f}, Avg. Time={average_time:.6f}s")

    # Append results to CSV
    file_exists = os.path.isfile(output_file)

    with open(output_file, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=[
            "source", "memory", "cardinality", "total_elements", "average_time",
            "algorithm", "hash_function", "average_error", "average_estimated_cardinality", "nb_of_run"
        ])
        if not file_exists:
            writer.writeheader()
        writer.writerows(results)

    print(f"\nResults saved to {output_file}")
  
def test_books_in_directory(directory, k_values, p_values, hash_functions, hash_functions_hll, runs=10):
    """
    Process all book pairs in a directory and run REC and HLL tests.
    Args:
        directory (str): Path to the directory containing book files.
        k_values (list): List of subset sizes for REC.
        p_values (list): List of precision values for HLL.
        hash_functions (dict): Hash functions for REC.
        hash_functions_hll (dict): Hash functions for HLL.
        runs (int): Number of runs for each configuration.
    """
    book_pairs = get_book_pairs(directory)
    print(f"Found {len(book_pairs)} books in directory: {directory}")

    for book_name, paths in book_pairs.items():
        print(f"\nProcessing Book: {book_name}\n")
        txt_path = paths["txt"]
        dat_path = paths["dat"]

        # Load the text and the cardinality info
        list_from_text = read_txt_as_list(txt_path)
        true_cardinality, frequency_dict = get_cardinality_and_dict_from_dat(dat_path)

        # REC
        #test_recordinality(
        #    k_values, 
        #    hash_functions, 
        #    "REC", 
        #    list_from_text, 
        #    true_cardinality, 
        #    runs=runs, 
        #    output_file="results_rec_book.csv", 
        #    source=book_name
        #)

        # HLL
        test_recordinality(
            p_values, 
            hash_functions_hll, 
            "HLL", 
            list_from_text, 
            true_cardinality, 
            runs=runs, 
            output_file="results_hll_book.csv", 
            source=book_name
        )
  
if __name__ == "__main__":
    # Batch Run for REC
    k_values = [16, 32, 64, 128, 256, 512, 1024, 2048] 
    
    # Batch Run for HLL
    p_values = [4, 6, 8, 9]
    p_values = [5, 7, 10, 11]
    # Config for REC
    hash_functions = {
        "SHA-256": sha256_hash,
        "xxHash32": xxhash32,
        "Python Hash": python_hash,
    }
    
    # Config for HLL
    hash_functions_hll = {
        "SHA-256": sha256_hash_int,
        "xxHash32": xxhash32_int,
        "Python Hash": python_hash_int,
        "RandomHashFamily": None
    }
    
    test_books_in_directory(book_directory, k_values, p_values, hash_functions, hash_functions_hll, runs=10)

    
    for config in configurations:
        N = config["N"]
        n = config["n"]
        alpha = config["alpha"]
        print(f"\nRunning tests for N={N}, n={n}, alpha={alpha}\n")
        # Generator
        data_generator_stream, data_generator_cardinality, data_generator_frequency_dict = generate_list(N, n, "zipf", alpha)
        #REC
        #test_recordinality(k_values, 
        #                  hash_functions, 
        #                  "REC", 
        #                  data_generator_stream, 
        #                  data_generator_cardinality,
        #                  runs=1, 
        #                  output_file="results_rec_generator.csv", 
        #                  source="generator"
        #                   )
        #HLL
        test_recordinality(p_values, 
                          hash_functions_hll, 
                          "HLL", 
                          data_generator_stream, 
                          data_generator_cardinality, 
                          runs=1, 
                          output_file="results_hll_generator.csv", 
                          source="generator"
                          )

