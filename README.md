JalSuchak - A tool for visualising and analysing Heavy Metal Water Pollution Indices

Background :-

The presence of heavy metals in drinking water, even at trace levels, poses significant health risks, making accurate and timely assessment critical for public safety and environmental monitoring. Although several indices exist for assessing heavy metal pollution, their manual computation is tedious, time-consuming, inconsistent, and vulnerable to human error due to the complexity and variability of formulas.

Proposed Solution :-

It is proposed to develop an automated, user-friendly application that can compute Heavy Metal Pollution Indices (HMPI) in groundwater using standard formulas with minimal manual intervention. This tool will streamline calculations, reduce errors, and provide reliable outputs for stakeholders.

Key Features :-

- Automated computation of heavy metal pollution indices using standard methodologies
- Integration of groundwater heavy metal concentration datasets with geo-coordinates
- Categorization of groundwater quality based on heavy metal presence
- User-friendly interface for scientists, researchers, and policymakers
- Reduction of manual effort and error-prone processes

Impact :-

The application will provide accessible and reliable insights into groundwater heavy metal contamination, enabling better decision-making, enhanced environmental monitoring, and improved public health protection.


Our Proposed Feature Ideas (Including Key Features) :-

1. Automated computation of heavy metal pollution indices using standard methodologies
2. Integration of groundwater heavy metal concentration datasets with geo-coordinates
3. Categorization of groundwater quality based on heavy metal presence
4. User-friendly interface for scientists, researchers, and policymakers
5. Reduction of manual effort and error-prone processes
6. Data graphs for analysing trends for set durations of time
7. User Signup/Login system to maintain and save a database uploaded by a user
8. Combining multiple data bases to produce a combined map for all HMPI calculation.


Roadmap for Prototype :-

1. Basic Data Processing Module (Done)
   Takes CSV or Excel as input and converts it to a DataFrame then validates and convert the data to standard form (Done)

2. HMPI Calculator Module. (Done)
   Categorize groundwater quality based on HMPI thresholds. (Done)

3. Generate a basic output file with HMPI Column added. (Done)

4. Good Looking UI. (Done)
   Result shown directly on webpage instead of separate spreadsheet. (Done).
   Makes it user-friendly for scientists, researchers, and policymakers. (Done)
   Validate and standardize geo-coordinates (Latitude/Longitude) for integration with maps. (Done)

5. Geopandas and Folium based Map for basic HMPI with colored values for quality index. (Done)

6. Add an Awareness page on website that informs the user about the effects of heavy metal contamination, and also a Did You Know Box on Home Page that Rotates through the effects.
   
7. Generate Maps and Trends based on Time Stamped Data.

8. Add the functionality to directly produce a report which combines the input data, HMPI, Map, Graphs, Trends etc into a single PDF for easy access or research.

9. Add User Signup/Login system to maintain and save a database uploaded by a user for multiple uses.

10. With consent from the user, use their database to produce a combined map for all HMPI calculation.

11. Add AI Integration to generate trends and recommend solution for each metal contamination.

12. Add PDF as a valid input for Data Processing.
Tech Stack :-
Front-end: HTML, CSS, JS

Back-end: Python (Pandas, Numpy, Flask)

Map: GeoPandas and Folium
