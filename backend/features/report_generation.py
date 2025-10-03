# backend/features/report_generation.py

from fpdf import FPDF
import pandas as pd
import os
from datetime import datetime

class PDF(FPDF):
    """
    Custom PDF class to handle headers, footers, and standardized styling.
    """
    def header(self):
        self.set_font('Arial', 'B', 12)
        # Add Logo if it exists
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
        self.set_font('Arial', 'B', 16)
        self.set_fill_color(220, 230, 240) # A softer blue
        self.cell(0, 10, title, 0, 1, 'L', fill=True)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 7, body)
        self.ln()
        
    def add_table(self, df, columns, col_widths):
        self.set_font('Arial', 'B', 9)
        # Header
        for i, header in enumerate(columns.values()):
            self.cell(col_widths[i], 10, header, 1, 0, 'C')
        self.ln()

        # Data
        self.set_font('Arial', '', 8)
        for _, row in df.iterrows():
            for i, key in enumerate(columns.keys()):
                value = row.get(key, 'N/A')
                if isinstance(value, float):
                    value = f"{value:.2f}"
                # Truncate long names to prevent cell overflow
                if len(str(value)) > 40:
                    value = str(value)[:37] + "..."
                self.cell(col_widths[i], 10, str(value), 1)
            self.ln()
        self.ln(8)

    def add_summary_stats(self, df, station_col):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 7, "Key Findings at a Glance:", 0, 1)
        self.set_font('Arial', '', 11)
        total_sites = len(df)
        avg_hmpi = df['HMPI'].mean()
        max_hmpi_row = df.loc[df['HMPI'].idxmax()]
        
        self.cell(0, 7, f"- Total Sites Analyzed: {total_sites}", 0, 1)
        self.cell(0, 7, f"- Average HMPI Score: {avg_hmpi:.2f}", 0, 1)
        self.cell(0, 7, f"- Most Contaminated Site: '{max_hmpi_row.get(station_col, 'N/A')}' (HMPI: {max_hmpi_row['HMPI']:.2f})", 0, 1)
        self.ln(5)

    def add_pollution_breakdown(self, df, pollution_col):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 7, "Site Classification Breakdown:", 0, 1)
        self.set_font('Arial', '', 11)
        pollution_counts = df[pollution_col].value_counts()
        for level, count in pollution_counts.items():
            self.cell(0, 7, f"- {level}: {count} sites ({count/len(df)*100:.1f}%)", 0, 1)
        self.ln(5)
        
    def add_graph(self, graph_name, title, description):
        self.add_page()
        self.chapter_title(title)
        self.chapter_body(description)
        graph_path = os.path.join(self.static_folder, f'images/graphs/{graph_name}')
        if os.path.exists(graph_path):
            self.image(graph_path, x=self.get_x() + 10, w=self.w - self.l_margin - self.r_margin - 20)
        else:
            self.set_font('Arial', 'I', 10)
            self.cell(0, 10, f"[Chart image '{graph_name}' not found]", 0, 1)
        self.ln(5)

