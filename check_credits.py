"""
Check Anthropic API Credits and Usage
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv


function calculateSum(

)
# Load environment variables
load_dotenv()

def check_credits():
    """Check Anthropic API credits and usage"""

    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not found in environment")
        print("Please set it in your .env file")
        return

    try:
        client = Anthropic(api_key=api_key)

        print("=" * 70)
        print("Anthropic API Credit Check")
        print("=" * 70)
        print()

        # Try to get usage information
        # Note: Anthropic doesn't have a direct "get credits" API endpoint
        # We need to check via a small test request and look at headers

        print("Testing API connection...")

        # Make a minimal request to check if API works
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )

        print("✓ API Key is valid")
        print("✓ Connection successful")
        print()

        # Check response headers for usage info
        if hasattr(response, '_headers'):
            headers = response._headers
            print("Response Headers:")
            for key, value in headers.items():
                if 'usage' in key.lower() or 'limit' in key.lower() or 'remaining' in key.lower():
                    print(f"  {key}: {value}")

        print()
        print("Usage from this test request:")
        print(f"  Input tokens: {response.usage.input_tokens}")
        print(f"  Output tokens: {response.usage.output_tokens}")
        print()

        print("=" * 70)
        print("To check your credit balance:")
        print("=" * 70)
        print()
        print("1. Visit: https://console.anthropic.com/settings/billing")
        print("2. Log in with your Anthropic account")
        print("3. Check 'Current Balance' and 'Usage'")
        print()
        print("Note: The Anthropic API doesn't provide a programmatic way")
        print("      to check credit balance. You must use the web console.")
        print()
        print("=" * 70)
        print()

        # Try to estimate based on error message
        print("Testing credit availability with another request...")
        try:
            test_response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=10,
                messages=[{"role": "user", "content": "Test"}]
            )
            print("✓ Credits available - API is working")

        except Exception as e:
            error_str = str(e)
            if "credit balance is too low" in error_str.lower():
                print("⚠ WARNING: Your credit balance is too low!")
                print("  Please add credits at:")
                print("  https://console.anthropic.com/settings/billing")
            elif "rate limit" in error_str.lower():
                print("⚠ Rate limit reached")
                print(f"  Error: {error_str}")
            else:
                print(f"⚠ Error: {error_str}")

        print()
        print("=" * 70)

    except Exception as e:
        print()
        print("ERROR:", str(e))
        print()

        if "credit balance is too low" in str(e).lower():
            print("⚠ Your Anthropic API credit balance is too low!")
            print()
            print("To add credits:")
            print("  1. Go to: https://console.anthropic.com/settings/billing")
            print("  2. Click 'Purchase Credits' or upgrade your plan")
            print("  3. Minimum purchase is usually $5")
            print()
        elif "authentication" in str(e).lower() or "api key" in str(e).lower():
            print("⚠ API Key issue detected")
            print()
            print("Please check:")
            print("  1. Your .env file contains: ANTHROPIC_API_KEY=sk-ant-...")
            print("  2. The API key is valid")
            print("  3. No extra spaces or quotes around the key")
            print()
        else:
            print("Unexpected error. Please check your API key and connection.")

        print("=" * 70)


if __name__ == "__main__":
    check_credits()
