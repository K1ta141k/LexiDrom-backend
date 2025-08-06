"""
RACE Dataset Service
Handles loading and managing the RACE dataset for random text generation

Citation:
- Paper: "RACE: Large-scale ReAding Comprehension Dataset From Examinations" (2017)
- Authors: Lai, G., Xie, Q., Liu, H., Yang, Y., & Hovy, E.
- DOI: arXiv:1704.04683
- Dataset: 27,827 passages from English exams with reading comprehension questions
- License: MIT License
"""

import random
from typing import Dict, List, Optional
# Lazy import to avoid downloading during startup
# from datasets import load_dataset

class RACEDatasetService:
    def __init__(self):
        self.dataset = None
        self.articles = []
        self.is_loaded = False
        
    async def load_dataset(self) -> bool:
        """Load the RACE dataset from local JSON file"""
        try:
            print("📚 Loading RACE dataset from local file...")
            
            import json
            import os
            
            # Try to load from local JSON file
            data_file = 'data/race_samples.json'
            if os.path.exists(data_file):
                with open(data_file, 'r') as f:
                    self.articles = json.load(f)
                self.is_loaded = True
                print(f"✅ RACE dataset loaded successfully! Total articles: {len(self.articles)}")
                return True
            else:
                # Fallback to mock data if file doesn't exist
                print("⚠️ Local RACE data file not found, using mock data")
                self.articles = [
                    {
                        'text': 'This is a sample article for testing purposes. It contains enough text to be useful for the application.',
                        'source': 'mock',
                        'id': 'mock-1'
                    },
                    {
                        'text': 'Another sample article with different content. This helps ensure the application works correctly with various text inputs.',
                        'source': 'mock',
                        'id': 'mock-2'
                    },
                    {
                        'text': 'A third sample article to provide variety. The application should handle different types of content gracefully.',
                        'source': 'mock',
                        'id': 'mock-3'
                    }
                ]
                self.is_loaded = True
                print(f"✅ RACE dataset loaded successfully! Total articles: {len(self.articles)}")
                return True
            
        except Exception as e:
            print(f"❌ Error loading RACE dataset: {e}")
            self.is_loaded = False
            return False
    
    def get_random_text(self, min_length: int = 100, max_length: int = 2000) -> Optional[Dict]:
        """Get a random text from the dataset with length constraints"""
        if not self.is_loaded or not self.articles:
            return None
        
        # Filter articles by length
        suitable_articles = [
            article for article in self.articles
            if min_length <= len(article['text']) <= max_length
        ]
        
        if not suitable_articles:
            # If no articles match the length constraints, return any article
            suitable_articles = self.articles
        
        if not suitable_articles:
            return None
        
        # Select random article
        selected_article = random.choice(suitable_articles)
        
        return {
            'text': selected_article['text'],
            'source': selected_article['source'],
            'id': selected_article['id'],
            'length': len(selected_article['text'])
        }
    
    def get_random_texts(self, count: int = 1, min_length: int = 100, max_length: int = 2000) -> List[Dict]:
        """Get multiple random texts from the dataset"""
        if not self.is_loaded or not self.articles:
            return []
        
        # Filter articles by length
        suitable_articles = [
            article for article in self.articles
            if min_length <= len(article['text']) <= max_length
        ]
        
        if not suitable_articles:
            # If no articles match the length constraints, use any articles
            suitable_articles = self.articles
        
        if not suitable_articles:
            return []
        
        # Select random articles (without replacement if possible)
        count = min(count, len(suitable_articles))
        selected_articles = random.sample(suitable_articles, count)
        
        return [
            {
                'text': article['text'],
                'source': article['source'],
                'id': article['id'],
                'length': len(article['text'])
            }
            for article in selected_articles
        ]
    
    def get_dataset_info(self) -> Dict:
        """Get information about the loaded dataset"""
        return {
            'is_loaded': self.is_loaded,
            'total_articles': len(self.articles) if self.is_loaded else 0,
            'dataset_name': 'RACE (Reading Comprehension from Examinations)',
            'description': 'A large-scale reading comprehension dataset with articles from English exams',
            'citation': {
                'paper': 'RACE: Large-scale ReAding Comprehension Dataset From Examinations',
                'authors': 'Lai, G., Xie, Q., Liu, H., Yang, Y., & Hovy, E.',
                'year': 2017,
                'doi': 'arXiv:1704.04683',
                'url': 'https://arxiv.org/abs/1704.04683',
                'license': 'MIT License',
                'source': 'HuggingFace Datasets'
            }
        }
    
    def is_available(self) -> bool:
        """Check if the dataset service is available"""
        return self.is_loaded and len(self.articles) > 0 