#!/usr/bin/env python3
"""
API Key Testing Script for Adastrea Director

This script tests the API keys defined in .env and helps diagnose configuration issues.
It checks:
1. Dependencies are properly installed
2. API keys are properly configured
3. API keys can authenticate with their respective services
4. All supported LLM providers (Gemini, OpenAI, OpenRouter)

⚠️  IMPORTANT: This script should be run from a STANDALONE Python environment,
NOT from within Unreal Engine's Python console!

The Adastrea Director plugin uses UE's built-in Python for in-editor operations,
but LLM functionality runs through a separate IPC server that uses your system Python
with the full dependencies installed.

Usage:
    python test_api_keys.py              # Test all configured providers
    python test_api_keys.py --provider gemini     # Test specific provider
    python test_api_keys.py --all        # Test all providers (even if not configured)
    python test_api_keys.py --skip-api-test       # Only check configuration, no API calls

If you accidentally run this from UE's Python console, it will detect this and provide
guidance on how to properly test your setup.
"""

import os
import sys
import argparse
import importlib
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime

# Constants
DEFAULT_PROVIDER = "gemini"
MAX_RESPONSE_LENGTH = 50
GEMINI_MODEL = "gemini-1.5-flash"
OPENAI_MODEL = "gpt-3.5-turbo"
OPENROUTER_MODEL = "mistralai/mistral-7b-instruct:free"

# Check if running inside Unreal Engine's Python environment
try:
    RUNNING_IN_UE = importlib.util.find_spec("unreal") is not None
