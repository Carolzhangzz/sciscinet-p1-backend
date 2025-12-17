import os

print("Current working directory:", os.getcwd())
print("\nChecking for data files...")

paths_to_check = [
    'data/processed/papers.csv',
    '../data/processed/papers.csv',
    './data/processed/papers.csv',
    'scripts/../data/processed/papers.csv'
]

for path in paths_to_check:
    exists = os.path.exists(path)
    abs_path = os.path.abspath(path)
    print(f"\n  Path: {path}")
    print(f"  Exists: {exists}")
    print(f"  Absolute: {abs_path}")

print("\n\nDirectory structure:")
print("\nCurrent directory contents:")
for item in os.listdir('.'):
    print(f"  - {item}")

if os.path.exists('data'):
    print("\n'data' directory contents:")
    for item in os.listdir('data'):
        print(f"  - {item}")
    
    if os.path.exists('data/processed'):
        print("\n'data/processed' directory contents:")
        for item in os.listdir('data/processed'):
            print(f"  - {item}")