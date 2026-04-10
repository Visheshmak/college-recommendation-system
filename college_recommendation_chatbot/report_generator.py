from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from datetime import datetime
import os


def generate_recommendation_report(student_name, student_email, percentile, category, branch, city, colleges_list, output_path):
    """
    Generate a professional PDF report for college recommendations
    
    Args:
        student_name: Student's full name
        student_email: Student's email
        percentile: MHT-CET percentile
        category: Category (OPEN/SC/ST/OBC)
        branch: Preferred branch
        city: Preferred city
        colleges_list: List of recommended colleges with details
        output_path: Where to save the PDF
    
    Returns:
        Path to the generated PDF file
    """
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create PDF document
    doc = SimpleDocTemplate(output_path, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=6,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2e5c8a'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6
    )
    
    # ==================== TITLE SECTION ====================
    story.append(Paragraph("COLLEGE RECOMMENDATION REPORT", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # ==================== STUDENT INFORMATION ====================
    story.append(Paragraph("STUDENT INFORMATION", heading_style))
    
    student_info = [
        ['Name:', student_name],
        ['Email:', student_email],
        ['MHT-CET Percentile:', f'{percentile}%'],
        ['Category:', category],
        ['Preferred Branch:', branch.title()],
        ['Preferred City:', city.title() if city else 'All Cities'],
        ['Report Generated:', datetime.now().strftime('%d %B %Y at %H:%M')],
    ]
    
    student_table = Table(student_info, colWidths=[2*inch, 4*inch])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F0F8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
    ]))
    
    story.append(student_table)
    story.append(Spacer(1, 0.3*inch))
    
    # ==================== RECOMMENDATIONS SECTION ====================
    story.append(Paragraph("RECOMMENDED COLLEGES", heading_style))
    
    # Create colleges table
    if colleges_list:
        # Table headers
        table_data = [['#', 'College Name', 'Branch', 'Category', 'Cutoff %', 'Chance']]
        
        # Table rows
        for idx, college in enumerate(colleges_list[:25], 1):
            certainty_marker = "★" if college['chance'] == 'High' else "◆" if college['chance'] == 'Medium' else "○"
            table_data.append([
                str(idx),
                college['college'][:20],
                college['branch'][:15],
                college['category'],
                f"{college['cutoff']}%",
                f"{college['chance']} {certainty_marker}"
            ])
        
        colleges_table = Table(table_data, colWidths=[0.4*inch, 2*inch, 1.5*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        
        # Style the table
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5F5')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9F9F9')]),
            ('ALIGN', (-1, 1), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]
        
        colleges_table.setStyle(TableStyle(table_style))
        story.append(colleges_table)
    else:
        story.append(Paragraph("No colleges found matching your criteria.", normal_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # ==================== LEGEND SECTION ====================
    story.append(Paragraph("ADMISSION CHANCE LEGEND", heading_style))
    
    legend_data = [
        ['★ HIGH CHANCE', 'Your percentile is 5% or more above the cutoff - Strong admission chances'],
        ['◆ MEDIUM CHANCE', 'Your percentile matches or is slightly above the cutoff - Reasonable chances'],
        ['○ LOW CHANCE', 'Your percentile is below the cutoff - Low admission chances'],
    ]
    
    legend_table = Table(legend_data, colWidths=[1.5*inch, 4.5*inch])
    legend_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFF9E6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
    ]))
    
    story.append(legend_table)
    story.append(Spacer(1, 0.3*inch))
    
    # ==================== FOOTER SECTION ====================
    footer_text = """
    <b>Important Notes:</b><br/>
    • Cutoff percentiles are based on the latest MHT-CET examination data<br/>
    • Admission is subject to availability of seats and merit list positions<br/>
    • Students must meet all eligibility criteria of the respective college<br/>
    • For official admissions, visit the colleges' official websites<br/>
    • This report is generated for informational purposes only<br/>
    <br/>
    <i>For more information, visit: www.college-recommendation.com</i>
    """
    story.append(Paragraph(footer_text, normal_style))
    
    # Build the PDF
    doc.build(story)
    
    return output_path


def generate_report_with_details(student_data, colleges_list, output_path):
    """
    Wrapper function to generate report with student data
    """
    return generate_recommendation_report(
        student_name=student_data['name'],
        student_email=student_data['email'],
        percentile=student_data['percentile'],
        category=student_data['category'],
        branch=student_data['branch'],
        city=student_data.get('city', ''),
        colleges_list=colleges_list,
        output_path=output_path
    )