except Exception:
    RUNNING_IN_UE = False

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
    timestamp: datetime = field(default_factory=lambda: datetime.now())


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
        if RUNNING_IN_UE:
            print()
            print("⚠️  WARNING: Detected Unreal Engine Python Environment")
            print("This script should be run from a standalone Python environment.")
            print("See output below for more information.")
        print()
    
    def check_dependencies(self) -> TestResult:
        """Check if required dependencies are installed."""
        print("Checking Dependencies...")
        print("-" * 80)
        
        # Check if running inside Unreal Engine
        if RUNNING_IN_UE:
            print("⚠️  RUNNING INSIDE UNREAL ENGINE")
            print()
            print("This script is designed to run in a standalone Python environment,")
            print("not inside Unreal Engine's bundled Python interpreter.")
            print()
            print("The Adastrea Director plugin uses Unreal Engine's built-in Python")
            print("environment which does NOT require these external dependencies.")
            print()
            print("✅ This is EXPECTED behavior when running from UE!")
            print()
            print("If you want to test API keys:")
            print("  1. Open a system terminal/command prompt (NOT UE Python console)")
            print("  2. Navigate to the Adastrea-Director repository")
            print("  3. Run: python test_api_keys.py")
            print()
            print("The plugin will work correctly without these dependencies installed")
            print("in UE's Python environment. API key testing and LLM functionality")
            print("is handled through the IPC server which runs in a separate Python")
            print("process with the proper dependencies installed.")
            print()
            result = TestResult(
                component="Dependencies",
                success=True,
                message="Running in UE - dependency check skipped (expected)",
                details={
                    'running_in_ue': True,
                    'note': 'Dependencies not needed in UE Python environment'
                }
            )
            self.results.append(result)
            return result
        
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
        
        Priority order matches llm_config.py:
        1. Config file (highest priority)
        2. Primary environment variable
        3. Legacy environment variables (for Gemini only)
        
        Args:
            provider: Provider name (gemini, openai, openrouter)
        
        Returns:
            Dictionary of source -> key value (ordered by priority)
        """
        sources = {}
        
        if provider == "gemini":
            # Check config file first (highest priority)
            try:
                from config_manager import get_api_key
                sources['config_file'] = get_api_key('gemini')
            except Exception:
                sources['config_file'] = None
            
            # Check environment variables in priority order (matches llm_config.py)
            sources['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')
            sources['GEMINI_KEY'] = os.getenv('GEMINI_KEY')
            sources['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')
        
        elif provider == "openai":
            # Check config file first (highest priority)
            try:
                from config_manager import get_api_key
                sources['config_file'] = get_api_key('openai')
            except Exception:
                sources['config_file'] = None
            
            # Check only OPENAI_API_KEY env var (matches llm_config.py)
            sources['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
        
        elif provider == "openrouter":
            # Check config file first (highest priority)
            try:
                from config_manager import get_api_key
                sources['config_file'] = get_api_key('openrouter')
            except Exception:
                sources['config_file'] = None
            
            # Check only OPENROUTER_API_KEY env var (matches llm_config.py)
            sources['OPENROUTER_API_KEY'] = os.getenv('OPENROUTER_API_KEY')
        
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
                # Mask the key for display - show first 4 and last 4 chars for long keys,
                # and show length-only information for short keys to aid diagnostics.
                key_length = len(key)
                if key_length > 8:
                    masked_key = key[:4] + "..." + key[-4:]
                elif key_length > 0:
                    masked_key = f"<{key_length} chars hidden>"
                else:
                    masked_key = "<empty key>"
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
                print("  1. Config file (HIGHEST PRIORITY): python main.py --set-api-key gemini")
                print("  2. Environment variable: export GEMINI_API_KEY='your-key-here'")
                print("  3. .env file: GEMINI_API_KEY=your-key-here")
                print("\nGet your Gemini API key from: https://makersuite.google.com/app/apikey")
            elif provider == "openai":
                print("  1. Config file (HIGHEST PRIORITY): python main.py --set-api-key openai")
                print("  2. Environment variable: export OPENAI_API_KEY='your-key-here'")
                print("  3. .env file: OPENAI_API_KEY=your-key-here")
                print("\nGet your OpenAI API key from: https://platform.openai.com/api-keys")
            elif provider == "openrouter":
                print("  1. Config file (HIGHEST PRIORITY): python main.py --set-api-key openrouter")
                print("  2. Environment variable: export OPENROUTER_API_KEY='your-key-here'")
                print("  3. .env file: OPENROUTER_API_KEY=your-key-here")
                print("\nGet your OpenRouter API key from: https://openrouter.ai/keys")
        
        print()
        self.results.append(result)
        return result
    
    def _get_first_api_key(self, provider: str) -> Optional[str]:
        """
        Get the first available API key from sources.
        
        Args:
            provider: Provider name
            
        Returns:
            First available API key or None
        """
        sources = self.get_api_key_sources(provider)
        for key in sources.values():
            if key:
                return key
        return None
    
    def _create_success_result(self, provider: str, model: str, response_text: str) -> TestResult:
        """
        Create a success TestResult for API connectivity test.
        
        Args:
            provider: Provider name
            model: Model name used
            response_text: Response from API
            
        Returns:
            TestResult indicating success
        """
        result = TestResult(
            component=f"{provider.upper()} API Test",
            success=True,
            message="API authentication successful",
            details={
                'provider': provider,
                'model': model,
                'test_response': response_text[:MAX_RESPONSE_LENGTH]
            }
        )
        print(f"✅ {provider.upper()} API connection successful!")
        print(f"   Model: {model}")
        print(f"   Test response: {response_text[:MAX_RESPONSE_LENGTH]}")
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
            # Get API key using helper method
            api_key = self._get_first_api_key(provider)
            if not api_key:
                raise ValueError("No API key found")
            
            if provider == "gemini":
                from langchain_google_genai import ChatGoogleGenerativeAI
                
                llm = ChatGoogleGenerativeAI(
                    model=GEMINI_MODEL,
                    temperature=0,
                    google_api_key=api_key
                )
                response = llm.invoke("Say 'OK'")
                response_text = response.content.strip()
                result = self._create_success_result(provider, GEMINI_MODEL, response_text)
            
            elif provider == "openai":
                from langchain_openai import ChatOpenAI
                
                llm = ChatOpenAI(
                    model=OPENAI_MODEL,
                    temperature=0,
                    api_key=api_key
                )
                response = llm.invoke("Say 'OK'")
                response_text = response.content.strip()
                result = self._create_success_result(provider, OPENAI_MODEL, response_text)
            
            elif provider == "openrouter":
                from langchain_openai import ChatOpenAI
                
                llm = ChatOpenAI(
                    model=OPENROUTER_MODEL,
                    temperature=0,
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
                response = llm.invoke("Say 'OK'")
                response_text = response.content.strip()
                result = self._create_success_result(provider, OPENROUTER_MODEL, response_text)
        
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
        
        # Check if running in UE
        if RUNNING_IN_UE:
            print("⚠️  RUNNING IN UNREAL ENGINE ENVIRONMENT")
            print()
            print("This script detected it's running inside Unreal Engine's Python interpreter.")
            print("This is NOT the intended environment for testing API keys.")
            print()
            print("The Adastrea Director plugin does not require LangChain dependencies")
            print("to be installed in Unreal Engine's Python environment.")
            print()
            print("✅ Your setup is likely correct!")
            print()
            print("To properly test API keys and dependencies:")
            print("  1. Open a system terminal/command prompt (NOT UE Python console)")
            print("  2. Navigate to: <your-path>/Adastrea-Director")
            print("  3. Run: python test_api_keys.py")
            print()
            print("=" * 80)
            return
        
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
    
    # If running in UE, skip all provider tests and go straight to summary
    if RUNNING_IN_UE:
        # Check environment
        tester.check_env_file()
        
        # Print summary and exit
        tester.print_summary()
        return 0
    
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
    
    # Return exit code based on test results
    failed = sum(1 for r in tester.results if not r.success)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