class ReportGenerator:
    def generate_report(self, df, report_data, static_folder_path):
        pdf = PDF()
        pdf.static_folder = static_folder_path
        
        # --- Robust Column Name Detection ---
        station_col = 'Station Name' if 'Station Name' in df.columns else 'sample_id'
        pollution_col = 'Pollution Level' if 'Pollution Level' in df.columns else 'poll_level'
        
        # --- Page 1: Title and Summary ---
        pdf.add_page()
        pdf.set_font('Arial', 'B', 28)
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
                "This analysis identifies pollution hotspots and provides a data-driven water quality assessment."
            )
            pdf.chapter_body(summary_text)
            pdf.add_summary_stats(df, station_col)

        if report_data.get('sections', {}).get('quality'):
            pdf.chapter_title('2. Water Quality Assessment')
            pdf.add_pollution_breakdown(df, pollution_col)

        # --- Page 2: High-Risk Areas (Using Graph) ---
        pdf.add_page()
        pdf.chapter_title('3. High-Risk Locations')
        pdf.chapter_body(
            "The bar chart below visualizes the HMPI scores of the ten most polluted sites, making it easy to identify the locations with the most critical contamination levels. "
            "These sites should be prioritized for further action."
        )
        pdf.add_graph('graph_8.png', '', '')

        # --- Page 3: Geospatial Overview ---
        if report_data.get('include_maps'):
            pdf.add_page()
            pdf.chapter_title('4. Geospatial Hotspot Overview')
            pdf.chapter_body(
                "The image below is a static snapshot of the geospatial analysis, highlighting pollution hotspots. "
                "For an interactive experience, please use the map feature in the web application."
            )
            map_image_path = os.path.join(pdf.static_folder, 'images/map_screenshot.png')
            if os.path.exists(map_image_path):
                 pdf.image(map_image_path, x=pdf.get_x() + 10, w=pdf.w - pdf.l_margin - pdf.r_margin - 20)
            else:
                 pdf.cell(0, 10, "[Map screenshot not available. Please add a 'map_screenshot.png' to the images folder.]", 0, 1)

        # --- Subsequent Pages: All Graphical Insights ---
        self.add_graph(pdf, 'graph_1.png', 'Insight 1: HMPI Distribution', "This histogram reveals the frequency of different HMPI scores. A skew towards higher values indicates widespread pollution.")
        self.add_graph(pdf, 'graph_2.png', 'Insight 2: Overall Water Quality', "This pie chart provides a clear, at-a-glance breakdown of the percentage of sites falling into each pollution category.")
        self.add_graph(pdf, 'graph_3.png', 'Insight 3: HMPI Values by Sample', "This line chart displays the unique pollution signature of each sample, making it easy to spot anomalies and high-risk sites.")
        self.add_graph(pdf, 'graph_4.png', 'Insight 4: Key Heavy Metal Concentrations', "This chart compares the levels of key toxic metals (As, Cd, Cr) across samples, highlighting which sites exceed safe limits.")
        self.add_graph(pdf, 'graph_5.png', 'Insight 5: Metal Concentration Distributions', "These plots show the statistical distribution for individual heavy metals, helping to identify which metals have the most extreme outliers.")
        self.add_graph(pdf, 'graph_6.png', 'Insight 6: Correlation Matrix', "This heatmap shows which metals are most strongly correlated with a high HMPI. A strong correlation (brighter color) points to a primary driver of pollution.")
        self.add_graph(pdf, 'graph_7.png', 'Insight 7: PCA Analysis', "Principal Component Analysis (PCA) simplifies complex data, showing the combined variance and relationships between different heavy metals.")
        
        # --- Final Page: Contaminant Analysis & Recommendations ---
        pdf.add_page()
        pdf.chapter_title('8. Primary Contaminant Analysis')
        pdf.chapter_body("The table below identifies the top 5 heavy metals that, on average, contribute most significantly to the pollution index across all samples.")
        
        metal_columns = ['as', 'cd', 'cr', 'pb', 'hg', 'ni', 'cu', 'zn', 'mn', 'fe']
        existing_metals = [col for col in df.columns if col.lower() in metal_columns]
        
        if existing_metals:
            avg_concentrations = df[existing_metals].mean().sort_values(ascending=False).head(5)
            metal_df = pd.DataFrame(avg_concentrations, columns=['Average Concentration (mg/L)']).reset_index()
            metal_cols = {'index': 'Heavy Metal', 'Average Concentration (mg/L)': 'Avg. Conc. (mg/L)'}
            metal_widths = [80, 80]
            pdf.add_table(metal_df, metal_cols, metal_widths)

        if report_data.get('recommendations'):
            pdf.chapter_title('9. Recommendations')
            recs_text = (
                "1.  **Immediate Investigation:** Sites classified as 'Extremely Poor' or 'Very Poor' require immediate follow-up sampling and public health advisories.\n\n"
                "2.  **Source Identification:** For high-HMPI sites, investigate primary sources of contamination (e.g., industrial discharge, agricultural runoff).\n\n"
                "3.  **Remediation Planning:** Evaluate and implement suitable remediation techniques for the most affected areas.\n\n"
                "4.  **Long-Term Monitoring:** Establish a regular monitoring program to track pollution trends and assess interventions."
            )
            pdf.chapter_body(recs_text)
        
        return bytes(pdf.output())
    
    def add_graph(self, pdf, graph_name, title, description):
        pdf.add_page()
        pdf.chapter_title(title)
        pdf.chapter_body(description)
        graph_path = os.path.join(pdf.static_folder, f'images/graphs/{graph_name}')
        if os.path.exists(graph_path):
            pdf.image(graph_path, x=pdf.get_x() + 10, w=pdf.w - pdf.l_margin - pdf.r_margin - 20)
        else:
            pdf.set_font('Arial', 'I', 10)
            pdf.cell(0, 10, f"[Chart image '{graph_name}' not found]", 0, 1)
        pdf.ln(5)
