"""
Módulo para impressão de etiquetas térmicas
Etiquetas: 11cm x 2.5cm para impressora térmica
"""
import io
import os
from typing import Optional, List
from datetime import datetime
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.graphics.barcode import qr
from reportlab.graphics import renderPDF
from reportlab.lib import colors
import qrcode
from PIL import Image

from utils.logger import logger


class ThermalLabelPrinter:
    """
    Gerador de etiquetas para impressora térmica
    Dimensões: 11cm x 2.5cm
    """

    # Dimensões da etiqueta em cm
    LABEL_WIDTH = 11 * cm
    LABEL_HEIGHT = 2.5 * cm

    # Margens
    MARGIN = 0.2 * cm

    # Tamanho do QR Code
    QR_SIZE = 2.0 * cm

    def __init__(self, output_dir: str = "labels"):
        """
        Inicializa gerador de etiquetas

        Args:
            output_dir: Diretório para salvar PDFs de etiquetas
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_qr_code(self, data: str, size: float = None) -> Image:
        """
        Gera QR Code como imagem PIL

        Args:
            data: Dados para codificar no QR
            size: Tamanho do QR em cm (usa padrão se não fornecido)

        Returns:
            Imagem PIL do QR Code
        """
        if size is None:
            size = self.QR_SIZE

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=1,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        return img

    def create_inventory_label(
        self,
        qr_data: str,
        material_name: str,
        material_type: str,
        color: Optional[str] = None,
        dimensions: Optional[str] = None,
        location: Optional[str] = None
    ) -> str:
        """
        Cria etiqueta para item de inventário

        Args:
            qr_data: Dados do QR Code (geralmente o código único)
            material_name: Nome do material
            material_type: Tipo de material
            color: Cor do material (opcional)
            dimensions: Dimensões do material (opcional)
            location: Localização do material (opcional)

        Returns:
            Caminho do arquivo PDF gerado
        """
        # Nome do arquivo
        safe_name = qr_data.replace("/", "_").replace("\\", "_")
        filename = f"label_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        # Criar PDF
        c = canvas.Canvas(filepath, pagesize=(self.LABEL_WIDTH, self.LABEL_HEIGHT))

        # Gerar QR Code
        qr_img = self.generate_qr_code(qr_data)
        qr_temp = os.path.join(self.output_dir, f"temp_qr_{safe_name}.png")
        qr_img.save(qr_temp)

        # Desenhar QR Code na esquerda
        c.drawImage(
            qr_temp,
            self.MARGIN,
            self.MARGIN,
            width=self.QR_SIZE,
            height=self.QR_SIZE,
            preserveAspectRatio=True
        )

        # Área de texto (à direita do QR)
        text_x = self.MARGIN + self.QR_SIZE + 0.3 * cm
        text_width = self.LABEL_WIDTH - text_x - self.MARGIN

        # Linha 1: Nome do Material (Bold, maior)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(text_x, self.LABEL_HEIGHT - 0.5 * cm, material_name[:35])

        # Linha 2: Tipo
        c.setFont("Helvetica", 7)
        y_pos = self.LABEL_HEIGHT - 0.9 * cm
        c.drawString(text_x, y_pos, f"Tipo: {material_type}")

        # Linha 3: Cor (se fornecida)
        if color:
            y_pos -= 0.35 * cm
            c.drawString(text_x, y_pos, f"Cor: {color}")

        # Linha 4: Dimensões (se fornecidas)
        if dimensions:
            y_pos -= 0.35 * cm
            c.setFont("Helvetica", 6)
            c.drawString(text_x, y_pos, dimensions[:40])

        # Linha 5: Localização (se fornecida)
        if location:
            y_pos -= 0.35 * cm
            c.setFont("Helvetica", 6)
            c.drawString(text_x, y_pos, f"Local: {location}")

        # Código QR em texto (rodapé, pequeno)
        c.setFont("Helvetica", 5)
        c.drawString(text_x, self.MARGIN, qr_data[:50])

        # Finalizar PDF
        c.save()

        # Remover QR temporário
        if os.path.exists(qr_temp):
            os.remove(qr_temp)

        logger.info(f"Etiqueta criada: {filepath}")
        return filepath

    def create_work_order_label(
        self,
        order_number: str,
        product_code: str,
        product_description: str,
        quantity: float,
        unit: str,
        machine_code: Optional[str] = None
    ) -> str:
        """
        Cria etiqueta para ordem de trabalho

        Args:
            order_number: Número da ordem
            product_code: Código do produto
            product_description: Descrição do produto
            quantity: Quantidade planejada
            unit: Unidade
            machine_code: Código da máquina (opcional)

        Returns:
            Caminho do arquivo PDF gerado
        """
        safe_name = order_number.replace("/", "_").replace("\\", "_")
        filename = f"wo_label_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        c = canvas.Canvas(filepath, pagesize=(self.LABEL_WIDTH, self.LABEL_HEIGHT))

        # QR Code com número da ordem
        qr_img = self.generate_qr_code(order_number)
        qr_temp = os.path.join(self.output_dir, f"temp_qr_{safe_name}.png")
        qr_img.save(qr_temp)

        c.drawImage(
            qr_temp,
            self.MARGIN,
            self.MARGIN,
            width=self.QR_SIZE,
            height=self.QR_SIZE,
            preserveAspectRatio=True
        )

        # Texto
        text_x = self.MARGIN + self.QR_SIZE + 0.3 * cm

        # Ordem de Trabalho
        c.setFont("Helvetica-Bold", 10)
        c.drawString(text_x, self.LABEL_HEIGHT - 0.5 * cm, f"OT: {order_number}")

        # Produto
        c.setFont("Helvetica-Bold", 8)
        c.drawString(text_x, self.LABEL_HEIGHT - 0.9 * cm, product_code)

        # Descrição
        c.setFont("Helvetica", 6)
        c.drawString(text_x, self.LABEL_HEIGHT - 1.3 * cm, product_description[:45])

        # Quantidade
        c.setFont("Helvetica", 7)
        c.drawString(text_x, self.LABEL_HEIGHT - 1.65 * cm, f"Qtd: {quantity} {unit}")

        # Máquina
        if machine_code:
            c.setFont("Helvetica", 6)
            c.drawString(text_x, self.LABEL_HEIGHT - 2.0 * cm, f"Máquina: {machine_code}")

        c.save()

        if os.path.exists(qr_temp):
            os.remove(qr_temp)

        logger.info(f"Etiqueta de OT criada: {filepath}")
        return filepath

    def create_batch_labels(
        self,
        labels_data: List[dict],
        labels_per_page: int = 10
    ) -> str:
        """
        Cria múltiplas etiquetas em um único PDF

        Args:
            labels_data: Lista de dicionários com dados das etiquetas
                         Cada dict deve conter: type, qr_data, e campos específicos
            labels_per_page: Número de etiquetas por página

        Returns:
            Caminho do arquivo PDF gerado
        """
        filename = f"batch_labels_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        c = canvas.Canvas(filepath, pagesize=letter)
        page_width, page_height = letter

        labels_count = 0
        y_position = page_height - self.LABEL_HEIGHT - 0.5 * cm

        for label_data in labels_data:
            if labels_count > 0 and labels_count % labels_per_page == 0:
                c.showPage()  # Nova página
                y_position = page_height - self.LABEL_HEIGHT - 0.5 * cm

            # Desenhar etiqueta na posição atual
            self._draw_label_on_canvas(c, label_data, 0.5 * cm, y_position)

            y_position -= self.LABEL_HEIGHT + 0.2 * cm
            labels_count += 1

        c.save()
        logger.info(f"Lote de {labels_count} etiquetas criado: {filepath}")
        return filepath

    def _draw_label_on_canvas(self, c: canvas.Canvas, label_data: dict, x: float, y: float):
        """
        Desenha uma etiqueta no canvas em posição específica

        Args:
            c: Canvas do ReportLab
            label_data: Dados da etiqueta
            x: Posição X
            y: Posição Y
        """
        label_type = label_data.get('type', 'inventory')

        if label_type == 'inventory':
            # Implementar desenho de etiqueta de inventário
            pass
        elif label_type == 'work_order':
            # Implementar desenho de etiqueta de OT
            pass

    def print_to_thermal_printer(self, pdf_path: str, printer_name: Optional[str] = None):
        """
        Envia PDF para impressora térmica

        NOTA: Requer configuração específica do Windows/Linux
        No Windows: usar win32print
        No Linux: usar CUPS/lp

        Args:
            pdf_path: Caminho do arquivo PDF
            printer_name: Nome da impressora (usa padrão se não fornecido)
        """
        import platform

        system = platform.system()

        try:
            if system == "Windows":
                # Windows: usar win32print
                import win32print
                import win32api

                if printer_name is None:
                    printer_name = win32print.GetDefaultPrinter()

                win32api.ShellExecute(
                    0,
                    "print",
                    pdf_path,
                    f'/d:"{printer_name}"',
                    ".",
                    0
                )
                logger.info(f"Enviado para impressora {printer_name}")

            elif system == "Linux":
                # Linux: usar lp
                cmd = f"lp {pdf_path}"
                if printer_name:
                    cmd = f"lp -d {printer_name} {pdf_path}"

                os.system(cmd)
                logger.info(f"Enviado para impressora via lp")

            else:
                logger.warning(f"Sistema {system} não suportado para impressão direta")

        except Exception as e:
            logger.error(f"Erro ao imprimir: {e}")


# ========== FUNÇÕES AUXILIARES ==========

def print_inventory_label(
    qr_code: str,
    material_name: str,
    material_type: str,
    **kwargs
) -> str:
    """
    Função auxiliar para imprimir etiqueta de inventário

    Args:
        qr_code: Código QR
        material_name: Nome do material
        material_type: Tipo de material
        **kwargs: Argumentos adicionais (color, dimensions, location)

    Returns:
        Caminho do PDF gerado
    """
    printer = ThermalLabelPrinter()
    return printer.create_inventory_label(
        qr_code,
        material_name,
        material_type,
        **kwargs
    )


def print_work_order_label(
    order_number: str,
    product_code: str,
    product_description: str,
    quantity: float,
    unit: str,
    **kwargs
) -> str:
    """
    Função auxiliar para imprimir etiqueta de ordem de trabalho

    Args:
        order_number: Número da ordem
        product_code: Código do produto
        product_description: Descrição
        quantity: Quantidade
        unit: Unidade
        **kwargs: Argumentos adicionais (machine_code)

    Returns:
        Caminho do PDF gerado
    """
    printer = ThermalLabelPrinter()
    return printer.create_work_order_label(
        order_number,
        product_code,
        product_description,
        quantity,
        unit,
        **kwargs
    )


# ========== EXEMPLOS DE USO ==========
"""
# 1. Etiqueta de inventário
from utils.label_printer import ThermalLabelPrinter

