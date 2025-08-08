import os
import hashlib
from PIL import Image
import imagehash
from collections import defaultdict

class Duplicate:
    def __init__(self):
        pass
    
    def find_exact_duplicates(self, image_paths):
        """Find exact duplicates using file size + partial hash"""
        print("Finding exact duplicates...")
        
        # Group by file size first (fast filter)
        size_groups = defaultdict(list)
        for path in image_paths:
            try:
                size = os.path.getsize(path)
                size_groups[size].append(path)
            except:
                continue
        
        # Check files with same size using hash
        duplicates = []
        for size, paths in size_groups.items():
            if len(paths) > 1:
                hash_groups = defaultdict(list)
                for path in paths:
                    try:
                        # Quick hash of first 8KB
                        with open(path, 'rb') as f:
                            chunk = f.read(8192)
                            quick_hash = hashlib.md5(chunk).hexdigest()
                            hash_groups[quick_hash].append(path)
                    except:
                        continue
                
                # Add groups with duplicates
                for hash_val, dup_paths in hash_groups.items():
                    if len(dup_paths) > 1:
                        duplicates.append(dup_paths)
        
        return duplicates
    
    def find_similar_images(self, image_paths, max_distance=5):
        """Find similar images using perceptual hashing"""
        print("Finding similar images...")
        
        # Calculate perceptual hashes
        hashes = {}
        for path in image_paths:
            try:
                with Image.open(path) as img:
                    # Convert to grayscale, resize small for speed
                    img = img.convert('L').resize((64, 64))
                    phash = imagehash.phash(img)
                    hashes[path] = phash
            except:
                continue
        
        # Find similar pairs
        similar_groups = []
        processed = set()
        
        paths = list(hashes.keys())
        for i, path1 in enumerate(paths):
            if path1 in processed:
                continue
                
            group = [path1]
            processed.add(path1)
            
            for path2 in paths[i+1:]:
                if path2 in processed:
                    continue
                    
                # Calculate Hamming distance
                distance = hashes[path1] - hashes[path2]
                if distance <= max_distance:
                    group.append(path2)
                    processed.add(path2)
            
            if len(group) > 1:
                similar_groups.append(group)
        
        return similar_groups
    
    def get_deletion_suggestions(self, duplicates, similar_groups):
        """Simple suggestions: keep newest file in each group"""
        suggestions = []
        
        for group in duplicates + similar_groups:
            # Sort by modification time (newest first)
            sorted_group = sorted(group, key=lambda x: os.path.getmtime(x), reverse=True)
            # Suggest deleting all but the newest
            suggestions.extend(sorted_group[1:])
        
        return suggestions
