#!/usr/bin/env python3
"""
Script to rename files in each subdirectory with sequential numbers.
Each subdirectory will have its files renamed as 1.ext, 2.ext, 3.ext, etc.
where ext is the original file extension.
"""
import os
import shutil
from pathlib import Path

def rename_files_sequentially(base_dir):
    """
    Rename files in each subdirectory with sequential numbers.
    
    Args:
        base_dir (str): Path to the base directory containing subdirectories
    """
    base_path = Path(base_dir)
    
    # Get all subdirectories
    subdirs = [d for d in base_path.iterdir() if d.is_dir()]
    
    for subdir in subdirs:
        print(f"Processing directory: {subdir.name}")
        
        # Get all files in the subdirectory
        files = [f for f in subdir.iterdir() if f.is_file()]
        
        # Sort files to ensure consistent ordering
        files.sort(key=lambda x: x.name)
        
        # Rename each file with sequential numbers
        for idx, file_path in enumerate(files, start=1):
            # Get the original extension
            original_ext = file_path.suffix  # includes the dot, e.g., '.jpg'
            
            # Create new filename with sequential number and original extension
            new_filename = f"{idx}{original_ext}"
            new_file_path = subdir / new_filename
            
            # Handle potential naming conflicts by adding a suffix
            counter = 1
            while new_file_path.exists():
                new_filename = f"{idx}_{counter}{original_ext}"
                new_file_path = subdir / new_filename
                counter += 1
            
            # Rename the file
            print(f"  Renaming: {file_path.name} -> {new_filename}")
            file_path.rename(new_file_path)
        
        print(f"Completed directory: {subdir.name} ({len(files)} files renamed)\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python rename_sequentially.py <base_directory>")
        sys.exit(1)
    
    base_directory = sys.argv[1]
    
    if not os.path.isdir(base_directory):
        print(f"Error: {base_directory} is not a directory")
        sys.exit(1)
    
    rename_files_sequentially(base_directory)
    print("All directories processed successfully!")