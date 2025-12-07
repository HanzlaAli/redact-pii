"""
Test script for the PII Redaction API.
"""
import requests
import sys
import os


def test_api(image_path: str, api_url: str = "http://localhost:5000"):
    """
    Test the PII redaction API with an image file.
    
    Args:
        image_path: Path to the image file to test
        api_url: Base URL of the API (default: http://localhost:5000)
    """
    if not os.path.exists(image_path):
        print(f"Error: File not found: {image_path}")
        return False
    
    endpoint = f"{api_url}/redact-pii"
    
    print(f"Testing PII Redaction API...")
    print(f"API URL: {endpoint}")
    print(f"Image: {image_path}")
    print("-" * 50)
    
    try:
        # Test health endpoint first
        print("\n1. Testing health endpoint...")
        health_response = requests.get(f"{api_url}/health")
        if health_response.status_code == 200:
            print(f"✓ Health check passed: {health_response.json()}")
        else:
            print(f"✗ Health check failed: {health_response.status_code}")
            return False
        
        # Test redaction endpoint
        print("\n2. Testing redaction endpoint...")
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(endpoint, files=files)
        
        if response.status_code == 200:
            # Save the redacted image
            output_path = f"redacted_{os.path.basename(image_path)}"
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✓ Redaction successful!")
            print(f"✓ Redacted image saved to: {output_path}")
            print(f"✓ Response size: {len(response.content)} bytes")
            return True
        else:
            print(f"✗ Redaction failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Response: {response.text}")
            return False
    
    except requests.exceptions.ConnectionError:
        print(f"✗ Connection error: Could not connect to {api_url}")
        print("Make sure the API server is running (python app.py)")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_api.py <image_path> [api_url]")
        print("Example: python test_api.py sample_image.png")
        print("Example: python test_api.py sample_image.png http://localhost:5000")
        sys.exit(1)
    
    image_path = sys.argv[1]
    api_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:5000"
    
    success = test_api(image_path, api_url)
    sys.exit(0 if success else 1)
