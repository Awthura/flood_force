#!/usr/bin/env python3
import os
from pathlib import Path
from pydub import AudioSegment
import argparse
import concurrent.futures
import time

def convert_wav_to_ogg(wav_path, output_dir=None, delete_original=False):
    """
    Convert a WAV file to OGG format.
    
    Args:
        wav_path (str): Path to the WAV file
        output_dir (str, optional): Directory to save the OGG file. If None, uses same directory as WAV
        delete_original (bool): Whether to delete the original WAV file after conversion
        
    Returns:
        bool: True if conversion was successful, False otherwise
    """
    try:
        # Create Path objects
        wav_path = Path(wav_path)
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = wav_path.parent

        # Generate output path
        ogg_path = output_dir / f"{wav_path.stem}.ogg"
        
        # Load and convert the audio file
        audio = AudioSegment.from_wav(str(wav_path))
        audio.export(str(ogg_path), format="ogg")
        
        # Delete original if requested
        if delete_original:
            wav_path.unlink()
            
        print(f"Converted: {wav_path.name} -> {ogg_path.name}")
        return True
        
    except Exception as e:
        print(f"Error converting {wav_path.name}: {str(e)}")
        return False

def process_directory(input_dir, output_dir=None, delete_original=False, max_workers=None):
    """
    Process all WAV files in a directory and its subdirectories.
    
    Args:
        input_dir (str): Input directory containing WAV files
        output_dir (str, optional): Output directory for OGG files
        delete_original (bool): Whether to delete original WAV files
        max_workers (int, optional): Maximum number of worker threads
    """
    input_dir = Path(input_dir)
    wav_files = list(input_dir.rglob("*.wav"))
    total_files = len(wav_files)
    
    if total_files == 0:
        print("No WAV files found in the specified directory.")
        return
    
    print(f"Found {total_files} WAV files to convert")
    start_time = time.time()
    
    # Convert files using a thread pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(convert_wav_to_ogg, wav_file, output_dir, delete_original)
            for wav_file in wav_files
        ]
        
        # Wait for all conversions to complete
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            completed += 1
            print(f"Progress: {completed}/{total_files} files processed")
    
    elapsed_time = time.time() - start_time
    print(f"\nConversion completed in {elapsed_time:.2f} seconds")

def main():
    parser = argparse.ArgumentParser(description="Convert WAV files to OGG format")
    parser.add_argument("input_dir", help="Input directory containing WAV files")
    parser.add_argument("-o", "--output-dir", help="Output directory for OGG files")
    parser.add_argument("-d", "--delete-original", action="store_true",
                      help="Delete original WAV files after conversion")
    parser.add_argument("-w", "--workers", type=int, default=None,
                      help="Maximum number of worker threads")
    
    args = parser.parse_args()
    
    process_directory(
        args.input_dir,
        args.output_dir,
        args.delete_original,
        args.workers
    )

if __name__ == "__main__":
    main()