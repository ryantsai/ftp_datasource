from typing import Any, Mapping
from ftplib import FTP

from dify_plugin.interfaces.datasource import DatasourceProvider


class FtpProvider(DatasourceProvider):
    def _validate_credentials(self, credentials: Mapping[str, Any]) -> None:
        """Validate FTP credentials by attempting to connect to the server"""
        try:
            host = credentials.get("host")
            username = credentials.get("username")
            password = credentials.get("password")

            if not all([host, username, password]):
                raise ValueError(
                    "Missing required credentials: host, username, and password are required")

            # Try to connect to FTP server
            ftp = FTP(host)
            ftp.login(username, password)
            ftp.quit()
        except Exception as e:
            raise ValueError(f"Failed to connect to FTP server: {str(e)}")
