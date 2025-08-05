"""
Test text comparison functionality
"""

import asyncio
import os
from app.services.text_comparison_service import TextComparisonService

async def test_text_comparison():
    """Test text comparison with Google AI"""
    print("🧪 Testing text comparison...")
    
    # Initialize service
    service = TextComparisonService()
    
    # Test data
    original_text = """
    Artificial Intelligence (AI) has revolutionized the way we interact with technology. 
    Machine learning algorithms can now process vast amounts of data to identify patterns 
    and make predictions. Deep learning, a subset of machine learning, uses neural networks 
    to model complex relationships in data. These technologies are being applied across 
    various industries including healthcare, finance, and transportation.
    """
    
    summary_text = """
    AI uses machine learning and deep learning to process data and make predictions. 
    It's used in healthcare, finance, and transportation.
    """
    
    # Test comparison
    try:
        accuracy_score, correct_points, missed_points, wrong_points = await service.compare_texts(
            original_text=original_text,
            summary_text=summary_text,
            reading_mode="detailed"
        )
        
        print(f"✅ Text comparison completed")
        print(f"   Accuracy Score: {accuracy_score}")
        print(f"   Correct Points: {len(correct_points)}")
        print(f"   Missed Points: {len(missed_points)}")
        print(f"   Wrong Points: {len(wrong_points)}")
        
        # Print details
        if correct_points:
            print("\n   Correct Points:")
            for point in correct_points[:3]:  # Show first 3
                print(f"     • {point}")
        
        if missed_points:
            print("\n   Missed Points:")
            for point in missed_points[:3]:  # Show first 3
                print(f"     • {point}")
        
        if wrong_points:
            print("\n   Wrong Points:")
            for point in wrong_points[:3]:  # Show first 3
                print(f"     • {point}")
        
        return True
        
    except Exception as e:
        print(f"❌ Text comparison failed: {e}")
        return False

async def test_different_reading_modes():
    """Test different reading modes"""
    print("\n🧪 Testing different reading modes...")
    
    service = TextComparisonService()
    
    original_text = """
    The Industrial Revolution was a period of major industrialization and innovation 
    during the late 18th and early 19th centuries. The Industrial Revolution began 
    in Great Britain and quickly spread throughout the world. This period saw the 
    development of new manufacturing processes, the rise of factory systems, and 
    significant social and economic changes.
    """
    
    summary_text = """
    The Industrial Revolution was a time of major changes in manufacturing and society.
    """
    
    reading_modes = ["skimming", "detailed", "critical"]
    
    for mode in reading_modes:
        try:
            accuracy_score, correct_points, missed_points, wrong_points = await service.compare_texts(
                original_text=original_text,
                summary_text=summary_text,
                reading_mode=mode
            )
            
            print(f"   {mode.capitalize()} mode - Accuracy: {accuracy_score}")
            
        except Exception as e:
            print(f"   ❌ {mode} mode failed: {e}")

async def test_simple_comparison():
    """Test simple comparison when AI is not available"""
    print("\n🧪 Testing simple comparison...")
    
    # Temporarily remove API key to test fallback
    original_key = os.getenv("GOOGLE_API_KEY")
    if original_key:
        os.environ["GOOGLE_API_KEY"] = ""
    
    try:
        service = TextComparisonService()
        
        original_text = "This is a test of the simple comparison functionality."
        summary_text = "This tests simple comparison."
        
        accuracy_score, correct_points, missed_points, wrong_points = await service.compare_texts(
            original_text=original_text,
            summary_text=summary_text
        )
        
        print(f"✅ Simple comparison completed")
        print(f"   Accuracy Score: {accuracy_score}")
        print(f"   Correct Points: {len(correct_points)}")
        print(f"   Missed Points: {len(missed_points)}")
        print(f"   Wrong Points: {len(wrong_points)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Simple comparison failed: {e}")
        return False
    finally:
        # Restore API key
        if original_key:
            os.environ["GOOGLE_API_KEY"] = original_key

def main():
    """Run text comparison tests"""
    print("🚀 Starting Text Comparison Tests\n")
    
    # Run tests
    try:
        # Test basic comparison
        basic_ok = asyncio.run(test_text_comparison())
        
        # Test different reading modes
        asyncio.run(test_different_reading_modes())
        
        # Test simple comparison
        simple_ok = asyncio.run(test_simple_comparison())
        
        # Summary
        print("\n📊 Test Results:")
        print(f"   Basic Comparison: {'✅ PASS' if basic_ok else '❌ FAIL'}")
        print(f"   Simple Comparison: {'✅ PASS' if simple_ok else '❌ FAIL'}")
        
        if basic_ok and simple_ok:
            print("\n🎉 Text comparison tests passed!")
            return True
        else:
            print("\n❌ Some text comparison tests failed.")
            return False
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

if __name__ == "__main__":
    main() 