printer = ThermalLabelPrinter()
pdf = printer.create_inventory_label(
    qr_data="INV-2025-001",
    material_name="Granito Branco Prime",
    material_type="Chapa",
    color="Branco",
    dimensions="300x200x2cm",
    location="Armazém A-15"
)
print(f"PDF criado: {pdf}")

# 2. Etiqueta de ordem de trabalho
pdf = printer.create_work_order_label(
    order_number="OT-2025-100",
    product_code="PROD-001",
    product_description="Mesa de Granito Polida",
    quantity=5,
    unit="UN",
    machine_code="M-001"
)

# 3. Imprimir diretamente
printer.print_to_thermal_printer(pdf, printer_name="Thermal Printer")

# 4. Lote de etiquetas
labels = [
    {
        'type': 'inventory',
        'qr_data': 'INV-001',
        'material_name': 'Granito',
        'material_type': 'Chapa'
    },
    {
        'type': 'inventory',
        'qr_data': 'INV-002',
        'material_name': 'Mármore',
        'material_type': 'Chapa'
    }
]
pdf = printer.create_batch_labels(labels)

# 5. Integrar com rota FastAPI
from fastapi import APIRouter
from fastapi.responses import FileResponse

@router.get("/label/{item_id}")
async def generate_label(item_id: int, db: Session = Depends(get_db)):
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()

    printer = ThermalLabelPrinter()
    pdf = printer.create_inventory_label(
        qr_data=item.qr_code,
        material_name=item.material_name,
        material_type=item.material_type.value,
        color=item.color
    )

    return FileResponse(pdf, media_type='application/pdf', filename=os.path.basename(pdf))
"""
