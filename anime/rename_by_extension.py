#!/usr/bin/env python3
"""
Script to rename files in each subdirectory with sequential numbers by extension.
Each subdirectory will have its files renamed separately by extension.
For example, in a folder with .jpg and .png files:
- .jpg files: 1.jpg, 2.jpg, 3.jpg, etc.
- .png files: 1.png, 2.png, 3.png, etc.
"""
import os
import shutil
from pathlib import Path
from collections import defaultdict
import tempfile

def rename_files_by_extension(base_dir):
    """
    Rename files in each subdirectory with sequential numbers by extension.
    
    Args:
        base_dir (str): Path to the base directory containing subdirectories
    """
    base_path = Path(base_dir)
    
    # Get all subdirectories
    subdirs = [d for d in base_path.iterdir() if d.is_dir()]
    
    for subdir in subdirs:
        print(f"Processing directory: {subdir.name}")
        
        # Group files by extension
        files_by_ext = defaultdict(list)
        
        # Get all files in the subdirectory
        files = [f for f in subdir.iterdir() if f.is_file()]
        
        # Group files by extension
        for file_path in files:
            ext = file_path.suffix.lower()  # Use lowercase for consistent grouping
            files_by_ext[ext].append(file_path)
        
        # Process each extension group separately
        for ext, ext_files in files_by_ext.items():
            # Sort files to ensure consistent ordering
            ext_files.sort(key=lambda x: x.name)
            
            # First, rename all files to temporary names to avoid conflicts
            temp_files = []
            for idx, file_path in enumerate(ext_files):
                temp_name = f"temp_{idx + 1}{ext}"
                temp_path = subdir / temp_name
                file_path.rename(temp_path)
                temp_files.append(temp_path)
            
            # Then rename from temporary names to final sequential names
            for idx, temp_path in enumerate(temp_files, start=1):
                new_filename = f"{idx}{ext}"
                new_file_path = subdir / new_filename
                
                # Handle potential naming conflicts by adding a suffix
                counter = 1
                while new_file_path.exists():
                    new_filename = f"{idx}_{counter}{ext}"
                    new_file_path = subdir / new_filename
                    counter += 1
                
                # Rename the file
                print(f"  Renaming: {temp_path.name} -> {new_filename}")
                temp_path.rename(new_file_path)
        
        print(f"Completed directory: {subdir.name}\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python rename_by_extension.py <base_directory>")
        sys.exit(1)
    
    base_directory = sys.argv[1]
    
    if not os.path.isdir(base_directory):
        print(f"Error: {base_directory} is not a directory")
        sys.exit(1)
    
    rename_files_by_extension(base_directory)
    print("All directories processed successfully!")