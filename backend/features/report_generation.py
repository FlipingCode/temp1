# backend/features/report_generation.py

from fpdf import FPDF
import pandas as pd
import os
from datetime import datetime

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        logo_path = os.path.join(self.static_folder, 'images/small_app_logo.png')
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 10)
        self.cell(0, 10, 'JalSuchak - Heavy Metal Analysis Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 10, title, 0, 1, 'L', fill=True)
        self.ln(5)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 7, body)
        self.ln()
        
    def add_table(self, df, title, columns, col_widths):
        self.set_font('Arial', 'B', 10)
        
        for i, header in enumerate(columns.values()):
            self.cell(col_widths[i], 10, header, 1, 0, 'C')
        self.ln()

        self.set_font('Arial', '', 9)
        for index, row in df.iterrows():
            for i, key in enumerate(columns.keys()):
                value = row.get(key, 'N/A')
                if isinstance(value, float):
                    value = f"{value:.2f}"
                self.cell(col_widths[i], 10, str(value), 1)
            self.ln()
        self.ln(10)

    def add_summary_stats(self, df):
        self.set_font('Arial', '', 11)
        total_sites = len(df)
        avg_hmpi = df['HMPI'].mean()
        max_hmpi_row = df.loc[df['HMPI'].idxmax()]
        
        self.cell(0, 7, f"- Total Sites Analyzed: {total_sites}", 0, 1)
        self.cell(0, 7, f"- Average HMPI: {avg_hmpi:.2f}", 0, 1)
        self.cell(0, 7, f"- Highest HMPI Recorded: {max_hmpi_row['HMPI']:.2f} at '{max_hmpi_row.get('Station Name', 'N/A')}'", 0, 1)
        self.ln(5)

    def add_pollution_breakdown(self, df):
        self.set_font('Arial', '', 11)
        pollution_counts = df['Pollution Level'].value_counts()
        for level, count in pollution_counts.items():
            self.cell(0, 7, f"- {level}: {count} sites", 0, 1)
        self.ln(5)
        
    def add_graph(self, graph_name, title):
        self.chapter_title(title)
        graph_path = os.path.join(self.static_folder, f'images/graphs/{graph_name}')
        if os.path.exists(graph_path):
            # Center the image
            self.image(graph_path, x=self.get_x() + 10, w=self.w - self.l_margin - self.r_margin - 20)
        else:
            self.cell(0, 10, f"[Graph '{graph_name}' not found]", 0, 1)
        self.ln(5)


class ReportGenerator:
    def generate_report(self, df, report_data, static_folder_path):
        pdf = PDF()
        pdf.static_folder = static_folder_path
        pdf.add_page()

        pdf.set_font('Arial', 'B', 24)
        pdf.cell(0, 30, report_data.get('title', 'Analysis Report'), 0, 1, 'C')
        pdf.ln(15)
        pdf.set_font('Arial', '', 12)
        
        report_date = report_data.get('date') or datetime.now().strftime('%Y-%m-%d')
        
        pdf.cell(0, 10, f"Date: {report_date}", 0, 1, 'C')
        pdf.cell(0, 10, f"Organization: {report_data.get('org', 'N/A')}", 0, 1, 'C')
        pdf.cell(0, 10, f"Author: {report_data.get('author', 'N/A')}", 0, 1, 'C')
        pdf.ln(25)

        if report_data.get('sections', {}).get('exec'):
            pdf.chapter_title('1. Executive Summary')
            summary_text = (
                f"This report details the analysis of {len(df)} groundwater samples to assess heavy metal contamination. "
                f"The average Heavy Metal Pollution Index (HMPI) across all sites was {df['HMPI'].mean():.2f}. "
                "This analysis identifies pollution hotspots and provides an overall water quality assessment based on established standards."
            )
            pdf.chapter_body(summary_text)
            pdf.add_summary_stats(df)

        if report_data.get('sections', {}).get('quality'):
            pdf.chapter_title('2. Overall Pollution Assessment')
            pdf.add_pollution_breakdown(df)
            pdf.add_graph('graph_2.png', 'Groundwater Quality Distribution')

        # --- Geospatial Insights Section ---
        if report_data.get('include_maps'):
            pdf.add_page()
            pdf.chapter_title('3. Geospatial Hotspots')
            pdf.chapter_body(
                "The following table lists the top 5 most contaminated locations based on their HMPI values. "
                "These areas should be considered high-priority for further investigation. The interactive map in the web tool provides a more detailed spatial analysis."
            )
            top_5_df = df.sort_values(by='HMPI', ascending=False).head(5)
            table_cols = {
                'Station Name': 'Station Name',
                'HMPI': 'HMPI',
                'Latitude': 'Latitude',
                'Longitude': 'Longitude'
            }
            col_widths = [80, 25, 35, 35]
            pdf.add_table(top_5_df, 'Top 5 Most Contaminated Sites', table_cols, col_widths)

        if report_data.get('recommendations'):
            pdf.chapter_title('4. Recommendations')
            recs_text = (
                "Based on the analysis, the following actions are recommended:\n\n"
                "1.  **Immediate Investigation:** Sites classified as 'Extremely Poor' or 'Very Poor' require immediate follow-up sampling to confirm contamination levels and identify specific sources.\n\n"
                "2.  **Remediation Planning:** For confirmed high-contamination areas, begin planning for remediation. Techniques such as pump-and-treat, in-situ chemical treatment, or phytoremediation should be evaluated.\n\n"
                "3.  **Public Health Advisory:** Issue advisories for communities relying on groundwater from the most contaminated sites. Provide alternative sources of safe drinking water.\n\n"
                "4.  **Long-Term Monitoring:** Establish a regular monitoring program for all sites to track pollution trends and assess the effectiveness of interventions."
            )
            pdf.chapter_body(recs_text)
        
        return bytes(pdf.output())