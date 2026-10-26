import base64

import pytest

from src.assets import validate_asset
from src.config import Settings
from src.errors import InvalidAssetError

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20
JPEG_SIGNATURE = b"\xff\xd8\xff" + b"\x00" * 20
PDF_SIGNATURE = b"%PDF-1.4\n" + b"\x00" * 20
ZIP_SIGNATURE = b"PK\x03\x04" + b"\x00" * 20


def _b64(content: bytes) -> str:
    return base64.b64encode(content).decode("ascii")


@pytest.fixture
def settings() -> Settings:
    return Settings()


def test_valid_image_is_accepted(settings):
    result = validate_asset(
        settings,
        kind="image",
        filename="como-fazer-cursos-a1b2c3d4.png",
        content_base64=_b64(PNG_SIGNATURE),
        alt="Tela de login",
    )
    assert result.filename == "como-fazer-cursos-a1b2c3d4.png"
    assert result.binary_content == PNG_SIGNATURE
    assert result.alt == "Tela de login"


def test_valid_file_is_accepted(settings):
    result = validate_asset(
        settings,
        kind="file",
        filename="manual-acesso-000123.pdf",
        content_base64=_b64(PDF_SIGNATURE),
        alt=None,
    )
    assert result.kind == "file"


def test_docx_uses_the_shared_zip_signature(settings):
    result = validate_asset(
        settings,
        kind="file",
        filename="formulario-abc12345.docx",
        content_base64=_b64(ZIP_SIGNATURE),
        alt=None,
    )
    assert result.filename.endswith(".docx")


def test_image_without_alt_text_is_rejected(settings):
    with pytest.raises(InvalidAssetError, match="alternativo"):
        validate_asset(
            settings,
            kind="image",
            filename="foto-abc12345.png",
            content_base64=_b64(PNG_SIGNATURE),
            alt="   ",
        )


def test_unknown_kind_is_rejected(settings):
    with pytest.raises(InvalidAssetError):
        validate_asset(
            settings,
            kind="video",  # type: ignore[arg-type]
            filename="video-abc12345.mp4",
            content_base64=_b64(b"\x00" * 10),
            alt=None,
        )


@pytest.mark.parametrize(
    "filename",
    [
        "../../etc/passwd.png",
        "/etc/passwd.png",
        "..\\windows\\system32.png",
        "Foto Com Espaco.png",
        "foto.PNG",
        "sem-extensao",
        "",
    ],
)
def test_unsafe_or_malformed_filenames_are_rejected(settings, filename):
    with pytest.raises(InvalidAssetError):
        validate_asset(
            settings,
            kind="image",
            filename=filename,
            content_base64=_b64(PNG_SIGNATURE),
            alt="Alt",
        )


def test_disallowed_extension_is_rejected(settings):
    with pytest.raises(InvalidAssetError, match="não permitida"):
        validate_asset(
            settings,
            kind="image",
            filename="script-abc12345.svg",
            content_base64=_b64(b"<svg></svg>"),
            alt="Alt",
        )


def test_extension_not_allowed_for_files_is_rejected(settings):
    with pytest.raises(InvalidAssetError, match="não permitida"):
        validate_asset(
            settings,
            kind="file",
            filename="programa-abc12345.exe",
            content_base64=_b64(b"MZ" + b"\x00" * 20),
            alt=None,
        )


def test_signature_mismatch_is_rejected(settings):
    with pytest.raises(InvalidAssetError, match="assinatura"):
        validate_asset(
            settings,
            kind="image",
            filename="foto-abc12345.png",
            content_base64=_b64(JPEG_SIGNATURE),  # extensão .png, bytes de JPEG
            alt="Alt",
        )


def test_invalid_base64_is_rejected(settings):
    with pytest.raises(InvalidAssetError, match="base64"):
        validate_asset(
            settings,
            kind="image",
            filename="foto-abc12345.png",
            content_base64="isto não é base64 válido!!!",
            alt="Alt",
        )


def test_empty_content_is_rejected(settings):
    with pytest.raises(InvalidAssetError, match="vazio"):
        validate_asset(
            settings,
            kind="image",
            filename="foto-abc12345.png",
            content_base64="",
            alt="Alt",
        )


def test_oversized_image_is_rejected(settings):
    settings = settings.model_copy(update={"max_image_size_bytes": 10})
    with pytest.raises(InvalidAssetError, match="limite"):
        validate_asset(
            settings,
            kind="image",
            filename="foto-abc12345.png",
            content_base64=_b64(PNG_SIGNATURE),
            alt="Alt",
        )
