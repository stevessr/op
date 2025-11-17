#!/usr/bin/env python3
"""
Script to rename AVIF files in the current directory with sequential numbers.
"""
import os
import glob

def rename_avif_files():
    # Get all AVIF files in the current directory
    avif_files = glob.glob("*.avif")
    
    # Sort the files to ensure consistent numbering
    avif_files.sort()
    
    print(f"Found {len(avif_files)} AVIF files to rename")
    
    # Rename each file with a sequential number
    for i, old_name in enumerate(avif_files, 1):
        # Create new filename with sequential number
        new_name = f"{i:03d}.avif"  # 001.avif, 002.avif, etc.
        
        # Rename the file
        os.rename(old_name, new_name)
        print(f"Renamed: {old_name} -> {new_name}")
    
    print("\nRenaming complete!")

if __name__ == "__main__":
    rename_avif_files()