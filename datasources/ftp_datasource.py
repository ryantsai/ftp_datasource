import logging
import os
from ftplib import FTP
from collections.abc import Generator
from typing import Any

from dify_plugin.entities.datasource import (
    DatasourceMessage,
    OnlineDriveBrowseFilesRequest,
    OnlineDriveBrowseFilesResponse,
    OnlineDriveDownloadFileRequest,
    OnlineDriveFile,
    OnlineDriveFileBucket,
)
from dify_plugin.interfaces.datasource.online_drive import OnlineDriveDatasource

logger = logging.getLogger(__name__)


class FtpDatasourceDataSource(OnlineDriveDatasource):
    def _browse_files(
        self, request: OnlineDriveBrowseFilesRequest
    ) -> OnlineDriveBrowseFilesResponse:
        credentials = self.runtime.credentials
        host = credentials.get("host")
        username = credentials.get("username")
        password = credentials.get("password")

        # Connect to FTP server
        ftp = FTP(host)
        ftp.login(username, password)

        # Get current path from prefix or use root
        prefix = request.prefix or "/"
        ftp.cwd(prefix)

        # List files and directories
        files = []
        dir_list = []

        def handle_line(line):
            parts = line.split()
            if len(parts) >= 9:
                name = " ".join(parts[8:])
                size = int(parts[4])
                is_dir = parts[0].startswith('d')

                file = OnlineDriveFile(
                    id=os.path.join(prefix, name),
                    name=name,
                    size=size,
                    type="folder" if is_dir else "file"
                )
                dir_list.append(file)

        ftp.retrlines('LIST', handle_line)
        ftp.quit()

        # Sort directories first, then files
        dir_list.sort(key=lambda x: (x.type != "folder", x.name))
        files.extend(dir_list)

        return OnlineDriveBrowseFilesResponse(result=[
            OnlineDriveFileBucket(
                bucket="ftp",
                files=files,
                is_truncated=False,
                next_page_parameters={}
            )
        ])

    def _download_file(self, request: OnlineDriveDownloadFileRequest) -> Generator[DatasourceMessage, None, None]:
        credentials = self.runtime.credentials
        host = credentials.get("host")
        username = credentials.get("username")
        password = credentials.get("password")
        file_path = request.id

        # Connect to FTP server
        ftp = FTP(host)
        ftp.login(username, password)

        # Download file content
        content = []
        ftp.retrbinary(f'RETR {file_path}', content.append)
        ftp.quit()

        file_content = b''.join(content)
        file_name = os.path.basename(file_path)

        mime_type = self._get_mime_type_from_filename(file_name)

        yield self.create_blob_message(file_content, meta={
            "file_name": file_name,
            "mime_type": mime_type
        })
