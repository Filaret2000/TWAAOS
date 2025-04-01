from sqlalchemy import Column, String, Text

from src.common.models.base import BaseModel

class ExcelTemplate(BaseModel):
    """Model pentru template-urile Excel utilizate pentru import/export date"""
    __tablename__ = 'excel_templates'
    
    name = Column(String(100), nullable=False, unique=True)
    file_path = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    def to_dict(self):
        """Convertește modelul într-un dicționar"""
        return super().to_dict()
