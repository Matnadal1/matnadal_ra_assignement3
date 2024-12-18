
import matplotlib.pyplot as plt
from randomhash import RandomHashFamily

random_hash_family = RandomHashFamily(count=1)
hashfunc = lambda x: random_hash_family.hashes(str(x))[0] / (2**32 - 1)

data = [f"element_{i}" for i in range(10000)]
scores = [hashfunc(element) for element in data]

plt.hist(scores, bins=50, edgecolor="k", alpha=0.7)
plt.title("Distribution of hash scores")
plt.xlabel("Score")
plt.ylabel("Frequency")
plt.show()