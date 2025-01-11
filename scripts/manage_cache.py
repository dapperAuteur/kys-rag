# scripts/manage_cache.py

import argparse
import json
from datetime import timedelta
from app.core.cache_manager import cache_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_age(age_str: str) -> timedelta:
    """Parse age string into timedelta.
    
    Formats:
        7d  = 7 days
        24h = 24 hours
        30m = 30 minutes
    """
    if not age_str:
        return cache_manager.MAX_FILE_AGE
        
    try:
        value = int(age_str[:-1])
        unit = age_str[-1].lower()
        
        if unit == 'd':
            return timedelta(days=value)
        elif unit == 'h':
            return timedelta(hours=value)
        elif unit == 'm':
            return timedelta(minutes=value)
        else:
            raise ValueError(f"Invalid age unit: {unit}")
    except Exception as e:
        logger.error(f"Error parsing age '{age_str}': {e}")
        return cache_manager.MAX_FILE_AGE

def display_cache_stats(stats: dict):
    """Display cache statistics in a readable format."""
    print("\nCache Statistics:")
    print("----------------")
    
    for cache_type, info in stats.items():
        print(f"\n{cache_type.upper()}:")
        for key, value in info.items():
            if isinstance(value, (int, float)) and 'bytes' in key:
                print(f"  {key}: {value:,} bytes")
            elif isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")

def main():
    parser = argparse.ArgumentParser(description='Manage application cache')
    parser.add_argument(
        '--action',
        choices=['stats', 'clear', 'cleanup'],
        default='stats',
        help='Action to perform'
    )
    parser.add_argument(
        '--cache-type',
        choices=['model', 'main', 'all'],
        default='all',
        help='Type of cache to manage'
    )
    parser.add_argument(
        '--format',
        choices=['human', 'json'],
        default='human',
        help='Output format'
    )
    parser.add_argument(
        '--max-age',
        help='Maximum file age for cleanup (e.g., 7d, 24h, 30m)',
        default=''
    )
    
    args = parser.parse_args()
    
    try:
        if args.action == 'stats':
            stats = cache_manager.get_cache_stats(force_check=True)
            if args.format == 'json':
                print(json.dumps(stats, indent=2))
            else:
                display_cache_stats(stats)
        
        elif args.action == 'clear':
            cache_type = None if args.cache_type == 'all' else args.cache_type
            success = cache_manager.clear_cache(cache_type)
            if success:
                print(f"Successfully cleared {args.cache_type} cache")
            else:
                print(f"Failed to clear {args.cache_type} cache")
                
        elif args.action == 'cleanup':
            max_age = parse_age(args.max_age)
            cleanup_stats = cache_manager.cleanup_old_files(max_age)
            
            if args.format == 'json':
                print(json.dumps(cleanup_stats, indent=2))
            else:
                print("\nCleanup Results:")
                print(f"Files removed: {cleanup_stats['removed']}")
                print(f"Failed removals: {cleanup_stats['failed']}")
                print(f"Space freed: {cache_manager.bytes_to_gb(cleanup_stats['size_freed']):.2f}GB")
    
    except Exception as e:
        logger.error(f"Error managing cache: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())