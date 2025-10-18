import os
import sys
from pathlib import Path

try:
    from dify_plugin import Plugin, DifyPluginEnv
except ModuleNotFoundError:
    # Auto-switch to local virtualenv if available
    repo_root = Path(__file__).resolve().parent
    venv_python = repo_root / ".venv" / "bin" / "python"
    if venv_python.exists():
        os.execv(str(venv_python), [str(venv_python), *sys.argv])
    raise
from provider.ftp_provider import FtpProvider
from datasources.ftp_datasource import FtpDatasourceDataSource
from dify_plugin.config.config import InstallMethod

# Initialize plugin with environment
env = DifyPluginEnv(MAX_REQUEST_TIMEOUT=120)
try:
    plugin = Plugin(env)
except Exception:
    # Fallback to local install method if remote/serverless cannot start (e.g., no network permissions)
    env = DifyPluginEnv(MAX_REQUEST_TIMEOUT=120, INSTALL_METHOD=InstallMethod.Local)
    plugin = Plugin(env)

# Register the provider and datasource
plugin.register_provider("ftp_provider", FtpProvider)
plugin.register_datasource(
    "ftp_provider", "ftp_datasource", FtpDatasourceDataSource)

if __name__ == '__main__':
    plugin.run()
