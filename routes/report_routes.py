"""
Report routes for analytics and PDF export
"""
from flask import Blueprint, render_template, session, flash, redirect, url_for, send_file
from datetime import datetime
from io import BytesIO
from models import RecordModel, CommentModel
from .auth_routes import login_required

report_bp = Blueprint('report', __name__)
record_model = RecordModel()
comment_model = CommentModel()


@report_bp.route('/reports')
@login_required
def reports():
    """Display comprehensive analytics dashboard"""
    """عرض لوحة تحكم تحليلات شاملة"""
    user_id = session.get('user_id')
    username = session.get('username')

    # Get record statistics
    record_stats = record_model.get_summary_stats(user_id)

    # Get comment statistics
    comment_stats = comment_model.get_comment_stats(user_id)

    # Combine stats
    stats = {**record_stats, 'comments': comment_stats}

    return render_template('reports.html', username=username, stats=stats)


@report_bp.route('/export-report')
@login_required
def export_report():
    """Export comprehensive report as PDF"""
    """تصدير تقرير شامل بصيغة PDF"""
    user_id = session.get('user_id')
    username = session.get('username')

    # Generate PDF report
    success, message, pdf_bytes = generate_pdf_report(user_id, username)

    if success:
        # Create a BytesIO object from the PDF bytes
        pdf_buffer = BytesIO(pdf_bytes)
        pdf_buffer.seek(0)

        # Send the PDF as a download
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'report_{username}_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    else:
        flash(message, 'error')
        return redirect(url_for('report.reports'))


def generate_pdf_report(user_id: str, username: str) -> tuple[bool, str, bytes]:
    """
    Generate a PDF report of user statistics including comments

    Args:
        user_id: User ID
        username: Username for display in report

    Returns:
        Tuple of (success: bool, message: str, pdf_bytes: bytes)
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER

        # Get statistics
        record_stats = record_model.get_summary_stats(user_id)
        comment_stats = comment_model.get_comment_stats(user_id)

        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2a2a2a'),
            spaceAfter=12,
            spaceBefore=12
        )

        # Title
        elements.append(Paragraph("Smart Records System", title_style))
        elements.append(Paragraph(f"Analytics Report for {username}", styles['Heading2']))
        elements.append(Paragraph(f"Generated on: {record_stats['generated_at']}", styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))

        # Overview Section
        elements.append(Paragraph("Overview", heading_style))
        overview_data = [
            ['Metric', 'Value'],
            ['Total Records', str(record_stats['total'])],
            ['Active Records', str(record_stats['status_breakdown']['active'])],
            ['Completed Records', str(record_stats['status_breakdown']['completed'])],
            ['Inactive Records', str(record_stats['status_breakdown']['inactive'])],
            ['Total Comments', str(comment_stats['total_comments'])],
            ['Comments on My Records', str(comment_stats['comments_on_my_records'])],
        ]

        if record_stats['date_range']['first_record']:
            overview_data.append(['First Record Date', record_stats['date_range']['first_record']])
        if record_stats['date_range']['last_record']:
            overview_data.append(['Last Record Date', record_stats['date_range']['last_record']])

        overview_table = Table(overview_data, colWidths=[3*inch, 3*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2a2a2a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        elements.append(overview_table)
        elements.append(Spacer(1, 0.3*inch))

        # Time-based Statistics
        elements.append(Paragraph("Recent Activity", heading_style))
        time_data = [
            ['Period', 'Records Created'],
            ['Today', str(record_stats['time_stats']['today'])],
            ['This Week', str(record_stats['time_stats']['this_week'])],
            ['This Month', str(record_stats['time_stats']['this_month'])],
        ]
        time_table = Table(time_data, colWidths=[3*inch, 3*inch])
        time_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2a2a2a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        elements.append(time_table)
        elements.append(Spacer(1, 0.3*inch))

        # Category Breakdown
        if record_stats['by_category']:
            elements.append(Paragraph("Records by Category", heading_style))
            category_data = [['Category', 'Count']]
            for category, count in sorted(record_stats['by_category'].items()):
                category_data.append([category, str(count)])

            category_table = Table(category_data, colWidths=[3*inch, 3*inch])
            category_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2a2a2a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            elements.append(category_table)
            elements.append(Spacer(1, 0.3*inch))

        # Top Commented Records
        if comment_stats['top_commented_records']:
            elements.append(Paragraph("Most Commented Records", heading_style))
            commented_data = [['Record Title', 'Comments']]
            for item in comment_stats['top_commented_records']:
                title = item['record_title'][:40] + '...' if len(item['record_title']) > 40 else item['record_title']
                commented_data.append([title, str(item['comment_count'])])

            commented_table = Table(commented_data, colWidths=[4*inch, 2*inch])
            commented_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2a2a2a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            elements.append(commented_table)
            elements.append(Spacer(1, 0.3*inch))

        # Recent Records
        if record_stats['recent_records']:
            elements.append(Paragraph("Recent Records (Last 5)", heading_style))
            recent_data = [['Title', 'Category', 'Status', 'Date']]
            for record in record_stats['recent_records']:
                title = record['title'][:30] + '...' if len(record['title']) > 30 else record['title']
                recent_data.append([
                    title,
                    record['category'],
                    record['status'],
                    record['date'].split(' ')[0]
                ])

            recent_table = Table(recent_data, colWidths=[2.2*inch, 1.5*inch, 1.3*inch, 1.5*inch])
            recent_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2a2a2a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            elements.append(recent_table)

        # Build PDF
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return True, "PDF generated successfully", pdf_bytes

    except ImportError:
        return False, "reportlab library not installed. Run: pip install reportlab", b''
    except Exception as e:
        return False, f"Error generating PDF: {str(e)}", b''
