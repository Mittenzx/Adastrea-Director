#!/usr/bin/env python3
"""
API Key Testing Script for Adastrea Director

This script tests the API keys defined in .env and helps diagnose configuration issues.
It checks:
1. Dependencies are properly installed
2. API keys are properly configured
3. API keys can authenticate with their respective services
4. All supported LLM providers (Gemini, OpenAI, OpenRouter)

Usage:
    python test_api_keys.py              # Test all configured providers
    python test_api_keys.py --provider gemini     # Test specific provider
    python test_api_keys.py --all        # Test all providers (even if not configured)
    python test_api_keys.py --skip-api-test       # Only check configuration, no API calls
"""

import os
import sys
import argparse
import importlib
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass, field
from datetime import datetime

# Constants
DEFAULT_PROVIDER = "gemini"
MAX_RESPONSE_LENGTH = 50
GEMINI_MODEL = "gemini-1.5-flash"
OPENAI_MODEL = "gpt-3.5-turbo"
OPENROUTER_MODEL = "mistralai/mistral-7b-instruct:free"

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
    ENV_LOADED = True
except ImportError:
    ENV_LOADED = False


@dataclass
class TestResult:
    """Result of a test."""
    component: str
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)


class APIKeyTester:
    """Tests API keys and system configuration."""
    
    def __init__(self, verbose: bool = False):
        """Initialize the tester."""
        self.verbose = verbose
        self.results: List[TestResult] = []
    
    def print_header(self):
        """Print the script header."""
        print("=" * 80)
        print("Adastrea Director - API Key Testing Script")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    def check_dependencies(self) -> TestResult:
        """Check if required dependencies are installed."""
        print("Checking Dependencies...")
        print("-" * 80)
        
        required_packages = {
            'dotenv': 'python-dotenv',
            'langchain': 'langchain',
            'langchain_google_genai': 'langchain-google-genai',
            'langchain_openai': 'langchain-openai',
            'chromadb': 'chromadb',
        }
        
        missing = []
        installed = []
        
        for module_name, package_name in required_packages.items():
            try:
                importlib.import_module(module_name)
                installed.append(package_name)
                if self.verbose:
                    print(f"  ✓ {package_name}")
            except ImportError:
                missing.append(package_name)
                print(f"  ✗ {package_name} NOT INSTALLED")
        
        print()
        
        if missing:
            result = TestResult(
                component="Dependencies",
                success=False,
                message=f"{len(missing)} package(s) missing",
                details={
                    'missing': missing,
                    'installed': installed
                }
            )
            print("❌ DEPENDENCIES CHECK FAILED")
            print(f"\nMissing packages: {', '.join(missing)}")
            print("\nTo fix this, run:")
            print("  pip install -r requirements.txt")
            print("\nOr install missing packages individually:")
            for pkg in missing:
                print(f"  pip install {pkg}")
        else:
            result = TestResult(
                component="Dependencies",
                success=True,
                message=f"All {len(installed)} required packages installed",
                details={'installed': installed}
            )
            print(f"✅ All dependencies installed ({len(installed)} packages)")
        
        print()
        self.results.append(result)
        return result
    
    def check_env_file(self) -> TestResult:
        """Check if .env file exists and is loaded."""
        print("Checking Environment Configuration...")
        print("-" * 80)
        
        env_file = os.path.join(os.getcwd(), '.env')
        env_exists = os.path.exists(env_file)
        
        if env_exists:
            print(f"  ✓ .env file found: {env_file}")
        else:
            print(f"  ⚠ .env file not found: {env_file}")
            print(f"    (Using environment variables or config file)")
        
        if ENV_LOADED:
            print(f"  ✓ python-dotenv loaded")
        else:
            print(f"  ⚠ python-dotenv not available")
        
        print()
        
        result = TestResult(
            component="Environment",
            success=True,  # Not a failure if .env doesn't exist
            message=".env file checked" if env_exists else ".env not found (using env vars)",
            details={
                'env_file_exists': env_exists,
                'env_file_path': env_file,
                'dotenv_loaded': ENV_LOADED
            }
        )
        
        self.results.append(result)
        return result
    
    def get_api_key_sources(self, provider: str) -> Dict[str, Optional[str]]:
        """
        Get all possible sources for an API key.
        
        Args:
            provider: Provider name (gemini, openai, openrouter)
        
        Returns:
            Dictionary of source -> key value
        """
        sources = {}
        
        if provider == "gemini":
            # Check environment variables in priority order
            sources['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')
            sources['GEMINI_KEY'] = os.getenv('GEMINI_KEY')
            sources['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')
            
            # Check config file
            try:
                from config_manager import get_api_key
                sources['config_file'] = get_api_key('gemini')
            except Exception:
                sources['config_file'] = None
        
        elif provider == "openai":
            sources['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
            sources['OPENAI_KEY'] = os.getenv('OPENAI_KEY')
            
            try:
                from config_manager import get_api_key
                sources['config_file'] = get_api_key('openai')
            except Exception:
                sources['config_file'] = None
        
        elif provider == "openrouter":
            sources['OPENROUTER_API_KEY'] = os.getenv('OPENROUTER_API_KEY')
            sources['OPENROUTER_KEY'] = os.getenv('OPENROUTER_KEY')
            
            try:
                from config_manager import get_api_key
                sources['config_file'] = get_api_key('openrouter')
            except Exception:
                sources['config_file'] = None
        
        return sources
    
    def check_api_key_configuration(self, provider: str) -> TestResult:
        """
        Check API key configuration for a provider.
        
        Args:
            provider: Provider name (gemini, openai, openrouter)
        
        Returns:
            TestResult with configuration status
        """
        print(f"Checking {provider.upper()} API Key Configuration...")
        print("-" * 80)
        
        sources = self.get_api_key_sources(provider)
        configured_sources = []
        active_key = None
        active_source = None
        
        # Check each source
        for source, key in sources.items():
            if key:
                # Mask the key for display - always show first 4 and last 4 chars
                if len(key) > 8:
                    masked_key = key[:4] + "..." + key[-4:]
                else:
                    masked_key = "***"
                configured_sources.append(source)
                print(f"  ✓ {source}: {masked_key}")
                
                # The first key found is the active one (by priority)
                if active_key is None:
                    active_key = key
                    active_source = source
            elif self.verbose:
                print(f"  ✗ {source}: Not set")
        
        print()
        
        if active_key:
            result = TestResult(
                component=f"{provider.upper()} Configuration",
                success=True,
                message=f"API key configured via {active_source}",
                details={
                    'provider': provider,
                    'active_source': active_source,
                    'all_sources': configured_sources,
                    'key_length': len(active_key)
                }
            )
            print(f"✅ {provider.upper()} API key configured")
            print(f"   Active source: {active_source}")
            if len(configured_sources) > 1:
                print(f"   Other sources: {', '.join([s for s in configured_sources if s != active_source])}")
        else:
            result = TestResult(
                component=f"{provider.upper()} Configuration",
                success=False,
                message="No API key found",
                details={
                    'provider': provider,
                    'checked_sources': list(sources.keys())
                }
            )
            print(f"❌ {provider.upper()} API key NOT configured")
            print(f"\nTo configure {provider.upper()} API key, use one of:")
            
            if provider == "gemini":
                print("  1. Environment variable: export GEMINI_API_KEY='your-key-here'")
                print("  2. .env file: GEMINI_API_KEY=your-key-here")
                print("  3. Config file: python main.py --set-api-key gemini")
                print("\nGet your Gemini API key from: https://makersuite.google.com/app/apikey")
            elif provider == "openai":
                print("  1. Environment variable: export OPENAI_API_KEY='your-key-here'")
                print("  2. .env file: OPENAI_API_KEY=your-key-here")
                print("  3. Config file: python main.py --set-api-key openai")
                print("\nGet your OpenAI API key from: https://platform.openai.com/api-keys")
            elif provider == "openrouter":
                print("  1. Environment variable: export OPENROUTER_API_KEY='your-key-here'")
                print("  2. .env file: OPENROUTER_API_KEY=your-key-here")
                print("  3. Config file: python main.py --set-api-key openrouter")
                print("\nGet your OpenRouter API key from: https://openrouter.ai/keys")
        
        print()
        self.results.append(result)
        return result
    
    def test_api_connectivity(self, provider: str, skip_test: bool = False) -> TestResult:
        """
        Test actual API connectivity with a minimal request.
        
        Args:
            provider: Provider name (gemini, openai, openrouter)
            skip_test: If True, skip the actual API call
        
        Returns:
            TestResult with connectivity status
        """
        if skip_test:
            result = TestResult(
                component=f"{provider.upper()} API Test",
                success=True,
                message="Skipped (--skip-api-test)",
                details={'skipped': True}
            )
            print(f"⏭️  {provider.upper()} API test skipped")
            print()
            self.results.append(result)
            return result
        
        print(f"Testing {provider.upper()} API Connectivity...")
        print("-" * 80)
        print("  Making a minimal API request to verify authentication...")
        
        try:
            if provider == "gemini":
                from langchain_google_genai import ChatGoogleGenerativeAI
                
                # Get API key
                sources = self.get_api_key_sources(provider)
                api_key = None
                for key in sources.values():
                    if key:
                        api_key = key
                        break
                
                if not api_key:
                    raise ValueError("No API key found")
                
                # Create client and make a minimal request
                llm = ChatGoogleGenerativeAI(
                    model=GEMINI_MODEL,
                    temperature=0,
                    google_api_key=api_key
                )
                
                # Test with a simple prompt
                response = llm.invoke("Say 'OK'")
                response_text = response.content.strip()
                
                result = TestResult(
                    component=f"{provider.upper()} API Test",
                    success=True,
                    message="API authentication successful",
                    details={
                        'provider': provider,
                        'model': GEMINI_MODEL,
                        'test_response': response_text[:MAX_RESPONSE_LENGTH]
                    }
                )
                print(f"✅ {provider.upper()} API connection successful!")
                print(f"   Model: {GEMINI_MODEL}")
                print(f"   Test response: {response_text[:MAX_RESPONSE_LENGTH]}")
            
            elif provider == "openai":
                from langchain_openai import ChatOpenAI
                
                sources = self.get_api_key_sources(provider)
                api_key = None
                for key in sources.values():
                    if key:
                        api_key = key
                        break
                
                if not api_key:
                    raise ValueError("No API key found")
                
                llm = ChatOpenAI(
                    model=OPENAI_MODEL,
                    temperature=0,
                    api_key=api_key
                )
                
                response = llm.invoke("Say 'OK'")
                response_text = response.content.strip()
                
                result = TestResult(
                    component=f"{provider.upper()} API Test",
                    success=True,
                    message="API authentication successful",
                    details={
                        'provider': provider,
                        'model': OPENAI_MODEL,
                        'test_response': response_text[:MAX_RESPONSE_LENGTH]
                    }
                )
                print(f"✅ {provider.upper()} API connection successful!")
                print(f"   Model: {OPENAI_MODEL}")
                print(f"   Test response: {response_text[:MAX_RESPONSE_LENGTH]}")
            
            elif provider == "openrouter":
                from langchain_openai import ChatOpenAI
                
                sources = self.get_api_key_sources(provider)
                api_key = None
                for key in sources.values():
                    if key:
                        api_key = key
                        break
                
                if not api_key:
                    raise ValueError("No API key found")
                
                llm = ChatOpenAI(
                    model=OPENROUTER_MODEL,
                    temperature=0,
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
                
                response = llm.invoke("Say 'OK'")
                response_text = response.content.strip()
                
                result = TestResult(
                    component=f"{provider.upper()} API Test",
                    success=True,
                    message="API authentication successful",
                    details={
                        'provider': provider,
                        'model': OPENROUTER_MODEL,
                        'test_response': response_text[:MAX_RESPONSE_LENGTH]
                    }
                )
                print(f"✅ {provider.upper()} API connection successful!")
                print(f"   Model: {OPENROUTER_MODEL}")
                print(f"   Test response: {response_text[:MAX_RESPONSE_LENGTH]}")
        
        except Exception as e:
            error_msg = str(e)
            result = TestResult(
                component=f"{provider.upper()} API Test",
                success=False,
                message=f"API test failed: {error_msg}",
                details={
                    'provider': provider,
                    'error': error_msg,
                    'error_type': type(e).__name__
                }
            )
            print(f"❌ {provider.upper()} API test failed!")
            print(f"   Error: {error_msg}")
            
            # Provide helpful hints
            if "API key" in error_msg or "authentication" in error_msg.lower():
                print("\n   Possible issues:")
                print("   - API key may be invalid or expired")
                print("   - Check for whitespace in the key")
                print("   - Verify the key is for the correct provider")
            elif "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                print("\n   Possible issues:")
                print("   - API quota exceeded")
                print("   - Rate limit reached")
            elif "connection" in error_msg.lower() or "network" in error_msg.lower():
                print("\n   Possible issues:")
                print("   - Network connectivity problem")
                print("   - Firewall blocking the connection")
        
        print()
        self.results.append(result)
        return result
    
    def print_summary(self):
        """Print a summary of all test results."""
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print()
        
        passed = sum(1 for r in self.results if r.success)
        failed = sum(1 for r in self.results if not r.success)
        total = len(self.results)
        
        print(f"Total tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print()
        
        if failed > 0:
            print("Failed tests:")
            for result in self.results:
                if not result.success:
                    print(f"  ❌ {result.component}: {result.message}")
            print()
        
        print("-" * 80)
        
        if failed == 0:
            print("✅ ALL TESTS PASSED - System is properly configured!")
        else:
            print("❌ SOME TESTS FAILED - Please review the errors above")
            print()
            print("Common solutions:")
            print("  1. Install dependencies: pip install -r requirements.txt")
            print("  2. Configure API key in .env file (copy .env.example to .env)")
            print("  3. Set environment variable: export GEMINI_API_KEY='your-key'")
            print("  4. Or use config file: python main.py --set-api-key gemini")
        
        print("=" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test API keys and system configuration for Adastrea Director",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_api_keys.py                    # Test all configured providers
  python test_api_keys.py --provider gemini  # Test only Gemini
  python test_api_keys.py --all              # Test all providers
  python test_api_keys.py --skip-api-test    # Only check config, no API calls
  python test_api_keys.py --verbose          # Show detailed output
        """
    )
    
    parser.add_argument(
        '--provider',
        choices=['gemini', 'openai', 'openrouter'],
        help='Test specific provider only'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Test all providers (even if not configured)'
    )
    
    parser.add_argument(
        '--skip-api-test',
        action='store_true',
        help='Skip actual API connectivity tests (only check configuration)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output'
    )
    
    args = parser.parse_args()
    
    tester = APIKeyTester(verbose=args.verbose)
    tester.print_header()
    
    # Check dependencies first
    deps_result = tester.check_dependencies()
    if not deps_result.success:
        print("\n⚠️  Dependencies check failed. Some tests may not work properly.")
        print("Install dependencies first: pip install -r requirements.txt\n")
    
    # Check environment
    tester.check_env_file()
    
    # Determine which providers to test
    if args.provider:
        providers = [args.provider]
    elif args.all:
        providers = ['gemini', 'openai', 'openrouter']
    else:
        # Test only configured providers
        providers = []
        llm_provider = os.getenv('LLM_PROVIDER', DEFAULT_PROVIDER).lower()
        providers.append(llm_provider)
        
        # Also test if other providers are configured
        for provider in ['gemini', 'openai', 'openrouter']:
            if provider != llm_provider:
                sources = tester.get_api_key_sources(provider)
                if any(sources.values()):
                    providers.append(provider)
    
    # Test each provider
    for provider in providers:
        config_result = tester.check_api_key_configuration(provider)
        
        if config_result.success and deps_result.success:
            tester.test_api_connectivity(provider, skip_test=args.skip_api_test)
        elif config_result.success:
            print(f"⏭️  Skipping {provider.upper()} API test (dependencies not available)\n")
        else:
            print(f"⏭️  Skipping {provider.upper()} API test (no key configured)\n")
    
    # Print summary
    tester.print_summary()
    
    # Return exit code
    failed = sum(1 for r in tester.results if not r.success)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
