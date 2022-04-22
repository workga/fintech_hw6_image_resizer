from fastapi import Header, HTTPException, status


def content_type_jpeg(content_type: str = Header(...)) -> None:
    if content_type != 'image/jpeg':
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f'Unsupported content type: {content_type}. It must be image/jpeg',
        )
