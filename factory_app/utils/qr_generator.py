"""
Gerador de QR Codes para inventário
"""
import qrcode
from io import BytesIO
import base64


def generate_qr_code(data: str, size: int = 10) -> str:
    """
    Gera QR code e retorna como string base64

    Args:
        data: Dados para codificar no QR code
        size: Tamanho da caixa do QR code

    Returns:
        String base64 da imagem do QR code
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Converter para base64
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()

    return img_base64


def generate_inventory_qr_code(inventory_id: int, qr_code: str) -> str:
    """
    Gera QR code específico para item de inventário

    Args:
        inventory_id: ID do item no inventário
        qr_code: Código QR único do item

    Returns:
        String base64 da imagem do QR code
    """
    data = f"INV-{inventory_id}-{qr_code}"
    return generate_qr_code(data)
