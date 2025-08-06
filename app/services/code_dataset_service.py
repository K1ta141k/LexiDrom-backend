"""
Code Dataset Service
Handles loading and managing code datasets for random code generation

Citation:
- Paper: "CodeSearchNet Challenge: Evaluating the State of Semantic Code Search" (2019)
- Authors: Husain, H., Wu, H. H., Gazit, T., Allamanis, M., & Brockschmidt, M.
- DOI: arXiv:1909.09436
- Dataset: 6.4M code functions from 6 programming languages (Go, Java, JavaScript, PHP, Python, Ruby)
- License: MIT License
- Source: GitHub repositories with permissive licenses
"""

import random
from typing import Dict, List, Optional
from datasets import load_dataset

class CodeDatasetService:
    def __init__(self):
        self.dataset = None
        self.code_samples = []
        self.is_loaded = False
        self.languages = ['python', 'javascript', 'java', 'go', 'php', 'ruby']
        self.difficulty_levels = ['beginner', 'intermediate', 'advanced']
        
    async def load_dataset(self) -> bool:
        """Load the CodeSearchNet dataset from HuggingFace"""
        try:
            print("📚 Loading CodeSearchNet dataset...")
            
            # Load dataset for each language
            self.code_samples = []
            
            for language in self.languages:
                try:
                    print(f"📖 Loading {language} code samples...")
                    dataset = load_dataset("code_search_net", language, trust_remote_code=True)
                    
                    # Process train split with limit of 10 samples per language
                    samples_count = 0
                    if 'train' in dataset:
                        for item in dataset['train']:
                            if samples_count >= 10:  # Limit to 10 samples per language
                                break
                            if 'func_code_string' in item and item['func_code_string']:
                                # Estimate difficulty based on code complexity
                                difficulty = self._estimate_difficulty(item['func_code_string'])
                                
                                self.code_samples.append({
                                    'code': item['func_code_string'],
                                    'language': language,
                                    'difficulty': difficulty,
                                    'source': 'train',
                                    'id': item.get('func_name', f"{language}_unknown"),
                                    'docstring': item.get('func_documentation_string', ''),
                                    'url': item.get('func_code_url', '')
                                })
                                samples_count += 1
                    
                    print(f"✅ Loaded {len([s for s in self.code_samples if s['language'] == language])} {language} samples")
                    
                except Exception as e:
                    print(f"⚠️ Error loading {language} dataset: {e}")
                    continue
            
            self.is_loaded = True
            print(f"✅ CodeSearchNet dataset loaded successfully! Total samples: {len(self.code_samples)}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading CodeSearchNet dataset: {e}")
            self.is_loaded = False
            return False
    
    def _estimate_difficulty(self, code: str) -> str:
        """Estimate code difficulty based on complexity metrics"""
        lines = code.split('\n')
        line_count = len(lines)
        
        # Count complexity indicators
        complexity_score = 0
        
        # Function definitions (multi-language)
        complexity_score += code.count('def ') * 2
        complexity_score += code.count('function ') * 2
        complexity_score += code.count('class ') * 3
        complexity_score += code.count('=>') * 2  # Arrow functions
        complexity_score += code.count('const ') * 1
        complexity_score += code.count('let ') * 1
        complexity_score += code.count('var ') * 1
        
        # Control structures
        complexity_score += code.count('if ') * 1
        complexity_score += code.count('for ') * 2
        complexity_score += code.count('while ') * 2
        complexity_score += code.count('try:') * 2
        complexity_score += code.count('except') * 2
        complexity_score += code.count('catch') * 2
        complexity_score += code.count('switch') * 2
        complexity_score += code.count('case') * 1
        
        # Advanced features
        complexity_score += code.count('lambda ') * 3
        complexity_score += code.count('import ') * 1
        complexity_score += code.count('from ') * 1
        complexity_score += code.count('async ') * 3
        complexity_score += code.count('await ') * 2
        complexity_score += code.count('Promise') * 2
        complexity_score += code.count('then(') * 2
        complexity_score += code.count('catch(') * 2
        complexity_score += code.count('return ') * 1
        
        # Object-oriented features
        complexity_score += code.count('this.') * 2
        complexity_score += code.count('new ') * 2
        complexity_score += code.count('extends') * 3
        complexity_score += code.count('implements') * 3
        
        # Normalize by line count
        if line_count > 0:
            normalized_score = complexity_score / line_count
        else:
            normalized_score = 0
        
        # Determine difficulty level
        if normalized_score < 0.8 and line_count < 25:
            return 'beginner'
        elif normalized_score < 2.0 and line_count < 60:
            return 'intermediate'
        else:
            return 'advanced'
    
    def get_random_code(
        self, 
        language: Optional[str] = None,
        difficulty: Optional[str] = None,
        min_length: int = 50,
        max_length: int = 2000
    ) -> Optional[Dict]:
        """Get a random code sample with optional filters"""
        if not self.is_loaded or not self.code_samples:
            return None
        
        # Filter samples by criteria
        suitable_samples = self.code_samples
        
        # Filter by language
        if language and language.lower() in self.languages:
            suitable_samples = [
                sample for sample in suitable_samples
                if sample['language'].lower() == language.lower()
            ]
        
        # Filter by difficulty
        if difficulty and difficulty.lower() in self.difficulty_levels:
            suitable_samples = [
                sample for sample in suitable_samples
                if sample['difficulty'].lower() == difficulty.lower()
            ]
        
        # Filter by length
        suitable_samples = [
            sample for sample in suitable_samples
            if min_length <= len(sample['code']) <= max_length
        ]
        
        if not suitable_samples:
            # If no samples match the criteria, return any sample
            suitable_samples = self.code_samples
        
        if not suitable_samples:
            return None
        
        # Select random sample
        selected_sample = random.choice(suitable_samples)
        
        return {
            'code': selected_sample['code'],
            'language': selected_sample['language'],
            'difficulty': selected_sample['difficulty'],
            'source': selected_sample['source'],
            'id': selected_sample['id'],
            'length': len(selected_sample['code']),
            'docstring': selected_sample.get('docstring', ''),
            'url': selected_sample.get('url', '')
        }
    
    def get_random_codes(
        self,
        count: int = 1,
        language: Optional[str] = None,
        difficulty: Optional[str] = None,
        min_length: int = 50,
        max_length: int = 2000
    ) -> List[Dict]:
        """Get multiple random code samples with optional filters"""
        if not self.is_loaded or not self.code_samples:
            return []
        
        # Filter samples by criteria
        suitable_samples = self.code_samples
        
        # Filter by language
        if language and language.lower() in self.languages:
            suitable_samples = [
                sample for sample in suitable_samples
                if sample['language'].lower() == language.lower()
            ]
        
        # Filter by difficulty
        if difficulty and difficulty.lower() in self.difficulty_levels:
            suitable_samples = [
                sample for sample in suitable_samples
                if sample['difficulty'].lower() == difficulty.lower()
            ]
        
        # Filter by length
        suitable_samples = [
            sample for sample in suitable_samples
            if min_length <= len(sample['code']) <= max_length
        ]
        
        if not suitable_samples:
            # If no samples match the criteria, use any samples
            suitable_samples = self.code_samples
        
        if not suitable_samples:
            return []
        
        # Select random samples (without replacement if possible)
        count = min(count, len(suitable_samples))
        selected_samples = random.sample(suitable_samples, count)
        
        return [
            {
                'code': sample['code'],
                'language': sample['language'],
                'difficulty': sample['difficulty'],
                'source': sample['source'],
                'id': sample['id'],
                'length': len(sample['code']),
                'docstring': sample.get('docstring', ''),
                'url': sample.get('url', '')
            }
            for sample in selected_samples
        ]
    
    def get_available_languages(self) -> List[str]:
        """Get list of available programming languages"""
        if not self.is_loaded:
            return []
        
        languages = set()
        for sample in self.code_samples:
            languages.add(sample['language'])
        
        return sorted(list(languages))
    
    def get_available_difficulties(self) -> List[str]:
        """Get list of available difficulty levels"""
        if not self.is_loaded:
            return []
        
        difficulties = set()
        for sample in self.code_samples:
            difficulties.add(sample['difficulty'])
        
        return sorted(list(difficulties))
    
    def get_dataset_info(self) -> Dict:
        """Get information about the loaded dataset"""
        if not self.is_loaded:
            return {
                'is_loaded': False,
                'total_samples': 0,
                'dataset_name': 'CodeSearchNet',
                'description': 'A large-scale dataset of code functions from multiple programming languages',
                'available_languages': [],
                'available_difficulties': []
            }
        
        # Count samples by language and difficulty
        language_counts = {}
        difficulty_counts = {}
        
        for sample in self.code_samples:
            lang = sample['language']
            diff = sample['difficulty']
            
            language_counts[lang] = language_counts.get(lang, 0) + 1
            difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
        
        return {
            'is_loaded': self.is_loaded,
            'total_samples': len(self.code_samples),
            'dataset_name': 'CodeSearchNet',
            'description': 'A large-scale dataset of code functions from multiple programming languages',
            'available_languages': self.get_available_languages(),
            'available_difficulties': self.get_available_difficulties(),
            'language_distribution': language_counts,
            'difficulty_distribution': difficulty_counts,
            'citation': {
                'paper': 'CodeSearchNet Challenge: Evaluating the State of Semantic Code Search',
                'authors': 'Husain, H., Wu, H. H., Gazit, T., Allamanis, M., & Brockschmidt, M.',
                'year': 2019,
                'doi': 'arXiv:1909.09436',
                'url': 'https://arxiv.org/abs/1909.09436',
                'license': 'MIT License',
                'source': 'HuggingFace Datasets'
            }
        }
    
    def is_available(self) -> bool:
        """Check if the dataset service is available"""
        return self.is_loaded and len(self.code_samples) > 0 