import random
import hashlib
import xxhash
from randomhash import RandomHashFamily
from REC.rec import Recordinality
from HLL.hll import HyperLogLog 
from Generator.generator import generate_list
from Tools.file_reader import read_txt_as_list, get_cardinality_and_dict_from_dat

text = "C:/Users/Utilisateur/OneDrive/Documents/cours_20242025/RA/assignement3/datasets/dracula.txt"
text_dat = "C:/Users/Utilisateur/OneDrive/Documents/cours_20242025/RA/assignement3/datasets/dracula.dat"

# Example of generator usage
N = 10000  # Total stream size
n = 1000    # Number of distinct elements
alpha = 1.2

def sha256_hash_int(element):
    return int(hashlib.sha256(str(element).encode()).hexdigest(), 16) & 0xFFFFFFFF  # Force un entier 32 bits

def xxhash32_int(element):
    return xxhash.xxh32(str(element).encode()).intdigest()  # xxhash32 produit déjà un entier 32 bits

def python_hash_int(element):
    return hash(element) & 0xFFFFFFFF  # Entier 32 bits

def sha256_hash(element):
    return int(hashlib.sha256(str(element).encode()).hexdigest(), 16) / (2**256 - 1)

def xxhash32(element):
    return xxhash.xxh32(str(element).encode()).intdigest() / (2**32 - 1)

def python_hash(element):
    return (hash(element) & 0xFFFFFFFF) / (2**32 - 1)

def test_recordinality(k_values, hash_functions, algorithm, data_stream, cardinality, runs=1000):
    """
    Test different configurations of Recordinality multiple times and compute average error.
    Args:
        k_values (list): List of subset sizes to test.
        hash_functions (dict): Dictionary of hash function names and callables.
        algorithm (string) : The name of the algorithm you want to try : HLL or REC
        data_stream (list): The list of data you want to evaluate with the algo.
        cardinality (int): Number of distinct elements in the stream.
        runs (int): Number of times to repeat each test to average results.
    """
    results = []
    print(f"\nTesting {algorithm} configurations with average error over multiple runs...\n")

    for k in k_values:
        for hash_name, hash_func in hash_functions.items():
            total_error = 0.0
            for _ in range(runs):
                if algorithm == "REC":
                    recordinality = Recordinality(k=k, hashfunc=hash_func)
                    recordinality.run_rec(data_stream)
                    estimated_cardinality = recordinality.estimate_cardinality()
                elif algorithm == "HLL":
                    hll = HyperLogLog(p=k, hashfunc=hash_func)
                    hll.add_elements_to_hll(data_stream)
                    estimated_cardinality = hll.count()
                error = abs(estimated_cardinality - cardinality) / cardinality
                total_error += error
            average_error = total_error / runs
            results.append({
                "k": k,
                "hash_function": hash_name,
                "average_error": average_error,
            })
            print(f"k={k}, Hash={hash_name}, Average Error={average_error:.6f}")

    # Analyse des résultats
    print("\nBest Configurations (sorted by average error):")
    sorted_results = sorted(results, key=lambda x: x["average_error"])
    for res in sorted_results[:5]:
        print(f"k={res['k']}, Hash={res['hash_function']}, Average Error={res['average_error']:.6f}")

if __name__ == "__main__":
    # Extract Text data
    list_from_text = read_txt_as_list(text)
    true_cardinality, frequency_dict = get_cardinality_and_dict_from_dat(text_dat)

    # Generator
    data_generator_stream, data_generator_cardinality, data_generator_frequency_dict = generate_list(N, n, "zipf", alpha)

    # HLL
    hll = HyperLogLog()
    hll.add_elements_to_hll(list_from_text)
    print("HLL : Estimated cardinality is", hll.count())
    
    # Batch Run for REC
    k_values = [16, 32, 64, 128, 256, 512, 1024, 2048] 
    p_values = [4, 6, 8, 9]
    hash_functions = {
        "SHA-256": sha256_hash,
        "xxHash32": xxhash32,
        "Python Hash": python_hash,
        "RandomHashFamily": lambda x: RandomHashFamily(count=1).hashes(str(x))[0] / (2**32 - 1)
    }
    hash_functions_hll = {
        "SHA-256": sha256_hash_int,
        "xxHash32": xxhash32_int,
        "Python Hash": python_hash_int,
        "RandomHashFamily": None
    }
    test_recordinality(k_values, hash_functions, "REC", list_from_text, true_cardinality, runs=1)

    test_recordinality(p_values, hash_functions_hll, "HLL", list_from_text, true_cardinality, runs=1)



