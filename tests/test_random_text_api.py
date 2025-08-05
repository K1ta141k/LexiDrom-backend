"""
Test suite for Random Text API endpoints
Tests the RACE dataset integration and random text generation functionality
"""

import pytest
import asyncio
import httpx
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List

# Test configuration
BASE_URL = "http://localhost:8000"
RANDOM_TEXT_BASE = f"{BASE_URL}/random-text"

class TestRandomTextAPI:
    """Test class for Random Text API endpoints"""
    
    @pytest.fixture
    async def client(self):
        """Create async HTTP client for testing"""
        async with httpx.AsyncClient() as client:
            yield client
    
    @pytest.fixture
    def mock_race_service(self):
        """Mock RACE dataset service"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.get_dataset_info.return_value = {
            'is_loaded': True,
            'total_articles': 27827,
            'dataset_name': 'RACE (Reading Comprehension from Examinations)',
            'description': 'A large-scale reading comprehension dataset with articles from English exams'
        }
        return mock_service
    
    @pytest.fixture
    def sample_random_text(self):
        """Sample random text response"""
        return {
            'text': 'This is a sample article from the RACE dataset. It contains educational content suitable for reading comprehension exercises.',
            'source': 'train',
            'id': 'test_article_001',
            'length': 150
        }
    
    @pytest.fixture
    def sample_multiple_texts(self):
        """Sample multiple random texts response"""
        return [
            {
                'text': 'First sample article from the RACE dataset.',
                'source': 'train',
                'id': 'test_article_001',
                'length': 50
            },
            {
                'text': 'Second sample article from the RACE dataset with more content.',
                'source': 'validation',
                'id': 'test_article_002',
                'length': 80
            },
            {
                'text': 'Third sample article from the RACE dataset for testing purposes.',
                'source': 'test',
                'id': 'test_article_003',
                'length': 70
            }
        ]

    async def test_get_random_text_success(self, client, mock_race_service, sample_random_text):
        """Test successful random text retrieval"""
        # Mock the service response
        mock_race_service.get_random_text.return_value = sample_random_text
        
        # Make request
        response = await client.get(f"{RANDOM_TEXT_BASE}/random")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert 'text' in data
        assert 'source' in data
        assert 'id' in data
        assert 'length' in data
        assert data['text'] == sample_random_text['text']
        assert data['source'] == sample_random_text['source']
        assert data['id'] == sample_random_text['id']
        assert data['length'] == sample_random_text['length']

    async def test_get_random_text_with_length_constraints(self, client, mock_race_service, sample_random_text):
        """Test random text retrieval with length constraints"""
        # Mock the service response
        mock_race_service.get_random_text.return_value = sample_random_text
        
        # Make request with length constraints
        response = await client.get(f"{RANDOM_TEXT_BASE}/random?min_length=100&max_length=200")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data['length'] >= 100
        assert data['length'] <= 200

    async def test_get_random_text_service_unavailable(self, client, mock_race_service):
        """Test random text when service is unavailable"""
        # Mock service as unavailable
        mock_race_service.is_available.return_value = False
        
        # Make request
        response = await client.get(f"{RANDOM_TEXT_BASE}/random")
        
        # Assertions
        assert response.status_code == 503
        data = response.json()
        assert 'detail' in data
        assert 'not available' in data['detail'].lower()

    async def test_get_random_text_no_suitable_text(self, client, mock_race_service):
        """Test random text when no suitable text is found"""
        # Mock service returning None
        mock_race_service.get_random_text.return_value = None
        
        # Make request
        response = await client.get(f"{RANDOM_TEXT_BASE}/random")
        
        # Assertions
        assert response.status_code == 404
        data = response.json()
        assert 'detail' in data
        assert 'not found' in data['detail'].lower()

    async def test_get_multiple_random_texts_success(self, client, mock_race_service, sample_multiple_texts):
        """Test successful multiple random texts retrieval"""
        # Mock the service response
        mock_race_service.get_random_texts.return_value = sample_multiple_texts
        
        # Make request
        response = await client.get(f"{RANDOM_TEXT_BASE}/random-multiple?count=3")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert 'texts' in data
        assert 'total_count' in data
        assert len(data['texts']) == 3
        assert data['total_count'] == 3
        
        # Check each text
        for i, text in enumerate(data['texts']):
            assert 'text' in text
            assert 'source' in text
            assert 'id' in text
            assert 'length' in text
            assert text['text'] == sample_multiple_texts[i]['text']

    async def test_get_multiple_random_texts_with_constraints(self, client, mock_race_service, sample_multiple_texts):
        """Test multiple random texts with length constraints"""
        # Mock the service response
        mock_race_service.get_random_texts.return_value = sample_multiple_texts
        
        # Make request with constraints
        response = await client.get(f"{RANDOM_TEXT_BASE}/random-multiple?count=2&min_length=50&max_length=100")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data['texts']) == 2
        
        # Check length constraints
        for text in data['texts']:
            assert text['length'] >= 50
            assert text['length'] <= 100

    async def test_get_multiple_random_texts_service_unavailable(self, client, mock_race_service):
        """Test multiple random texts when service is unavailable"""
        # Mock service as unavailable
        mock_race_service.is_available.return_value = False
        
        # Make request
        response = await client.get(f"{RANDOM_TEXT_BASE}/random-multiple?count=3")
        
        # Assertions
        assert response.status_code == 503
        data = response.json()
        assert 'detail' in data
        assert 'not available' in data['detail'].lower()

    async def test_get_multiple_random_texts_no_suitable_texts(self, client, mock_race_service):
        """Test multiple random texts when no suitable texts are found"""
        # Mock service returning empty list
        mock_race_service.get_random_texts.return_value = []
        
        # Make request
        response = await client.get(f"{RANDOM_TEXT_BASE}/random-multiple?count=3")
        
        # Assertions
        assert response.status_code == 404
        data = response.json()
        assert 'detail' in data
        assert 'not found' in data['detail'].lower()

    async def test_get_dataset_info_success(self, client, mock_race_service):
        """Test successful dataset info retrieval"""
        # Mock the service response
        mock_race_service.get_dataset_info.return_value = {
            'is_loaded': True,
            'total_articles': 27827,
            'dataset_name': 'RACE (Reading Comprehension from Examinations)',
            'description': 'A large-scale reading comprehension dataset with articles from English exams'
        }
        
        # Make request
        response = await client.get(f"{RANDOM_TEXT_BASE}/info")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert 'is_loaded' in data
        assert 'total_articles' in data
        assert 'dataset_name' in data
        assert 'description' in data
        assert data['is_loaded'] == True
        assert data['total_articles'] == 27827
        assert 'RACE' in data['dataset_name']

    async def test_get_dataset_info_service_not_initialized(self, client):
        """Test dataset info when service is not initialized"""
        # Make request without service
        response = await client.get(f"{RANDOM_TEXT_BASE}/info")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data['is_loaded'] == False
        assert data['total_articles'] == 0
        assert 'RACE' in data['dataset_name']

    async def test_health_check_success(self, client, mock_race_service):
        """Test successful health check"""
        # Mock the service response
        mock_race_service.is_available.return_value = True
        mock_race_service.get_dataset_info.return_value = {
            'total_articles': 27827
        }
        
        # Make request
        response = await client.get(f"{RANDOM_TEXT_BASE}/health")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert 'service' in data
        assert 'status' in data
        assert 'dataset_loaded' in data
        assert 'total_articles' in data
        assert data['service'] == 'random-text'
        assert data['status'] == 'healthy'
        assert data['dataset_loaded'] == True
        assert data['total_articles'] == 27827

    async def test_health_check_service_unavailable(self, client, mock_race_service):
        """Test health check when service is unavailable"""
        # Mock service as unavailable
        mock_race_service.is_available.return_value = False
        mock_race_service.get_dataset_info.return_value = {
            'total_articles': 0
        }
        
        # Make request
        response = await client.get(f"{RANDOM_TEXT_BASE}/health")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'unavailable'
        assert data['dataset_loaded'] == False
        assert data['total_articles'] == 0

    async def test_parameter_validation_min_length(self, client, mock_race_service, sample_random_text):
        """Test parameter validation for minimum length"""
        # Mock the service response
        mock_race_service.get_random_text.return_value = sample_random_text
        
        # Make request with very small min_length
        response = await client.get(f"{RANDOM_TEXT_BASE}/random?min_length=5")
        
        # Should still work (API adjusts min_length to 10)
        assert response.status_code == 200

    async def test_parameter_validation_max_length(self, client, mock_race_service, sample_random_text):
        """Test parameter validation for maximum length"""
        # Mock the service response
        mock_race_service.get_random_text.return_value = sample_random_text
        
        # Make request with very large max_length
        response = await client.get(f"{RANDOM_TEXT_BASE}/random?max_length=50000")
        
        # Should still work (API adjusts max_length to 10000)
        assert response.status_code == 200

    async def test_parameter_validation_count_limit(self, client, mock_race_service, sample_multiple_texts):
        """Test parameter validation for count limit"""
        # Mock the service response
        mock_race_service.get_random_texts.return_value = sample_multiple_texts
        
        # Make request with count > 10
        response = await client.get(f"{RANDOM_TEXT_BASE}/random-multiple?count=15")
        
        # Should still work (API limits count to 10)
        assert response.status_code == 200

    async def test_parameter_validation_swapped_lengths(self, client, mock_race_service, sample_random_text):
        """Test parameter validation when min_length > max_length"""
        # Mock the service response
        mock_race_service.get_random_text.return_value = sample_random_text
        
        # Make request with min_length > max_length
        response = await client.get(f"{RANDOM_TEXT_BASE}/random?min_length=1000&max_length=500")
        
        # Should still work (API swaps the values)
        assert response.status_code == 200

class TestRandomTextAPIIntegration:
    """Integration tests for Random Text API with actual service"""
    
    @pytest.fixture
    async def client(self):
        """Create async HTTP client for testing"""
        async with httpx.AsyncClient() as client:
            yield client
    
    @pytest.mark.integration
    async def test_live_api_health_check(self, client):
        """Test health check with live API"""
        try:
            response = await client.get(f"{RANDOM_TEXT_BASE}/health")
            assert response.status_code == 200
            data = response.json()
            assert 'service' in data
            assert data['service'] == 'random-text'
        except httpx.ConnectError:
            pytest.skip("API server not running")

    @pytest.mark.integration
    async def test_live_api_dataset_info(self, client):
        """Test dataset info with live API"""
        try:
            response = await client.get(f"{RANDOM_TEXT_BASE}/info")
            assert response.status_code == 200
            data = response.json()
            assert 'dataset_name' in data
            assert 'RACE' in data['dataset_name']
        except httpx.ConnectError:
            pytest.skip("API server not running")

    @pytest.mark.integration
    async def test_live_api_random_text(self, client):
        """Test random text with live API"""
        try:
            response = await client.get(f"{RANDOM_TEXT_BASE}/random")
            assert response.status_code == 200
            data = response.json()
            assert 'text' in data
            assert 'source' in data
            assert 'id' in data
            assert 'length' in data
            assert len(data['text']) > 0
        except httpx.ConnectError:
            pytest.skip("API server not running")

    @pytest.mark.integration
    async def test_live_api_multiple_random_texts(self, client):
        """Test multiple random texts with live API"""
        try:
            response = await client.get(f"{RANDOM_TEXT_BASE}/random-multiple?count=2")
            assert response.status_code == 200
            data = response.json()
            assert 'texts' in data
            assert 'total_count' in data
            assert len(data['texts']) == 2
            assert data['total_count'] == 2
        except httpx.ConnectError:
            pytest.skip("API server not running")

def run_tests():
    """Run the test suite"""
    import sys
    import os
    
    # Add the project root to Python path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    
    # Run pytest
    pytest.main([
        __file__,
        "-v",
        "--tb=short"
    ])

if __name__ == "__main__":
    run_tests() 