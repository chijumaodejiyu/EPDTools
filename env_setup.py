import sys
import subprocess
import platform
import os
from typing import List, Dict

# Color output constants
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

# Required packages with minimum versions
REQUIREMENTS = {
    'opencv-python': '4.5.1.48',
    'pyserial': '3.5',
    'numpy': '1.19.0'
}

def is_venv():
    """Check if running in a virtual environment"""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def check_python_version():
    """Check if Python version meets requirement (>=3.6)"""
    if sys.version_info < (3, 6):
        print(f"{Colors.RED}Error: Python 3.6 or higher is required (current: {platform.python_version()}){Colors.END}")
        return False
    return True

def generate_requirements_file():
    """Generate requirements.txt file"""
    with open('requirements.txt', 'w') as f:
        for pkg, ver in REQUIREMENTS.items():
            f.write(f"{pkg}>={ver}\n")
    print(f"{Colors.GREEN}Generated requirements.txt{Colors.END}")

def check_package(package: str, min_version: str) -> bool:
    """Check if a package is installed with minimum version"""
    try:
        # Modern Python (3.8+) version check
        from importlib.metadata import version as get_version
        from packaging import version as packaging_version
        
        try:
            installed_version = get_version(package)
            return packaging_version.parse(installed_version) >= packaging_version.parse(min_version)
        except ImportError:
            # Fallback for older Python versions
            import importlib
            module = importlib.import_module(package)
            if hasattr(module, '__version__'):
                installed_version = module.__version__
                return packaging_version.parse(installed_version) >= packaging_version.parse(min_version)
            return False
    except Exception:
        return False

def install_package(package: str, version: str = None):
    """Install a package using pip with improved error handling"""
    cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade']
    
    # Special handling for opencv-python on Windows
    if package == 'opencv-python' and platform.system() == 'Windows':
        # First ensure setuptools is up to date
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'setuptools'])
        
        # Try with default pip first
        try:
            install_cmd = cmd + [f"{package}=={version}"] if version else cmd + [package]
            subprocess.check_call(install_cmd)
            return True
        except subprocess.CalledProcessError:
            print(f"{Colors.YELLOW}Trying alternative installation method...{Colors.END}")
            # Try with pre-built wheel from Tsinghua mirror
            try:
                mirror_cmd = cmd + [
                    f"{package}=={version}",
                    '--index-url', 'https://pypi.tuna.tsinghua.edu.cn/simple',
                    '--trusted-host', 'pypi.tuna.tsinghua.edu.cn'
                ] if version else cmd + [
                    package,
                    '--index-url', 'https://pypi.tuna.tsinghua.edu.cn/simple',
                    '--trusted-host', 'pypi.tuna.tsinghua.edu.cn'
                ]
                subprocess.check_call(mirror_cmd)
                return True
            except subprocess.CalledProcessError as e:
                print(f"{Colors.RED}Error: {e}{Colors.END}")
                return False
    
    # Normal package installation
    try:
        install_cmd = cmd + [f"{package}=={version}"] if version else cmd + [package]
        subprocess.check_call(install_cmd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
        return False

def verify_environment() -> Dict[str, bool]:
    """Verify all required packages are installed"""
    results = {}
    for pkg, min_ver in REQUIREMENTS.items():
        installed = check_package(pkg, min_ver)
        results[pkg] = installed
        status = "OK" if installed else "MISSING"
        print(f"{pkg} (>= {min_ver}): {status}")
    return results

def setup_environment():
    """Main setup function"""
    print(f"{Colors.GREEN}EPD Tools Environment Setup{Colors.END}")
    print("=" * 40)
    
    # Check virtual environment
    if not is_venv():
        print(f"{Colors.YELLOW}Warning: Not running in a virtual environment{Colors.END}")
        print("Consider creating one with: python -m venv venv")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Verify current environment
    print("\nChecking dependencies:")
    status = verify_environment()
    
    # Install missing packages
    missing = [pkg for pkg, installed in status.items() if not installed]
    if missing:
        print("\nInstalling missing packages:")
        for pkg in missing:
            print(f"- Installing {pkg}...", end=' ')
            success = install_package(pkg, REQUIREMENTS[pkg])
            print("Success" if success else "Failed")
            if not success:
                print(f"Failed to install {pkg}. Please install manually.")
                sys.exit(1)
    
    # Final verification
    print("\nFinal verification:")
    final_status = verify_environment()
    if all(final_status.values()):
        print("\nEnvironment setup completed successfully!")
    else:
        print("\nSome dependencies are still missing. Please install them manually.")
        sys.exit(1)

if __name__ == "__main__":
    setup_environment()
    # Generate requirements file
    generate_requirements_file()
    
    print(f"\n{Colors.GREEN}You can now run the EPD Tools application.{Colors.END}")
