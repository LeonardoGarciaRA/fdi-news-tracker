import pandas as pd
from datetime import datetime
import os

def export_to_excel(news_items, filename=None):
    """
    Export news items to Excel file
    """
    if not filename:
        os.makedirs('data', exist_ok=True)
        filename = f"data/fdi_projects_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    # Prepare data for Excel
    data = []
    for item in news_items:
        data.append({
            'Title': item.get('title', ''),
            'Summary': item.get('summary', ''),
            'Source URL': item.get('url', ''),
            'Source': item.get('source', ''),
            'Published Date': item.get('published', ''),
            'Collected At': item.get('collected_at', ''),
            'Country': item.get('country', ''),
            'Sector': item.get('sector', ''),
            'Investment Amount': item.get('amount', ''),
            'Company': item.get('company', '')
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Export to Excel with formatting
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='FDI Projects', index=False)
        
        # Get workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['FDI Projects']
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 100)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    return filename

